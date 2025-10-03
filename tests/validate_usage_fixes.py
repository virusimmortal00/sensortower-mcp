#!/usr/bin/env python3
"""
Validate Usage Intelligence Tool Fixes

This script tests all three usage intelligence tools 
with the fixes applied based on our 404 investigation.
"""

import os
import json
import requests

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def test_usage_tools_fixes():
    """Test all usage intelligence tools with applied fixes"""
    
    token = os.getenv("SENSOR_TOWER_API_TOKEN")
    if not token:
        print("⚠️  No API token - cannot validate fixes")
        return False
    
    base_url = "https://api.sensortower.com"
    
    print("🔧 Validating Usage Intelligence Tool Fixes")
    print("=" * 60)
    print("Testing all 3 tools with corrected endpoints and parameters:")
    print("• get_usage_active_users: /usage_intelligence/ → /usage/")
    print("• app_analysis_retention: /usage_intelligence/ → /usage/")
    print("• app_analysis_demographics: /usage_intelligence/ → /usage/")
    print("• All tools: Added required end_date parameter")
    print()
    
    results = []
    
    # Test 1: get_usage_active_users with corrected endpoint
    print("🔍 Test 1: get_usage_active_users with /usage/ endpoint")
    try:
        url = f"{base_url}/v1/ios/usage/active_users"
        params = {
            "app_ids": "284882215",
            "start_date": "2024-01-01",
            "end_date": "2024-01-07",  # Required parameter
            "countries": "US",
            "date_granularity": "daily",
            "auth_token": token
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            print("✅ get_usage_active_users: SUCCESS!")
            data = response.json()
            print(f"   📊 Response: {type(data)} with {len(data) if isinstance(data, list) else 'dict'} content")
            results.append(("get_usage_active_users", True, "Working with /usage/ endpoint"))
        else:
            print(f"❌ get_usage_active_users: Failed with {response.status_code}")
            results.append(("get_usage_active_users", False, f"Status {response.status_code}"))
            if response.status_code == 422:
                try:
                    error = response.json()
                    print(f"   🔍 Error: {json.dumps(error, indent=6)}")
                except Exception:
                    pass
                    
    except Exception as e:
        print(f"❌ get_usage_active_users: Error - {e}")
        results.append(("get_usage_active_users", False, f"Exception: {e}"))
    
    # Test 2: app_analysis_retention with corrected endpoint
    print("\n🔍 Test 2: app_analysis_retention with /usage/ endpoint")
    try:
        url = f"{base_url}/v1/ios/usage/retention"
        params = {
            "app_ids": "284882215",
            "start_date": "2024-01-01",
            "end_date": "2024-01-07",  # Required parameter
            "date_granularity": "monthly",
            "auth_token": token
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            print("✅ app_analysis_retention: SUCCESS!")
            data = response.json()
            print(f"   📊 Response: {type(data)}")
            if isinstance(data, dict):
                print(f"   📋 Keys: {list(data.keys())}")
            results.append(("app_analysis_retention", True, "Working with /usage/ endpoint"))
        else:
            print(f"❌ app_analysis_retention: Failed with {response.status_code}")
            results.append(("app_analysis_retention", False, f"Status {response.status_code}"))
            if response.status_code == 422:
                try:
                    error = response.json()
                    print(f"   🔍 Error: {json.dumps(error, indent=6)}")
                except Exception:
                    pass
                    
    except Exception as e:
        print(f"❌ app_analysis_retention: Error - {e}")
        results.append(("app_analysis_retention", False, f"Exception: {e}"))
    
    # Test 3: app_analysis_demographics with corrected endpoint
    print("\n🔍 Test 3: app_analysis_demographics with /usage/ endpoint")
    try:
        url = f"{base_url}/v1/ios/usage/demographics"
        params = {
            "app_ids": "284882215",
            "start_date": "2024-01-01",
            "end_date": "2024-01-07",  # Required parameter
            "date_granularity": "monthly",
            "auth_token": token
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            print("✅ app_analysis_demographics: SUCCESS!")
            data = response.json()
            print(f"   📊 Response: {type(data)}")
            if isinstance(data, dict):
                print(f"   📋 Keys: {list(data.keys())}")
            results.append(("app_analysis_demographics", True, "Working with /usage/ endpoint"))
        else:
            print(f"❌ app_analysis_demographics: Failed with {response.status_code}")
            results.append(("app_analysis_demographics", False, f"Status {response.status_code}"))
            if response.status_code == 422:
                try:
                    error = response.json()
                    print(f"   🔍 Error: {json.dumps(error, indent=6)}")
                except Exception:
                    pass
                    
    except Exception as e:
        print(f"❌ app_analysis_demographics: Error - {e}")
        results.append(("app_analysis_demographics", False, f"Exception: {e}"))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 USAGE INTELLIGENCE TOOL FIXES VALIDATION")
    print("=" * 60)
    
    successful = [r for r in results if r[1]]
    failed = [r for r in results if not r[1]]
    
    print(f"✅ Working: {len(successful)}/3 tools")
    for tool, status, details in successful:
        print(f"   ✅ {tool}: {details}")
    
    if failed:
        print(f"\n❌ Still Failing: {len(failed)}/3 tools")
        for tool, status, details in failed:
            print(f"   ❌ {tool}: {details}")
    
    print("\n🎯 PROGRESS UPDATE:")
    if len(successful) == 3:
        print("🎉 ALL USAGE INTELLIGENCE TOOLS FIXED!")
        print("   • 404 endpoint errors resolved")
        print("   • Correct /usage/ endpoints implemented")
        print("   • Required end_date parameters added")
    elif len(successful) > 0:
        print(f"🟡 {len(successful)}/3 tools fixed - investigate remaining issues")
    else:
        print("🔴 No tools fixed yet - review endpoint URLs")
    
    return len(successful) == 3

def main():
    """Run usage tools validation"""
    print("🚀 USAGE INTELLIGENCE TOOL FIXES VALIDATION")
    print("=" * 60)
    print("Validating fixes applied based on 404 endpoint investigation")
    print()
    
    success = test_usage_tools_fixes()
    
    if success:
        print("\n🎉 All usage intelligence tools fixed successfully!")
        print("Ready to run comprehensive validation of all fixes")
        return 0
    else:
        print("\n⚠️  Some tools still need fixes - continue investigation")
        return 1

if __name__ == "__main__":
    exit(main())
