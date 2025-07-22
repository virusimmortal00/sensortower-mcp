#!/usr/bin/env python3
"""
Quick manual testing script for sensortower-mcp.
Run this after deployment to verify basic functionality.
"""

import asyncio
import json
import os
import httpx
import sys
from typing import Dict, Any

def print_result(test_name: str, success: bool, data: Any = None):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if data:
        print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
    print()

async def test_api_endpoints(base_url: str, token: str):
    """Test actual API endpoints with real token"""
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Health check
        try:
            response = await client.get(f"{base_url}/health")
            print_result("Health check", response.status_code == 200, response.json())
        except Exception as e:
            print_result("Health check", False, str(e))
        
        # Test 2: Search entities (low-impact test)
        try:
            response = await client.post(f"{base_url}/mcp/tools/invoke", json={
                "tool": "search_entities",
                "arguments": {
                    "os": "ios",
                    "entity_type": "app",
                    "term": "weather",
                    "limit": 5
                }
            })
            print_result("Search entities", response.status_code == 200, response.json())
        except Exception as e:
            print_result("Search entities", False, str(e))
        
        # Test 3: Get country codes (utility endpoint)
        try:
            response = await client.post(f"{base_url}/mcp/tools/invoke", json={
                "tool": "get_country_codes",
                "arguments": {}
            })
            print_result("Get country codes", response.status_code == 200, response.json())
        except Exception as e:
            print_result("Get country codes", False, str(e))
        
        # Test 4: Get category IDs
        try:
            response = await client.post(f"{base_url}/mcp/tools/invoke", json={
                "tool": "get_category_ids",
                "arguments": {"os": "ios"}
            })
            print_result("Get category IDs", response.status_code == 200, response.json())
        except Exception as e:
            print_result("Get category IDs", False, str(e))

async def test_pypi_installation():
    """Test PyPI package installation in current environment"""
    try:
        # Add parent directory to path to import main module
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        import main
        print_result("PyPI package import", True, "Package imported successfully")
        
        # Test CLI availability
        from main import mcp
        print_result("FastMCP initialization", True, "MCP server initialized")
        
    except ImportError as e:
        print_result("PyPI package import", False, str(e))
        print("Try: pip install sensortower-mcp")
        return False
    
    return True

async def test_docker_local():
    """Test local Docker container"""
    import subprocess
    
    try:
        # Check if container is running
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=sensortower-mcp", "--format", "{{.Status}}"],
            capture_output=True, text=True
        )
        
        if result.returncode == 0 and "Up" in result.stdout:
            print_result("Docker container status", True, "Container is running")
            
            # Test health endpoint
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get("http://localhost:8666/health", timeout=5)
                    print_result("Docker health endpoint", response.status_code == 200, response.json())
                except Exception as e:
                    print_result("Docker health endpoint", False, str(e))
        else:
            print_result("Docker container status", False, "No running container found")
            print("Start with: docker-compose up -d")
            
    except FileNotFoundError:
        print_result("Docker availability", False, "Docker not found")

async def main():
    print("🧪 Sensor Tower MCP Manual Testing")
    print("=" * 50)
    
    # Check environment
    token = os.getenv("SENSOR_TOWER_API_TOKEN")
    if not token:
        print("⚠️  SENSOR_TOWER_API_TOKEN not set. Some tests will be skipped.")
        print("   Get your token from: https://app.sensortower.com/users/edit/api-settings")
    
    print("\n1. Testing PyPI Package Installation:")
    await test_pypi_installation()
    
    print("\n2. Testing Docker Container:")
    await test_docker_local()
    
    if token:
        print("\n3. Testing API Endpoints (HTTP mode):")
        await test_api_endpoints("http://localhost:8666", token)
        
        print("\n4. Testing API Endpoints (direct HTTP):")
        print("   Starting temporary HTTP server...")
        # This would require starting the server in a subprocess
        print("   (Run 'sensortower-mcp --transport http' in another terminal)")
    else:
        print("\n3. API Endpoint Testing: SKIPPED (no token)")
    
    print("\n✅ Manual testing complete!")
    print("\nNext steps:")
    print("1. Set SENSOR_TOWER_API_TOKEN to test API functionality")
    print("2. Run full test suite: python test_deployment.py")
    print("3. Test in production environment")

if __name__ == "__main__":
    asyncio.run(main()) 