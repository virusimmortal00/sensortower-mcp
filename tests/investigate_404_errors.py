#!/usr/bin/env python3
"""
Systematic Investigation of 404 Errors for Usage Intelligence Tools

Based on diagnostics: Endpoints exist (405 status) but return 404 with parameters.
This suggests parameter, auth, or access level issues.

Tools with 404 errors:
- get_usage_active_users
- app_analysis_retention  
- app_analysis_demographics
"""

import os
import json
import requests
from typing import Dict, Any

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Usage404Investigator:
    def __init__(self):
        self.token = os.getenv("SENSOR_TOWER_API_TOKEN")
        self.base_url = "https://api.sensortower.com"
        
    def print_test(self, test_name: str, status: str, details: str):
        emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "🔍"
        print(f"{emoji} {test_name}: {details}")
    
    def investigate_404_patterns(self):
        """Investigate different approaches to resolve 404 errors"""
        
        if not self.token:
            print("⚠️  No API token - limited investigation possible")
            self._investigate_without_token()
            return
            
        print("🔍 SYSTEMATIC 404 ERROR INVESTIGATION")
        print("=" * 60)
        print("Testing different approaches for usage intelligence tools")
        print()
        
        # Test different endpoint structures
        self._test_endpoint_variations()
        
        # Test different parameter combinations
        self._test_parameter_variations()
        
        # Test access level requirements
        self._test_access_requirements()
        
        # Test alternative endpoints
        self._test_alternative_endpoints()
        
    def _test_endpoint_variations(self):
        """Test different endpoint URL structures"""
        print("🔍 Phase 1: Testing Endpoint URL Variations")
        print("-" * 50)
        
        # Original endpoints that return 404
        endpoints_to_test = [
            # Original problematic endpoints
            ("/v1/ios/usage_intelligence/active_users", "Original active_users"),
            ("/v1/ios/usage_intelligence/retention", "Original retention"),
            ("/v1/ios/usage_intelligence/demographics", "Original demographics"),
            
            # Try different versions
            ("/v2/ios/usage_intelligence/active_users", "v2 active_users"),
            ("/v1/ios/usage/active_users", "Shortened usage path"),
            ("/v1/ios/analytics/active_users", "Analytics instead of usage_intelligence"),
            
            # Try different naming patterns
            ("/v1/ios/usage_intelligence/users", "Simplified users"),
            ("/v1/ios/usage_intelligence/user_analytics", "user_analytics"),
            ("/v1/ios/app_intelligence/active_users", "app_intelligence path"),
        ]
        
        for endpoint, description in endpoints_to_test:
            self._test_single_endpoint_structure(endpoint, description)
    
    def _test_single_endpoint_structure(self, endpoint: str, description: str):
        """Test a single endpoint structure"""
        try:
            url = f"{self.base_url}{endpoint}"
            params = {
                "app_ids": "284882215",
                "start_date": "2024-01-01",
                "auth_token": self.token
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                self.print_test(description, "PASS", "Endpoint works!")
                try:
                    data = response.json()
                    print(f"   📊 Response: {type(data)}")
                except Exception:
                    print("   📊 Response: Non-JSON data")
            elif response.status_code == 404:
                self.print_test(description, "FAIL", "Still 404")
            elif response.status_code == 401:
                self.print_test(description, "FAIL", "401 - Auth issue")
            elif response.status_code == 403:
                self.print_test(description, "FAIL", "403 - Access forbidden")
            elif response.status_code == 422:
                self.print_test(description, "UNKNOWN", "422 - Parameter issue")
                try:
                    error = response.json()
                    print(f"   🔍 422 Error: {json.dumps(error, indent=6)}")
                except Exception:
                    pass
            else:
                self.print_test(description, "UNKNOWN", f"Status {response.status_code}")
                
        except Exception as e:
            self.print_test(description, "ERROR", f"Request error: {e}")
    
    def _test_parameter_variations(self):
        """Test different parameter combinations for usage intelligence"""
        print("\n🔍 Phase 2: Testing Parameter Variations")
        print("-" * 50)
        
        endpoint = "/v1/ios/usage_intelligence/active_users"
        
        parameter_sets = [
            # Test 1: Minimal parameters
            {
                "name": "minimal_params",
                "params": {
                    "app_ids": "284882215",
                    "start_date": "2024-01-01"
                }
            },
            # Test 2: Add end_date
            {
                "name": "with_end_date",
                "params": {
                    "app_ids": "284882215", 
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-07"
                }
            },
            # Test 3: Add countries
            {
                "name": "with_countries",
                "params": {
                    "app_ids": "284882215",
                    "start_date": "2024-01-01",
                    "countries": "US"
                }
            },
            # Test 4: Add date_granularity
            {
                "name": "with_granularity",
                "params": {
                    "app_ids": "284882215",
                    "start_date": "2024-01-01",
                    "date_granularity": "daily"
                }
            },
            # Test 5: Different app_id format
            {
                "name": "app_id_singular",
                "params": {
                    "app_id": "284882215",  # Singular
                    "start_date": "2024-01-01"
                }
            },
            # Test 6: Try with period parameter (like advertising intelligence)
            {
                "name": "with_period",
                "params": {
                    "app_ids": "284882215",
                    "start_date": "2024-01-01",
                    "period": "day"
                }
            }
        ]
        
        for param_set in parameter_sets:
            self._test_parameter_set(endpoint, param_set)
    
    def _test_parameter_set(self, endpoint: str, param_set: Dict[str, Any]):
        """Test a specific parameter set"""
        try:
            url = f"{self.base_url}{endpoint}"
            params = param_set["params"].copy()
            params["auth_token"] = self.token
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                self.print_test(param_set["name"], "PASS", "Parameters work!")
            elif response.status_code == 404:
                self.print_test(param_set["name"], "FAIL", "Still 404 with these params")
            elif response.status_code == 422:
                self.print_test(param_set["name"], "UNKNOWN", "422 - Different parameter issue")
                try:
                    error = response.json()
                    print(f"   🔍 422 Details: {error}")
                except Exception:
                    pass
            else:
                self.print_test(param_set["name"], "UNKNOWN", f"Status {response.status_code}")
                
        except Exception as e:
            self.print_test(param_set["name"], "ERROR", f"Error: {e}")
    
    def _test_access_requirements(self):
        """Test if endpoints require specific access levels"""
        print("\n🔍 Phase 3: Testing Access Requirements")
        print("-" * 50)
        
        # Test if these are premium-only endpoints
        # Try with different HTTP methods
        endpoint = "/v1/ios/usage_intelligence/active_users"
        url = f"{self.base_url}{endpoint}"
        
        methods_to_test = [
            ("GET", "Standard GET request"),
            ("POST", "POST request (some APIs use POST)"),
            ("OPTIONS", "OPTIONS request (check capabilities)")
        ]
        
        for method, description in methods_to_test:
            try:
                if method == "GET":
                    response = requests.get(url, params={"auth_token": self.token}, timeout=30)
                elif method == "POST":
                    response = requests.post(url, json={"auth_token": self.token}, timeout=30)
                elif method == "OPTIONS":
                    response = requests.options(url, timeout=30)
                
                self.print_test(f"{method}_method", "INFO", f"Status {response.status_code}")
                
                # Look for specific access-related error codes
                if response.status_code == 402:
                    print("   💰 402 Payment Required - Premium feature")
                elif response.status_code == 403:
                    print("   🚫 403 Forbidden - Access level insufficient")
                elif response.status_code == 401:
                    print("   🔐 401 Unauthorized - Auth issue")
                    
            except Exception as e:
                self.print_test(f"{method}_method", "ERROR", f"Error: {e}")
    
    def _test_alternative_endpoints(self):
        """Test alternative endpoint patterns based on working tools"""
        print("\n🔍 Phase 4: Testing Alternative Patterns")
        print("-" * 50)
        
        # Based on working tools, try similar patterns
        alternatives = [
            # Pattern from app metadata (working)
            ("/v1/ios/app/app_metadata", "app_metadata pattern", {"app_ids": "284882215"}),
            
            # Pattern from downloads (working) 
            ("/v1/ios/sales_report_estimates", "sales_report pattern", {
                "app_ids": "284882215", 
                "start_date": "2024-01-01"
            }),
            
            # Try intelligence instead of usage_intelligence
            ("/v1/ios/intelligence/active_users", "intelligence pattern", {
                "app_ids": "284882215",
                "start_date": "2024-01-01"
            }),
            
            # Try mobile_intelligence (sometimes different naming)
            ("/v1/ios/mobile_intelligence/users", "mobile_intelligence pattern", {
                "app_ids": "284882215",
                "start_date": "2024-01-01"
            })
        ]
        
        for endpoint, description, base_params in alternatives:
            try:
                url = f"{self.base_url}{endpoint}"
                params = base_params.copy()
                params["auth_token"] = self.token
                
                response = requests.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    self.print_test(description, "PASS", "Alternative endpoint works!")
                elif response.status_code == 404:
                    self.print_test(description, "FAIL", "404 - Not found")
                else:
                    self.print_test(description, "INFO", f"Status {response.status_code}")
                    
            except Exception as e:
                self.print_test(description, "ERROR", f"Error: {e}")
    
    def _investigate_without_token(self):
        """Investigation possible without API token"""
        print("🔍 ENDPOINT STRUCTURE ANALYSIS (No Token)")
        print("=" * 60)
        
        print("📋 HYPOTHESIS ANALYSIS:")
        print("1. 🔍 Endpoint URL Changes:")
        print("   • usage_intelligence → app_intelligence")
        print("   • Different versioning (v1 → v2)")
        print("   • Different path structure")
        
        print("\n2. 🔐 Access Level Requirements:")
        print("   • Premium-only features (402 errors)")
        print("   • Different authentication method")
        print("   • Special permissions required")
        
        print("\n3. 📊 Parameter Requirements:")
        print("   • Different required parameters")
        print("   • Different parameter names")
        print("   • Different date/time requirements")
        
        print("\n4. 🏗️  Architecture Changes:")
        print("   • Features moved to different endpoints")
        print("   • Deprecated and not available")
        print("   • Merged into other tools")
        
        print("\n💡 RECOMMENDED ACTIONS:")
        print("1. Check Sensor Tower API documentation")
        print("2. Contact API support for endpoint changes")
        print("3. Verify current API plan includes usage intelligence")
        print("4. Test with working endpoints to confirm auth")
    
    def run_full_investigation(self):
        """Run complete 404 investigation"""
        print("🔍 USAGE INTELLIGENCE 404 ERROR INVESTIGATION")
        print("=" * 60)
        print("Investigating 3 tools with 404 errors")
        print()
        
        self.investigate_404_patterns()
        
        print("\n" + "=" * 60)
        print("📊 404 INVESTIGATION SUMMARY")
        print("=" * 60)
        print("🎯 NEXT STEPS BASED ON FINDINGS:")
        print("1. Review any working endpoints found")
        print("2. Check API documentation for endpoint changes")
        print("3. Verify API plan includes usage intelligence features")
        print("4. Consider if these features require different access")
        
        return True

def main():
    """Run 404 investigation"""
    investigator = Usage404Investigator()
    investigator.run_full_investigation()
    
    print("\n💡 RECOMMENDATION:")
    print("If no working endpoints found, these may be:")
    print("• Premium-only features")
    print("• Deprecated endpoints")
    print("• Requiring different API access level")
    
    return 0

if __name__ == "__main__":
    exit(main())
