# Sensor Tower MCP Server

[![PyPI version](https://badge.fury.io/py/sensortower-mcp.svg)](https://badge.fury.io/py/sensortower-mcp)
[![Python versions](https://img.shields.io/pypi/pyversions/sensortower-mcp.svg)](https://pypi.org/project/sensortower-mcp/)
[![Downloads](https://pepy.tech/badge/sensortower-mcp)](https://pepy.tech/project/sensortower-mcp)

A Model Context Protocol (MCP) server providing access to Sensor Tower's comprehensive mobile app intelligence APIs. Connect to app store data, rankings, downloads, revenue estimates, and competitor intelligence through a standardized interface.

## 🚀 Quick Install

```bash
# Install with uvx (recommended)
uvx sensortower-mcp

# Or install with pip
pip install sensortower-mcp
```

📦 **[View on PyPI](https://pypi.org/project/sensortower-mcp/)**

## Available Tools

### 📱 App Intelligence API
- **`get_app_metadata`** - Get app details like name, publisher, categories, descriptions, ratings
- **`get_category_rankings`** - Fetch top ranking apps by category and chart type  
- **`get_download_estimates`** - Retrieve download estimates by country and date ranges
- **`get_revenue_estimates`** - Get revenue estimates and financial trends

### 🏪 Store Intelligence API
- **`get_featured_apps`** - Get apps featured on App Store's Apps & Games pages
- **`get_featured_today_stories`** - Fetch App Store Today tab story metadata

### 🔍 Usage Intelligence API
- **`search_entities`** - Search for apps and publishers by name/description  
- **`get_app_ids_by_category`** - Get app IDs from specific categories and date ranges

### 📊 Connected Apps API
- **`get_analytics_metrics`** - Access your own apps' analytics data (impressions, downloads, sessions)

### 📺 Ad Intelligence API
- **`get_advertising_creatives`** - Get advertising creative data for competitor analysis

### 🛠️ Utility Tools
- **`get_country_codes`** - Get available country codes
- **`get_category_ids`** - Get category IDs for iOS/Android
- **`get_chart_types`** - Get available chart types for rankings


[Get your API token](https://app.sensortower.com/users/edit/api-settings) from Sensor Tower, then update your API token in the MCP server configuration.

## Installation

### Prerequisites

Make sure you have `uvx` installed for the easiest setup:
```bash
# Install uv (which includes uvx)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Claude Desktop

**Option 1: Using uvx (recommended for local development)**
```json
{
  "mcpServers": {
    "sensortower": {
      "command": "uvx",
      "args": ["--from", "/path/to/sensortower-mcp", "sensortower-mcp"],
      "env": {
        "SENSOR_TOWER_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

**Option 2: From PyPI**
```json
{
  "mcpServers": {
    "sensortower": {
      "command": "uvx",
      "args": ["sensortower-mcp"],
      "env": {
        "SENSOR_TOWER_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

**Option 3: Direct Python execution**
```json
{
  "mcpServers": {
    "sensortower": {
      "command": "python",
      "args": ["/path/to/sensortower-mcp/main.py"],
      "env": {
        "SENSOR_TOWER_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

### Cursor

**Setup Instructions:**
- Follow the [Cursor MCP guide](https://docs.cursor.com/context/model-context-protocol) for complete setup
- Make sure to use [Agent mode](https://docs.cursor.com/chat/agent) for best results

**Manual configuration for cursor-mcp-config.json:**
```json
{
  "sensortower": {
    "command": "uvx",
    "args": ["sensortower-mcp"],
    "env": {
      "SENSOR_TOWER_API_TOKEN": "your_api_token_here"
    }
  }
}
```

### VSCode

Install the MCP extension and add this server configuration:

```json
{
  "name": "Sensor Tower",
  "command": "python",
  "args": ["/path/to/sensortower-mcp/main.py"],
  "env": {
    "SENSOR_TOWER_API_TOKEN": "your_api_token_here"
  }
}
```

### Docker

**Pull and run from Docker Hub:**
```bash
# Run in stdio mode (MCP)
docker run -e SENSOR_TOWER_API_TOKEN="your_token" bobbysayers492/sensortower-mcp

# Run in HTTP mode
docker run -e SENSOR_TOWER_API_TOKEN="your_token" -p 8666:8666 \
  bobbysayers492/sensortower-mcp sensortower-mcp --transport http --port 8666
```

**Available on Docker Hub:** [bobbysayers492/sensortower-mcp](https://hub.docker.com/r/bobbysayers492/sensortower-mcp)

**Docker Compose:**
```yaml
version: '3.8'
services:
  sensortower-mcp:
    image: bobbysayers492/sensortower-mcp:latest
    environment:
      - SENSOR_TOWER_API_TOKEN=your_api_token_here
      - TRANSPORT=http
      - PORT=8666
    ports:
      - "8666:8666"
```

### Direct Installation

**Prerequisites:**
- Python 3.10+
- Sensor Tower API access

**Install dependencies:**
```bash
pip install fastmcp httpx
```

**Get your API token:**
1. Visit [Sensor Tower API Settings](https://app.sensortower.com/users/edit/api-settings)
2. Generate or copy your API token
3. Ensure your organization has access to the required API products

**Set your API token:**
```bash
export SENSOR_TOWER_API_TOKEN="your_api_token_here"
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SENSOR_TOWER_API_TOKEN` | Your Sensor Tower API authentication token | - | ✅ |
| `TRANSPORT` | Transport mode: `stdio` or `http` | `stdio` | ❌ |
| `PORT` | HTTP server port (when using `--transport=http`) | `8666` | ❌ |
| `API_BASE_URL` | Sensor Tower API base URL | `https://api.sensortower.com` | ❌ |

### Command Line Options

| Option | Environment Variable | Description | Default |
|--------|---------------------|-------------|---------|
| `--transport` | `TRANSPORT` | Transport mode: `stdio` or `http` | `stdio` |
| `--port` | `PORT` | HTTP server port (only for `--transport=http`) | `8666` |
| `--token` | `SENSOR_TOWER_API_TOKEN` | API authentication token | Required |

### Transport

- **stdio** (default) - for direct integration with Claude Desktop, Cursor, VSCode:
  ```bash
  python main.py --transport stdio
  ```

- **http** - for browser and network clients:
  ```bash
  python main.py --transport http --port 8666
  ```

## Usage Examples

### Basic App Research

```bash
# Search for apps
search_entities(
    os="unified", 
    entity_type="app", 
    term="fitness tracker", 
    limit=20
)

# Get detailed metadata  
get_app_metadata(
    os="ios", 
    app_ids="284882215,1262148500", 
    country="US"
)

# Analyze market position
get_category_rankings(
    os="ios", 
    category="6005", 
    chart_type="topfreeapplications", 
    country="US", 
    date="2024-01-15"
)
```

### Competitor Analysis

```bash
# Download trends
get_download_estimates(
    os="android", 
    app_ids="com.facebook.katana", 
    countries="US,GB,DE", 
    start_date="2024-01-01", 
    end_date="2024-01-31"
)

# Revenue analysis
get_revenue_estimates(
    os="ios", 
    app_ids="284882215", 
    countries="US,JP,GB", 
    start_date="2023-12-01", 
    end_date="2023-12-31"
)
```

### Market Discovery

```bash
# Find new apps in category
get_app_ids_by_category(
    os="android", 
    category="games", 
    start_date="2024-01-01", 
    limit=100
)

# Check featured placement
get_featured_apps(
    category="6014", 
    country="US", 
    start_date="2024-01-10", 
    end_date="2024-01-15"
)
```

## Parameter Reference

### Common Parameters

| Parameter | Description | Format | Examples |
|-----------|-------------|---------|----------|
| **`os`** | Operating system | String | `"ios"`, `"android"`, `"unified"` |
| **`country`** | Country code | ISO 2-letter | `"US"`, `"GB"`, `"JP"`, `"DE"` |
| **`app_ids`** | App identifiers | Comma-separated | iOS: `"284882215"`, Android: `"com.facebook.katana"` |
| **`category`** | Category ID | String/Number | iOS: `"6005"` (Social), Android: `"social"` |
| **`chart_type`** | Ranking chart | String | `"topfreeapplications"`, `"toppaidapplications"` |
| **`dates`** | Date format | YYYY-MM-DD | `"2024-01-15"` |

### Discovery Helpers

```bash
# Get available countries  
get_country_codes()

# Get iOS categories
get_category_ids(os="ios")  

# Get Android categories
get_category_ids(os="android")

# Get chart types
get_chart_types()
```

## Error Handling

The server provides comprehensive error handling:

- ✅ **Authentication validation** - Checks for required API token
- ✅ **Request timeouts** - 30-second timeout for all requests  
- ✅ **Parameter validation** - OpenAPI schema validation
- ✅ **Rate limit handling** - Respects Sensor Tower API limits
- ✅ **Clear error messages** - Helpful debugging information

Common error responses:
- **401 Unauthorized**: Invalid API token
- **403 Forbidden**: API token lacks required permissions  
- **422 Unprocessable Entity**: Invalid request parameters
- **429 Too Many Requests**: Rate limit exceeded

## Resources

The server provides built-in documentation resources:

- **`sensor-tower://docs`** - Complete API documentation
- **`sensor-tower://examples`** - Practical usage examples

## Tips

- **App IDs**: iOS uses numeric IDs, Android uses package names
- **Date ranges**: Use YYYY-MM-DD format for all dates
- **Rate limiting**: Sensor Tower APIs have rate limits - space out requests
- **Categories**: Use `get_category_ids()` to find the right category for your platform  
- **Countries**: Use `get_country_codes()` to see supported markets
- **Testing**: Use the demo endpoints first to verify connectivity

## Links

- [Sensor Tower API Documentation](https://docs.sensortower.com/)
- [Sensor Tower API Settings](https://app.sensortower.com/users/edit/api-settings) 
- [FastMCP Documentation](https://github.com/gofastmcp/fastmcp)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## License

This project is licensed under the MIT License.
## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality  
4. Ensure all tools work with valid API tokens
5. Update documentation
6. Submit a pull request

## Security

- **Never commit API tokens**: This repository includes a `.gitignore` file to prevent accidentally committing sensitive data
- **Use environment variables**: Store your `SENSOR_TOWER_API_TOKEN` in environment variables, not in code
- **Token permissions**: Ensure your API token has only the minimum required permissions
- **Rotate tokens**: Regularly rotate your API tokens for security

## Disclaimer

This is an unofficial MCP server for Sensor Tower APIs. It is not affiliated with or endorsed by Sensor Tower. You must have a valid Sensor Tower subscription and API access to use this server.

