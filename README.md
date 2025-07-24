# Sensor Tower MCP Server

[![PyPI version](https://badge.fury.io/py/sensortower-mcp.svg)](https://badge.fury.io/py/sensortower-mcp)
[![Docker Pulls](https://img.shields.io/docker/pulls/bobbysayers492/sensortower-mcp)](https://hub.docker.com/r/bobbysayers492/sensortower-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Model Context Protocol server for Sensor Tower APIs using FastMCP with OpenAPI integration.

## 🚀 Quick Start

### For Claude Desktop Users
1. **Install uv**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. **Get API token**: [Sensor Tower API Settings](https://app.sensortower.com/users/edit/api-settings)
3. **Add to Claude config** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
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
4. **Restart Claude Desktop**

### For HTTP API Access
```bash
# Install uv (handles Python automatically)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run server
SENSOR_TOWER_API_TOKEN="your_token" uvx sensortower-mcp --transport http --port 8666
```

---

## 📦 Installation

### Option 1: MCP Client Integration (Recommended)

**Prerequisites:** [uv](https://docs.astral.sh/uv/getting-started/installation/) (automatically manages Python)

#### Claude Desktop
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

### Option 2: Docker
```bash
# Quick start
docker run -p 8666:8666 -e SENSOR_TOWER_API_TOKEN="your_token" \
  bobbysayers492/sensortower-mcp:latest

# Production with compose
echo "SENSOR_TOWER_API_TOKEN=your_token" > .env
docker-compose up -d
```

### Option 3: Direct Installation
```bash
pip install sensortower-mcp
SENSOR_TOWER_API_TOKEN="your_token" sensortower-mcp --transport http --port 8666
```

---

## ⚙️ Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `SENSOR_TOWER_API_TOKEN` | Your API token (**required**) | None |
| `TRANSPORT` | Transport mode (`stdio` or `http`) | `stdio` |
| `PORT` | HTTP server port | `8666` |
| `API_BASE_URL` | Sensor Tower API base URL | `https://api.sensortower.com` |

**Get your API token:** [Sensor Tower API Settings](https://app.sensortower.com/users/edit/api-settings)

### Using .env File
```bash
# .env
SENSOR_TOWER_API_TOKEN=your_actual_token_here
TRANSPORT=http
PORT=8666
```

---

## 🔧 Usage Examples

### App Intelligence
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

### Search & Discovery
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

### Market Rankings
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

---

## 📊 Available Tools

### Core API Tools
- **get_app_metadata**: App details, ratings, descriptions
- **get_category_rankings**: Top ranking apps by category
- **get_download_estimates**: Download estimates by country/date
- **get_revenue_estimates**: Revenue estimates and trends
- **search_entities**: Search apps and publishers
- **get_reviews**: App reviews and ratings data
- **get_keywords**: Keyword rankings for apps

### Analytics Tools  
- **get_usage_active_users**: Active user analytics
- **app_analysis_retention**: User retention analysis
- **app_analysis_demographics**: Demographic breakdowns
- **get_churn_analysis**: User churn metrics
- **get_impressions**: Ad impression data

### Utility Tools
- **get_country_codes**: Available country codes
- **get_category_ids**: Category IDs for iOS/Android
- **get_chart_types**: Available chart types
- **health_check**: Service health status

---

## 📊 API Coverage

| Category | Coverage | Key Endpoints |
|----------|----------|---------------|
| **App Analysis** | ✅ 19+ endpoints | metadata, downloads, revenue, retention, demographics |
| **Store Marketing** | ✅ 6+ endpoints | keywords, reviews, featured content, creatives |
| **Market Analysis** | ✅ 4 endpoints | rankings, trending, publishers, store summary |
| **Consumer Intelligence** | ✅ 5+ endpoints | churn, engagement, power users, cohort retention |
| **Publisher Analytics** | ✅ 3+ endpoints | publisher apps, unified analytics |

**Total: 39+ endpoints covering all major Sensor Tower API categories**

---

## 🛠️ Development

```bash
# Clone and setup
git clone https://github.com/yourusername/sensortower-mcp
cd sensortower-mcp
pip install -e .

# Run locally
python main.py --transport http --port 8666

# Health check
curl http://localhost:8666/health
```

---

## 🐳 Docker Deployment

### Production Setup
```bash
# With Docker Compose
SENSOR_TOWER_API_TOKEN="your_token" docker-compose --profile production up -d

# Manual container
docker run -d \
  -p 8666:8666 \
  -e SENSOR_TOWER_API_TOKEN="your_token" \
  --restart unless-stopped \
  bobbysayers492/sensortower-mcp:latest
```

### Resource Configuration
- **Memory**: 256MB limit
- **CPU**: 0.5 cores  
- **Health checks**: Every 30s
- **Auto-restart**: On failure

### Monitoring
Health endpoint: `GET /health`
```json
{
  "status": "healthy",
  "service": "Sensor Tower MCP Server", 
  "transport": "http",
  "tools_available": 39
}
```

---

## 🔒 Security & Performance

### Security Features
- Non-root container execution
- Input validation and request timeouts
- No hardcoded secrets
- Security headers and rate limiting
- Regular dependency scanning

### Performance Benchmarks
- **Response Time**: <100ms utility, <500ms API calls
- **Throughput**: >50 RPS mixed workload
- **Memory Usage**: <256MB normal load
- **Success Rate**: >99% valid requests

---

## 🧪 Testing

Comprehensive test suite available in `tests/`:

```bash
# Quick validation
python tests/test_manual.py

# Full production readiness  
python tests/test_all.py

# Load testing
python tests/test_load.py
```

See [tests/README.md](tests/README.md) for detailed testing documentation.

---

## 📄 License

MIT License - see LICENSE file for details.
