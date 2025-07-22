# Testing Guide for Sensor Tower MCP

This guide provides comprehensive testing strategies for the Sensor Tower MCP package and Docker image to ensure production readiness.

## Quick Start

### Prerequisites
```bash
# Install testing dependencies
pip install httpx aiohttp

# Set your API token (optional but recommended)
export SENSOR_TOWER_API_TOKEN="your_token_here"

# Ensure Docker is installed for container tests
docker --version
```

### Run All Tests
```bash
# Comprehensive test suite
python test_deployment.py

# Quick manual validation  
python test_manual.py

# Load testing
python test_load.py
```

## Test Suites Overview

### 1. Deployment Testing (`test_deployment.py`)
**Purpose**: Comprehensive validation of both PyPI package and Docker image

**What it tests**:
- ✅ PyPI package installation in clean environment
- ✅ Virtual environment compatibility
- ✅ CLI functionality and help commands
- ✅ Docker image pull and startup
- ✅ Health check endpoints
- ✅ Container logs and error handling
- ✅ Resource limits (256MB RAM, 0.5 CPU)
- ✅ Security scanning (if Trivy available)
- ✅ Docker Compose configuration
- ✅ Environment variable handling

**Run time**: 3-5 minutes

### 2. Manual Testing (`test_manual.py`)
**Purpose**: Quick validation for manual verification

**What it tests**:
- ✅ Package import and basic functionality
- ✅ Docker container status
- ✅ Health endpoints
- ✅ Basic API tool invocation
- ✅ Utility endpoints (country codes, categories)

**Run time**: 30 seconds

### 3. Load Testing (`test_load.py`)
**Purpose**: Performance validation under concurrent load

**What it tests**:
- ✅ Concurrent request handling
- ✅ Response time statistics
- ✅ Throughput (requests per second)
- ✅ Error rates under load
- ✅ Different endpoint types (health, utilities, API calls)

**Run time**: 1-2 minutes per test scenario

## Testing Strategies by Environment

### Pre-Release Testing

1. **Development Environment**
   ```bash
   # Test local changes
   python test_manual.py
   
   # Test resource usage
   python test_deployment.py
   ```

2. **CI/CD Pipeline**
   ```bash
   # Automated testing
   python test_deployment.py --ci-mode
   
   # Security scanning
   docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
     aquasec/trivy image sensortower-mcp:latest
   ```

### Production Validation

1. **Staging Environment**
   ```bash
   # Full deployment test
   SENSOR_TOWER_API_TOKEN="staging_token" python test_deployment.py
   
   # Load testing
   python test_load.py
   ```

2. **Production Health Checks**
   ```bash
   # Minimal validation
   curl http://your-domain.com/health
   
   # Quick API test
   python test_manual.py
   ```

## Test Scenarios by Use Case

### PyPI Package Testing

```bash
# Test fresh installation
pip install sensortower-mcp

# Test CLI
sensortower-mcp --help
sensortower-mcp --transport http --port 8666

# Test programmatic usage
python -c "import main; print('OK')"
```

### Docker Image Testing

```bash
# Test image pull
docker pull bobbysayers492/sensortower-mcp:latest

# Test stdio mode (default)
docker run -e SENSOR_TOWER_API_TOKEN="your_token" \
  bobbysayers492/sensortower-mcp:latest

# Test HTTP mode
docker run -p 8666:8666 \
  -e SENSOR_TOWER_API_TOKEN="your_token" \
  bobbysayers492/sensortower-mcp:latest \
  sensortower-mcp --transport http --port 8666

# Test with resource limits
docker run --memory=256m --cpus=0.5 \
  -e SENSOR_TOWER_API_TOKEN="your_token" \
  bobbysayers492/sensortower-mcp:latest
```

### Docker Compose Testing

```bash
# Start services
SENSOR_TOWER_API_TOKEN="your_token" docker-compose up -d

# Test health
curl http://localhost:8666/health

# Check logs
docker-compose logs sensortower-mcp

# Test with production profile
SENSOR_TOWER_API_TOKEN="your_token" \
  docker-compose --profile production up -d
```

## API Testing Examples

### Using curl
```bash
# Health check
curl http://localhost:8666/health

# Get country codes
curl -X POST http://localhost:8666/mcp/tools/invoke \
  -H "Content-Type: application/json" \
  -d '{"tool": "get_country_codes", "arguments": {}}'

# Search apps (requires valid token)
curl -X POST http://localhost:8666/mcp/tools/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "search_entities",
    "arguments": {
      "os": "ios",
      "entity_type": "app",
      "term": "weather",
      "limit": 5
    }
  }'
```

