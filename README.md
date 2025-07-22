# Sensor Tower MCP Server

Model Context Protocol server for Sensor Tower APIs using FastMCP with OpenAPI integration.

## 🚀 Quick Start

### Option 1: Pre-built Docker Image (Recommended)

The fastest way to get started is using our pre-built Docker image:

```bash
# Run with HTTP transport
docker run -p 8666:8666 \
  -e SENSOR_TOWER_API_TOKEN="your_token_here" \
  bobbysayers492/sensortower-mcp:latest \
  sensortower-mcp --transport http --port 8666

# Run with stdio transport (for MCP clients)
docker run -i \
  -e SENSOR_TOWER_API_TOKEN="your_token_here" \
  bobbysayers492/sensortower-mcp:latest \
  sensortower-mcp --transport stdio
```

### Option 2: PyPI Installation

```bash
# From PyPI
pip install sensortower-mcp

# From source
git clone https://github.com/yourusername/sensortower-mcp
cd sensortower-mcp
pip install -e .
```

### Configuration

```bash
# Set your API token
export SENSOR_TOWER_API_TOKEN="your_token_here"
```

Get your API token from: https://app.sensortower.com/users/edit/api-settings

### Usage

#### Stdio Mode (for MCP clients)
```bash
# Local installation
sensortower-mcp --transport stdio

# Docker
docker run -i \
  -e SENSOR_TOWER_API_TOKEN="your_token" \
  bobbysayers492/sensortower-mcp:latest \
  sensortower-mcp --transport stdio
```

#### HTTP Mode (for web integration)
```bash
# Local installation
sensortower-mcp --transport http --port 8666

# Docker
docker run -p 8666:8666 \
  -e SENSOR_TOWER_API_TOKEN="your_token" \
  bobbysayers492/sensortower-mcp:latest \
  sensortower-mcp --transport http --port 8666
```

#### Docker Compose (for persistent deployment)
```bash
# Using Docker Compose (recommended for production)
SENSOR_TOWER_API_TOKEN="your_token" docker-compose up -d
```

## 📊 Available Tools

### App Intelligence API
- **get_app_metadata**: Get app details like name, publisher, categories, descriptions, ratings
- **get_category_rankings**: Get top ranking apps by category and chart type
- **get_download_estimates**: Retrieve download estimates by country and date
- **get_revenue_estimates**: Get revenue estimates and trends

### Search & Discovery
- **search_entities**: Search for apps and publishers by name/description

### Utility Tools
- **get_country_codes**: Get available country codes
- **get_category_ids**: Get category IDs for iOS/Android
- **get_chart_types**: Get available chart types for rankings
- **health_check**: Health check endpoint for monitoring

## 🔧 Development

### Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/sensortower-mcp
cd sensortower-mcp

# Install in development mode
pip install -e .

# Start in development mode
python main.py --transport http --port 8666
```

### Environment Variables

- `SENSOR_TOWER_API_TOKEN`: Your Sensor Tower API token (required)
- `TRANSPORT`: Transport mode (`stdio` or `http`, default: `stdio`)
- `PORT`: HTTP server port (default: `8666`)
- `API_BASE_URL`: Sensor Tower API base URL (default: `https://api.sensortower.com`)

### Health Check

```bash
# Check service health
curl http://localhost:8666/health
```

## 📋 API Examples

### Get App Metadata
```json
{
  "tool": "get_app_metadata",
  "arguments": {
    "os": "ios",
    "app_ids": "284882215",
    "country": "US"
  }
}
```

### Search Apps
```json
{
  "tool": "search_entities",
  "arguments": {
    "os": "ios",
    "entity_type": "app",
    "term": "social media",
    "limit": 10
  }
}
```

### Get Rankings
```json
{
  "tool": "get_category_rankings",
  "arguments": {
    "os": "ios",
    "category": "6005",
    "chart_type": "topfreeapplications",
    "country": "US",
    "date": "2024-01-15"
  }
}
```

## 🐳 Docker Deployment

### Production Deployment

```bash
# Using Docker Compose
SENSOR_TOWER_API_TOKEN="your_token" docker-compose up -d

# With nginx reverse proxy
SENSOR_TOWER_API_TOKEN="your_token" \
  docker-compose --profile production up -d
```

### Resource Limits

The container is configured with reasonable defaults:
- Memory: 256MB limit
- CPU: 0.5 cores
- Health checks every 30s

### Monitoring

Health check endpoint: `http://localhost:8666/health`

```json
{
  "status": "healthy",
  "service": "Sensor Tower MCP Server",
  "transport": "http",
  "api_base_url": "https://api.sensortower.com",
  "tools_available": 9
}
```

## 🔒 Security

- Non-root container user
- No hardcoded secrets
- Input validation and timeouts
- Regular security scanning
- HTTPS/TLS configuration for production
- Security headers and rate limiting

## 📈 Performance

Expected performance benchmarks:
- **Response Time**: <100ms for utility endpoints, <500ms for API calls
- **Throughput**: >50 RPS for mixed workload
- **Memory Usage**: <256MB under normal load
- **Success Rate**: >99% for valid requests

## 🧪 Testing

We provide a comprehensive testing suite. See [tests/README.md](tests/README.md) for details.

```bash
# Quick validation
python tests/test_manual.py

# Full production readiness check
python tests/test_all.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the test suite: `python tests/test_all.py`
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Documentation**: See [tests/TESTING.md](tests/TESTING.md) for comprehensive guides
- **Issues**: Create an issue on GitHub
- **API Documentation**: https://docs.sensortower.com

## 🏗️ Architecture

```
sensortower-mcp/
├── main.py                 # Main MCP server implementation
├── pyproject.toml         # Package configuration
├── docker-compose.yml     # Docker deployment
├── Dockerfile            # Container definition
├── swaggerdocs/          # API documentation
└── tests/                # Testing framework
    ├── test_all.py       # Master test runner
    ├── test_deployment.py # PyPI & Docker tests
    ├── test_manual.py    # Quick validation
    ├── test_load.py      # Performance tests
    ├── test_security.py  # Security audit
    └── README.md         # Testing documentation
```

Built with [FastMCP](https://github.com/jlowin/fastmcp) for streamlined MCP server development.

