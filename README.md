# Sensor Tower MCP Server

[![PyPI version](https://badge.fury.io/py/sensortower-mcp.svg)](https://badge.fury.io/py/sensortower-mcp)
[![Docker Pulls](https://img.shields.io/docker/pulls/bobbysayers492/sensortower-mcp)](https://hub.docker.com/r/bobbysayers492/sensortower-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

Model Context Protocol server for Sensor Tower APIs using FastMCP with OpenAPI integration.

## 📊 API Coverage Status

| API Category | Endpoints | Coverage | Implemented |
|--------------|-----------|----------|-------------|
| **App Analysis** | 17 total | ✅ Nearly Complete (16/17) | `apps`, `sales_report_estimates`, `top_in_app_purchases`, `creatives`, `impressions`, `usage_active_users`, `category_history`, `get_search_entities`, `compact_sales_report_estimates`, `category_ranking_summary`, `impressions_rank`, `app_analysis_retention`, `downloads_by_sources`, `app_analysis_demographics`, `app_update_timeline`, `version_history` |
| **Store Marketing** | 15 total | 🔄 Partial (4/15) | `featured_today_stories`, `featured_apps`, `keywords`, `get_reviews` |
| **Market Analysis** | 7 total | 🔄 Partial (4/7) | `get_category_rankings`, `top_and_trending`, `top_publishers`, `store_summary` |
| **Custom Fields** | 13 total | ⏸️ Planned | *Not yet implemented* |
| **Your Metrics** | 5 total | ⏸️ Planned | *Not yet implemented* |

**Overall Coverage: 24/39 endpoints (62%)**

> 💡 **Endpoint names match Sensor Tower's official API documentation `operationId` values**

---

## ⚙️ Configuration

### Using .env File (Recommended)

Create a `.env` file in your project root for easy configuration:

```bash
# Required: Your Sensor Tower API token
SENSOR_TOWER_API_TOKEN=your_actual_token_here

# Optional: Server configuration
TRANSPORT=http
PORT=8666
API_BASE_URL=https://api.sensortower.com

# Optional: Performance tuning
TIMEOUT=30
```

### Environment Variables

All configuration can also be set via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `SENSOR_TOWER_API_TOKEN` | Your API token (required) | None |
| `TRANSPORT` | Transport mode (`stdio` or `http`) | `stdio` |
| `PORT` | HTTP server port | `8666` |
| `API_BASE_URL` | Sensor Tower API base URL | `https://api.sensortower.com` |

### Getting Your API Token

1. Visit [Sensor Tower API Settings](https://app.sensortower.com/users/edit/api-settings)
2. Generate a new API token if you don't have one
3. Copy the token to your `.env` file or environment variables

---

## �� Table of Contents

- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
  - [Docker (Recommended)](#option-1-docker-recommended)
  - [MCP Client Integration](#option-2-mcp-client-integration)
  - [Direct Installation](#option-3-direct-installation)
- [Available Tools](#-available-tools)
- [Development](#-development)
- [API Examples](#-api-examples)
- [Docker Deployment](#-docker-deployment)
- [Security](#-security)
- [Performance](#-performance)
- [Testing](#-testing)
- [License](#-license)

---

## 📋 Prerequisites

Before installing, you'll need:

1. **Sensor Tower API Token**: Get your token from [Sensor Tower API Settings](https://app.sensortower.com/users/edit/api-settings)
2. **uv** (for MCP client integrations): See [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/)

## 🚀 Installation

### Option 1: Docker (Recommended)

The fastest way to get started is using our pre-built Docker image:

**Using .env file (Recommended):**
```bash
# Create .env file with your token
echo "SENSOR_TOWER_API_TOKEN=your_token_here" > .env

# Run with HTTP transport
docker run -p 8666:8666 --env-file .env \
  bobbysayers492/sensortower-mcp:latest \
  sensortower-mcp --transport http --port 8666

# Run with stdio transport (for MCP clients)
docker run --env-file .env \
  bobbysayers492/sensortower-mcp:latest \
  sensortower-mcp --transport stdio
```

**Using environment variables:**
```bash
# Run with HTTP transport
docker run -p 8666:8666 \
  -e SENSOR_TOWER_API_TOKEN="your_token_here" \
  bobbysayers492/sensortower-mcp:latest \
  sensortower-mcp --transport http --port 8666

# Run with stdio transport (for MCP clients)
docker run -e SENSOR_TOWER_API_TOKEN="your_token_here" \
  bobbysayers492/sensortower-mcp:latest \
  sensortower-mcp --transport stdio
```

### Option 2: MCP Client Integration

For AI assistants and IDEs that support MCP, add this server to your configuration:

#### Cursor
Add to your MCP settings (`~/.cursor-mcp/config.json`):
```json
{
  "mcpServers": {
    "sensortower": {
      "command": "uvx",
      "args": ["sensortower-mcp", "--transport", "stdio"],
      "env": {
        "SENSOR_TOWER_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

#### VSCode with MCP Extension
Add to your MCP configuration:
```json
{
  "sensortower": {
    "command": "uvx",
    "args": ["sensortower-mcp", "--transport", "stdio"],
    "env": {
      "SENSOR_TOWER_API_TOKEN": "your_token_here"
    }
  }
}
```

#### Claude Desktop
Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):
```json
{
  "mcpServers": {
    "sensortower": {
      "command": "uvx",
      "args": ["sensortower-mcp", "--transport", "stdio"],
      "env": {
        "SENSOR_TOWER_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

#### OpenAI Agents SDK
For OpenAI agents, configure the MCP server:
```python
from openai import OpenAI
from mcp import McpClient

# Configure MCP client
mcp_client = McpClient(
    command="uvx",
    args=["sensortower-mcp", "--transport", "stdio"],
    env={"SENSOR_TOWER_API_TOKEN": "your_token_here"}
)

# Use with OpenAI agent
client = OpenAI()
# Integrate MCP tools with your agent implementation
```

After adding the configuration, restart your client to load the Sensor Tower MCP server.

### Option 3: Direct Installation

Install the package directly from PyPI:

```bash
# Install the package
pip install sensortower-mcp

# Create .env file with your token (recommended)
echo "SENSOR_TOWER_API_TOKEN=your_token_here" > .env

# Run with HTTP transport
sensortower-mcp --transport http --port 8666

# Or run with stdio transport (for MCP clients)  
sensortower-mcp --transport stdio
```

**Alternative: Using environment variables**
```bash
# Set environment variable
export SENSOR_TOWER_API_TOKEN="your_token_here"

# Run the server
sensortower-mcp --transport http --port 8666
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

## 📄 License

MIT License - see LICENSE file for details.

Built with [FastMCP](https://github.com/jlowin/fastmcp) for streamlined MCP server development.

