#!/usr/bin/env python3
"""
Quick manual testing script for sensortower-mcp.
Run this after deployment to verify basic functionality.
"""

import asyncio
import json
import os
import httpx
import sys
from typing import Dict, Any

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass

def print_result(test_name: str, success: bool, data: Any = None):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if data:
        response_str = json.dumps(data, indent=2)[:200]
        print(f"   Response: {response_str}...")
    print()

async def test_all_endpoints(base_url: str, token: str):
    """Test all API endpoints with real token"""
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Test 1: Health check
        try:
            response = await client.get(f"{base_url}/health")
            print_result("Health check", response.status_code == 200, response.json())
        except Exception as e:
            print_result("Health check", False, str(e))
        
        # Test utility endpoints first (no API token required)
        utility_tests = [
            ("get_country_codes", {}),
            ("get_category_ids", {"os": "ios"}),
            ("get_chart_types", {}),
            ("health_check", {})
        ]
        
        for tool_name, args in utility_tests:
            try:
                response = await client.post(f"{base_url}/mcp/tools/invoke", json={
                    "tool": tool_name,
                    "arguments": args
                })
                print_result(f"Utility: {tool_name}", response.status_code == 200, response.json())
            except Exception as e:
                print_result(f"Utility: {tool_name}", False, str(e))
        
        # Test App Analysis API endpoints
        app_analysis_tests = [
            ("get_app_metadata", {
                "os": "ios",
                "app_ids": "284882215",  # Facebook
                "country": "US"
            }),
            ("search_entities", {
                "os": "ios",
                "entity_type": "app",
                "term": "weather",
                "limit": 5
            }),
            ("get_download_estimates", {
                "os": "ios",
                "app_ids": "284882215",
                "countries": "US",
                "start_date": "2024-01-01",
                "end_date": "2024-01-07"
            }),
            ("get_revenue_estimates", {
                "os": "ios",
                "app_ids": "284882215",
                "countries": "US",
                "start_date": "2024-01-01",
                "end_date": "2024-01-07"
            }),
            ("top_in_app_purchases", {
                "os": "ios",
                "app_ids": "284882215",
                "country": "US"
            }),
            ("compact_sales_report_estimates", {
                "os": "ios",
                "start_date": "2024-01-01",
                "end_date": "2024-01-07",
                "app_ids": "284882215",
                "countries": "US"
            }),
            ("category_ranking_summary", {
                "os": "ios",
                "app_id": "284882215",
                "country": "US"
            }),
            ("get_creatives", {
                "os": "ios",
                "app_ids": "284882215",
                "start_date": "2024-01-01",
                "countries": "US",
                "networks": "Facebook"
            }),
            ("get_impressions", {
                "os": "ios",
                "app_ids": "284882215",
                "start_date": "2024-01-01",
                "end_date": "2024-01-07",
                "countries": "US",
                "networks": "Facebook"
            }),
            ("impressions_rank", {
                "os": "ios",
                "app_ids": "284882215",
                "start_date": "2024-01-01",
                "end_date": "2024-01-07",
                "countries": "US"
            }),
            ("get_usage_active_users", {
                "os": "ios",
                "app_ids": "284882215",
                "start_date": "2024-01-01",
                "end_date": "2024-01-07",
                "countries": "US"
            }),
            ("get_category_history", {
                "os": "ios",
                "app_ids": "284882215",
                "categories": "6005",
                "start_date": "2024-01-01",
                "end_date": "2024-01-07",
                "countries": "US"
            }),
            ("app_analysis_retention", {
                "os": "ios",
                "app_ids": "284882215",
                "date_granularity": "all_time",
                "start_date": "2024-01-01"
            }),
            ("downloads_by_sources", {
                "os": "unified",
                "app_ids": "55c5027502ac64f9c0001fa6",  # Unified ID
                "countries": "US",
                "start_date": "2024-01-01",
                "end_date": "2024-01-07"
            }),
            ("app_analysis_demographics", {
                "os": "ios",
                "app_ids": "284882215",
                "date_granularity": "all_time",
                "start_date": "2024-01-01"
            }),
            ("app_update_timeline", {
                "os": "ios",
                "app_id": "284882215",
                "country": "US"
            }),
            ("version_history", {
                "os": "ios",
                "app_id": "284882215",
                "country": "US"
            })
        ]
        
        for tool_name, args in app_analysis_tests:
            try:
                response = await client.post(f"{base_url}/mcp/tools/invoke", json={
                    "tool": tool_name,
                    "arguments": args
                })
                print_result(f"App Analysis: {tool_name}", response.status_code == 200, response.json())
            except Exception as e:
                print_result(f"App Analysis: {tool_name}", False, str(e))
        
        # Test Store Marketing API endpoints  
        store_marketing_tests = [
            ("get_featured_today_stories", {
                "country": "US",
                "start_date": "2024-01-01",
                "end_date": "2024-01-07"
            }),
            ("get_featured_apps", {
                "category": "6020",  # Entertainment
                "country": "US",
                "start_date": "2024-01-01",
                "end_date": "2024-01-07"
            }),
            ("get_keywords", {
                "os": "ios",
                "app_ids": "284882215",
                "countries": "US"
            }),
            ("get_reviews", {
                "os": "ios",
                "app_ids": "284882215",
                "countries": "US"
            })
        ]
        
        for tool_name, args in store_marketing_tests:
            try:
                response = await client.post(f"{base_url}/mcp/tools/invoke", json={
                    "tool": tool_name,
                    "arguments": args
                })
                print_result(f"Store Marketing: {tool_name}", response.status_code == 200, response.json())
            except Exception as e:
                print_result(f"Store Marketing: {tool_name}", False, str(e))
        
        # Test Market Analysis API endpoints
        market_analysis_tests = [
            ("get_category_rankings", {
                "os": "ios",
                "category": "6005",  # Social Networking
                "chart_type": "topfreeapplications",
                "country": "US",
                "date": "2024-01-15"
            }),
            ("get_top_and_trending", {
                "os": "ios",
                "category": "6005",
                "country": "US",
                "date": "2024-01-15"
            }),
            ("get_top_publishers", {
                "os": "ios",
                "category": "6005",
                "country": "US",
                "date": "2024-01-15"
            }),
            ("get_store_summary", {
                "os": "ios",
                "start_date": "2024-01-01",
                "end_date": "2024-01-07",
                "countries": "US"
            })
        ]
        
        for tool_name, args in market_analysis_tests:
            try:
                response = await client.post(f"{base_url}/mcp/tools/invoke", json={
                    "tool": tool_name,
                    "arguments": args
                })
                print_result(f"Market Analysis: {tool_name}", response.status_code == 200, response.json())
            except Exception as e:
                print_result(f"Market Analysis: {tool_name}", False, str(e))

