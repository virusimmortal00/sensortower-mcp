# 🧪 Testing Framework for Sensor Tower MCP

Complete testing suite to ensure your PyPI package and Docker image work perfectly in production.

## 🚀 Quick Start

```bash
# Install testing dependencies
pip install httpx aiohttp

# Set your API token (optional but recommended)
export SENSOR_TOWER_API_TOKEN="your_token_here"

# Run comprehensive testing
python tests/test_all.py
```

## 📋 Test Scripts

| Script | Purpose | Time | Prerequisites |
|--------|---------|------|--------------|
| `test_all.py` | **Master script** - runs everything | 5-10 min | Python |
| `test_manual.py` | Quick validation | 30 sec | httpx |
| `test_deployment.py` | Full PyPI + Docker testing | 3-5 min | httpx, Docker |
| `test_load.py` | Performance under load | 1-2 min | aiohttp, running server |
| `test_security.py` | Security best practices | 2-3 min | httpx |

## 🎯 Testing Scenarios

### Before Release
```bash
# Quick check during development
python tests/test_manual.py

# Full validation before tagging
python tests/test_deployment.py
```

### Production Deployment
```bash
# Complete production readiness check
python tests/test_all.py

# Security audit
python tests/test_security.py
```

### Performance Testing
```bash
# Start your server first
docker-compose up -d
# or
sensortower-mcp --transport http

# Then test performance
python tests/test_load.py
```

## ✅ What Gets Tested

### PyPI Package
- ✅ Installation in clean environment
- ✅ CLI functionality (`sensortower-mcp --help`)
- ✅ Import and basic functionality
- ✅ Environment variable handling

### Docker Image
- ✅ Image pull and startup
- ✅ Health check endpoints
- ✅ Both stdio and HTTP modes
- ✅ Resource limits (256MB RAM, 0.5 CPU)
- ✅ Container logs and error handling

### Security
- ✅ No hardcoded secrets
- ✅ Non-root user in container
- ✅ Vulnerability scanning (if Trivy available)
- ✅ Input validation and timeouts
- ✅ Secure configuration practices

### Performance
- ✅ Response times (<100ms for utilities, <500ms for API)
- ✅ Throughput (>50 RPS mixed workload)
- ✅ Concurrent request handling
- ✅ Error rates under load (<1%)

### Integration
- ✅ API endpoint functionality
- ✅ Docker Compose configuration
- ✅ Environment variable substitution
- ✅ Health monitoring

## 📊 Understanding Results

### Production Readiness Status
- 🟢 **READY FOR PRODUCTION** - All tests passed
- 🟡 **READY WITH CAUTIONS** - Minor issues to review
- 🟡 **PARTIALLY VALIDATED** - Some tests skipped
- 🔴 **NOT READY** - Critical failures need fixing

### Test Results
- ✅ **PASSED** - Test completed successfully
- ❌ **FAILED** - Issues found, needs attention
- ⏭️ **SKIPPED** - Missing prerequisites

## 🛠️ Troubleshooting

### Common Issues

**"Docker not found"**
```bash
# Install Docker Desktop or Docker Engine
# macOS: brew install --cask docker
# Linux: curl -fsSL https://get.docker.com | sh
```

**"Missing dependencies"**
```bash
pip install httpx aiohttp
```

**"Container fails to start"**
```bash
# Check your API token
echo $SENSOR_TOWER_API_TOKEN

# Check Docker logs
docker logs sensortower-mcp
```

**"Port already in use"**
```bash
# Kill process using port 8666
lsof -ti:8666 | xargs kill -9

# Or use different port
docker run -p 8667:8666 ...
```

## 📋 Production Deployment Checklist

Before going live, ensure:

- [ ] All tests pass (`python tests/test_all.py`)
- [ ] API token configured securely
- [ ] Resource limits appropriate for your load
- [ ] Monitoring and alerting set up
- [ ] Backup and rollback procedures documented
- [ ] Security scan results reviewed
- [ ] Load testing matches expected traffic

## 📚 Documentation

- `README_TESTING.md` - Quick reference guide
- `TESTING.md` - Comprehensive testing guide with examples
- `__init__.py` - Package documentation and test descriptions

---

**Ready to test?** Run `python tests/test_all.py` and get your production readiness report! 🚀 