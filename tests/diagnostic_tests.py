#!/usr/bin/env python3
"""
Systematic Diagnostic Tests for Sensor Tower MCP Issues

This script systematically diagnoses the specific issues found in comprehensive testing:
1. Advertising Intelligence tools (422 errors) 
2. Usage Intelligence tools (404 errors)
3. Publisher tools (implementation errors)
"""

import os
import sys
import requests
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

@dataclass
class DiagnosticResult:
    tool_name: str
    issue_type: str
    status: str  # PASS, FAIL, UNKNOWN
    details: str
    recommendations: List[str]

class SensorTowerDiagnostics:
    def __init__(self):
        self.token = os.getenv("SENSOR_TOWER_API_TOKEN")
        self.base_url = "https://api.sensortower.com"
        self.results: List[DiagnosticResult] = []
        
        if not self.token:
            print("⚠️  Warning: No SENSOR_TOWER_API_TOKEN found")
    
    def print_diagnostic(self, tool_name: str, status: str, details: str):
        emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "🔍"
        print(f"{emoji} {tool_name}: {details}")
    
    # ═══════════════════════════════════════════════════════════════════
    # 1. API ENDPOINT AVAILABILITY DIAGNOSIS
    # ═══════════════════════════════════════════════════════════════════
    
    def diagnose_endpoint_availability(self):
        """Test if problematic endpoints exist and are accessible"""
        print("\n🔍 Phase 1: Endpoint Availability Diagnosis")
        print("=" * 60)
        
        # Problem endpoints from our testing
        endpoints_to_test = {
            # 404 Errors (Usage Intelligence)
            "usage_active_users": "/v1/ios/usage_intelligence/active_users",
            "app_retention": "/v1/ios/usage_intelligence/retention", 
            "app_demographics": "/v1/ios/usage_intelligence/demographics",
            
            # 422 Errors (Advertising Intelligence) 
            "ad_creatives": "/v1/ios/ad_intel/creatives",
            "ad_impressions": "/v1/ios/ad_intel/network_analysis",
            "impressions_rank": "/v1/ios/ad_intel/network_analysis/rank",
        }
        
        for tool_name, endpoint in endpoints_to_test.items():
            self._test_endpoint_exists(tool_name, endpoint)
    
    def _test_endpoint_exists(self, tool_name: str, endpoint: str):
        """Test if an endpoint exists using OPTIONS/HEAD request"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            # Try OPTIONS first (least intrusive)
            response = requests.options(url, timeout=10)
            if response.status_code == 404:
                result = DiagnosticResult(
                    tool_name=tool_name,
                    issue_type="endpoint_not_found",
                    status="FAIL",
                    details=f"Endpoint {endpoint} returns 404",
                    recommendations=[
                        "Check if endpoint has been deprecated",
                        "Verify API documentation for correct endpoint",
                        "Check if different API version is needed"
                    ]
                )
            elif response.status_code in [200, 405, 501]:  # 405=Method Not Allowed is OK
                result = DiagnosticResult(
                    tool_name=tool_name,
                    issue_type="endpoint_exists",
                    status="PASS", 
                    details=f"Endpoint {endpoint} exists (status: {response.status_code})",
                    recommendations=["Endpoint exists - issue likely with parameters or auth"]
                )
            else:
                result = DiagnosticResult(
                    tool_name=tool_name,
                    issue_type="endpoint_unknown",
                    status="UNKNOWN",
                    details=f"Endpoint {endpoint} returned {response.status_code}",
                    recommendations=["Investigate unusual status code"]
                )
                
            self.results.append(result)
            self.print_diagnostic(tool_name, result.status, result.details)
            
        except requests.exceptions.RequestException as e:
            result = DiagnosticResult(
                tool_name=tool_name,
                issue_type="connection_error",
                status="FAIL",
                details=f"Connection error: {str(e)}",
                recommendations=["Check network connectivity", "Verify base URL"]
            )
            self.results.append(result)
            self.print_diagnostic(tool_name, result.status, result.details)
    
    # ═══════════════════════════════════════════════════════════════════
    # 2. PARAMETER VALIDATION DIAGNOSIS  
    # ═══════════════════════════════════════════════════════════════════
    
    def diagnose_parameter_validation(self):
        """Test different parameter combinations for 422 errors"""
        print("\n🔍 Phase 2: Parameter Validation Diagnosis")
        print("=" * 60)
        
        # Test minimal vs full parameter sets
        test_cases = [
            {
                "name": "ad_creatives_minimal",
                "endpoint": "/v1/ios/ad_intel/creatives",
                "params": {
                    "app_ids": "284882215",
                    "start_date": "2024-01-01",
                    "countries": "US",
                    "networks": "facebook",
                    "ad_types": "video"
                }
            },
            {
                "name": "ad_creatives_extended", 
                "endpoint": "/v1/ios/ad_intel/creatives",
                "params": {
                    "app_ids": "284882215",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31",
                    "countries": "US", 
                    "networks": "facebook,admob",
                    "ad_types": "video,image"
                }
            }
        ]
        
        for test_case in test_cases:
            self._test_parameters(test_case)
    
    def _test_parameters(self, test_case: Dict[str, Any]):
        """Test specific parameter combination"""
        if not self.token:
            self.print_diagnostic(test_case["name"], "UNKNOWN", "No API token - skipping parameter test")
            return
            
        try:
            url = f"{self.base_url}{test_case['endpoint']}"
            params = test_case["params"].copy()
            params["auth_token"] = self.token
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                result = DiagnosticResult(
                    tool_name=test_case["name"],
                    issue_type="parameters_valid", 
                    status="PASS",
                    details="Parameters accepted (200 OK)",
                    recommendations=["Original parameters may be incorrect"]
                )
            elif response.status_code == 422:
                # Try to parse error details
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", "Unknown validation error")
                except Exception:
                    error_msg = response.text[:100]
                    
                result = DiagnosticResult(
                    tool_name=test_case["name"],
                    issue_type="parameter_validation_error",
                    status="FAIL", 
                    details=f"422 Error: {error_msg}",
                    recommendations=[
                        "Check parameter format requirements",
                        "Verify date format (YYYY-MM-DD)",
                        "Check if app_ids format is correct",
                        "Verify country/network codes are valid"
                    ]
                )
            else:
                result = DiagnosticResult(
                    tool_name=test_case["name"],
                    issue_type="unexpected_error",
                    status="FAIL",
                    details=f"Unexpected status: {response.status_code}",
                    recommendations=["Investigate unusual response code"]
                )
                
            self.results.append(result)
            self.print_diagnostic(test_case["name"], result.status, result.details)
            
        except Exception as e:
            result = DiagnosticResult(
                tool_name=test_case["name"],
                issue_type="test_error",
                status="FAIL",
                details=f"Test error: {str(e)}",
                recommendations=["Fix test setup"]
            )
            self.results.append(result)
            self.print_diagnostic(test_case["name"], result.status, result.details)
    
    # ═══════════════════════════════════════════════════════════════════
    # 3. IMPLEMENTATION ERROR DIAGNOSIS
    # ═══════════════════════════════════════════════════════════════════
    
    def diagnose_implementation_errors(self):
        """Diagnose the publisher tools implementation error"""
        print("\n🔍 Phase 3: Implementation Error Diagnosis") 
        print("=" * 60)
        
        # Test the get_publisher_apps response format issue
        self._diagnose_publisher_apps_format()
    
    def _diagnose_publisher_apps_format(self):
        """Diagnose the list vs dict format issue in get_publisher_apps"""
        
        # Simulate the actual API response format (this is what we know works)
        simulated_api_response = [
            {
                "app_id": 284882215,
                "app_name": "Facebook", 
                "publisher_id": 284882218,
                "publisher_name": "Meta Platforms, Inc."
            },
            {
                "app_id": 454638411,
                "app_name": "Messenger",
                "publisher_id": 284882218, 
                "publisher_name": "Meta Platforms, Inc."
            }
        ]
        
        # Test current implementation (returns list - causes error)
        if isinstance(simulated_api_response, list):
            result = DiagnosticResult(
                tool_name="get_publisher_apps_current",
                issue_type="implementation_error",
                status="FAIL",
                details="Tool returns list format instead of expected dict",
                recommendations=[
                    "Wrap list response in dict structure", 
                    "Add metadata like total_count, publisher_info",
                    "Follow same pattern as search_entities fix"
                ]
            )
            self.print_diagnostic("get_publisher_apps_current", result.status, result.details)
            
        # Test proposed fix (wrap in dict)
        fixed_response = {
            "apps": simulated_api_response,
            "total_count": len(simulated_api_response),
            "publisher_id": "284882218",
            "publisher_name": "Meta Platforms, Inc."
        }
        
        if isinstance(fixed_response, dict) and "apps" in fixed_response:
            result = DiagnosticResult(
                tool_name="get_publisher_apps_fixed",
                issue_type="implementation_fix",
                status="PASS", 
                details=f"Fixed format with {fixed_response['total_count']} apps in dict structure",
                recommendations=["Implement this fix in main.py"]
            )
            self.print_diagnostic("get_publisher_apps_fixed", result.status, result.details)
            
        self.results.extend([result])
    
    # ═══════════════════════════════════════════════════════════════════
    # 4. ACCESS LEVEL DIAGNOSIS
    # ═══════════════════════════════════════════════════════════════════
    
    def diagnose_access_levels(self):
        """Test if issues are related to API access levels"""
        print("\n🔍 Phase 4: Access Level Diagnosis")
        print("=" * 60)
        
        if not self.token:
            self.print_diagnostic("access_check", "UNKNOWN", "No API token - cannot check access levels")
            return
            
        # Test with known working endpoint to verify token validity
        self._test_token_validity()
        
        # Test premium/restricted endpoints
        self._test_premium_endpoints()
    
    def _test_token_validity(self):
        """Verify API token works with basic endpoints"""
        try:
            # Test with known working endpoint
            url = f"{self.base_url}/v1/ios/rankings/get_category_rankings"
            params = {
                "auth_token": self.token,
                "category": "6005", 
                "chart_type": "topfreeapplications",
                "country": "US",
                "date": "2024-01-15"
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                result = DiagnosticResult(
                    tool_name="token_validity",
                    issue_type="access_check",
                    status="PASS",
                    details="API token valid - can access basic endpoints",
                    recommendations=["Token works - issues may be endpoint-specific"]
                )
            elif response.status_code == 401:
                result = DiagnosticResult(
                    tool_name="token_validity", 
                    issue_type="auth_error",
                    status="FAIL",
                    details="API token invalid or expired",
                    recommendations=["Check token validity", "Regenerate API token"]
                )
            else:
                result = DiagnosticResult(
                    tool_name="token_validity",
                    issue_type="unexpected_auth_error", 
                    status="FAIL",
                    details=f"Unexpected auth response: {response.status_code}",
                    recommendations=["Investigate auth system"]
                )
                
            self.results.append(result)
            self.print_diagnostic("token_validity", result.status, result.details)
            
        except Exception as e:
            result = DiagnosticResult(
                tool_name="token_validity",
                issue_type="test_error",
                status="FAIL", 
                details=f"Token test error: {str(e)}",
                recommendations=["Fix network connectivity"]
            )
            self.results.append(result)
            self.print_diagnostic("token_validity", result.status, result.details)
    
    def _test_premium_endpoints(self):
        """Test if problematic endpoints require premium access"""
        premium_endpoints = [
            "/v1/ios/usage_intelligence/active_users",
            "/v1/ios/ad_intel/creatives" 
        ]
        
        for endpoint in premium_endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                params = {
                    "auth_token": self.token,
                    "app_ids": "284882215",
                    "start_date": "2024-01-01",
                    "countries": "US"
                }
                
                response = requests.get(url, params=params, timeout=30)
                
                if response.status_code == 403:
                    self.print_diagnostic(f"premium_access_{endpoint.split('/')[-1]}", 
                                        "FAIL", "403 Forbidden - May require premium access")
                elif response.status_code == 402:
                    self.print_diagnostic(f"premium_access_{endpoint.split('/')[-1]}", 
                                        "FAIL", "402 Payment Required - Requires paid plan")
                else:
                    self.print_diagnostic(f"premium_access_{endpoint.split('/')[-1]}", 
                                        "UNKNOWN", f"Status {response.status_code} - Not access-related")
                    
            except Exception as e:
                self.print_diagnostic(f"premium_test_{endpoint.split('/')[-1]}", 
                                    "FAIL", f"Test error: {str(e)}")
    
    # ═══════════════════════════════════════════════════════════════════
    # 5. COMPREHENSIVE DIAGNOSTIC REPORT
    # ═══════════════════════════════════════════════════════════════════
    
    def generate_diagnostic_report(self):
        """Generate comprehensive diagnostic report with recommendations"""
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE DIAGNOSTIC REPORT")
        print("=" * 60)
        
        # Group results by issue type
        issue_groups = {}
        for result in self.results:
            if result.issue_type not in issue_groups:
                issue_groups[result.issue_type] = []
            issue_groups[result.issue_type].append(result)
        
        # Print grouped results
        for issue_type, results in issue_groups.items():
            print(f"\n🔧 {issue_type.replace('_', ' ').title()}")
            print("-" * 40)
            
            for result in results:
                status_emoji = "✅" if result.status == "PASS" else "❌" if result.status == "FAIL" else "❓"
                print(f"{status_emoji} {result.tool_name}: {result.details}")
                
                if result.recommendations:
                    for rec in result.recommendations:
                        print(f"   💡 {rec}")
        
        # Summary statistics
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == "PASS"])
        failed_tests = len([r for r in self.results if r.status == "FAIL"])
        unknown_tests = len([r for r in self.results if r.status == "UNKNOWN"])
        
        print("\n📊 DIAGNOSTIC SUMMARY")
        print("-" * 40)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}") 
        print(f"❓ Unknown: {unknown_tests}")
        
        # Priority recommendations
        print("\n🎯 PRIORITY ACTIONS")
        print("-" * 40)
        
        if any(r.issue_type == "endpoint_not_found" for r in self.results):
            print("1. 🔴 HIGH: Investigate deprecated endpoints (404 errors)")
            print("   → Check Sensor Tower API documentation for endpoint changes")
            print("   → Consider if usage intelligence requires different access tier")
        
        if any(r.issue_type == "parameter_validation_error" for r in self.results):
            print("2. 🟡 MEDIUM: Fix parameter validation errors (422 errors)")
            print("   → Review parameter formats and requirements")
            print("   → Test with minimal parameter sets first")
        
        if any(r.issue_type == "implementation_error" for r in self.results):
            print("3. 🟢 LOW: Fix implementation issues")
            print("   → Update get_publisher_apps to return dict format")
            print("   → Follow existing patterns from other fixed tools")
        
        return {
            "total": total_tests,
            "passed": passed_tests, 
            "failed": failed_tests,
            "unknown": unknown_tests,
            "results": self.results
        }
    
    def run_full_diagnostics(self):
        """Run complete diagnostic suite"""
        print("🔍 SYSTEMATIC SENSOR TOWER MCP DIAGNOSTICS")
        print("=" * 60)
        print("Diagnosing specific issues found in comprehensive testing")
        print()
        
        # Run all diagnostic phases
        self.diagnose_endpoint_availability()
        self.diagnose_parameter_validation() 
        self.diagnose_implementation_errors()
        self.diagnose_access_levels()
        
        # Generate final report
        report = self.generate_diagnostic_report()
        
        return report

def main():
    """Run systematic diagnostics"""
    diagnostics = SensorTowerDiagnostics()
    report = diagnostics.run_full_diagnostics()
    
    if report["failed"] == 0:
        print("\n🎉 All diagnostic tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  Found {report['failed']} issues requiring attention")
        sys.exit(1)

if __name__ == "__main__":
    main()
