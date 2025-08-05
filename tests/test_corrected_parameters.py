#!/usr/bin/env python3
"""
Test with Corrected Parameters

Based on 422 investigation findings, test the advertising intelligence
tools with the correct parameter values.
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

def test_corrected_parameters():
    """Test advertising intelligence tools with corrected parameters"""
    
    token = os.getenv("SENSOR_TOWER_API_TOKEN")
    if not token:
        print("⚠️  No API token - cannot test corrected parameters")
        return False
    
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
            "auth_token": token
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            print("✅ SUCCESS: Creatives API working with Instagram network!")
            data = response.json()
            print(f"   📊 Response type: {type(data)}")
            if isinstance(data, dict):
                print(f"   📋 Keys: {list(data.keys())}")
            elif isinstance(data, list):
                print(f"   📦 Items: {len(data)}")
        else:
            print(f"❌ Still failing: {response.status_code}")
            if response.status_code == 422:
                try:
                    error_data = response.json()
                    print(f"   🔍 Error: {json.dumps(error_data, indent=6)}")
                except:
                    print(f"   🔍 Error: {response.text[:200]}")
                    
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
            "period": "daily",  # Added required period parameter
            "auth_token": token
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            print("✅ SUCCESS: Network analysis working with period parameter!")
            data = response.json()
            print(f"   📊 Response type: {type(data)}")
            if isinstance(data, dict):
                print(f"   📋 Keys: {list(data.keys())}")
        else:
            print(f"❌ Still failing: {response.status_code}")
            if response.status_code == 422:
                try:
                    error_data = response.json()
                    print(f"   🔍 Error: {json.dumps(error_data, indent=6)}")
                except:
                    print(f"   🔍 Error: {response.text[:200]}")
                    
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
            "auth_token": token
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            print("✅ SUCCESS: Multiple networks working!")
            data = response.json()
            print(f"   📊 Response: {type(data)} with content")
        else:
            print(f"❌ Multiple networks failed: {response.status_code}")
            
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
    
    return True

def main():
    """Run corrected parameter tests"""
    print("🚀 CORRECTED PARAMETER TESTING")
    print("=" * 50)
    print("Testing advertising intelligence tools with fixes from 422 investigation")
    print()
    
    success = test_corrected_parameters()
    
    if success:
        print("\n🎉 Parameter correction testing completed!")
        return 0
    else:
        print("\n⚠️  Could not test - check API token")
        return 1

if __name__ == "__main__":
    exit(main())