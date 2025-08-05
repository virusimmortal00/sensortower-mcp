#!/usr/bin/env python3
"""
Test Usage Intelligence Discovery

Based on 404 investigation, test the discovered endpoint pattern:
/v1/ios/usage/ instead of /v1/ios/usage_intelligence/

Key finding: usage/active_users returned 422 "end_date missing" instead of 404
"""

import os
import sys
import json
import requests
from pathlib import Path

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def test_usage_endpoint_discovery():
    """Test the discovered usage endpoint pattern"""
    
    token = os.getenv("SENSOR_TOWER_API_TOKEN")
    if not token:
        print("⚠️  No API token - cannot test usage discovery")
        return False
    
    base_url = "https://api.sensortower.com"
    
    print("🔍 Testing Usage Intelligence Endpoint Discovery")
    print("=" * 60)
    print("Based on 404 investigation finding:")
    print("• /v1/ios/usage/active_users returned 422 instead of 404")
    print("• Error: 'Required parameter: end_date is missing'")
    print("• Testing shortened endpoint paths with required parameters")
    print()
    
    # Test the discovered pattern with all required parameters
    endpoints_to_test = [
        {
            "name": "usage_active_users_corrected",
            "endpoint": "/v1/ios/usage/active_users",
            "params": {
                "app_ids": "284882215",
                "start_date": "2024-01-01",
                "end_date": "2024-01-07",  # Required parameter discovered
                "countries": "US"
            }
        },
        {
            "name": "usage_retention_shortened",
            "endpoint": "/v1/ios/usage/retention",
            "params": {
                "app_ids": "284882215",
                "start_date": "2024-01-01",
                "end_date": "2024-01-07",
                "date_granularity": "monthly"
            }
        },
        {
            "name": "usage_demographics_shortened", 
            "endpoint": "/v1/ios/usage/demographics",
            "params": {
                "app_ids": "284882215",
                "start_date": "2024-01-01",
                "end_date": "2024-01-07",
                "date_granularity": "monthly"
            }
        }
    ]
    
    successful_tests = []
    
    for test in endpoints_to_test:
        print(f"🔍 Testing: {test['name']}")
        print(f"   Endpoint: {test['endpoint']}")
        print(f"   Params: {json.dumps(test['params'], indent=6)}")
        
        try:
            url = f"{base_url}{test['endpoint']}"
            params = test["params"].copy()
            params["auth_token"] = token
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                print("✅ SUCCESS: Endpoint working!")
                try:
                    data = response.json()
                    print(f"   📊 Response: {type(data)}")
                    if isinstance(data, dict):
                        print(f"   📋 Keys: {list(data.keys())}")
                    elif isinstance(data, list):
                        print(f"   📦 Items: {len(data)}")
                    successful_tests.append(test)
                except:
                    print("   📊 Response: Non-JSON data received")
                    successful_tests.append(test)
                    
            elif response.status_code == 422:
                print("❌ 422 Parameter Error")
                try:
                    error_data = response.json()
                    print(f"   🔍 Error details: {json.dumps(error_data, indent=6)}")
                    # Parse specific error to understand missing parameters
                    if "errors" in error_data:
                        for error in error_data["errors"]:
                            if "title" in error:
                                print(f"   💡 Specific issue: {error['title']}")
                except:
                    print(f"   🔍 Raw error: {response.text[:200]}")
                    
            elif response.status_code == 404:
                print("❌ Still 404 - endpoint doesn't exist")
                
            elif response.status_code == 401:
                print("❌ 401 Unauthorized - auth issue")
                
            elif response.status_code == 403:
                print("❌ 403 Forbidden - access issue")
                
            else:
                print(f"❌ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request error: {e}")
        
        print()  # Add spacing between tests
    
    # Summary
    print("=" * 60)
    print("📊 USAGE INTELLIGENCE DISCOVERY RESULTS")
    print("=" * 60)
    
    if successful_tests:
        print(f"🎉 BREAKTHROUGH: {len(successful_tests)} endpoint(s) working!")
        for test in successful_tests:
            print(f"   ✅ {test['name']}: {test['endpoint']}")
        
        print(f"\n🔧 REQUIRED FIXES FOR MCP TOOLS:")
        print("1. Update endpoint URLs from /usage_intelligence/ to /usage/")
        print("2. Ensure end_date parameter is always provided")
        print("3. Test with proper parameter combinations")
        
    else:
        print("⚠️  No working endpoints found")
        print("\n💡 POSSIBLE REASONS:")
        print("• Still missing required parameters")
        print("• Different parameter names needed")
        print("• Premium access required")
        print("• Features deprecated/unavailable")
    
    print(f"\n🎯 NEXT STEPS:")
    if successful_tests:
        print("1. Apply endpoint URL fixes to MCP tools")
        print("2. Update parameter requirements") 
        print("3. Test all usage intelligence tools")
    else:
        print("1. Continue parameter investigation")
        print("2. Check API documentation")
        print("3. Consider premium access requirements")
        
    return len(successful_tests) > 0

def main():
    """Run usage intelligence discovery test"""
    print("🚀 USAGE INTELLIGENCE ENDPOINT DISCOVERY")
    print("=" * 60)
    print("Testing endpoint pattern discovery from 404 investigation")
    print()
    
    success = test_usage_endpoint_discovery()
    
    if success:
        print("\n🎉 Usage intelligence endpoints discovered!")
        return 0
    else:
        print("\n⚠️  No working endpoints found - continue investigation")
        return 1

if __name__ == "__main__":
    exit(main())