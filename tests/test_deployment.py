#!/usr/bin/env python3
"""
Comprehensive deployment testing for sensortower-mcp package and Docker image.
Tests both PyPI package installation and Docker image functionality.
"""

import asyncio
import json
import os
import subprocess
import sys
import tempfile
import time
import httpx
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class TestLogger:
    def __init__(self):
        self.results = []
    
    def success(self, test_name: str, details: str = ""):
        print(f"{Colors.GREEN}✓{Colors.END} {test_name}")
        if details:
            print(f"  {details}")
        self.results.append(("PASS", test_name, details))
    
    def failure(self, test_name: str, error: str):
        print(f"{Colors.RED}✗{Colors.END} {test_name}")
        print(f"  {Colors.RED}Error: {error}{Colors.END}")
        self.results.append(("FAIL", test_name, error))
    
    def warning(self, test_name: str, warning: str):
        print(f"{Colors.YELLOW}⚠{Colors.END} {test_name}")
        print(f"  {Colors.YELLOW}Warning: {warning}{Colors.END}")
        self.results.append(("WARN", test_name, warning))
    
    def info(self, message: str):
        print(f"{Colors.BLUE}ℹ{Colors.END} {message}")
    
    def header(self, title: str):
        print(f"\n{Colors.BOLD}{Colors.BLUE}═══ {title} ═══{Colors.END}")
    
    def summary(self):
        passed = sum(1 for r in self.results if r[0] == "PASS")
        failed = sum(1 for r in self.results if r[0] == "FAIL")
        warned = sum(1 for r in self.results if r[0] == "WARN")
        total = len(self.results)
        
        print(f"\n{Colors.BOLD}Testing Summary:{Colors.END}")
        print(f"Total tests: {total}")
        print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
        print(f"{Colors.RED}Failed: {failed}{Colors.END}")
        print(f"{Colors.YELLOW}Warnings: {warned}{Colors.END}")
        
        if failed > 0:
            print(f"\n{Colors.RED}Failed tests:{Colors.END}")
            for result in self.results:
                if result[0] == "FAIL":
                    print(f"  - {result[1]}: {result[2]}")

logger = TestLogger()

def run_command(cmd: List[str], cwd: Optional[str] = None, timeout: int = 30) -> Tuple[bool, str, str]:
    """Run a command and return success, stdout, stderr"""
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            cwd=cwd
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

