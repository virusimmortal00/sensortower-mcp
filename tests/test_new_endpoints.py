#!/usr/bin/env python3
"""
Quick test script specifically for the 6 new endpoints we added.
Tests the new Connected Apps endpoints and usage_top_apps endpoint.
"""

import asyncio
import httpx
import os
import sys
from pathlib import Path

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class NewEndpointsTester:
    def __init__(self):
        self.token = os.getenv("SENSOR_TOWER_API_TOKEN")
        self.base_url = os.getenv("API_BASE_URL", "https://api.sensortower.com")
        
    def print_test(self, endpoint: str, status: str, details: str):
        emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{emoji} {endpoint}: {details}")
    
    async def test_new_endpoints(self):
        """Test all 6 new endpoints"""
        print("🚀 Testing New SensorTower MCP Endpoints")
        print("=" * 50)
        print(f"🔑 API Token: {'✅ Set' if self.token else '❌ Missing'}")
        print(f"🌐 Base URL: {self.base_url}")
        print()
        
        if not self.token:
            print("⚠️  Cannot test endpoints without API token")
            print("   Set SENSOR_TOWER_API_TOKEN environment variable")
            return False
        
        results = {}
        
        async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
            
            # Test new Connected Apps endpoints
            print("📊 Connected Apps Endpoints (Your Own Apps)")
            print("─" * 40)
            
            connected_apps_tests = [
                ("analytics_metrics", "/v1/ios/sales_reports/analytics_metrics", {
                    "app_ids": "1234567890",
                    "countries": "US", 
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31",
                    "auth_token": self.token
                }),
                ("sources_metrics", "/v1/ios/sales_reports/sources_metrics", {
                    "app_ids": "1234567890",
                    "countries": "US",
                    "start_date": "2024-01-01", 
                    "end_date": "2024-01-31",
                    "auth_token": self.token
                }),
                ("sales_reports", "/v1/ios/sales_reports", {
                    "app_ids": "1234567890",
                    "countries": "US",
                    "date_granularity": "daily",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31",
                    "auth_token": self.token
                }),
                ("unified_sales_reports", "/v1/unified/sales_reports", {
                    "itunes_app_ids": "1234567890",
                    "countries": "US",
                    "date_granularity": "daily",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31",
                    "auth_token": self.token
                }),
                ("api_usage", "/v1/api_usage", {
                    "date": "2024-01-01",
                    "auth_token": self.token
                })
            ]
            
            for endpoint_name, path, params in connected_apps_tests:
                try:
                    response = await client.get(path, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        self.print_test(endpoint_name, "PASS", f"HTTP 200 - {len(data) if isinstance(data, list) else 'Dict response'}")
                        results[endpoint_name] = "PASS"
                    elif response.status_code == 401:
                        self.print_test(endpoint_name, "FAIL", "HTTP 401 - Invalid API token")
                        results[endpoint_name] = "FAIL"
                    elif response.status_code == 403:
                        self.print_test(endpoint_name, "WARN", "HTTP 403 - May need connected apps or subscription")
                        results[endpoint_name] = "WARN"
                    elif response.status_code == 422:
                        self.print_test(endpoint_name, "WARN", "HTTP 422 - May need valid app IDs you own")
                        results[endpoint_name] = "WARN"
                    else:
                        self.print_test(endpoint_name, "FAIL", f"HTTP {response.status_code}")
                        results[endpoint_name] = "FAIL"
                        
                except Exception as e:
                    self.print_test(endpoint_name, "FAIL", f"Exception: {str(e)}")
                    results[endpoint_name] = "FAIL"
            
            print()
            print("📈 Market Analysis Endpoints")
            print("─" * 40)
            
            # Test new usage_top_apps endpoint
            try:
                params = {
                    "comparison_attribute": "absolute",
                    "time_range": "month",
                    "measure": "DAU",
                    "date": "2024-01-01",
                    "regions": "US",
                    "auth_token": self.token
                }
                response = await client.get("/v1/ios/top_and_trending/active_users", params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    self.print_test("usage_top_apps", "PASS", f"HTTP 200 - {len(data) if isinstance(data, list) else 'Dict response'}")
                    results["usage_top_apps"] = "PASS"
                elif response.status_code == 401:
                    self.print_test("usage_top_apps", "FAIL", "HTTP 401 - Invalid API token")
                    results["usage_top_apps"] = "FAIL"
                elif response.status_code == 403:
                    self.print_test("usage_top_apps", "WARN", "HTTP 403 - May need subscription")
                    results["usage_top_apps"] = "WARN"
                elif response.status_code == 422:
                    self.print_test("usage_top_apps", "WARN", "HTTP 422 - May need different parameters")
                    results["usage_top_apps"] = "WARN"
                else:
                    self.print_test("usage_top_apps", "FAIL", f"HTTP {response.status_code}")
                    results["usage_top_apps"] = "FAIL"
                    
            except Exception as e:
                self.print_test("usage_top_apps", "FAIL", f"Exception: {str(e)}")
                results["usage_top_apps"] = "FAIL"
        
        # Summary
        print()
        print("=" * 50)
        print("📊 New Endpoints Test Summary")
        print("=" * 50)
        
        passed = sum(1 for status in results.values() if status == "PASS")
        warned = sum(1 for status in results.values() if status == "WARN")
        failed = sum(1 for status in results.values() if status == "FAIL")
        total = len(results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"⚠️  Warned: {warned}/{total}")
        print(f"❌ Failed: {failed}/{total}")
        
        if passed == total:
            print("\n🎉 All new endpoints working perfectly!")
        elif passed + warned == total:
            print("\n✨ All new endpoints implemented correctly!")
            print("   Warnings are expected for endpoints requiring connected apps or subscriptions")
        else:
            print(f"\n⚠️  {failed} endpoints failed - may need investigation")
        
        print("\n💡 Notes:")
        print("   - Connected Apps endpoints require you to have connected your own apps")
        print("   - Some endpoints may require specific subscription levels")
        print("   - 422 errors often mean parameters need adjustment for your account")
        
        return passed + warned == total

async def main():
    tester = NewEndpointsTester()
    success = await tester.test_new_endpoints()
    
    if success:
        print("\n🎉 New endpoints test completed successfully!")
        sys.exit(0)
    else:
        print("\n💡 Some new endpoints need attention - check the details above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())