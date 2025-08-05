#!/usr/bin/env python3
"""
Quick Diagnostic Runner for Sensor Tower MCP Issues

This script provides an easy way to run systematic diagnostics
and get actionable results for fixing the identified issues.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Run diagnostics with proper setup"""
    
    print("🔍 SENSOR TOWER MCP DIAGNOSTIC RUNNER")
    print("=" * 50)
    
    # Check if we're in the right directory
    project_root = Path(__file__).parent
    diagnostic_script = project_root / "tests" / "diagnostic_tests.py"
    
    if not diagnostic_script.exists():
        print("❌ Error: diagnostic_tests.py not found")
        print(f"Expected at: {diagnostic_script}")
        return 1
    
    # Check for API token
    token = os.getenv("SENSOR_TOWER_API_TOKEN")
    if not token:
        print("⚠️  Warning: No SENSOR_TOWER_API_TOKEN environment variable found")
        print("   Some diagnostic tests will be limited without API access")
        print("   Set your token with: export SENSOR_TOWER_API_TOKEN=your_token")
        print()
    else:
        print("✅ API token found - full diagnostics available")
        print()
    
    print("🚀 Running systematic diagnostics...")
    print("   This will test the 7 tools with issues found in comprehensive testing")
    print()
    
    try:
        # Run the diagnostic script
        result = subprocess.run([
            sys.executable, 
            str(diagnostic_script)
        ], cwd=project_root, capture_output=False)
        
        print("\n" + "=" * 50)
        if result.returncode == 0:
            print("✅ Diagnostics completed successfully!")
            print("\n📋 NEXT STEPS:")
            print("1. Review the diagnostic results above")
            print("2. Check DIAGNOSTIC_PLAN.md for detailed guidance")
            print("3. Apply fixes based on the recommendations")
            print("4. Re-run comprehensive tests to verify fixes")
        else:
            print("⚠️  Diagnostics completed with issues found")
            print("\n📋 NEXT STEPS:")
            print("1. Review the specific failures above")
            print("2. Check DIAGNOSTIC_PLAN.md for systematic resolution")
            print("3. Start with quick wins (implementation fixes)")
            print("4. Investigate API access issues if needed")
        
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error running diagnostics: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())