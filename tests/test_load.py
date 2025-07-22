#!/usr/bin/env python3
"""
Load testing script for sensortower-mcp to ensure it can handle production traffic.
"""

import asyncio
import aiohttp
import time
import json
import os
import statistics
from dataclasses import dataclass
from typing import List, Dict, Any

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass

@dataclass
class TestResult:
    success: bool
    response_time: float
    status_code: int
    error: str = ""

class LoadTester:
    def __init__(self, base_url: str, token: str = None):
        self.base_url = base_url
        self.token = token
        self.results: List[TestResult] = []
    
    async def make_request(self, session: aiohttp.ClientSession, endpoint: str, payload: Dict[str, Any]) -> TestResult:
        """Make a single request and record results"""
        start_time = time.time()
        
        try:
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            
            async with session.post(f"{self.base_url}{endpoint}", 
                                  json=payload, 
                                  headers=headers,
                                  timeout=aiohttp.ClientTimeout(total=30)) as response:
                await response.read()  # Consume response
                response_time = time.time() - start_time
                
                return TestResult(
                    success=response.status == 200,
                    response_time=response_time,
                    status_code=response.status
                )
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                success=False,
                response_time=response_time,
                status_code=0,
                error=str(e)
            )
    
    async def test_health_endpoint(self, session: aiohttp.ClientSession) -> TestResult:
        """Test health endpoint"""
        start_time = time.time()
        try:
            async with session.get(f"{self.base_url}/health", 
                                 timeout=aiohttp.ClientTimeout(total=10)) as response:
                await response.read()
                response_time = time.time() - start_time
                return TestResult(
                    success=response.status == 200,
                    response_time=response_time,
                    status_code=response.status
                )
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                success=False,
                response_time=response_time,
                status_code=0,
                error=str(e)
            )
    
    async def run_concurrent_tests(self, num_concurrent: int, num_requests: int):
        """Run concurrent load tests"""
        print(f"🚀 Running {num_requests} requests with {num_concurrent} concurrent connections")
        
        # Test scenarios
        test_scenarios = [
            {
                "name": "Health Check",
                "weight": 0.4,  # 40% of requests
                "endpoint": "/health",
                "method": "health"
            },
            {
                "name": "Get Country Codes",
                "weight": 0.3,  # 30% of requests
                "endpoint": "/mcp/tools/invoke",
                "payload": {
                    "tool": "get_country_codes",
                    "arguments": {}
                }
            },
            {
                "name": "Get Category IDs",
                "weight": 0.2,  # 20% of requests
                "endpoint": "/mcp/tools/invoke", 
                "payload": {
                    "tool": "get_category_ids",
                    "arguments": {"os": "ios"}
                }
            },
            {
                "name": "Search Entities",
                "weight": 0.1,  # 10% of requests (most expensive)
                "endpoint": "/mcp/tools/invoke",
                "payload": {
                    "tool": "search_entities",
                    "arguments": {
                        "os": "ios",
                        "entity_type": "app", 
                        "term": "test",
                        "limit": 5
                    }
                }
            }
        ]
        
        # Generate request distribution
        requests_to_make = []
        for scenario in test_scenarios:
            count = int(num_requests * scenario["weight"])
            requests_to_make.extend([scenario] * count)
        
        # Fill to exact number
        while len(requests_to_make) < num_requests:
            requests_to_make.append(test_scenarios[0])  # Fill with health checks
        
        async with aiohttp.ClientSession() as session:
            # Create semaphore to limit concurrent connections
            semaphore = asyncio.Semaphore(num_concurrent)
            
            async def make_single_request(scenario):
                async with semaphore:
                    if scenario.get("method") == "health":
                        return await self.test_health_endpoint(session)
                    else:
                        return await self.make_request(session, scenario["endpoint"], scenario["payload"])
            
            start_time = time.time()
            
            # Execute all requests concurrently
            tasks = [make_single_request(scenario) for scenario in requests_to_make]
            results = await asyncio.gather(*tasks)
            
            total_time = time.time() - start_time
            
            self.results.extend(results)
            
            # Analyze results
            self.print_results(total_time, num_requests, num_concurrent)
    
    def print_results(self, total_time: float, num_requests: int, num_concurrent: int):
        """Print load test results"""
        successful_requests = [r for r in self.results if r.success]
        failed_requests = [r for r in self.results if not r.success]
        
        print(f"\n📊 Load Test Results")
        print(f"=" * 50)
        print(f"Total Requests: {num_requests}")
        print(f"Concurrent Connections: {num_concurrent}")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Requests per Second: {num_requests / total_time:.2f}")
        print(f"Successful Requests: {len(successful_requests)} ({len(successful_requests)/num_requests*100:.1f}%)")
        print(f"Failed Requests: {len(failed_requests)} ({len(failed_requests)/num_requests*100:.1f}%)")
        
        if successful_requests:
            response_times = [r.response_time for r in successful_requests]
            print(f"\n⏱️  Response Time Statistics:")
            print(f"Average: {statistics.mean(response_times):.3f}s")
            print(f"Median: {statistics.median(response_times):.3f}s")
            print(f"95th percentile: {sorted(response_times)[int(len(response_times) * 0.95)]:.3f}s")
            print(f"Min: {min(response_times):.3f}s")
            print(f"Max: {max(response_times):.3f}s")
        
        if failed_requests:
            print(f"\n❌ Failed Request Details:")
            error_counts = {}
            for req in failed_requests:
                key = f"Status {req.status_code}: {req.error}"
                error_counts[key] = error_counts.get(key, 0) + 1
            
            for error, count in error_counts.items():
                print(f"  {error}: {count} requests")
        
        # Performance recommendations
        print(f"\n💡 Performance Assessment:")
        if len(successful_requests) / num_requests >= 0.99:
            print("✅ Excellent reliability (>99% success rate)")
        elif len(successful_requests) / num_requests >= 0.95:
            print("⚠️  Good reliability (>95% success rate)")
        else:
            print("❌ Poor reliability (<95% success rate)")
        
        if successful_requests:
            avg_response = statistics.mean([r.response_time for r in successful_requests])
            if avg_response < 0.1:
                print("✅ Excellent response times (<100ms average)")
            elif avg_response < 0.5:
                print("✅ Good response times (<500ms average)")
            elif avg_response < 1.0:
                print("⚠️  Acceptable response times (<1s average)")
            else:
                print("❌ Poor response times (>1s average)")
        
        rps = num_requests / total_time
        if rps > 100:
            print("✅ High throughput (>100 RPS)")
        elif rps > 50:
            print("✅ Good throughput (>50 RPS)")
        elif rps > 10:
            print("⚠️  Moderate throughput (>10 RPS)")
        else:
            print("❌ Low throughput (<10 RPS)")

