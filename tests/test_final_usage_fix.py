#!/usr/bin/env python3
"""
Test Final Usage Intelligence Fix

Quick test for the get_usage_active_users date_granularity fix.
"""

import os
import sys
import json
import requests

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def test_final_usage_fix():
    """Test the final date_granularity fix for get_usage_active_users"""
    
    token = os.getenv("SENSOR_TOWER_API_TOKEN")
    if not token:
        print("⚠️  No API token available")
        return False
    
    base_url = "https://api.sensortower.com"
    
    print("🔧 Testing Final get_usage_active_users Fix")
    print("=" * 50)
    print("Testing date_granularity fix: daily → monthly")
    print()
    
    try:
        url = f"{base_url}/v1/ios/usage/active_users"
        params = {
            "app_ids": "284882215",
            "start_date": "2024-01-01",
            "end_date": "2024-01-07",
            "countries": "US",
            "date_granularity": "monthly",  # Fixed value
            "auth_token": token
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            print("✅ SUCCESS: get_usage_active_users working!")
            data = response.json()
            print(f"   📊 Response: {type(data)} with {len(data) if isinstance(data, list) else 'dict'} content")
            return True
        else:
            print(f"❌ Still failing: {response.status_code}")
            if response.status_code == 422:
                try:
                    error = response.json()
                    print(f"   🔍 Error: {json.dumps(error, indent=6)}")
                except:
                    pass
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    """Run final usage fix test"""
    print("🚀 FINAL USAGE INTELLIGENCE FIX TEST")
    print("=" * 50)
    
    success = test_final_usage_fix()
    
    if success:
        print("\n🎉 Final fix successful!")
        print("All usage intelligence tools should now be working!")
        return 0
    else:
        print("\n⚠️  Fix unsuccessful - may need further investigation")
        return 1

if __name__ == "__main__":
    exit(main())