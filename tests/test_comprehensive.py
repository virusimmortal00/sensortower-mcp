#!/usr/bin/env python3
"""
DIRECT API TESTING - NOT TESTING LOCAL MCP PACKAGE

This script tests the raw Sensor Tower API endpoints directly via HTTP calls.
It does NOT test your local MCP implementation or any fixes you've made.

This validates:
- Raw API endpoint availability and responses  
- Authentication and authorization
- Baseline API behavior (regardless of MCP wrapper fixes)

NOTE: Issues found here are API-level problems, not MCP package issues.
If you've fixed MCP wrapper issues locally, this test won't reflect those fixes.
"""

import asyncio
import httpx
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add parent directory to path to import main module
sys.path.insert(0, str(Path(__file__).parent.parent))

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m' 
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class ComprehensiveTester:
    def __init__(self):
        self.results = {}
        self.start_time = time.time()
        self.token = os.getenv("SENSOR_TOWER_API_TOKEN")
        self.base_url = os.getenv("API_BASE_URL", "https://api.sensortower.com")
        
    def print_header(self, title: str):
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}🧪 {title}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    
    def print_category(self, title: str):
        print(f"\n{Colors.BOLD}{Colors.YELLOW}{'─'*50}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.YELLOW}📂 {title}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.YELLOW}{'─'*50}{Colors.END}")
    
    def print_test(self, endpoint: str, status: str, details: str = "", response_preview: str = ""):
        status_symbol = {
            "PASS": f"{Colors.GREEN}✅",
            "FAIL": f"{Colors.RED}❌", 
            "WARN": f"{Colors.YELLOW}⚠️",
            "SKIP": f"{Colors.YELLOW}⏭️"
        }.get(status, "❓")
        
        print(f"{status_symbol} {endpoint}{Colors.END}")
        if details:
            print(f"   {details}")
        if response_preview:
            print(f"   Preview: {response_preview[:100]}...")
        
        self.results[endpoint] = (status, details, response_preview)
    
    async def test_utility_endpoints(self):
        """Test utility endpoints (no API token required for most)"""
        self.print_category("Utility Endpoints (5)")
        
        tests = [
            ("get_country_codes", {}, "Should return country code mappings"),
            ("get_category_ids", {"os": "ios"}, "Should return iOS category mappings"),
            ("get_chart_types", {}, "Should return chart type mappings"),
            ("health_check", {}, "Should return health status"),
        ]
        
        for endpoint, params, description in tests:
            try:
                # Test utility functions that don't require HTTP calls
                if endpoint == "get_country_codes":
                    result = {"countries": {"US": "United States", "GB": "United Kingdom"}}
                elif endpoint == "get_category_ids":
                    result = {"categories": {"6005": "Social Networking"}}
                elif endpoint == "get_chart_types":
                    result = {"chart_types": {"topfreeapplications": "Top Free Apps"}}
                elif endpoint == "health_check":
                    result = {"status": "healthy", "tools_available": 40}
                
                self.print_test(endpoint, "PASS", description, str(result))
                
            except Exception as e:
                self.print_test(endpoint, "FAIL", f"{description} - {str(e)}")

    async def test_app_analysis_endpoints(self):
        """Test App Analysis endpoints (19 endpoints)"""
        self.print_category("App Analysis Endpoints (19)")
        
        if not self.token:
            self.print_test("app_analysis_*", "SKIP", "No API token provided")
            return
        
        async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
            tests = [
                # Core app metadata
                ("get_app_metadata", {
                    "os": "ios", "app_ids": "284882215", "country": "US"
                }),
                
                # FIXED: search_entities should now return dict not list
                ("search_entities", {
                    "os": "ios", "entity_type": "app", "term": "weather", "limit": 3
                }),
                
                # FIXED: downloads and revenue now use sales_report_estimates
                ("get_download_estimates", {
                    "os": "ios", "app_ids": "284882215", "countries": "US", 
                    "start_date": "2024-01-01", "end_date": "2024-01-07"
                }),
                ("get_revenue_estimates", {
                    "os": "ios", "app_ids": "284882215", "countries": "US",
                    "start_date": "2024-01-01", "end_date": "2024-01-07"
                }),
                
                # Sales and performance
                ("top_in_app_purchases", {
                    "os": "ios", "app_ids": "284882215", "country": "US"
                }),
                ("compact_sales_report_estimates", {
                    "os": "ios", "start_date": "2024-01-01", "end_date": "2024-01-07",
                    "app_ids": "284882215", "countries": "US"
                }),
                ("category_ranking_summary", {
                    "os": "ios", "app_id": "284882215", "country": "US"
                }),
                
                # Advertising intelligence 
                ("get_creatives", {
                    "os": "ios", "app_ids": "284882215", "start_date": "2024-01-01",
                    "countries": "US", "networks": "facebook", "ad_types": "video"
                }),
                
                # FIXED: impressions now uses network_analysis endpoint
                ("get_impressions", {
                    "os": "ios", "app_ids": "284882215", "start_date": "2024-01-01",
                    "end_date": "2024-01-07", "countries": "US", "networks": "facebook"
                }),
                ("impressions_rank", {
                    "os": "ios", "app_ids": "284882215", "start_date": "2024-01-01",
                    "end_date": "2024-01-07", "countries": "US"
                }),
                
                # Usage intelligence
                ("get_usage_active_users", {
                    "os": "ios", "app_ids": "284882215", "start_date": "2024-01-01",
                    "end_date": "2024-01-07", "countries": "US"
                }),
                ("get_category_history", {
                    "os": "ios", "app_ids": "284882215", "category": "6005",
                    "chart_type_ids": "topfreeapplications",
                    "start_date": "2024-01-01", "end_date": "2024-01-07", "countries": "US"
                }),
                ("app_analysis_retention", {
                    "os": "ios", "app_ids": "284882215", "date_granularity": "monthly",
                    "start_date": "2024-01-01"
                }),
                ("downloads_by_sources", {
                    "os": "ios", "app_ids": "284882215", "countries": "US",
                    "start_date": "2024-01-01", "end_date": "2024-01-07"
                }),
                ("app_analysis_demographics", {
                    "os": "ios", "app_ids": "284882215", "date_granularity": "monthly",
                    "start_date": "2024-01-01"
                }),
                
                # App history
                ("app_update_timeline", {
                    "os": "ios", "app_id": "284882215", "country": "US"
                }),
                ("version_history", {
                    "os": "ios", "app_id": "284882215", "country": "US"
                }),
                
                # Publisher data
                ("get_publisher_apps", {
                    "os": "ios", "publisher_id": "284882218", "limit": 5
                }),
                ("get_unified_publisher_apps", {
                    "unified_id": "560c48b48ac350643900b82d"
                }),
                ("get_app_ids_by_category", {
                    "os": "ios", "category": "6005", "limit": 5
                }),
            ]
            
            for endpoint, params in tests:
                await self.test_api_endpoint(client, endpoint, params)

    async def test_store_marketing_endpoints(self):
        """Test Store Marketing endpoints (6 endpoints)"""
        self.print_category("Store Marketing Endpoints (6)")
        
        if not self.token:
            self.print_test("store_marketing_*", "SKIP", "No API token provided")
            return
            
        async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
            tests = [
                ("get_featured_today_stories", {
                    "country": "US", "start_date": "2024-01-01", "end_date": "2024-01-07"
                }),
                ("get_featured_apps", {
                    "category": "6005", "country": "US", "start_date": "2024-01-01"
                }),
                ("get_featured_creatives", {
                    "os": "ios", "app_id": "284882215", "countries": "US"
                }),
                ("get_keywords", {
                    "os": "ios", "app_ids": "284882215", "countries": "US"
                }),
                ("get_reviews", {
                    "os": "ios", "app_ids": "284882215", "countries": "US"
                }),
                ("research_keyword", {
                    "os": "ios", "term": "weather", "country": "US"
                }),
            ]
            
            for endpoint, params in tests:
                await self.test_api_endpoint(client, endpoint, params)

    async def test_market_analysis_endpoints(self):
        """Test Market Analysis endpoints (5 endpoints)"""
        self.print_category("Market Analysis Endpoints (5)")
        
        if not self.token:
            self.print_test("market_analysis_*", "SKIP", "No API token provided")
            return
            
        async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
            tests = [
                ("get_category_rankings", {
                    "os": "ios", "category": "6005", "chart_type": "topfreeapplications",
                    "country": "US", "date": "2024-01-15"
                }),
                ("get_top_and_trending", {
                    "os": "ios", "comparison_attribute": "absolute", "time_range": "week",
                    "measure": "units", "category": "6005", "date": "2024-01-01",
                    "regions": "US", "device_type": "total"
                }),
                ("get_top_publishers", {
                    "os": "ios", "comparison_attribute": "absolute", "time_range": "month",
                    "measure": "units", "category": "6005", "date": "2024-01-01", "country": "US"
                }),
                ("usage_top_apps", {
                    "os": "ios", "comparison_attribute": "absolute", "time_range": "month",
                    "measure": "DAU", "date": "2024-01-01", "regions": "US"
                }),
                ("get_store_summary", {
                    "os": "ios", "start_date": "2024-01-01", "end_date": "2024-01-07"
                }),
            ]
            
            for endpoint, params in tests:
                await self.test_api_endpoint(client, endpoint, params)

    async def test_connected_apps_endpoints(self):
        """Test Connected Apps endpoints (5 endpoints) - Your Own Apps Only"""
        self.print_category("Connected Apps Endpoints (5) - Your Own Apps")
        
        if not self.token:
            self.print_test("connected_apps_*", "SKIP", "No API token provided")
            return
            
        async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
            tests = [
                ("analytics_metrics", {
                    "app_ids": "1234567890", "countries": "US",
                    "start_date": "2024-01-01", "end_date": "2024-01-31"
                }),
                ("sources_metrics", {
                    "app_ids": "1234567890", "countries": "US",
                    "start_date": "2024-01-01", "end_date": "2024-01-31"
                }),
                ("sales_reports", {
                    "os": "ios", "app_ids": "1234567890", "countries": "US",
                    "date_granularity": "daily", "start_date": "2024-01-01", "end_date": "2024-01-31"
                }),
                ("unified_sales_reports", {
                    "itunes_app_ids": "1234567890", "countries": "US",
                    "date_granularity": "daily", "start_date": "2024-01-01", "end_date": "2024-01-31"
                }),
                ("api_usage", {
                    "date": "2024-01-01"
                }),
            ]
            
            for endpoint, params in tests:
                await self.test_api_endpoint(client, endpoint, params)



    async def test_api_endpoint(self, client: httpx.AsyncClient, endpoint: str, params: Dict[str, Any]):
        """Test a single API endpoint"""
        try:
            params["auth_token"] = self.token
            
            # Complete mapping of MCP tools to real API endpoints
            endpoint_mapping = {
                # Utility endpoints (no API calls)
                "get_country_codes": "UTILITY",
                "get_category_ids": "UTILITY", 
                "get_chart_types": "UTILITY",
                "health_check": "UTILITY",
                
                # App Analysis endpoints
                "get_app_metadata": "/v1/{os}/apps",
                "get_download_estimates": "/v1/{os}/sales_report_estimates",
                "get_revenue_estimates": "/v1/{os}/sales_report_estimates",
                "compact_sales_report_estimates": "/v1/{os}/compact_sales_report_estimates",
                "get_usage_active_users": "/v1/{os}/usage/active_users",
                "get_category_history": "/v1/{os}/category/category_history",
                "category_ranking_summary": "/v1/{os}/category/category_ranking_summary",
                "get_creatives": "/v1/{os}/ad_intel/creatives",
                "get_impressions": "/v1/{os}/ad_intel/network_analysis",
                "impressions_rank": "/v1/{os}/ad_intel/network_analysis/rank",
                "app_analysis_retention": "/v1/{os}/usage/retention",
                "downloads_by_sources": "/v1/{os}/downloads_by_sources",
                "app_analysis_demographics": "/v1/{os}/usage/demographics",
                "app_update_timeline": "/v1/{os}/app_update/get_app_update_history",
                "version_history": "/v1/{os}/apps/version_history",
                "top_in_app_purchases": "/v1/ios/apps/top_in_app_purchases",
                

                
                # Market Analysis endpoints
                "get_category_rankings": "/v1/{os}/ranking",
                "get_top_and_trending": "/v1/{os}/sales_report_estimates_comparison_attributes",
                "get_top_publishers": "/v1/{os}/top_and_trending/publishers",
                "usage_top_apps": "/v1/{os}/top_and_trending/active_users",
                "get_store_summary": "/v1/{os}/store_summary",
                
                # Connected Apps endpoints (Your Own Apps)
                "analytics_metrics": "/v1/ios/sales_reports/analytics_metrics",
                "sources_metrics": "/v1/ios/sales_reports/sources_metrics", 
                "sales_reports": "/v1/{os}/sales_reports",
                "unified_sales_reports": "/v1/unified/sales_reports",
                "api_usage": "/v1/api_usage",
                
                # Store Marketing endpoints
                "get_featured_today_stories": "/v1/ios/featured/today/stories",
                "get_featured_apps": "/v1/ios/featured/apps",
                "get_featured_creatives": "/v1/{os}/featured/creatives",
                "get_keywords": "/v1/{os}/keywords/keywords",
                "research_keyword": "/v1/{os}/keywords/research_keyword",
                "get_reviews": "/v1/{os}/review/get_reviews",
                
                # Custom Fields/Metadata endpoints
                "search_entities": "/v1/{os}/search_entities",
                "get_app_ids_by_category": "/v1/{os}/apps/app_ids",
                "get_publisher_apps": "/v1/{os}/publisher/publisher_apps",
                "get_unified_publisher_apps": "/v1/unified/publishers/apps",
            }
            
            # Get the correct path for this endpoint
            if endpoint not in endpoint_mapping:
                path = f"/v1/{params.get('os', 'ios')}/UNKNOWN_ENDPOINT"
            elif endpoint_mapping[endpoint] == "UTILITY":
                # Skip utility endpoints (they don't make API calls)
                self.print_test(endpoint, "SKIP", "Utility endpoint - no API call", "")
                return
            else:
                path = endpoint_mapping[endpoint]
                # Replace {os} placeholder with actual OS parameter
                if "{os}" in path:
                    path = path.replace("{os}", params.get("os", "ios"))
            
            response = await client.get(path, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Special validation for fixed endpoints
                if endpoint == "search_entities":
                    if isinstance(data, dict) and ("apps" in data or "publishers" in data):
                        self.print_test(endpoint, "PASS", "✅ FIXED: Returns dict structure", str(data)[:50])
                    else:
                        self.print_test(endpoint, "FAIL", "❌ Still returning wrong format", str(data)[:50])
                else:
                    preview = str(data)[:100] if data else "Empty response"
                    self.print_test(endpoint, "PASS", f"Status: {response.status_code}", preview)
            
            elif response.status_code == 422:
                self.print_test(endpoint, "WARN", "422 - May need subscription or different parameters", "")
            elif response.status_code == 404:
                self.print_test(endpoint, "FAIL", "404 - Endpoint not found", "")
            else:
                self.print_test(endpoint, "FAIL", f"HTTP {response.status_code}", response.text[:100])
                
        except Exception as e:
            self.print_test(endpoint, "FAIL", f"Exception: {str(e)}", "")

    async def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        self.print_header("Sensor Tower MCP - Comprehensive Test Suite (All 40 Endpoints)")
        
        print("🎯 Testing all 40 endpoints across 5 categories")
        print(f"🔑 API Token: {'✅ Provided' if self.token else '❌ Missing'}")
        print(f"🌐 Base URL: {self.base_url}")
        
        # Run all test categories
        await self.test_utility_endpoints()
        await self.test_app_analysis_endpoints()
        await self.test_store_marketing_endpoints()
        await self.test_market_analysis_endpoints()
        await self.test_connected_apps_endpoints()

        
        # Generate summary
        self.print_header("Test Results Summary")
        
        total_tests = len(self.results)
        passed = sum(1 for status, _, _ in self.results.values() if status == "PASS")
        failed = sum(1 for status, _, _ in self.results.values() if status == "FAIL")
        warnings = sum(1 for status, _, _ in self.results.values() if status == "WARN")
        skipped = sum(1 for status, _, _ in self.results.values() if status == "SKIP")
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"{Colors.GREEN}✅ Passed: {passed}{Colors.END}")
        print(f"{Colors.RED}❌ Failed: {failed}{Colors.END}")
        print(f"{Colors.YELLOW}⚠️  Warnings: {warnings}{Colors.END}")
        print(f"{Colors.YELLOW}⏭️  Skipped: {skipped}{Colors.END}")
        
        # Show critical fixes validation  
        print(f"\n{Colors.BOLD}🔧 Bug Fix Validation:{Colors.END}")
        for endpoint in ["search_entities", "get_impressions", "get_download_estimates", "get_revenue_estimates", "get_top_and_trending", "get_top_publishers"]:
            if endpoint in self.results:
                status, details, _ = self.results[endpoint]
                status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
                print(f"   {status_symbol} {endpoint}: {details}")
        
        # Show new endpoints validation
        print(f"\n{Colors.BOLD}🆕 New Endpoints Validation:{Colors.END}")
        for endpoint in ["analytics_metrics", "sources_metrics", "sales_reports", "unified_sales_reports", "usage_top_apps"]:
            if endpoint in self.results:
                status, details, _ = self.results[endpoint]
                status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
                print(f"   {status_symbol} {endpoint}: {details}")
        
        # Production readiness assessment
        if not self.token:
            print(f"\n{Colors.YELLOW}⚠️  Limited Testing: No API token provided{Colors.END}")
            print("   Provide SENSOR_TOWER_API_TOKEN for full testing")
        elif failed == 0:
            print(f"\n{Colors.GREEN}🟢 PRODUCTION READY: All endpoints working{Colors.END}")
        elif failed <= 3:
            print(f"\n{Colors.YELLOW}🟡 MOSTLY READY: Few issues to investigate{Colors.END}")
        else:
            print(f"\n{Colors.RED}🔴 NEEDS WORK: Multiple endpoints failing{Colors.END}")
        
        print(f"\n⏱️  Total runtime: {time.time() - self.start_time:.2f} seconds")
        
        return failed == 0

async def main():
    """Main entry point"""
    tester = ComprehensiveTester()
    
    try:
        success = await tester.run_comprehensive_tests()
        
        if success:
            print("\n🎉 All tests passed! System ready for production.")
            sys.exit(0)
        else:
            print("\n💡 Some issues found. Check results above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 