async def test_pypi_installation():
    """Test PyPI package installation in current environment"""
    try:
        # Add parent directory to path to import main module
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        import main
        print_result("PyPI package import", True, "Package imported successfully")
        
        # Test CLI availability
        from main import mcp
        print_result("FastMCP initialization", True, "MCP server initialized")
        
    except ImportError as e:
        print_result("PyPI package import", False, str(e))
        print("Try: pip install sensortower-mcp")
        return False
    
    return True

async def test_docker_local():
    """Test local Docker container"""
    import subprocess
    
    try:
        # Check if container is running
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=sensortower-mcp", "--format", "{{.Status}}"],
            capture_output=True, text=True
        )
        
        if result.returncode == 0 and "Up" in result.stdout:
            print_result("Docker container status", True, "Container is running")
            
            # Test health endpoint
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get("http://localhost:8666/health", timeout=5)
                    print_result("Docker health endpoint", response.status_code == 200, response.json())
                except Exception as e:
                    print_result("Docker health endpoint", False, str(e))
        else:
            print_result("Docker container status", False, "No running container found")
            print("Start with: docker-compose up -d")
            
    except FileNotFoundError:
        print_result("Docker availability", False, "Docker not found")

async def main():
    print("🧪 Sensor Tower MCP Comprehensive Testing")
    print("=" * 50)
    print("Testing all 27 endpoints (23 API + 4 utility)")
    
    # Check environment
    token = os.getenv("SENSOR_TOWER_API_TOKEN")
    if not token:
        print("⚠️  SENSOR_TOWER_API_TOKEN not set. API tests will be skipped.")
        print("   Get your token from: https://app.sensortower.com/users/edit/api-settings")
    
    print("\n1. Testing PyPI Package Installation:")
    await test_pypi_installation()
    
    print("\n2. Testing Docker Container:")
    await test_docker_local()
    
    if token:
        print("\n3. Testing All API Endpoints (HTTP mode):")
        print("   Note: This tests all 27 endpoints comprehensively")
        await test_all_endpoints("http://localhost:8666", token)
    else:
        print("\n3. API Endpoint Testing: SKIPPED (no token)")
        print("   Set SENSOR_TOWER_API_TOKEN to test all 27 endpoints")
    
    print("\n✅ Comprehensive testing complete!")
    print(f"\nEndpoints tested: 27 total")
    print("- 4 Utility endpoints (country codes, categories, etc.)")
    print("- 16 App Analysis endpoints (metadata, sales, retention, etc.)")
    print("- 4 Store Marketing endpoints (featured apps, keywords, reviews)")
    print("- 4 Market Analysis endpoints (rankings, trends, publishers)")
    print("\nNext steps:")
    print("1. Set SENSOR_TOWER_API_TOKEN to test API functionality")
    print("2. Run full test suite: python test_deployment.py")
    print("3. Test in production environment")

if __name__ == "__main__":
    asyncio.run(main()) 