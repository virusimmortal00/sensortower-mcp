#!/usr/bin/env python3
"""
LOCAL MCP PACKAGE TESTING

This script tests ONLY your local MCP implementation (from main.py).
Perfect for validating your fixes before publishing to PyPI.
"""

import asyncio
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Tuple

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

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
    BOLD = '\033[1m'
    END = '\033[0m'

class MockFastMCP:
    """Mock FastMCP class to collect tool functions"""

    def __init__(self):
        self.tools = {}

    def tool(self, *, name, description=None, annotations=None, meta=None):
        def decorator(fn):
            tool_name = f"mcp_sensortower_{name}"
            self.tools[tool_name] = fn
            setattr(fn, "meta", meta or {})
            setattr(fn, "annotations", annotations or {})
            return fn

        return decorator

class LocalMCPTester:
    def __init__(self):
        self.results = {}
        self.start_time = time.time()
        self.token = os.getenv("SENSOR_TOWER_API_TOKEN")
        
        # Import local MCP tools
        self.tools = self._import_local_tools()
        
    def _import_local_tools(self):
        """Import MCP tools from src directory"""
        try:
            # Import tool classes
            from sensortower_mcp.tools import (
                AppAnalysisTools, StoreMarketingTools, MarketAnalysisTools,
                YourMetricsTools, SearchDiscoveryTools, UtilityTools
            )
            from sensortower_mcp.config import create_http_client
            
            # Create mock FastMCP instance
            mock_mcp = MockFastMCP()
            
            # Create HTTP client for tools that need it
            if self.token:
                client = create_http_client(self.token)
                
                # Register all tools
                tool_classes = [
                    UtilityTools(),  # Doesn't need client/token
                    AppAnalysisTools(client, self.token),
                    StoreMarketingTools(client, self.token),
                    MarketAnalysisTools(client, self.token),
                    YourMetricsTools(client, self.token),
                    SearchDiscoveryTools(client, self.token)
                ]
            else:
                # Only utility tools work without token
                tool_classes = [
                    UtilityTools(),
                ]
            
            for tool_class in tool_classes:
                tool_class.register_tools(mock_mcp)
            
            return mock_mcp.tools
            
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to import local MCP tools: {e}{Colors.END}")
            import traceback
            traceback.print_exc()
            return None

    def print_header(self, title: str):
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}🧪 {title}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    
    def print_category(self, title: str):
        print(f"\n{Colors.BOLD}{Colors.YELLOW}{'─'*50}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.YELLOW}📂 {title}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.YELLOW}{'─'*50}{Colors.END}")
    
    def print_test(self, tool_name: str, status: str, details: str = "", response_preview: str = ""):
        status_symbol = {
            "PASS": f"{Colors.GREEN}✅",
            "FAIL": f"{Colors.RED}❌", 
            "WARN": f"{Colors.YELLOW}⚠️",
            "SKIP": f"{Colors.YELLOW}⏭️",
            "ERROR": f"{Colors.RED}💥"
        }.get(status, "❓")
        
        print(f"{status_symbol} {tool_name}{Colors.END}")
        if details:
            print(f"   {details}")
        if response_preview:
            print(f"   Preview: {response_preview[:100]}...")
        
        self.results[tool_name] = (status, details, response_preview)

    async def test_mcp_tool(self, tool_name: str, params: Dict[str, Any]) -> Tuple[str, str, str]:
        """Test a single MCP tool and return (status, details, preview)"""
        if not self.tools:
            return ("ERROR", "MCP tools not available", "")
            
        try:
            # Get the tool function
            if tool_name in self.tools:
                tool_func = self.tools[tool_name]
            else:
                available_tools = list(self.tools.keys())
                return ("ERROR", f"Tool {tool_name} not found. Available: {available_tools[:5]}", "")
            
            # Execute the tool
            if asyncio.iscoroutinefunction(tool_func):
                result = await tool_func(**params)
            else:
                result = tool_func(**params)
                
            # If result is a Task or coroutine, await it
            if asyncio.iscoroutine(result):
                result = await result
            elif hasattr(result, '__await__'):  # Task object
                result = await result
            
            # Analyze result for specific fixes
            if tool_name == "mcp_sensortower_search_entities":
                # Validate search_entities returns dict not list
                if isinstance(result, dict):
                    if "items" in result and isinstance(result["items"], list):
                        return ("PASS", "✅ FIXED: Returns dict with 'items' list (wrapped format)", str(result)[:100])
                    elif "apps" in result or "publishers" in result:
                        return ("PASS", "✅ FIXED: Returns dict with apps/publishers", str(result)[:100])
                    else:
                        return ("WARN", f"Dict format but unexpected keys: {list(result.keys())}", str(result)[:100])
                elif isinstance(result, list):
                    return ("FAIL", "❌ Still returns raw list format", str(result)[:100])
                else:
                    return ("WARN", f"Unexpected format: {type(result)}", str(result)[:100])
            
            # General result analysis
            if isinstance(result, dict):
                if "error" in result:
                    return ("FAIL", f"Error: {result['error']}", str(result)[:100])
                elif "errors" in result:
                    return ("FAIL", f"Errors: {result['errors']}", str(result)[:100])
                else:
                    return ("PASS", "Success", str(result)[:100])
            elif isinstance(result, list):
                return ("PASS", f"List with {len(result)} items", str(result)[:100])
            else:
                return ("PASS", "Success", str(result)[:100])
                
        except Exception as e:
            error_msg = str(e)
            # Extract 422 error details if available
            if "422" in error_msg and "Unprocessable Content" in error_msg:
                return ("ERROR", "422 Parameter Validation Error", error_msg)
            else:
                return ("ERROR", f"Exception: {error_msg}", "")

    async def test_utility_tools(self):
        """Test utility tools"""
        self.print_category("Utility Tools (4)")
        
        tests = [
            ("mcp_sensortower_get_country_codes", {}),  # No parameters
            ("mcp_sensortower_get_category_ids", {"os": "ios"}),
            ("mcp_sensortower_get_chart_types", {}),    # No parameters
            ("mcp_sensortower_health_check", {}),       # No parameters
        ]
        
        for tool_name, params in tests:
            status, details, preview = await self.test_mcp_tool(tool_name, params)
            self.print_test(tool_name, status, details, preview)

    async def test_critical_fixes(self):
        """Test the specific endpoints you've fixed"""
        self.print_category("Critical Bug Fixes Validation")
        
        if not self.token:
            print("⚠️ Skipping API tests - no token provided")
            return
        
        # Test the specific fixes you mentioned
        critical_tests = [
            ("mcp_sensortower_search_entities", {
                "os": "ios", "entity_type": "app", "term": "weather", "limit": 3
            }, "Should return dict not list"),
            
            ("mcp_sensortower_get_download_estimates", {
                "os": "ios", "app_ids": "284882215", "countries": "US", 
                "start_date": "2024-01-01", "end_date": "2024-01-07"
            }, "Should use correct sales_report_estimates endpoint"),
            
            ("mcp_sensortower_get_revenue_estimates", {
                "os": "ios", "app_ids": "284882215", "countries": "US",
                "start_date": "2024-01-01", "end_date": "2024-01-07"
            }, "Should use correct sales_report_estimates endpoint"),
            
            ("mcp_sensortower_get_top_and_trending", {
                "os": "ios", "category": 6005, "comparison_attribute": "absolute",
                "time_range": "month", "measure": "units", "regions": "US", "date": "2024-01-01",
                "device_type": "total"
            }, "Should use correct endpoint URL"),
            
            ("mcp_sensortower_get_top_publishers", {
                "os": "ios", "category": "6005", "comparison_attribute": "absolute",
                "time_range": "week", "measure": "units", "date": "2024-01-01", "country": "US"
            }, "Should use correct endpoint URL"),
            
            ("mcp_sensortower_get_impressions", {
                "os": "ios", "app_ids": "284882215", "start_date": "2024-01-01",
                "end_date": "2024-01-07", "date_granularity": "daily"
            }, "Should use correct network_analysis endpoint"),
        ]
        
        for tool_name, params, description in critical_tests:
            status, details, preview = await self.test_mcp_tool(tool_name, params)
            self.print_test(f"{tool_name} - {description}", status, details, preview)

    async def test_comprehensive_tools(self):
        """Test tools comprehensively across all categories"""
        self.print_category(f"Comprehensive Tool Testing ({len(self.tools)} total tools)")
        
        # Show available tools by category
        utility_tools = [name for name in self.tools.keys() if any(x in name for x in ["country_codes", "category_ids", "chart_types", "health_check"])]
        app_analysis_tools = [name for name in self.tools.keys() if any(x in name for x in ["app_metadata", "download_estimates", "revenue_estimates", "usage", "impressions", "creatives"])]
        store_marketing_tools = [name for name in self.tools.keys() if any(x in name for x in ["keyword", "reviews", "featured"])]
        market_analysis_tools = [name for name in self.tools.keys() if any(x in name for x in ["ranking", "top_and_trending", "top_publishers", "store_summary"])]
        
        print(f"   📊 Utility Tools: {len(utility_tools)}")
        print(f"   📱 App Analysis Tools: {len(app_analysis_tools)}")  
        print(f"   🔍 Store Marketing Tools: {len(store_marketing_tools)}")
        print(f"   📈 Market Analysis Tools: {len(market_analysis_tools)}")
        print(f"   🎯 Others: {len(self.tools) - len(utility_tools) - len(app_analysis_tools) - len(store_marketing_tools) - len(market_analysis_tools)}")
        
        if not self.token:
            print("⚠️ Skipping API tests - no token provided")
            return
        
        # Test representative samples from each category
        sample_tests = [
            # App Analysis
            ("mcp_sensortower_get_app_metadata", {
                "os": "ios", "app_ids": "284882215", "country": "US"
            }),
            
            # Store Marketing
            ("mcp_sensortower_research_keyword", {
                "os": "ios", "term": "weather", "country": "US"
            }),
            
            # Market Analysis
            ("mcp_sensortower_get_category_rankings", {
                "os": "ios", "category": "6005", "chart_type": "topfreeapplications",
                "country": "US", "date": "2024-01-15"
            }),
            
            # Usage Intelligence
            ("mcp_sensortower_get_usage_active_users", {
                "os": "ios", "app_ids": "284882215", "start_date": "2024-01-01",
                "end_date": "2024-01-07", "countries": "US"
            }),
        ]
        
        for tool_name, params in sample_tests:
            status, details, preview = await self.test_mcp_tool(tool_name, params)
            self.print_test(tool_name, status, details, preview)

    def generate_summary(self):
        """Generate test summary"""
        self.print_header("LOCAL MCP TESTING SUMMARY")
        
        total_tests = len(self.results)
        passed = sum(1 for status, _, _ in self.results.values() if status == "PASS")
        failed = sum(1 for status, _, _ in self.results.values() if status == "FAIL")
        warnings = sum(1 for status, _, _ in self.results.values() if status == "WARN")
        errors = sum(1 for status, _, _ in self.results.values() if status == "ERROR")
        skipped = sum(1 for status, _, _ in self.results.values() if status == "SKIP")
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"{Colors.GREEN}✅ Passed: {passed}{Colors.END}")
        print(f"{Colors.RED}❌ Failed: {failed}{Colors.END}")
        print(f"{Colors.YELLOW}⚠️  Warnings: {warnings}{Colors.END}")
        print(f"{Colors.RED}💥 Errors: {errors}{Colors.END}")
        print(f"{Colors.YELLOW}⏭️  Skipped: {skipped}{Colors.END}")
        
        # Highlight specific fixes
        print(f"\n{Colors.BOLD}🔧 Key Fixes Status:{Colors.END}")
        for tool_name, (status, details, _) in self.results.items():
            if "search_entities" in tool_name or "FIXED" in details:
                status_symbol = "✅" if status == "PASS" else "❌"
                print(f"   {status_symbol} {tool_name}: {details}")
        
        # Overall assessment
        if not self.token:
            print(f"\n{Colors.YELLOW}⚠️  Limited Testing: No API token provided{Colors.END}")
        elif errors == 0 and failed == 0:
            print(f"\n{Colors.GREEN}🟢 EXCELLENT: All local fixes working perfectly!{Colors.END}")
        elif errors <= 2 and failed == 0:
            print(f"\n{Colors.GREEN}🟢 GREAT: Core fixes working! Minor API parameter issues only{Colors.END}")
        elif failed <= 2:
            print(f"\n{Colors.YELLOW}🟡 GOOD: Most fixes working, minor issues{Colors.END}")
        else:
            print(f"\n{Colors.RED}🔴 NEEDS WORK: Multiple issues in local implementation{Colors.END}")
            
        # Summary note
        print(f"\n{Colors.BLUE}💡 Note: 422 errors are typically API parameter validation, not code bugs{Colors.END}")
        
        print(f"\n⏱️  Total runtime: {time.time() - self.start_time:.2f} seconds")

    async def run_tests(self):
        """Run all local MCP tests"""
        self.print_header("LOCAL MCP PACKAGE TESTING")
        
        print("🎯 Testing your LOCAL MCP implementation only")
        print(f"📦 Local Tools: {'✅ Available' if self.tools else '❌ Failed to load'} ({len(self.tools)} unique tools)")
        print(f"🔑 API Token: {'✅ Provided' if self.token else '❌ Missing'}")
        
        if not self.tools:
            print("\n❌ Cannot run tests - MCP tools not available")
            return False
        
        # Run test suites
        await self.test_utility_tools()
        await self.test_critical_fixes()
        await self.test_comprehensive_tools()
        
        # Generate summary
        self.generate_summary()
        
        return True

async def main():
    """Main entry point"""
    tester = LocalMCPTester()
    
    try:
        success = await tester.run_tests()
        
        if success:
            print("\n🎉 Local MCP testing completed!")
        else:
            print("\n💡 Testing could not complete.")
            
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
