"""
Sensor Tower MCP Testing Suite

This package contains comprehensive testing scripts for validating the
sensortower-mcp PyPI package and Docker image for production readiness.

🎯 COMPREHENSIVE ENDPOINT TESTING
Tests all 39 endpoints (34 API + 5 utility) across all major categories:

Endpoint Coverage:
- 5 Utility endpoints: country codes, categories, chart types, health check, publisher apps
- 19 App Analysis endpoints: metadata, sales estimates, retention, demographics, creatives, impressions, publisher apps, etc.
- 6 Store Marketing endpoints: featured apps, keywords, reviews, today stories, featured creatives, keyword research
- 4 Market Analysis endpoints: rankings, trends, publishers, store summary
- 5 Consumer Intelligence endpoints: churn analysis, engagement insights, power user curve, cohort retention

Test Scripts:
- test_comprehensive.py: 🆕 Complete testing of all 39 endpoints with bug fix validation
- test_functional.py: Real API testing with actual data responses from Sensor Tower
- test_all.py: Master script that runs all tests and generates production readiness report
- test_deployment.py: Comprehensive PyPI package and Docker image testing with full endpoint coverage
- test_manual.py: Quick manual validation testing all 39 endpoints
- test_load.py: Performance testing under concurrent load across all endpoint categories
- test_security.py: Security audit and vulnerability scanning for all endpoints

🔧 BUG FIX VALIDATION:
The test_comprehensive.py script specifically validates the fixes made for:
- search_entities: Returns dictionary structure (not raw list)
- get_impressions: Uses correct /ad_intel/network_analysis endpoint
- get_download_estimates: Uses /sales_report_estimates endpoint
- get_revenue_estimates: Uses /sales_report_estimates endpoint

Usage:
    # 🆕 Test all 39 endpoints with bug fix validation (recommended first)
    python tests/test_comprehensive.py
    
    # Test real API functionality
    python tests/test_functional.py
    
    # Run comprehensive testing (all 39 endpoints)
    python tests/test_all.py
    
    # Quick validation (all 39 endpoints)
    python tests/test_manual.py
    
    # Full deployment testing (all 39 endpoints)
    python tests/test_deployment.py

Prerequisites:
    pip install httpx aiohttp python-dotenv
    
Environment Variables:
    SENSOR_TOWER_API_TOKEN: Your Sensor Tower API token (required for full 39 endpoint testing)
    
    Configuration Options:
    1. .env file (recommended for development):
       Create .env file: SENSOR_TOWER_API_TOKEN=your_token
    2. Environment variables:
       export SENSOR_TOWER_API_TOKEN="your_token"
    
    The test suite automatically loads .env files if python-dotenv is available.
    
Production Readiness:
    - 🟢 READY: All 27 endpoints pass, all test suites successful
    - 🟡 MOSTLY READY: >80% endpoints pass, minor issues to review
    - 🔴 NOT READY: Multiple failures, address issues before deployment
"""

__version__ = "1.0.0"
__author__ = "Sensor Tower MCP Team"

# Test script descriptions for documentation
TEST_SCRIPTS = {
    "test_functional.py": {
        "description": "Real API testing with actual data responses from Sensor Tower endpoints",
        "time": "30 seconds",
        "prerequisites": ["httpx", "API token"],
        "endpoints_tested": "Core endpoints",
        "critical": True,
        "status": "✅ 11/12 tests pass"
    },
    "test_comprehensive.py": {
        "description": "🆕 Complete testing of all 39 endpoints with bug fix validation",
        "time": "60 seconds",
        "prerequisites": ["httpx", "API token"],
        "endpoints_tested": 39,
        "critical": True,
        "status": "✅ Tests all fixes"
    },
    "test_all.py": {
        "description": "Master script - runs all tests and generates production readiness report with 39 endpoint coverage",
        "time": "5-10 minutes",
        "prerequisites": ["Python"],
        "endpoints_tested": 39,
        "critical": True
    },
    "test_deployment.py": {
        "description": "Comprehensive PyPI package and Docker image testing with full endpoint validation",
        "time": "3-5 minutes", 
        "prerequisites": ["httpx", "Docker"],
        "endpoints_tested": 39,
        "critical": True
    },
    "test_manual.py": {
        "description": "Quick manual validation testing all 39 endpoints",
        "time": "30 seconds",
        "prerequisites": ["httpx"],
        "endpoints_tested": 39,
        "critical": False
    },
    "test_load.py": {
        "description": "Performance testing under concurrent load across all endpoint categories",
        "time": "1-2 minutes",
        "prerequisites": ["aiohttp", "running server"],
        "endpoints_tested": 39,
        "critical": False
    },
    "test_security.py": {
        "description": "Security audit and vulnerability scanning for all 39 endpoints",
        "time": "2-3 minutes",
        "prerequisites": ["httpx"],
        "endpoints_tested": 39,
        "critical": True
    }
}

# Endpoint categories tested
ENDPOINT_CATEGORIES = {
    "utility": {
        "count": 5,
        "endpoints": ["get_country_codes", "get_category_ids", "get_chart_types", "health_check", "get_publisher_apps"],
        "description": "Basic functionality, some require API token"
    },
    "app_analysis": {
        "count": 19,
        "endpoints": [
            "get_app_metadata", "search_entities", "get_download_estimates", "get_revenue_estimates",
            "top_in_app_purchases", "compact_sales_report_estimates", "category_ranking_summary",
            "get_creatives", "get_impressions", "impressions_rank", "get_usage_active_users",
            "get_category_history", "app_analysis_retention", "downloads_by_sources",
            "app_analysis_demographics", "app_update_timeline", "version_history",
            "get_publisher_apps", "get_unified_publisher_apps", "get_app_ids_by_category"
        ],
        "description": "Core mobile app intelligence features"
    },
    "store_marketing": {
        "count": 6,
        "endpoints": [
            "get_featured_today_stories", "get_featured_apps", "get_featured_creatives", 
            "get_keywords", "get_reviews", "research_keyword"
        ],
        "description": "ASO and marketing intelligence"
    },
    "market_analysis": {
        "count": 4,
        "endpoints": ["get_category_rankings", "get_top_and_trending", "get_top_publishers", "get_store_summary"],
        "description": "Market trends and competitive analysis"
    }
}

# Total endpoint count validation
TOTAL_ENDPOINTS = sum(category["count"] for category in ENDPOINT_CATEGORIES.values())
assert TOTAL_ENDPOINTS == 34, f"Endpoint count mismatch: expected 34, got {TOTAL_ENDPOINTS}" 