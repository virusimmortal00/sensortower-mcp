"""
Sensor Tower MCP Testing Suite

This package contains comprehensive testing scripts for validating the
sensortower-mcp PyPI package and Docker image for production readiness.

Test Scripts:
- test_all.py: Master script that runs all tests and generates production readiness report
- test_deployment.py: Comprehensive PyPI package and Docker image testing
- test_manual.py: Quick manual validation for development
- test_load.py: Performance testing under concurrent load
- test_security.py: Security audit and vulnerability scanning

Usage:
    # Run all tests
    python tests/test_all.py
    
    # Quick validation
    python tests/test_manual.py
    
    # Full deployment testing
    python tests/test_deployment.py

Prerequisites:
    pip install httpx aiohttp
    
Environment Variables:
    SENSOR_TOWER_API_TOKEN: Your Sensor Tower API token (optional but recommended)
"""

__version__ = "1.0.0"
__author__ = "Sensor Tower MCP Team"

# Test script descriptions for documentation
TEST_SCRIPTS = {
    "test_all.py": {
        "description": "Master script - runs all tests and generates production readiness report",
        "time": "5-10 minutes",
        "prerequisites": ["Python"],
        "critical": True
    },
    "test_deployment.py": {
        "description": "Comprehensive PyPI package and Docker image testing",
        "time": "3-5 minutes", 
        "prerequisites": ["httpx", "Docker"],
        "critical": True
    },
    "test_manual.py": {
        "description": "Quick manual validation for development",
        "time": "30 seconds",
        "prerequisites": ["httpx"],
        "critical": False
    },
    "test_load.py": {
        "description": "Performance testing under concurrent load",
        "time": "1-2 minutes",
        "prerequisites": ["aiohttp", "running server"],
        "critical": False
    },
    "test_security.py": {
        "description": "Security audit and vulnerability scanning",
        "time": "2-3 minutes",
        "prerequisites": ["httpx"],
        "critical": True
    }
} 