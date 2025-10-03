#!/usr/bin/env python3
"""
LOCAL vs PUBLISHED MCP PACKAGE COMPARISON TEST

This script tests both:
1. Your LOCAL development version (from main.py) 
2. The PUBLISHED PyPI package (sensortower-mcp)

And compares their behavior side-by-side to validate fixes.
"""

import asyncio
import importlib.util
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Tuple
import subprocess

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m' 
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class LocalVsPublishedTester:
    def __init__(self):
        self.results = {"local": {}, "published": {}}
        self.start_time = time.time()
        self.token = os.getenv("SENSOR_TOWER_API_TOKEN")
        
        # Import local version
        self.local_tools = self._import_local_tools()
        
        # Import published version
        self.published_tools = self._import_published_tools()
        
    def _import_local_tools(self):
        """Import MCP tools from local main.py"""
        try:
            main_path = Path(__file__).parent.parent / "main.py"
            spec = importlib.util.spec_from_file_location("main", main_path)
            main_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(main_module)
            return main_module
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to import local tools: {e}{Colors.END}")
            return None
    
    def _import_published_tools(self):
        """Import MCP tools from published package"""
        try:
            # Try to import published package
            import sensortower_mcp
            return sensortower_mcp
        except ImportError:
            print(f"{Colors.YELLOW}⚠️ Published package not installed. Installing...{Colors.END}")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "sensortower-mcp"])
                import sensortower_mcp
                return sensortower_mcp
            except Exception as e:
                print(f"{Colors.RED}❌ Failed to install/import published package: {e}{Colors.END}")
                return None

    def print_header(self, title: str):
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}🧪 {title}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
    
    def print_category(self, title: str):
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'─'*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}📂 {title}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'─'*60}{Colors.END}")
    
    def print_comparison(self, endpoint: str, local_result: tuple, published_result: tuple):
        """Print side-by-side comparison of local vs published results"""
        local_status, local_details, local_preview = local_result
        pub_status, pub_details, pub_preview = published_result
        
        # Determine if there's a difference
        is_different = (local_status != pub_status) or (local_details != pub_details)
        diff_marker = f"{Colors.BOLD}🔄 DIFF{Colors.END}" if is_different else "   "
        
        print(f"{diff_marker} {Colors.BOLD}{endpoint}{Colors.END}")
        
        # Local result
        local_symbol = {
            "PASS": f"{Colors.GREEN}✅",
            "FAIL": f"{Colors.RED}❌", 
            "WARN": f"{Colors.YELLOW}⚠️",
            "SKIP": f"{Colors.YELLOW}⏭️",
            "ERROR": f"{Colors.RED}💥"
        }.get(local_status, "❓")
        
        # Published result  
        pub_symbol = {
            "PASS": f"{Colors.GREEN}✅",
            "FAIL": f"{Colors.RED}❌", 
            "WARN": f"{Colors.YELLOW}⚠️",
            "SKIP": f"{Colors.YELLOW}⏭️",
            "ERROR": f"{Colors.RED}💥"
        }.get(pub_status, "❓")
        
        print(f"   📦 LOCAL:     {local_symbol} {local_details}{Colors.END}")
        print(f"   🌐 PUBLISHED: {pub_symbol} {pub_details}{Colors.END}")
        
        if local_preview and local_preview != pub_preview:
            print(f"   📋 LOCAL Preview:     {local_preview[:80]}...")
            print(f"   📋 PUBLISHED Preview: {pub_preview[:80]}...")
        elif local_preview:
            print(f"   📋 Preview: {local_preview[:80]}...")
        
        # Store results
        self.results["local"][endpoint] = local_result
        self.results["published"][endpoint] = published_result

    async def test_mcp_tool(self, tools_module, tool_name: str, params: Dict[str, Any]) -> Tuple[str, str, str]:
        """Test a single MCP tool and return (status, details, preview)"""
        if not tools_module:
            return ("ERROR", "Module not available", "")
            
        try:
            # Add auth token if needed
            if "auth_token" not in params and self.token:
                params["auth_token"] = self.token
            
            # Get the tool function
            if hasattr(tools_module, tool_name):
                tool_func = getattr(tools_module, tool_name)
            else:
                return ("ERROR", f"Tool {tool_name} not found", "")
            
            # Execute the tool
            if asyncio.iscoroutinefunction(tool_func):
                result = await tool_func(**params)
            else:
                result = tool_func(**params)
            
            # Analyze result
            if isinstance(result, dict):
                if "error" in result:
                    return ("FAIL", f"Error: {result['error']}", str(result))
                elif "errors" in result:
                    return ("FAIL", f"Errors: {result['errors']}", str(result))
                else:
                    return ("PASS", "Success", str(result)[:100])
            elif isinstance(result, list):
                return ("PASS", f"List with {len(result)} items", str(result)[:100])
            else:
                return ("PASS", "Success", str(result)[:100])
                
        except Exception as e:
            return ("ERROR", f"Exception: {str(e)}", "")

    async def test_utility_tools(self):
        """Test utility tools that don't require API calls"""
        self.print_category("Utility Tools (4)")
        
        tests = [
            ("mcp_sensortower_get_country_codes", {"random_string": "test"}),
            ("mcp_sensortower_get_category_ids", {"os": "ios"}),
            ("mcp_sensortower_get_chart_types", {"random_string": "test"}),
            ("mcp_sensortower_health_check", {"random_string": "test"}),
        ]
        
        for tool_name, params in tests:
            local_result = await self.test_mcp_tool(self.local_tools, tool_name, params)
            published_result = await self.test_mcp_tool(self.published_tools, tool_name, params)
            self.print_comparison(tool_name, local_result, published_result)

    async def test_app_analysis_tools(self):
        """Test App Analysis MCP tools"""
        self.print_category("App Analysis Tools (19)")
        
        if not self.token:
            print("⚠️ Skipping API tests - no token provided")
            return
        
        tests = [
            ("mcp_sensortower_get_app_metadata", {
                "os": "ios", "app_ids": "284882215", "country": "US"
            }),
            ("mcp_sensortower_search_entities", {
                "os": "ios", "entity_type": "app", "term": "weather", "limit": 3
            }),
            ("mcp_sensortower_get_download_estimates", {
                "os": "ios", "app_ids": "284882215", "countries": "US", 
                "start_date": "2024-01-01", "end_date": "2024-01-07"
            }),
            ("mcp_sensortower_get_revenue_estimates", {
                "os": "ios", "app_ids": "284882215", "countries": "US",
                "start_date": "2024-01-01", "end_date": "2024-01-07"
            }),
            ("mcp_sensortower_top_in_app_purchases", {
                "os": "ios", "app_ids": "284882215", "country": "US"
            }),
            ("mcp_sensortower_compact_sales_report_estimates", {
                "os": "ios", "start_date": "2024-01-01", "end_date": "2024-01-07",
                "app_ids": "284882215", "countries": "US"
            }),
            ("mcp_sensortower_category_ranking_summary", {
                "os": "ios", "app_id": "284882215", "country": "US"
            }),
            ("mcp_sensortower_get_creatives", {
                "os": "ios", "app_ids": "284882215", "start_date": "2024-01-01",
                "countries": "US", "networks": "facebook", "ad_types": "video"
            }),
            ("mcp_sensortower_get_impressions", {
                "os": "ios", "app_ids": "284882215", "start_date": "2024-01-01",
                "end_date": "2024-01-07", "countries": "US", "networks": "facebook"
            }),
            ("mcp_sensortower_impressions_rank", {
                "os": "ios", "app_ids": "284882215", "start_date": "2024-01-01",
                "end_date": "2024-01-07", "countries": "US"
            }),
            ("mcp_sensortower_get_usage_active_users", {
                "os": "ios", "app_ids": "284882215", "start_date": "2024-01-01",
                "end_date": "2024-01-07", "countries": "US"
            }),
            ("mcp_sensortower_get_category_history", {
                "os": "ios", "app_ids": "284882215", "category": "6005",
                "chart_type_ids": "topfreeapplications",
                "start_date": "2024-01-01", "end_date": "2024-01-07", "countries": "US"
            }),
            ("mcp_sensortower_app_analysis_retention", {
                "os": "ios", "app_ids": "284882215", "date_granularity": "monthly",
                "start_date": "2024-01-01"
            }),
            ("mcp_sensortower_downloads_by_sources", {
                "os": "ios", "app_ids": "284882215", "countries": "US",
                "start_date": "2024-01-01", "end_date": "2024-01-07"
            }),
            ("mcp_sensortower_app_analysis_demographics", {
                "os": "ios", "app_ids": "284882215", "date_granularity": "monthly",
                "start_date": "2024-01-01"
            }),
            ("mcp_sensortower_app_update_timeline", {
                "os": "ios", "app_id": "284882215", "country": "US"
            }),
            ("mcp_sensortower_version_history", {
                "os": "ios", "app_id": "284882215", "country": "US"
            }),
            ("mcp_sensortower_get_publisher_apps", {
                "os": "ios", "publisher_id": "284882218", "limit": 5
            }),
            ("mcp_sensortower_get_unified_publisher_apps", {
                "unified_id": "560c48b48ac350643900b82d"
            }),
            ("mcp_sensortower_get_app_ids_by_category", {
                "os": "ios", "category": "6005", "limit": 5
            }),
        ]
        
        for tool_name, params in tests:
            local_result = await self.test_mcp_tool(self.local_tools, tool_name, params)
            published_result = await self.test_mcp_tool(self.published_tools, tool_name, params)
            self.print_comparison(tool_name, local_result, published_result)

    async def test_store_marketing_tools(self):
        """Test Store Marketing MCP tools"""
        self.print_category("Store Marketing Tools (6)")
        
        if not self.token:
            print("⚠️ Skipping API tests - no token provided")
            return
            
        tests = [
            ("mcp_sensortower_get_featured_today_stories", {
                "country": "US", "start_date": "2024-01-01", "end_date": "2024-01-07"
            }),
            ("mcp_sensortower_get_featured_apps", {
                "category": "6005", "country": "US", "start_date": "2024-01-01"
            }),
            ("mcp_sensortower_get_featured_creatives", {
                "os": "ios", "app_id": "284882215", "countries": "US"
            }),
            ("mcp_sensortower_get_keywords", {
                "os": "ios", "app_ids": "284882215", "countries": "US"
            }),
            ("mcp_sensortower_get_reviews", {
                "os": "ios", "app_ids": "284882215", "countries": "US"
            }),
            ("mcp_sensortower_research_keyword", {
                "os": "ios", "term": "weather", "country": "US"
            }),
        ]
        
        for tool_name, params in tests:
            local_result = await self.test_mcp_tool(self.local_tools, tool_name, params)
            published_result = await self.test_mcp_tool(self.published_tools, tool_name, params)
            self.print_comparison(tool_name, local_result, published_result)

    async def test_market_analysis_tools(self):
        """Test Market Analysis MCP tools"""
        self.print_category("Market Analysis Tools (5)")
        
        if not self.token:
            print("⚠️ Skipping API tests - no token provided")
            return
            
        tests = [
            ("mcp_sensortower_get_category_rankings", {
                "os": "ios", "category": "6005", "chart_type": "topfreeapplications",
                "country": "US", "date": "2024-01-15"
            }),
            ("mcp_sensortower_get_top_and_trending", {
                "os": "ios", "comparison_attribute": "absolute", "time_range": "week",
                "measure": "units", "category": 6005, "date": "2024-01-01",
                "regions": "US", "device_type": "total"
            }),
            ("mcp_sensortower_get_top_publishers", {
                "os": "ios", "comparison_attribute": "absolute", "time_range": "month",
                "measure": "revenue", "category": 6005, "date": "2024-01-01",
                "country": "US"
            }),
            ("mcp_sensortower_get_store_summary", {
                "os": "ios", "start_date": "2024-01-01", "end_date": "2024-01-07"
            }),
        ]
        
        for tool_name, params in tests:
            local_result = await self.test_mcp_tool(self.local_tools, tool_name, params)
            published_result = await self.test_mcp_tool(self.published_tools, tool_name, params)
            self.print_comparison(tool_name, local_result, published_result)

    def generate_summary(self):
        """Generate comparison summary"""
        self.print_header("LOCAL vs PUBLISHED COMPARISON SUMMARY")
        
        local_results = self.results["local"]
        pub_results = self.results["published"]
        
        total_tests = len(local_results)
        improvements = 0
        regressions = 0
        
        print(f"📊 Total Tools Tested: {total_tests}")
        print(f"🔑 API Token: {'✅ Provided' if self.token else '❌ Missing'}")
        
        print(f"\n{Colors.BOLD}🔍 DETAILED COMPARISON:{Colors.END}")
        
        for tool in local_results:
            if tool not in pub_results:
                continue
                
            local_status = local_results[tool][0]
            pub_status = pub_results[tool][0]
            
            if local_status == "PASS" and pub_status in ["FAIL", "ERROR"]:
                improvements += 1
                print(f"   {Colors.GREEN}🎯 FIXED IN LOCAL:{Colors.END} {tool}")
                print(f"      Published: {pub_status} -> Local: {local_status}")
                
            elif local_status in ["FAIL", "ERROR"] and pub_status == "PASS":
                regressions += 1  
                print(f"   {Colors.RED}📉 REGRESSION:{Colors.END} {tool}")
                print(f"      Published: {pub_status} -> Local: {local_status}")
                
            elif local_status != pub_status:
                print(f"   {Colors.YELLOW}🔄 DIFFERENT:{Colors.END} {tool}")
                print(f"      Published: {pub_status} -> Local: {local_status}")
        
        print(f"\n{Colors.BOLD}📈 IMPROVEMENT SUMMARY:{Colors.END}")
        print(f"   {Colors.GREEN}✅ Tools Fixed Locally: {improvements}{Colors.END}")
        print(f"   {Colors.RED}❌ Regressions: {regressions}{Colors.END}")
        
        if improvements > 0:
            print(f"\n{Colors.GREEN}🎉 LOCAL VERSION HAS IMPROVEMENTS!{Colors.END}")
            print(f"   Your local fixes resolve {improvements} issues from the published version.")
        elif regressions > 0:
            print(f"\n{Colors.RED}⚠️  LOCAL VERSION HAS REGRESSIONS{Colors.END}")
            print("   Consider reviewing recent changes.")
        else:
            print(f"\n{Colors.BLUE}📋 VERSIONS ARE EQUIVALENT{Colors.END}")
            print("   No significant differences detected.")
        
        print(f"\n⏱️  Total runtime: {time.time() - self.start_time:.2f} seconds")

    async def run_comparison_tests(self):
        """Run all comparison tests"""
        self.print_header("LOCAL vs PUBLISHED MCP PACKAGE COMPARISON")
        
        print("🎯 Testing LOCAL development version vs PUBLISHED PyPI package")
        print(f"📦 Local: {'✅ Available' if self.local_tools else '❌ Failed to load'}")
        print(f"🌐 Published: {'✅ Available' if self.published_tools else '❌ Failed to load'}")
        
        if not self.local_tools or not self.published_tools:
            print("\n❌ Cannot run comparison - missing tools")
            return False
        
        # Run all test categories
        await self.test_utility_tools()
        await self.test_app_analysis_tools()
        await self.test_store_marketing_tools()
        await self.test_market_analysis_tools()
        
        # Generate summary
        self.generate_summary()
        
        return True

async def main():
    """Main entry point"""
    tester = LocalVsPublishedTester()
    
    try:
        success = await tester.run_comparison_tests()
        
        if success:
            print("\n🎉 Comparison completed successfully!")
        else:
            print("\n💡 Comparison could not complete.")
            
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