### Using Python
```python
import asyncio
import httpx

async def test_api():
    async with httpx.AsyncClient() as client:
        # Health check
        response = await client.get("http://localhost:8666/health")
        print(f"Health: {response.json()}")
        
        # Tool invocation
        response = await client.post(
            "http://localhost:8666/mcp/tools/invoke",
            json={
                "tool": "get_country_codes",
                "arguments": {}
            }
        )
        print(f"Countries: {response.json()}")

asyncio.run(test_api())
```

## Performance Benchmarks

### Expected Performance
- **Response Time**: <100ms for utility endpoints, <500ms for API calls
- **Throughput**: >50 RPS for mixed workload
- **Memory Usage**: <256MB under normal load
- **CPU Usage**: <0.5 CPU cores under normal load
- **Success Rate**: >99% for valid requests

### Load Testing Scenarios
```bash
# Light load (development)
python test_load.py  # 10 concurrent, 100 requests

# Medium load (staging)
# Modify test_load.py for 25 concurrent, 250 requests

# Heavy load (stress testing)
# Modify test_load.py for 50 concurrent, 500 requests
```

## Security Testing

### Automated Security Scans
```bash
# Vulnerability scanning
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image bobbysayers492/sensortower-mcp:latest

# Container security
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy fs .
```

### Manual Security Checks
- ✅ No hardcoded secrets in image
- ✅ Non-root user in container
- ✅ Minimal attack surface (slim base image)
- ✅ HTTPS endpoints in production
- ✅ API token validation
- ✅ Input sanitization

## Troubleshooting

### Common Issues

1. **"Docker not found"**
   ```bash
   # Install Docker
   # macOS: brew install --cask docker
   # Linux: curl -fsSL https://get.docker.com | sh
   ```

2. **"Container fails to start"**
   ```bash
   # Check logs
   docker logs sensortower-mcp
   
   # Verify token
   echo $SENSOR_TOWER_API_TOKEN
   ```

3. **"Port already in use"**
   ```bash
   # Find and kill process
   lsof -ti:8666 | xargs kill -9
   
   # Or use different port
   docker run -p 8667:8666 ...
   ```

4. **"API calls failing"**
   ```bash
   # Verify token is valid
   curl -H "Authorization: Bearer $SENSOR_TOWER_API_TOKEN" \
     https://api.sensortower.com/v1/ios/apps?app_ids=284882215
   ```

### Test Environment Setup

```bash
# Clean test environment
docker system prune -f
python -m venv test_env
source test_env/bin/activate  # or test_env\Scripts\activate on Windows
pip install sensortower-mcp

# Production-like environment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Test Deployment

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install httpx aiohttp
          pip install sensortower-mcp
      
      - name: Run deployment tests
        run: python test_deployment.py
        env:
          SENSOR_TOWER_API_TOKEN: ${{ secrets.SENSOR_TOWER_API_TOKEN }}
      
      - name: Security scan
        run: |
          docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
            aquasec/trivy image bobbysayers492/sensortower-mcp:latest
```

## Monitoring in Production

### Health Check Endpoints
```bash
# Application health
curl http://your-domain.com/health

# Docker health check
docker inspect --format='{{.State.Health.Status}}' sensortower-mcp
```

### Metrics to Monitor
- Response time (95th percentile <500ms)
- Error rate (<1%)
- Memory usage (<256MB)
- CPU usage (<50%)
- Request throughput
- Container restart count

### Alerting Thresholds
- **Critical**: Health check fails, error rate >5%
- **Warning**: Response time >1s, memory >200MB
- **Info**: High request volume, container restart

## Best Practices

1. **Always test in clean environments** (fresh containers, new virtual environments)
2. **Use real API tokens** for integration testing when possible
3. **Test both transport modes** (stdio for MCP clients, HTTP for web integration)
4. **Validate resource limits** match your production constraints
5. **Run security scans** before deploying new versions
6. **Monitor performance** under realistic load conditions
7. **Test error handling** with invalid tokens and network failures
8. **Validate environment variables** are properly substituted
9. **Check logs** for startup errors and warnings
10. **Test rollback procedures** in case of deployment issues 