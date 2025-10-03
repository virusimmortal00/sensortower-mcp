#!/usr/bin/env python3
"""
Test Final Usage Intelligence Fix

Quick test for the get_usage_active_users date_granularity fix.
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

def test_final_usage_fix():
    """Test the final date_granularity fix for get_usage_active_users"""
    
    token = os.getenv("SENSOR_TOWER_API_TOKEN")
    if not token:
        pytest.skip("SENSOR_TOWER_API_TOKEN is required for live API checks")
    
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
        
        if response.status_code != 200:
            details = response.text[:200]
            if response.status_code == 422:
                try:
                    details = json.dumps(response.json(), indent=2)[:200]
                except Exception:  # pragma: no cover - defensive
                    details = response.text[:200]
            pytest.fail(f"get_usage_active_users returned {response.status_code}: {details}")

        print("✅ SUCCESS: get_usage_active_users working!")
        data = response.json()
        length = len(data) if isinstance(data, list) else 'dict'
        print(f"   📊 Response: {type(data)} with {length} content")

    except Exception as e:
        pytest.fail(f"Request error: {e}")

def main():
    """Run final usage fix test"""
    print("🚀 FINAL USAGE INTELLIGENCE FIX TEST")
    print("=" * 50)
    
    try:
        test_final_usage_fix()
    except pytest.SkipTest as exc:  # pragma: no cover - CLI convenience
        print(f"\n⚠️  {exc.msg}")
        return 0
    except AssertionError as exc:  # pragma: no cover - CLI convenience
        print(f"\n⚠️  Fix unsuccessful - {exc}")
        return 1

    print("\n🎉 Final fix successful!")
    print("All usage intelligence tools should now be working!")
    return 0

if __name__ == "__main__":
    exit(main())
