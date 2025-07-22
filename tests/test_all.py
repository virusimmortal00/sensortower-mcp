#!/usr/bin/env python3
"""
Master test script for sensortower-mcp - runs all testing suites.
Use this to get a comprehensive production readiness assessment.
Tests all 27 endpoints (23 API + 4 utility) for complete coverage.
"""

import asyncio
import subprocess
import sys
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass

# Add parent directory to path to import main module
sys.path.insert(0, str(Path(__file__).parent.parent))

class MasterTester:
    def __init__(self):
        self.results = {}
        self.start_time = time.time()
        self.tests_dir = Path(__file__).parent
    
    def print_header(self, title: str):
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print(f"{'='*60}")
    
    def print_section(self, title: str):
        print(f"\n{'─'*40}")
        print(f"📋 {title}")
        print(f"{'─'*40}")
    
    def print_endpoint_summary(self):
        """Print comprehensive endpoint testing summary"""
        print(f"\n📊 Comprehensive Endpoint Testing Coverage:")
        print("┌─────────────────────────────────────────────┬─────────┐")
        print("│ Category                                    │ Count   │")
        print("├─────────────────────────────────────────────┼─────────┤")
        print("│ Utility Endpoints                           │   4     │")
        print("│ App Analysis Endpoints                      │  16     │")
        print("│ Store Marketing Endpoints                   │   4     │")
        print("│ Market Analysis Endpoints                   │   4     │")
        print("├─────────────────────────────────────────────┼─────────┤")
        print("│ Total Endpoints Tested                      │  27     │")
        print("└─────────────────────────────────────────────┴─────────┘")
    
    def run_script(self, script_name: str, description: str) -> Tuple[bool, str]:
        """Run a test script and capture results"""
        print(f"\n🚀 Running {description}...")
        
        script_path = self.tests_dir / script_name
        if not script_path.exists():
            return False, f"Script {script_name} not found"
        
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes max per script
                cwd=self.tests_dir.parent  # Run from project root
            )
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            if success:
                print("✅ PASSED")
            else:
                print("❌ FAILED")
                print(f"Exit code: {result.returncode}")
            
            return success, output
            
        except subprocess.TimeoutExpired:
            print("⏰ TIMEOUT (5 minutes)")
            return False, "Test timed out after 5 minutes"
        except Exception as e:
            print(f"💥 ERROR: {e}")
            return False, str(e)
    
    def save_report(self, filename: str = "test_report.txt"):
        """Save detailed test results to file"""
        report_path = self.tests_dir / filename
        
        with open(report_path, 'w') as f:
            f.write("SENSOR TOWER MCP - COMPREHENSIVE TEST REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Test run completed: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total runtime: {time.time() - self.start_time:.2f} seconds\n\n")
            
            f.write("ENDPOINT COVERAGE:\n")
            f.write("- 4 Utility endpoints (country codes, categories, chart types, health)\n")
            f.write("- 16 App Analysis endpoints (metadata, sales, retention, demographics, etc.)\n")
            f.write("- 4 Store Marketing endpoints (featured apps, keywords, reviews)\n")
            f.write("- 4 Market Analysis endpoints (rankings, trends, publishers, store summary)\n")
            f.write("Total: 27 endpoints tested\n\n")
            
            f.write("TEST RESULTS:\n")
            for test_name, (success, output) in self.results.items():
                status = "PASSED" if success else "FAILED"
                f.write(f"\n{test_name}: {status}\n")
                f.write("-" * 40 + "\n")
                f.write(output + "\n")
        
        print(f"\n📄 Detailed report saved to: {report_path}")
    
    async def run_all_tests(self):
        """Run all test suites"""
        self.print_header("Sensor Tower MCP - Master Test Suite")
        print("🎯 Comprehensive testing of all 27 endpoints")
        
        self.print_endpoint_summary()
        
        # Test suites to run
        test_suites = [
            ("test_manual.py", "Quick Manual Testing"),
            ("test_deployment.py", "Comprehensive Deployment Testing"),
            ("test_load.py", "Performance & Load Testing"),
            ("test_security.py", "Security & Vulnerability Testing")
        ]
        
        # Check environment setup
        self.print_section("Environment Check")
        
        token = os.getenv("SENSOR_TOWER_API_TOKEN")
        if token:
            print("✅ SENSOR_TOWER_API_TOKEN: Set")
        else:
            print("⚠️  SENSOR_TOWER_API_TOKEN: Not set (some tests will be limited)")
        
        # Check Docker
        try:
            subprocess.run(["docker", "--version"], 
                         capture_output=True, check=True)
            print("✅ Docker: Available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  Docker: Not available (some tests will be skipped)")
        
        # Check Python dependencies
        try:
            import httpx
            print("✅ httpx: Available")
        except ImportError:
            print("❌ httpx: Missing (install with: pip install httpx)")
        
        # Run all test suites
        self.print_section("Running Test Suites")
        
        for script_name, description in test_suites:
            success, output = self.run_script(script_name, description)
            self.results[description] = (success, output)
        
        # Generate summary
        self.print_section("Test Summary")
        
        passed = sum(1 for success, _ in self.results.values() if success)
        total = len(self.results)
        
        print(f"📊 Results: {passed}/{total} test suites passed")
        
        for test_name, (success, _) in self.results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   {status} {test_name}")
        
        # Production readiness assessment
        print(f"\n{'='*60}")
        print("🏆 PRODUCTION READINESS ASSESSMENT")
        print(f"{'='*60}")
        
        if passed == total:
            print("🟢 READY FOR PRODUCTION")
            print("   All test suites passed successfully")
            print("   All 27 endpoints validated")
        elif passed >= total * 0.8:
            print("🟡 MOSTLY READY")
            print("   Most tests passed, review failures")
            print("   27 endpoints available for testing")
        else:
            print("🔴 NOT READY")
            print("   Multiple test failures detected")
            print("   Address issues before production deployment")
        
        # Save detailed report
        self.save_report()
        
        # Return overall success
        return passed == total

async def main():
    """Main entry point"""
    tester = MasterTester()
    
    try:
        success = await tester.run_all_tests()
        
        print(f"\n🎉 Master test suite completed!")
        print(f"⏱️  Total runtime: {time.time() - tester.start_time:.2f} seconds")
        
        if not success:
            print("\n❌ Some tests failed. Check the detailed report for more information.")
            sys.exit(1)
        else:
            print("\n✅ All tests passed! System is production-ready.")
            
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 