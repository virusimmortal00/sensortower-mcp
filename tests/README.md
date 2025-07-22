# Sensor Tower MCP Testing Suite

Comprehensive testing scripts for validating the sensortower-mcp PyPI package and Docker image for production readiness.

## 🎯 Comprehensive Endpoint Testing

Our test suite validates **all 27 endpoints** (23 API + 4 utility) to ensure complete functionality:

### **Endpoint Coverage:**
- **4 Utility endpoints**: country codes, categories, chart types, health check
- **16 App Analysis endpoints**: metadata, sales estimates, retention, demographics, creatives, impressions, etc.
- **4 Store Marketing endpoints**: featured apps, keywords, reviews, today stories  
- **4 Market Analysis endpoints**: rankings, trends, publishers, store summary

## Test Scripts

### 🎯 `test_functional.py` - Real API Testing
**NEW: Comprehensive functional testing with actual data**

Tests real API calls to Sensor Tower endpoints and validates actual data responses.

```bash
python tests/test_functional.py
```

**What it tests:**
- ✅ **Environment setup** with .env file loading
- ✅ **Utility endpoints** (country codes, categories, chart types)
- ✅ **Core API endpoints** with real data validation:
  - `search_entities` → Found real weather apps
  - `get_app_metadata` → Retrieved Facebook app details
  - `get_category_rankings` → Got 500 rankings from Social Networking
  - `sales_report_estimates` → Retrieved download/revenue data
- ✅ **Specialized endpoints** (IAP data, ranking summaries)

**Time:** ~30 seconds | **Results:** ✅ 11/12 passed, 1 warning

### 🚀 `test_all.py` - Master Test Suite
**Recommended for comprehensive validation**

Runs all test suites and generates a production readiness report with complete endpoint coverage.

```bash
python tests/test_all.py
```

**What it tests:**
- All 27 endpoints across all categories
- PyPI package installation and functionality
- Docker image build and deployment
- Security best practices validation
- Performance under concurrent load
- Production readiness assessment

**Output:** Detailed report with pass/fail status for all 27 endpoints and production recommendations.

### ⚡ `test_manual.py` - Quick Validation
**Use for rapid development testing**

Quick manual testing script for immediate feedback during development.

```bash
python tests/test_manual.py
```

**What it tests:**
- All 27 endpoints with real API calls
- PyPI package import and initialization
- Docker container health check
- Basic functionality validation

**Time:** ~2-3 minutes with API token

### 🏗️ `test_deployment.py` - Deployment Testing  
**Use before production deployment**

Comprehensive testing of both PyPI package and Docker image for production deployment.

```bash
python tests/test_deployment.py
```

**What it tests:**
- Clean virtual environment installation
- All 27 endpoints in both PyPI and Docker environments
- Package functionality validation
- Docker image build and run testing
- Production configuration validation

**Time:** ~5-7 minutes

### ⚡ `test_load.py` - Performance Testing
**Use to validate performance characteristics**

Tests the server under concurrent load to validate performance.

```bash
python tests/test_load.py
```

**What it tests:**
- Concurrent requests to all endpoint categories
- Response time analysis across all 27 endpoints
- Error rate measurement under load
- Memory and CPU usage patterns
- Scalability assessment

**Time:** ~2-3 minutes

### 🔒 `test_security.py` - Security Validation
**Use to validate security best practices**

Security-focused testing to identify potential vulnerabilities.

```bash
python tests/test_security.py
```

**What it tests:**
- All 27 endpoints for security issues
- Authentication handling
- Input validation across all endpoints
- Error message security
- Docker security best practices

**Time:** ~3-4 minutes

## Prerequisites

### Required
- Python 3.11+
- `httpx` library: `pip install httpx`

### Optional but Recommended
- **SENSOR_TOWER_API_TOKEN**: For full API testing of all 27 endpoints
  - Get your token: https://app.sensortower.com/users/edit/api-settings
  - Without token: Only utility endpoints (4/27) will be tested
- **Docker**: For Docker image testing
- **aiohttp**: For advanced load testing
- **python-dotenv**: For .env file support (`pip install python-dotenv`)

## Quick Start

### 1. Configure API Token

**Option A: Using .env file (Recommended for development)**
```bash
# Create .env file in project root
echo "SENSOR_TOWER_API_TOKEN=your_token_here" > .env

# Run tests (automatically loads from .env)
python tests/test_all.py
```

