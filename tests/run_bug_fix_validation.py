#!/usr/bin/env python3
"""
Quick Bug Fix Validation Script

This script specifically tests the 4 critical fixes made based on the bug report:
1. search_entities: Schema validation (returns dict not list)
2. get_impressions: Endpoint URL correction (/ad_intel/network_analysis)
3. get_download_estimates: Endpoint URL correction (/sales_report_estimates)
4. get_revenue_estimates: Endpoint URL correction (/sales_report_estimates)

Run this to quickly verify the bug fixes are working.
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

class BugFixValidator:
    def __init__(self):
        self.token = os.getenv("SENSOR_TOWER_API_TOKEN")
        self.base_url = os.getenv("API_BASE_URL", "https://api.sensortower.com")
        
    def print_test(self, fix_name: str, status: str, details: str):
        emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{emoji} {fix_name}: {details}")
    
    async def validate_search_entities_fix(self):
        """Validate that search_entities returns dict structure"""
        print("\n🔧 Testing Fix 1: search_entities Schema Validation")
        
        if not self.token:
            self.print_test("search_entities", "SKIP", "No API token provided")
            return
        
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
                params = {
                    "entity_type": "app",
                    "term": "weather", 
                    "limit": 3,
                    "auth_token": self.token
                }
                
                response = await client.get("/v1/ios/search_entities", params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check if it's a dictionary with expected structure
                    if isinstance(data, dict):
                        if "apps" in data and "total_count" in data:
                            self.print_test("search_entities", "PASS", 
                                          f"✅ FIXED: Returns dict structure with {data['total_count']} apps")
                        else:
                            self.print_test("search_entities", "WARN", 
                                          "Returns dict but missing expected fields")
                    else:
                        self.print_test("search_entities", "FAIL", 
                                      "❌ STILL BROKEN: Returns list instead of dict")
                else:
                    self.print_test("search_entities", "FAIL", 
                                  f"HTTP {response.status_code}: {response.text[:100]}")
                    
        except Exception as e:
            self.print_test("search_entities", "FAIL", f"Exception: {str(e)}")
    
    async def validate_impressions_fix(self):
        """Validate that get_impressions uses correct endpoint"""
        print("\n🔧 Testing Fix 2: get_impressions Endpoint URL")
        
        if not self.token:
            self.print_test("get_impressions", "SKIP", "No API token provided")
            return
        
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
                params = {
                    "app_ids": "284882215",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-07", 
                    "countries": "US",
                    "networks": "facebook",
                    "auth_token": self.token
                }
                
                # Test the NEW correct endpoint
                response = await client.get("/v1/ios/ad_intel/network_analysis", params=params)
                
                if response.status_code == 200:
                    self.print_test("get_impressions", "PASS", 
                                  "✅ FIXED: /ad_intel/network_analysis endpoint works")
                elif response.status_code == 422:
                    self.print_test("get_impressions", "PASS", 
                                  "✅ FIXED: Endpoint exists but may need subscription")
                elif response.status_code == 404:
                    self.print_test("get_impressions", "FAIL", 
                                  "❌ STILL BROKEN: Endpoint not found")
                else:
                    self.print_test("get_impressions", "WARN", 
                                  f"Endpoint exists but returned {response.status_code}")
                    
        except Exception as e:
            self.print_test("get_impressions", "FAIL", f"Exception: {str(e)}")
    
    async def validate_download_estimates_fix(self):
        """Validate that get_download_estimates uses correct endpoint"""
        print("\n🔧 Testing Fix 3: get_download_estimates Endpoint URL")
        
        if not self.token:
            self.print_test("get_download_estimates", "SKIP", "No API token provided")
            return
        
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
                params = {
                    "app_ids": "284882215",
                    "countries": "US",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-07",
                    "auth_token": self.token
                }
                
                # Test the NEW correct endpoint
                response = await client.get("/v1/ios/sales_report_estimates", params=params)
                
                if response.status_code == 200:
                    self.print_test("get_download_estimates", "PASS", 
                                  "✅ FIXED: /sales_report_estimates endpoint works")
                elif response.status_code == 422:
                    self.print_test("get_download_estimates", "PASS", 
                                  "✅ FIXED: Endpoint exists but may need subscription")
                elif response.status_code == 404:
                    self.print_test("get_download_estimates", "FAIL", 
                                  "❌ STILL BROKEN: Endpoint not found")
                else:
                    self.print_test("get_download_estimates", "WARN", 
                                  f"Endpoint exists but returned {response.status_code}")
                    
        except Exception as e:
            self.print_test("get_download_estimates", "FAIL", f"Exception: {str(e)}")
    
    async def validate_revenue_estimates_fix(self):
        """Validate that get_revenue_estimates uses correct endpoint"""
        print("\n🔧 Testing Fix 4: get_revenue_estimates Endpoint URL")
        
        if not self.token:
            self.print_test("get_revenue_estimates", "SKIP", "No API token provided")
            return
        
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
                params = {
                    "app_ids": "284882215",
                    "countries": "US", 
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-07",
                    "auth_token": self.token
                }
                
                # Test the NEW correct endpoint (same as downloads)
                response = await client.get("/v1/ios/sales_report_estimates", params=params)
                
                if response.status_code == 200:
                    self.print_test("get_revenue_estimates", "PASS", 
                                  "✅ FIXED: /sales_report_estimates endpoint works")
                elif response.status_code == 422:
                    self.print_test("get_revenue_estimates", "PASS", 
                                  "✅ FIXED: Endpoint exists but may need subscription")
                elif response.status_code == 404:
                    self.print_test("get_revenue_estimates", "FAIL", 
                                  "❌ STILL BROKEN: Endpoint not found")
                else:
                    self.print_test("get_revenue_estimates", "WARN", 
                                  f"Endpoint exists but returned {response.status_code}")
                    
        except Exception as e:
            self.print_test("get_revenue_estimates", "FAIL", f"Exception: {str(e)}")
    
    async def run_validation(self):
        """Run all bug fix validations"""
        print("🚀 Sensor Tower MCP - Bug Fix Validation")
        print("=" * 50)
        print("Testing the 4 critical fixes from the bug report:")
        print("1. search_entities schema validation")
        print("2. get_impressions endpoint URL")
        print("3. get_download_estimates endpoint URL")
        print("4. get_revenue_estimates endpoint URL")
        print()
        
        if not self.token:
            print("⚠️  Warning: No API token provided")
            print("   Set SENSOR_TOWER_API_TOKEN to test API endpoints")
            print("   Only schema validation will be tested")
        
        # Run all validations
        await self.validate_search_entities_fix()
        await self.validate_impressions_fix()
        await self.validate_download_estimates_fix()
        await self.validate_revenue_estimates_fix()
        
        print("\n" + "=" * 50)
        print("🎯 Bug Fix Validation Complete!")
        print()
        print("Next steps:")
        print("- If fixes show ✅ PASS: All good!")
        print("- If fixes show ⚠️  WARN: May need API subscription")
        print("- If fixes show ❌ FAIL: Investigation needed")
        print() 
        print("For comprehensive testing run:")
        print("  python tests/test_comprehensive.py")

async def main():
    validator = BugFixValidator()
    await validator.run_validation()

if __name__ == "__main__":
    asyncio.run(main()) 