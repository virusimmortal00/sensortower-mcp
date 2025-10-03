#!/usr/bin/env python3
"""
Validate Advertising Intelligence Tool Fixes

This script tests all three advertising intelligence tools 
with the fixes applied based on our 422 investigation.
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

def test_advertising_tools_fixes():
    """Test all advertising intelligence tools with applied fixes"""
    
    token = os.getenv("SENSOR_TOWER_API_TOKEN")
    if not token:
        print("⚠️  No API token - cannot validate fixes")
        return False
    
    base_url = "https://api.sensortower.com"
    
    print("🔧 Validating Advertising Intelligence Tool Fixes")
    print("=" * 60)
    print("Testing all 3 tools with corrected parameters:")
    print("• get_creatives: Using valid network names")
    print("• get_impressions: Added period parameter")
    print("• impressions_rank: Added period parameter")
    print()
    
    results = []
    
    # Test 1: get_creatives with Instagram network
    print("🔍 Test 1: get_creatives with Instagram network")
    try:
        url = f"{base_url}/v1/ios/ad_intel/creatives"
        params = {
            "app_ids": "284882215",
            "start_date": "2024-01-01",
            "end_date": "2024-01-07",
            "countries": "US",
            "networks": "Instagram",  # Valid network name
            "ad_types": "video",
            "auth_token": token
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            print("✅ get_creatives: SUCCESS!")
            data = response.json()
            print(f"   📊 Response: {type(data)} with keys {list(data.keys()) if isinstance(data, dict) else f'{len(data)} items'}")
            results.append(("get_creatives", True, "Working with Instagram network"))
        else:
            print(f"❌ get_creatives: Failed with {response.status_code}")
            results.append(("get_creatives", False, f"Status {response.status_code}"))
            if response.status_code == 422:
                try:
                    error = response.json()
                    print(f"   🔍 Error: {json.dumps(error, indent=6)}")
                except Exception:
                    pass
                    
    except Exception as e:
        print(f"❌ get_creatives: Error - {e}")
        results.append(("get_creatives", False, f"Exception: {e}"))
    
    # Test 2: get_impressions (network_analysis) with period parameter
    print("\n🔍 Test 2: get_impressions with period parameter")
    try:
        url = f"{base_url}/v1/ios/ad_intel/network_analysis"
        params = {
            "app_ids": "284882215",
            "start_date": "2024-01-01",
            "end_date": "2024-01-07",
            "countries": "US",
            "networks": "Instagram",
            "period": "day",  # Required period parameter (our fix)
            "auth_token": token
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            print("✅ get_impressions: SUCCESS!")
            data = response.json()
            print(f"   📊 Response: {type(data)} with content")
            results.append(("get_impressions", True, "Working with period parameter"))
        else:
            print(f"❌ get_impressions: Failed with {response.status_code}")
            results.append(("get_impressions", False, f"Status {response.status_code}"))
            if response.status_code == 422:
                try:
                    error = response.json()
                    print(f"   🔍 Error: {json.dumps(error, indent=6)}")
                except Exception:
                    pass
                    
    except Exception as e:
        print(f"❌ get_impressions: Error - {e}")
        results.append(("get_impressions", False, f"Exception: {e}"))
    
    # Test 3: impressions_rank with period parameter
    print("\n🔍 Test 3: impressions_rank with period parameter")
    try:
        url = f"{base_url}/v1/ios/ad_intel/network_analysis/rank"
        params = {
            "app_ids": "284882215",
            "start_date": "2024-01-01",
            "end_date": "2024-01-07",
            "countries": "US",
            "networks": "Instagram",
            "period": "day",  # Required period parameter (our fix)
            "auth_token": token
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            print("✅ impressions_rank: SUCCESS!")
            data = response.json()
            print(f"   📊 Response: {type(data)} with content")
            results.append(("impressions_rank", True, "Working with period parameter"))
        else:
            print(f"❌ impressions_rank: Failed with {response.status_code}")
            results.append(("impressions_rank", False, f"Status {response.status_code}"))
            if response.status_code == 422:
                try:
                    error = response.json()
                    print(f"   🔍 Error: {json.dumps(error, indent=6)}")
                except Exception:
                    pass
                    
    except Exception as e:
        print(f"❌ impressions_rank: Error - {e}")
        results.append(("impressions_rank", False, f"Exception: {e}"))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 ADVERTISING INTELLIGENCE TOOL FIXES VALIDATION")
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
        print("🎉 ALL ADVERTISING INTELLIGENCE TOOLS FIXED!")
        print("   • 422 parameter errors resolved")
        print("   • Network name mappings corrected")
        print("   • Required period parameters added")
    elif len(successful) > 0:
        print(f"🟡 {len(successful)}/3 tools fixed - investigate remaining issues")
    else:
        print("🔴 No tools fixed yet - review parameter requirements")
    
    return len(successful) == 3

def main():
    """Run advertising tools validation"""
    print("🚀 ADVERTISING INTELLIGENCE TOOL FIXES VALIDATION")
    print("=" * 60)
    print("Validating fixes applied based on 422 parameter investigation")
    print()
    
    success = test_advertising_tools_fixes()
    
    if success:
        print("\n🎉 All advertising intelligence tools fixed successfully!")
        print("Ready to update comprehensive test results")
        return 0
    else:
        print("\n⚠️  Some tools still need fixes - continue investigation")
        return 1

if __name__ == "__main__":
    exit(main())