**Option B: Using environment variables**
```bash
# Set environment variable
export SENSOR_TOWER_API_TOKEN="your_token_here"

# Run tests
python tests/test_all.py
```

### 2. Full Production Validation
```bash
# Run comprehensive test suite (all 27 endpoints)
python tests/test_all.py
```

### 3. Development Testing
```bash
# Quick validation during development
python tests/test_manual.py
```

### 4. Pre-Production Testing
```bash
# Before deploying to production
python tests/test_deployment.py
```

## Test Results

### Success Indicators
- ✅ **All 27 endpoints respond with status 200**
- ✅ **Valid JSON responses from all API endpoints**
- ✅ **Docker container starts and responds to health checks**
- ✅ **PyPI package installs and imports successfully**
- ✅ **Performance metrics within acceptable ranges**

### Common Issues
- ❌ **SENSOR_TOWER_API_TOKEN not set**: API endpoints (23/27) will fail
- ❌ **Docker not available**: Container tests will be skipped
- ❌ **Network connectivity**: API calls may timeout
- ❌ **Rate limiting**: Sensor Tower API may throttle requests

## Environment Variables

### Required for Full Testing
**Option 1: .env file (Recommended)**
```bash
# Create .env file in project root
SENSOR_TOWER_API_TOKEN=your_api_token
```

**Option 2: Environment variables**
```bash
export SENSOR_TOWER_API_TOKEN="your_api_token"
```

### Optional
```bash
# In .env file or as environment variables
API_BASE_URL=https://api.sensortower.com  # Custom API base URL
PORT=8666                                  # Custom HTTP port for testing
```

### .env File Example
Create a `.env` file in your project root:
```bash
# Sensor Tower API Configuration
SENSOR_TOWER_API_TOKEN=your_actual_token_here
API_BASE_URL=https://api.sensortower.com
PORT=8666

# Optional: Custom settings for testing
TIMEOUT=60
```

**Security Note:** 
- Never commit `.env` files to version control
- Use `.env.example` as a template
- Keep your API tokens secure and private

**Note:** The test suite will automatically load `.env` files if `python-dotenv` is installed. If not available, it falls back to standard environment variables.

## Interpreting Results

### Production Readiness Levels

**🟢 READY FOR PRODUCTION**
- All test suites passed
- All 27 endpoints validated
- No critical issues detected

**🟡 MOSTLY READY**  
- Most tests passed (>80%)
- Minor issues detected
- Review failures before deployment

**🔴 NOT READY**
- Multiple test failures
- Critical issues detected
- Address issues before deployment

### Endpoint Categories Validation

The test suite validates endpoints across all major categories:

1. **Utility Endpoints (4)**: Basic functionality, no API token required
2. **App Analysis (16)**: Core mobile app intelligence features
3. **Store Marketing (4)**: ASO and marketing intelligence
4. **Market Analysis (4)**: Market trends and competitive analysis

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run Sensor Tower MCP Tests
  run: |
    pip install httpx
    export SENSOR_TOWER_API_TOKEN="${{ secrets.SENSOR_TOWER_API_TOKEN }}"
    python tests/test_deployment.py
```

### Docker Integration
```bash
# Test Docker image
docker build -t sensortower-mcp-test .
docker run -e SENSOR_TOWER_API_TOKEN="$SENSOR_TOWER_API_TOKEN" \
  sensortower-mcp-test python tests/test_deployment.py
```

## Troubleshooting

### Test Failures
1. **Check API token**: Ensure SENSOR_TOWER_API_TOKEN is valid
2. **Verify connectivity**: Test network access to api.sensortower.com
3. **Review rate limits**: Sensor Tower API has usage limits
4. **Check Docker**: Ensure Docker daemon is running for container tests

### Performance Issues
1. **Increase timeouts**: Some endpoints may need longer timeouts
2. **Reduce concurrency**: Lower concurrent requests in load tests
3. **Check system resources**: Ensure adequate memory/CPU

### Security Issues
1. **Update dependencies**: Keep packages up to date
2. **Review configurations**: Check Docker and Python security settings
3. **Validate inputs**: Ensure proper input sanitization

## Support

For issues with the testing suite:
1. Check the generated test reports for detailed error information
2. Review the endpoint-specific error messages
3. Verify all prerequisites are installed and configured correctly
4. Test individual endpoints manually to isolate issues

The comprehensive test suite ensures your Sensor Tower MCP server is production-ready with full validation of all 27 endpoints across all API categories. 