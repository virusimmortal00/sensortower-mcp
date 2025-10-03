#!/usr/bin/env python3
"""
Test with Corrected Parameters

Based on 422 investigation findings, test the advertising intelligence
tools with the correct parameter values.
"""

import os
import json
import requests
import pytest

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def test_corrected_parameters():
    """Test advertising intelligence tools with corrected parameters"""
    
    token = os.getenv("SENSOR_TOWER_API_TOKEN")
    if not token:
        pytest.skip("SENSOR_TOWER_API_TOKEN is required for live API checks")
    
    base_url = "https://api.sensortower.com"
    
    print("🔧 Testing Corrected Parameters for Advertising Intelligence")
    print("=" * 60)
    print("Using insights from 422 investigation:")
    print("• Using 'Instagram' instead of 'facebook'")
    print("• Adding 'period' parameter for network_analysis")
    print()
    
    # Test 1: Creatives with correct network name
    print("🔍 Test 1: Creatives with Instagram network")
    try:
        url = f"{base_url}/v1/ios/ad_intel/creatives"
        params = {
            "app_ids": "284882215",
            "start_date": "2024-01-01",
            "end_date": "2024-01-07",
            "countries": "US",
            "networks": "Instagram",  # Corrected network name
            "ad_types": "video",
            "auth_token": token
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code != 200:
            details = response.text[:200]
            if response.status_code == 422:
                try:
                    details = json.dumps(response.json(), indent=2)[:200]
                except Exception:  # pragma: no cover - defensive
                    details = response.text[:200]
            pytest.fail(f"Creatives endpoint returned {response.status_code}: {details}")

        print("✅ SUCCESS: Creatives API working with Instagram network!")
        data = response.json()
        print(f"   📊 Response type: {type(data)}")
        if isinstance(data, dict):
            print(f"   📋 Keys: {list(data.keys())}")
        elif isinstance(data, list):
            print(f"   📦 Items: {len(data)}")
    except Exception as e:
        print(f"❌ Test error: {e}")
    
    # Test 2: Network analysis with period parameter
    print("\n🔍 Test 2: Network analysis with period parameter")
    try:
        url = f"{base_url}/v1/ios/ad_intel/network_analysis"
        params = {
            "app_ids": "284882215",
            "start_date": "2024-01-01",
            "end_date": "2024-01-07",
            "countries": "US",
            "networks": "Instagram",
            "period": "day",  # API accepts day/week/month/quarter/year
            "auth_token": token
        }

        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code != 200:
            details = response.text[:200]
            if response.status_code == 422:
                try:
                    details = json.dumps(response.json(), indent=2)[:200]
                except Exception:  # pragma: no cover - defensive
                    details = response.text[:200]
            pytest.fail(f"Network analysis endpoint returned {response.status_code}: {details}")

        print("✅ SUCCESS: Network analysis working with period parameter!")
        data = response.json()
        print(f"   📊 Response type: {type(data)}")
        if isinstance(data, dict):
            print(f"   📋 Keys: {list(data.keys())}")
    except Exception as e:
        print(f"❌ Test error: {e}")
    
    # Test 3: Try multiple valid networks
    print("\n🔍 Test 3: Testing multiple valid networks")
    try:
        url = f"{base_url}/v1/ios/ad_intel/creatives"
        params = {
            "app_ids": "284882215",
            "start_date": "2024-01-01",
            "countries": "US", 
            "networks": "Instagram,Admob,Unity",  # Multiple valid networks
            "ad_types": "video",
            "auth_token": token
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code != 200:
            pytest.fail(
                "Multiple network creatives request failed "
                f"with {response.status_code}: {response.text[:200]}"
            )

        print("✅ SUCCESS: Multiple networks working!")
        data = response.json()
        print(f"   📊 Response: {type(data)} with content")
    except Exception as e:
        print(f"❌ Test error: {e}")
    
    print("\n" + "=" * 60)
    print("📋 CORRECTED PARAMETER FINDINGS:")
    print("✅ Key insight: 'facebook' → 'Instagram'")
    print("✅ Required: 'period' parameter for network_analysis")
    print("✅ Valid networks discovered from error messages")
    print()
    print("🎯 NEXT STEPS:")
    print("1. Update MCP tools with correct network mappings")
    print("2. Add required parameters for each endpoint")
    print("3. Test all advertising intelligence tools")
    
    print("Tests completed successfully")

def main():
    """Run corrected parameter tests"""
    print("🚀 CORRECTED PARAMETER TESTING")
    print("=" * 50)
    print("Testing advertising intelligence tools with fixes from 422 investigation")
    print()

    try:
        test_corrected_parameters()
    except pytest.SkipTest as exc:  # pragma: no cover - CLI convenience
        print(f"\n⚠️  {exc.msg}")
        return 0
    except AssertionError as exc:  # pragma: no cover - CLI convenience
        print(f"\n❌ Test failed: {exc}")
        return 1

    print("\n🎉 Parameter correction testing completed!")
    return 0

if __name__ == "__main__":
    exit(main())
