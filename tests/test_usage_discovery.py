#!/usr/bin/env python3
"""
Test Usage Intelligence Discovery

Based on 404 investigation, test the discovered endpoint pattern:
/v1/ios/usage/ instead of /v1/ios/usage_intelligence/

Key finding: usage/active_users returned 422 "end_date missing" instead of 404
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

def test_usage_endpoint_discovery():
    """Test the discovered usage endpoint pattern"""
    
    token = os.getenv("SENSOR_TOWER_API_TOKEN")
    if not token:
        pytest.skip("SENSOR_TOWER_API_TOKEN is required for live API checks")
    
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
            
            if response.status_code != 200:
                details = response.text[:200]
                if response.status_code == 422:
                    try:
                        details = json.dumps(response.json(), indent=2)[:200]
                    except Exception:  # pragma: no cover
                        details = response.text[:200]
                pytest.fail(
                    f"{test['name']} returned {response.status_code}: {details}"
                )

            print("✅ SUCCESS: Endpoint working!")
            try:
                data = response.json()
                print(f"   📊 Response: {type(data)}")
                if isinstance(data, dict):
                    print(f"   📋 Keys: {list(data.keys())}")
                elif isinstance(data, list):
                    print(f"   📦 Items: {len(data)}")
            except Exception:  # pragma: no cover - defensive
                print("   📊 Response: Non-JSON data received")
            successful_tests.append(test)

        except Exception as e:
            pytest.fail(f"Request error for {test['name']}: {e}")
        
        print()  # Add spacing between tests
    
    # Summary
    print("=" * 60)
    print("📊 USAGE INTELLIGENCE DISCOVERY RESULTS")
    print("=" * 60)
    
    assert len(successful_tests) == len(endpoints_to_test), (
        "Some usage endpoints failed", successful_tests
    )

def main():
    """Run usage intelligence discovery test"""
    print("🚀 USAGE INTELLIGENCE ENDPOINT DISCOVERY")
    print("=" * 60)
    print("Testing endpoint pattern discovery from 404 investigation")
    print()
    
    try:
        test_usage_endpoint_discovery()
    except pytest.SkipTest as exc:  # pragma: no cover - CLI convenience
        print(f"\n⚠️  {exc.msg}")
        return 0
    except AssertionError as exc:  # pragma: no cover - CLI convenience
        print(f"\n⚠️  Discovery incomplete - {exc}")
        return 1

    print("\n🎉 Usage intelligence endpoints discovered!")
    return 0

if __name__ == "__main__":
    exit(main())
