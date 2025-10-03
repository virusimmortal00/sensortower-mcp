#!/usr/bin/env python3
"""
Systematic Investigation of 422 Parameter Errors

This script systematically tests different parameter combinations
for the advertising intelligence tools that return 422 errors.

Based on diagnostics: Endpoints exist (405 status) but reject parameters (422).
"""

import os
import json
import requests
from typing import Dict, List, Any
from dataclasses import dataclass

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

@dataclass
class ParameterTest:
    name: str
    endpoint: str
    params: Dict[str, Any]
    description: str

class Parameter422Investigator:
    def __init__(self):
        self.token = os.getenv("SENSOR_TOWER_API_TOKEN")
        self.base_url = "https://api.sensortower.com"
        self.results = []
        
    def print_test(self, test_name: str, status: str, details: str):
        emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "🔍"
        print(f"{emoji} {test_name}: {details}")
    
    def test_parameter_combination(self, test: ParameterTest) -> Dict[str, Any]:
        """Test a specific parameter combination"""
        if not self.token:
            return {
                "test_name": test.name,
                "status": "SKIPPED",
                "details": "No API token available",
                "recommendations": ["Set SENSOR_TOWER_API_TOKEN environment variable"]
            }
        
        try:
            url = f"{self.base_url}{test.endpoint}"
            params = test.params.copy()
            params["auth_token"] = self.token
            
            print(f"\n🔍 Testing: {test.name}")
            print(f"   Endpoint: {test.endpoint}")
            print(f"   Params: {json.dumps(test.params, indent=6)}")
            
            response = requests.get(url, params=params, timeout=30)
            
            result = {
                "test_name": test.name,
                "status_code": response.status_code,
                "endpoint": test.endpoint,
                "params_tested": test.params
            }
            
            if response.status_code == 200:
                result["status"] = "PASS"
                result["details"] = "Parameters accepted - 200 OK"
                result["recommendations"] = ["Parameters are correct", "Original MCP tool may have different parameter construction"]
                
                # Try to get response size for validation
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        result["response_info"] = f"Dict with keys: {list(data.keys())}"
                    elif isinstance(data, list):
                        result["response_info"] = f"List with {len(data)} items"
                    else:
                        result["response_info"] = f"Response type: {type(data)}"
                except Exception:
                    result["response_info"] = "Response received but not JSON"
                    
            elif response.status_code == 422:
                result["status"] = "FAIL"
                
                # Try to parse the 422 error details
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", error_data.get("error", "Unknown validation error"))
                    result["details"] = f"422 Validation Error: {error_msg}"
                    result["error_response"] = error_data
                    
                    # Specific recommendations based on common 422 causes
                    result["recommendations"] = [
                        "Check parameter names (case sensitive?)",
                        "Verify date format (YYYY-MM-DD vs other formats)",
                        "Check app_ids format (string vs integer?)",
                        "Validate country codes (US vs us?)",
                        "Check network names (facebook vs Facebook?)",
                        "Verify required parameters are not missing"
                    ]
                    
                except Exception:
                    error_text = response.text[:200]
                    result["details"] = f"422 Error (unparseable): {error_text}"
                    result["recommendations"] = ["Check raw response format", "Verify API documentation"]
                    
            elif response.status_code == 401:
                result["status"] = "FAIL"
                result["details"] = "401 Unauthorized - Token issue"
                result["recommendations"] = ["Check API token validity", "Verify token permissions"]
                
            elif response.status_code == 404:
                result["status"] = "FAIL" 
                result["details"] = "404 Not Found - Endpoint issue"
                result["recommendations"] = ["Verify endpoint URL", "Check API version"]
                
            else:
                result["status"] = "FAIL"
                result["details"] = f"Unexpected status: {response.status_code}"
                result["recommendations"] = ["Investigate unusual response code"]
                
            self.print_test(test.name, result["status"], result["details"])
            if "response_info" in result:
                print(f"   📊 Response: {result['response_info']}")
                
            return result
            
        except Exception as e:
            result = {
                "test_name": test.name,
                "status": "ERROR",
                "details": f"Request error: {str(e)}",
                "recommendations": ["Check network connectivity", "Verify base URL"]
            }
            self.print_test(test.name, result["status"], result["details"])
            return result
    
    def run_systematic_tests(self):
        """Run systematic parameter tests for 422 errors"""
        print("🔍 SYSTEMATIC 422 PARAMETER ERROR INVESTIGATION")
        print("=" * 60)
        print("Testing different parameter combinations for advertising intelligence tools")
        print()
        
        # Define test cases with different parameter combinations
        test_cases = [
            # Test 1: Minimal parameters for creatives
            ParameterTest(
                name="creatives_minimal",
                endpoint="/v1/ios/ad_intel/creatives",
                params={
                    "app_ids": "284882215",
                    "start_date": "2024-01-01",
                    "countries": "US",
                    "networks": "facebook",
                    "ad_types": "video"
                },
                description="Minimal required parameters"
            ),
            
            # Test 2: Different app_ids format
            ParameterTest(
                name="creatives_app_id_as_int",
                endpoint="/v1/ios/ad_intel/creatives", 
                params={
                    "app_ids": 284882215,  # Integer instead of string
                    "start_date": "2024-01-01",
                    "countries": "US",
                    "networks": "facebook",
                    "ad_types": "video"
                },
                description="app_ids as integer instead of string"
            ),
            
            # Test 3: Different date format
            ParameterTest(
                name="creatives_date_format_alt",
                endpoint="/v1/ios/ad_intel/creatives",
                params={
                    "app_ids": "284882215",
                    "start_date": "2024/01/01",  # Different date format
                    "countries": "US", 
                    "networks": "facebook",
                    "ad_types": "video"
                },
                description="Alternative date format (YYYY/MM/DD)"
            ),
            
            # Test 4: Single parameters (no arrays)
            ParameterTest(
                name="creatives_single_values",
                endpoint="/v1/ios/ad_intel/creatives",
                params={
                    "app_id": "284882215",  # Singular instead of plural
                    "start_date": "2024-01-01",
                    "country": "US",  # Singular instead of plural
                    "network": "facebook",  # Singular instead of plural
                    "ad_types": "video"
                },
                description="Singular parameter names instead of plural"
            ),
            
            # Test 5: Add end_date
            ParameterTest(
                name="creatives_with_end_date",
                endpoint="/v1/ios/ad_intel/creatives",
                params={
                    "app_ids": "284882215",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-07",  # Add end_date
                    "countries": "US",
                    "networks": "facebook",
                    "ad_types": "video"
                },
                description="Include end_date parameter"
            ),
            
            # Test 6: Test network_analysis endpoint
            ParameterTest(
                name="network_analysis_basic",
                endpoint="/v1/ios/ad_intel/network_analysis",
                params={
                    "app_ids": "284882215",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-07",
                    "countries": "US",
                    "networks": "facebook"
                },
                description="Basic network_analysis parameters"
            ),
            
            # Test 7: Test without networks parameter
            ParameterTest(
                name="creatives_no_networks",
                endpoint="/v1/ios/ad_intel/creatives", 
                params={
                    "app_ids": "284882215",
                    "start_date": "2024-01-01",
                    "countries": "US",
                    "ad_types": "video"
                    # No networks parameter
                },
                description="Test without networks parameter"
            ),
            
            # Test 8: Test different network values
            ParameterTest(
                name="creatives_different_networks",
                endpoint="/v1/ios/ad_intel/creatives",
                params={
                    "app_ids": "284882215",
                    "start_date": "2024-01-01", 
                    "countries": "US",
                    "networks": "admob,unity,ironsource",  # Different networks
                    "ad_types": "video"
                },
                description="Test with different network values"
            )
        ]
        
        # Run all test cases
        results = []
        for test_case in test_cases:
            result = self.test_parameter_combination(test_case)
            results.append(result)
            self.results.append(result)
        
        # Analyze results
        self._analyze_results(results)
        
        return results
    
    def _analyze_results(self, results: List[Dict[str, Any]]):
        """Analyze test results and provide insights"""
        print("\n" + "=" * 60)
        print("📊 PARAMETER TEST ANALYSIS")
        print("=" * 60)
        
        passed_tests = [r for r in results if r.get("status") == "PASS"]
        failed_tests = [r for r in results if r.get("status") == "FAIL"]
        error_tests = [r for r in results if r.get("status") == "ERROR"]
        skipped_tests = [r for r in results if r.get("status") == "SKIPPED"]
        
        print("📈 Test Summary:")
        print(f"   ✅ Passed: {len(passed_tests)}")
        print(f"   ❌ Failed: {len(failed_tests)}")
        print(f"   🔥 Errors: {len(error_tests)}")
        print(f"   ⏭️  Skipped: {len(skipped_tests)}")
        
        if passed_tests:
            print("\n🎉 WORKING PARAMETER COMBINATIONS:")
            for test in passed_tests:
                print(f"   ✅ {test['test_name']}")
                print(f"      → {test.get('response_info', 'Response received')}")
        
        if failed_tests:
            print("\n🔍 FAILED TESTS WITH INSIGHTS:")
            
            # Group by status code
            by_status = {}
            for test in failed_tests:
                status_code = test.get("status_code", "unknown")
                if status_code not in by_status:
                    by_status[status_code] = []
                by_status[status_code].append(test)
            
            for status_code, tests in by_status.items():
                print(f"\n   📋 Status {status_code} ({len(tests)} tests):")
                for test in tests:
                    print(f"      ❌ {test['test_name']}: {test['details']}")
                    
                    # Look for patterns in error responses
                    if "error_response" in test:
                        error_data = test["error_response"]
                        if isinstance(error_data, dict):
                            print(f"         🔍 Error details: {json.dumps(error_data, indent=12)}")
        
        # Provide recommendations
        print("\n💡 RECOMMENDATIONS:")
        
        if not passed_tests and failed_tests:
            print("   🔴 No parameters worked - possible issues:")
            print("      • API endpoint may have changed")
            print("      • Different authentication method required")
            print("      • Feature requires premium API access")
            print("      • Parameter names or formats have changed")
            
        elif passed_tests:
            print("   🟢 Some parameters work - recommended actions:")
            print("      • Use working parameter combinations in MCP tools")
            print("      • Compare working vs failing parameters")
            print("      • Update MCP tool parameter construction")
            
        if any("422" in str(r.get("status_code", "")) for r in failed_tests):
            print("   🟡 422 errors suggest parameter validation issues:")
            print("      • Check parameter names (exact spelling)")
            print("      • Verify required vs optional parameters")
            print("      • Test parameter value formats")
            
        return results

def main():
    """Run the 422 parameter investigation"""
    investigator = Parameter422Investigator()
    
    if not investigator.token:
        print("⚠️  Warning: No SENSOR_TOWER_API_TOKEN environment variable")
        print("   Set your token to run parameter tests:")
        print("   export SENSOR_TOWER_API_TOKEN=your_token_here")
        print()
        print("🔍 Running offline analysis instead...")
        
        # Even without token, we can analyze the approach
        print("\n📋 PARAMETER INVESTIGATION PLAN:")
        print("1. Test minimal vs full parameter sets")
        print("2. Try different parameter name formats (singular vs plural)")
        print("3. Test different value formats (string vs int, date formats)")
        print("4. Compare with known working tools")
        print("5. Analyze 422 error responses for specific validation messages")
        
        return 0
    
    results = investigator.run_systematic_tests()
    
    # Determine exit code based on results
    if any(r.get("status") == "PASS" for r in results):
        print("\n🎉 Found working parameter combinations!")
        return 0
    elif any(r.get("status") == "FAIL" for r in results):
        print("\n⚠️  All parameter tests failed - investigation needed")
        return 1
    else:
        print("\n🔍 Investigation incomplete - check results")
        return 1

if __name__ == "__main__":
    exit(main())