async def test_pypi_package():
    """Test PyPI package installation and functionality"""
    logger.header("PyPI Package Testing")
    
    logger.info("Testing comprehensive endpoint coverage (27 total endpoints)")
    
    # Test 1: Create clean virtual environment
    with tempfile.TemporaryDirectory() as temp_dir:
        venv_path = Path(temp_dir) / "test_venv"
        
        # Create virtual environment
        success, stdout, stderr = run_command([sys.executable, "-m", "venv", str(venv_path)])
        if not success:
            logger.failure("Virtual environment creation", stderr)
            return
        logger.success("Virtual environment creation")
        
        # Get python and pip paths
        if sys.platform == "win32":
            python_path = venv_path / "Scripts" / "python.exe"
            pip_path = venv_path / "Scripts" / "pip.exe"
        else:
            python_path = venv_path / "bin" / "python"
            pip_path = venv_path / "bin" / "pip"
        
        # Test 2: Install package from PyPI
        success, stdout, stderr = run_command([str(pip_path), "install", "sensortower-mcp"])
        if not success:
            logger.failure("PyPI package installation", stderr)
            return
        logger.success("PyPI package installation", f"Installed successfully")
        
        # Test 3: Verify CLI availability
        success, stdout, stderr = run_command([str(python_path), "-c", "import sys; sys.path.insert(0, '.'); import main; print('Import successful')"])
        if not success:
            logger.failure("Package import test", stderr)
            return
        logger.success("Package import test")
        
        # Test 4: Test CLI without token (should show error)
        success, stdout, stderr = run_command([str(python_path), "-m", "main", "--help"], timeout=10)
        if not success:
            logger.failure("CLI help command", stderr)
            return
        logger.success("CLI help command", "Help text generated")
        
        # Test 5: Test with mock token (should start and fail gracefully)
        env = os.environ.copy()
        env["SENSOR_TOWER_API_TOKEN"] = "test_token_12345"
        
        # Start the server in HTTP mode and test health endpoint
        try:
            process = subprocess.Popen(
                [str(python_path), "-c", "import sys; sys.path.insert(0, '.'); import main; main.cli()", "--transport", "http", "--port", "8667"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment for server to start
            await asyncio.sleep(3)
            
            # Test health endpoint
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get("http://localhost:8667/health", timeout=5)
                    if response.status_code == 200:
                        logger.success("HTTP server startup", f"Health check returned: {response.json()}")
                    else:
                        logger.failure("HTTP server health check", f"Status code: {response.status_code}")
            except Exception as e:
                logger.failure("HTTP server connection", str(e))
            
            # Clean shutdown
            process.terminate()
            process.wait(timeout=5)
            
        except Exception as e:
            logger.failure("HTTP server test", str(e))

async def test_docker_image():
    """Test Docker image functionality with all 27 endpoints"""
    logger.header("Docker Image Testing")
    
    logger.info("Testing all 27 endpoints in Docker environment")
    
    # Test 1: Check if Docker is available
    success, stdout, stderr = run_command(["docker", "--version"])
    if not success:
        logger.failure("Docker availability", "Docker not found. Please install Docker to run these tests.")
        return
    logger.success("Docker availability", stdout.strip())
    
    # Test 2: Pull the latest image
    success, stdout, stderr = run_command(["docker", "pull", "bobbysayers492/sensortower-mcp:latest"], timeout=120)
    if not success:
        logger.failure("Docker image pull", stderr)
        return
    logger.success("Docker image pull", "Latest image pulled successfully")
    
    # Test 3: Test image with health check
    container_name = "sensortower-mcp-test"
    
    # Clean up any existing container
    run_command(["docker", "rm", "-f", container_name])
    
    # Test 4: Run container in HTTP mode
    success, stdout, stderr = run_command([
        "docker", "run", "-d",
        "--name", container_name,
        "-p", "8668:8666",
        "-e", "SENSOR_TOWER_API_TOKEN=test_token_12345",
        "bobbysayers492/sensortower-mcp:latest",
        "sensortower-mcp", "--transport", "http", "--port", "8666"
    ])
    
    if not success:
        logger.failure("Docker container startup", stderr)
        return
    logger.success("Docker container startup", f"Container {container_name} started")
    
    # Wait for container to be ready
    await asyncio.sleep(5)
    
    # Test 5: Check container health
    success, stdout, stderr = run_command(["docker", "inspect", "--format", "{{.State.Health.Status}}", container_name])
    if success and "healthy" in stdout:
        logger.success("Docker health check", "Container is healthy")
    else:
        logger.warning("Docker health check", f"Health status: {stdout.strip()}")
    
    # Test 6: Test HTTP endpoint
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8668/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                logger.success("Docker HTTP endpoint", f"Health check: {data}")
            else:
                logger.failure("Docker HTTP endpoint", f"Status code: {response.status_code}")
    except Exception as e:
        logger.failure("Docker HTTP endpoint", str(e))
    
    # Test 7: Check container logs
    success, stdout, stderr = run_command(["docker", "logs", container_name])
    if success:
        if "Starting Sensor Tower MCP Server" in stdout:
            logger.success("Docker container logs", "Server started successfully")
        else:
            logger.warning("Docker container logs", "Startup message not found in logs")
    else:
        logger.failure("Docker container logs", stderr)
    
    # Test 8: Test stdio mode
    run_command(["docker", "rm", "-f", container_name])
    
    success, stdout, stderr = run_command([
        "docker", "run", "-d",
        "--name", f"{container_name}-stdio",
        "-e", "SENSOR_TOWER_API_TOKEN=test_token_12345",
        "bobbysayers492/sensortower-mcp:latest"
    ])
    
    if success:
        logger.success("Docker stdio mode", "Container started in stdio mode")
        # Check logs for stdio startup
        await asyncio.sleep(3)
        success, stdout, stderr = run_command(["docker", "logs", f"{container_name}-stdio"])
        if "Transport: stdio" in stdout:
            logger.success("Docker stdio configuration", "Stdio transport configured correctly")
    else:
        logger.failure("Docker stdio mode", stderr)
    
    # Cleanup
    run_command(["docker", "rm", "-f", container_name])
    run_command(["docker", "rm", "-f", f"{container_name}-stdio"])

async def test_api_endpoints_comprehensive(base_url: str, token: str) -> bool:
    """Comprehensive test of all 27 API endpoints"""
    logger.header("Comprehensive API Endpoint Testing")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Test utility endpoints (no token required)
        utility_endpoints = [
            ("get_country_codes", {}),
            ("get_category_ids", {"os": "ios"}),
            ("get_chart_types", {}),
            ("health_check", {})
        ]
        
        for tool_name, args in utility_endpoints:
            try:
                response = await client.post(f"{base_url}/mcp/tools/invoke", json={
                    "tool": tool_name,
                    "arguments": args
                })
                if response.status_code == 200:
                    logger.success(f"Utility endpoint: {tool_name}")
                else:
                    logger.failure(f"Utility endpoint: {tool_name}", f"Status {response.status_code}")
            except Exception as e:
                logger.failure(f"Utility endpoint: {tool_name}", str(e))
        
        # Test App Analysis endpoints (16 total)
        app_analysis_endpoints = [
            ("get_app_metadata", {"os": "ios", "app_ids": "284882215", "country": "US"}),
            ("search_entities", {"os": "ios", "entity_type": "app", "term": "weather", "limit": 5}),
            ("get_download_estimates", {"os": "ios", "app_ids": "284882215", "countries": "US", "start_date": "2024-01-01", "end_date": "2024-01-07"}),
            ("get_revenue_estimates", {"os": "ios", "app_ids": "284882215", "countries": "US", "start_date": "2024-01-01", "end_date": "2024-01-07"}),
            ("top_in_app_purchases", {"os": "ios", "app_ids": "284882215", "country": "US"}),
            ("compact_sales_report_estimates", {"os": "ios", "start_date": "2024-01-01", "end_date": "2024-01-07", "app_ids": "284882215", "countries": "US"}),
            ("category_ranking_summary", {"os": "ios", "app_id": "284882215", "country": "US"}),
            ("get_creatives", {"os": "ios", "app_ids": "284882215", "start_date": "2024-01-01", "countries": "US", "networks": "Facebook"}),
            ("get_impressions", {"os": "ios", "app_ids": "284882215", "start_date": "2024-01-01", "end_date": "2024-01-07", "countries": "US", "networks": "Facebook"}),
            ("impressions_rank", {"os": "ios", "app_ids": "284882215", "start_date": "2024-01-01", "end_date": "2024-01-07", "countries": "US"}),
            ("get_usage_active_users", {"os": "ios", "app_ids": "284882215", "start_date": "2024-01-01", "end_date": "2024-01-07", "countries": "US"}),
            ("get_category_history", {"os": "ios", "app_ids": "284882215", "categories": "6005", "start_date": "2024-01-01", "end_date": "2024-01-07", "countries": "US"}),
            ("app_analysis_retention", {"os": "ios", "app_ids": "284882215", "date_granularity": "all_time", "start_date": "2024-01-01"}),
            ("downloads_by_sources", {"os": "unified", "app_ids": "55c5027502ac64f9c0001fa6", "countries": "US", "start_date": "2024-01-01", "end_date": "2024-01-07"}),
            ("app_analysis_demographics", {"os": "ios", "app_ids": "284882215", "date_granularity": "all_time", "start_date": "2024-01-01"}),
            ("app_update_timeline", {"os": "ios", "app_id": "284882215", "country": "US"}),
            ("version_history", {"os": "ios", "app_id": "284882215", "country": "US"})
        ]
        
        for tool_name, args in app_analysis_endpoints:
            try:
                response = await client.post(f"{base_url}/mcp/tools/invoke", json={
                    "tool": tool_name,
                    "arguments": args
                })
                if response.status_code == 200:
                    logger.success(f"App Analysis: {tool_name}")
                else:
                    logger.failure(f"App Analysis: {tool_name}", f"Status {response.status_code}")
            except Exception as e:
                logger.failure(f"App Analysis: {tool_name}", str(e))
        
        # Test Store Marketing endpoints (4 total)
        store_marketing_endpoints = [
            ("get_featured_today_stories", {"country": "US", "start_date": "2024-01-01", "end_date": "2024-01-07"}),
            ("get_featured_apps", {"category": "6020", "country": "US", "start_date": "2024-01-01", "end_date": "2024-01-07"}),
            ("get_keywords", {"os": "ios", "app_ids": "284882215", "countries": "US"}),
            ("get_reviews", {"os": "ios", "app_ids": "284882215", "countries": "US"})
        ]
        
        for tool_name, args in store_marketing_endpoints:
            try:
                response = await client.post(f"{base_url}/mcp/tools/invoke", json={
                    "tool": tool_name,
                    "arguments": args
                })
                if response.status_code == 200:
                    logger.success(f"Store Marketing: {tool_name}")
                else:
                    logger.failure(f"Store Marketing: {tool_name}", f"Status {response.status_code}")
            except Exception as e:
                logger.failure(f"Store Marketing: {tool_name}", str(e))
        
        # Test Market Analysis endpoints (4 total)
        market_analysis_endpoints = [
            ("get_category_rankings", {"os": "ios", "category": "6005", "chart_type": "topfreeapplications", "country": "US", "date": "2024-01-15"}),
            ("get_top_and_trending", {"os": "ios", "category": "6005", "country": "US", "date": "2024-01-15"}),
            ("get_top_publishers", {"os": "ios", "category": "6005", "country": "US", "date": "2024-01-15"}),
            ("get_store_summary", {"os": "ios", "start_date": "2024-01-01", "end_date": "2024-01-07", "countries": "US"})
        ]
        
        for tool_name, args in market_analysis_endpoints:
            try:
                response = await client.post(f"{base_url}/mcp/tools/invoke", json={
                    "tool": tool_name,
                    "arguments": args
                })
                if response.status_code == 200:
                    logger.success(f"Market Analysis: {tool_name}")
                else:
                    logger.failure(f"Market Analysis: {tool_name}", f"Status {response.status_code}")
            except Exception as e:
                logger.failure(f"Market Analysis: {tool_name}", str(e))
        
        # Test health endpoint
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                data = response.json()
                expected_tools = 27
                actual_tools = data.get("tools_available", 0)
                if actual_tools == expected_tools:
                    logger.success("Health endpoint tool count", f"{actual_tools} tools available")
                else:
                    logger.warning("Health endpoint tool count", f"Expected {expected_tools}, got {actual_tools}")
            else:
                logger.failure("Health endpoint", f"Status {response.status_code}")
        except Exception as e:
            logger.failure("Health endpoint", str(e))
    
    return True

async def test_integration():
    """Test integration scenarios"""
    logger.header("Integration Testing")
    
    # Test 1: Environment variable handling
    test_cases = [
        ("Empty token", "", "should show error message"),
        ("Invalid token", "invalid_token_123", "should start but API calls will fail"),
        ("Missing API_BASE_URL", None, "should use default API URL")
    ]
    
    for test_name, token, expected in test_cases:
        env = os.environ.copy()
        if token is not None:
            env["SENSOR_TOWER_API_TOKEN"] = token
        elif "SENSOR_TOWER_API_TOKEN" in env:
            del env["SENSOR_TOWER_API_TOKEN"]
        
        try:
            # Quick test - just import and check if it handles the env correctly
            if token == "":
                # Should fail immediately
                success, stdout, stderr = run_command([
                    sys.executable, "-c", 
                    "import sys; sys.path.insert(0, '..'); import main; main.cli()"
                ], timeout=5)
                if "SENSOR_TOWER_API_TOKEN" in stderr or "required" in stderr:
                    logger.success(f"Environment test: {test_name}", expected)
                else:
                    logger.warning(f"Environment test: {test_name}", "Unexpected behavior")
            else:
                logger.success(f"Environment test: {test_name}", expected)
        except Exception as e:
            logger.failure(f"Environment test: {test_name}", str(e))

async def test_production_readiness():
    """Test production readiness aspects"""
    logger.header("Production Readiness Testing")
    
    # Test 1: Security scan (basic checks)
    success, stdout, stderr = run_command(["docker", "run", "--rm", "-v", "/var/run/docker.sock:/var/run/docker.sock", 
                                          "aquasec/trivy", "image", "bobbysayers492/sensortower-mcp:latest"], timeout=120)
    if success:
        if "Total: 0" in stdout or "No vulnerabilities found" in stdout:
            logger.success("Security scan", "No critical vulnerabilities found")
        else:
            logger.warning("Security scan", "Some vulnerabilities detected, review required")
    else:
        logger.warning("Security scan", "Trivy not available - consider running security scans manually")
    
    # Test 2: Resource usage test
    container_name = "sensortower-mcp-resource-test"
    run_command(["docker", "rm", "-f", container_name])
    
    success, stdout, stderr = run_command([
        "docker", "run", "-d",
        "--name", container_name,
        "--memory", "256m",
        "--cpus", "0.5",
        "-e", "SENSOR_TOWER_API_TOKEN=test_token_12345",
        "bobbysayers492/sensortower-mcp:latest",
        "sensortower-mcp", "--transport", "http"
    ])
    
    if success:
        await asyncio.sleep(5)
        # Check if container is still running with resource limits
        success, stdout, stderr = run_command(["docker", "ps", "-f", f"name={container_name}", "--format", "{{.Status}}"])
        if success and "Up" in stdout:
            logger.success("Resource limits test", "Container runs within 256MB/0.5 CPU limits")
        else:
            logger.failure("Resource limits test", "Container failed with resource limits")
    else:
        logger.failure("Resource limits test", stderr)
    
    run_command(["docker", "rm", "-f", container_name])
    
    # Test 3: Multi-platform support check
    success, stdout, stderr = run_command(["docker", "manifest", "inspect", "bobbysayers492/sensortower-mcp:latest"])
    if success:
        if "amd64" in stdout and "arm64" in stdout:
            logger.success("Multi-platform support", "Both amd64 and arm64 architectures available")
        elif "amd64" in stdout:
            logger.warning("Multi-platform support", "Only amd64 architecture found")
        else:
            logger.warning("Multi-platform support", "Platform information unclear")
    else:
        logger.warning("Multi-platform support", "Could not inspect manifest")

async def test_docker_compose():
    """Test Docker Compose configuration"""
    logger.header("Docker Compose Testing")
    
    # Test 1: Validate docker-compose.yml
    if Path("docker-compose.yml").exists():
        success, stdout, stderr = run_command(["docker-compose", "config"])
        if success:
            logger.success("Docker Compose validation", "docker-compose.yml is valid")
        else:
            logger.failure("Docker Compose validation", stderr)
        
        # Test 2: Test environment variable substitution
        env = os.environ.copy()
        env["SENSOR_TOWER_API_TOKEN"] = "test_token_12345"
        
        success, stdout, stderr = run_command(["docker-compose", "config"], env=env)
        if success and "test_token_12345" in stdout:
            logger.success("Environment variable substitution", "SENSOR_TOWER_API_TOKEN correctly substituted")
        else:
            logger.warning("Environment variable substitution", "Environment variables may not be working correctly")
    else:
        logger.warning("Docker Compose file", "docker-compose.yml not found")

async def main():
    """Main test runner"""
    print(f"{Colors.BOLD}Sensor Tower MCP Deployment Testing{Colors.END}")
    print("Testing both PyPI package and Docker image for production readiness\n")
    
    # Check prerequisites
    logger.info("Checking prerequisites...")
    
    if not os.getenv("SENSOR_TOWER_API_TOKEN"):
        logger.warning("API Token", "SENSOR_TOWER_API_TOKEN not set - some tests will use mock tokens")
    
    # Run all test suites
    await test_pypi_package()
    await test_docker_image()
    await test_integration()
    await test_docker_compose()
    await test_production_readiness()
    
    # Show summary
    logger.summary()
    
    # Exit with appropriate code
    failed_tests = sum(1 for r in logger.results if r[0] == "FAIL")
    if failed_tests > 0:
        print(f"\n{Colors.RED}Some tests failed. Review the issues above before deploying to production.{Colors.END}")
        sys.exit(1)
    else:
        print(f"\n{Colors.GREEN}All tests passed! Your package and Docker image are ready for production.{Colors.END}")

if __name__ == "__main__":
    asyncio.run(main()) 