async def test_docker_container():
    """Test Docker container under load"""
    print("🐳 Testing Docker Container")
    tester = LoadTester("http://localhost:8666")
    
    # Light load test
    await tester.run_concurrent_tests(num_concurrent=10, num_requests=100)
    
    # Reset results for medium test
    tester.results = []
    
    # Medium load test
    print(f"\n" + "="*50)
    await tester.run_concurrent_tests(num_concurrent=25, num_requests=250)

async def test_pypi_http_server():
    """Test PyPI package HTTP server under load"""
    print("📦 Testing PyPI Package HTTP Server")
    print("Note: Start server with 'sensortower-mcp --transport http --port 8667'")
    
    tester = LoadTester("http://localhost:8667")
    
    # Test connection first
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("http://localhost:8667/health", timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status != 200:
                    print("❌ Server not responding. Please start the server first.")
                    return
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            print("Start with: sensortower-mcp --transport http --port 8667")
            return
    
    # Light load test
    await tester.run_concurrent_tests(num_concurrent=10, num_requests=100)

async def main():
    print("🔥 Sensor Tower MCP Load Testing")
    print("=" * 50)
    
    token = os.getenv("SENSOR_TOWER_API_TOKEN")
    if not token:
        print("⚠️  SENSOR_TOWER_API_TOKEN not set. API endpoints may not work.")
        print("   Some tests will use mock data only.")
    
    print("\nSelect test scenario:")
    print("1. Test Docker container (localhost:8666)")
    print("2. Test PyPI HTTP server (localhost:8667)")
    print("3. Test custom endpoint")
    print("4. Run all tests")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        await test_docker_container()
    elif choice == "2":
        await test_pypi_http_server()
    elif choice == "3":
        url = input("Enter base URL (e.g., http://localhost:8666): ").strip()
        tester = LoadTester(url, token)
        concurrent = int(input("Concurrent connections (default 10): ") or "10")
        requests = int(input("Total requests (default 100): ") or "100")
        await tester.run_concurrent_tests(concurrent, requests)
    elif choice == "4":
        await test_docker_container()
        print("\n" + "="*70)
        await test_pypi_http_server()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    asyncio.run(main()) 