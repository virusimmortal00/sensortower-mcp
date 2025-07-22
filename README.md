# Sensor Tower MCP Server

A Model Context Protocol (MCP) server providing access to Sensor Tower's comprehensive mobile app intelligence APIs. Connect to app store data, rankings, downloads, revenue estimates, and competitor intelligence through a standardized interface.

> **Note**: Brought to you as an example of FastMCP integration with enterprise APIs.

## 🚀 Quick Install

### Add to Cursor

[![Add Sensor Tower MCP to Cursor](https://cursor.com/deeplink/mcp-install-dark.png)](cursor://anysphere.cursor-deeplink/mcp/install?name=sensortower&config=eyJzZW5zb3J0b3dlciI6eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJzZW5zb3J0b3dlci1tY3AiXSwiZW52Ijp7IlNFTlNPUl9UT1dFUl9BUElfVE9LRU4iOiJ5b3VyX2FwaV90b2tlbl9oZXJlIn19fQ==)



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
docker run -e SENSOR_TOWER_API_TOKEN="your_token" sensortower/sensortower-mcp
```

**Build locally:**
```bash
git clone https://github.com/sensortower/sensortower-mcp.git
cd sensortower-mcp
docker build -t sensortower-mcp .
docker run -e SENSOR_TOWER_API_TOKEN="your_token" sensortower-mcp
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  sensortower-mcp:
    image: sensortower/sensortower-mcp
    environment:
      - SENSOR_TOWER_API_TOKEN=your_api_token_here
      - TRANSPORT=http
      - PORT=8080
    ports:
      - "8080:8080"
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
| `PORT` | HTTP server port (when using `--transport=http`) | `8080` | ❌ |
| `API_BASE_URL` | Sensor Tower API base URL | `https://api.sensortower.com` | ❌ |

### Command Line Options

| Option | Environment Variable | Description | Default |
|--------|---------------------|-------------|---------|
| `--transport` | `TRANSPORT` | Transport mode: `stdio` or `http` | `stdio` |
| `--port` | `PORT` | HTTP server port (only for `--transport=http`) | `8080` |
| `--token` | `SENSOR_TOWER_API_TOKEN` | API authentication token | Required |

### Transport

- **stdio** (default) - for direct integration with Claude Desktop, Cursor, VSCode:
  ```bash
  python main.py --transport stdio
  ```

- **http** - for browser and network clients:
  ```bash
  python main.py --transport http --port 8080
  ```

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

## Development

### Setup

1. **Clone repository:**
   ```bash
git clone https://github.com/sensortower/sensortower-mcp.git
cd sensortower-mcp
```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   # or
   pip install fastmcp httpx
   ```

3. **Set up environment:**
   ```bash
   export SENSOR_TOWER_API_TOKEN="your_api_token_here"
   ```

4. **Run in development mode:**
   ```bash
   python main.py --transport stdio
   ```

### Project Structure

```
sensortower-mcp/
├── main.py              # FastMCP server implementation
├── pyproject.toml       # Project configuration  
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker container setup
├── docker-compose.yml  # Docker Compose configuration
├── example.py          # Test script
├── README.md          # This documentation
└── swaggerdocs/       # API documentation
    ├── app_analysis.yml
    ├── market_analysis.yml
    ├── store_marketing.yml
    ├── custom_fields_metadata.yml
    └── your_metrics.yml
```

### Testing

**Run the test script:**
```bash
python example.py
```

**Test with MCP Inspector:**

**stdio mode:**
```bash
SENSOR_TOWER_API_TOKEN="your_token" npx @modelcontextprotocol/inspector python main.py
```

**HTTP mode:**
```bash
# Start server
python main.py --transport http --port 8080

# In another terminal, test the health endpoint
curl http://localhost:8080/health
```

### Building

**Build for production:**
```bash
# Create distribution
python -m build

# Or create standalone executable
pip install pyinstaller
pyinstaller --onefile main.py
```

**Docker build:**
```bash
docker build -t sensortower-mcp .
```

## Architecture

### FastMCP Integration

This server leverages **FastMCP's automatic OpenAPI integration**:

```
FastMCP Server
├── OpenAPI Spec → Auto-generated Tools (11 endpoints)
├── Manual Tools → Utility functions (3 tools)  
├── HTTP Client → httpx with auth headers
└── Resources → Documentation & examples
```

**Benefits over manual MCP implementation:**
- ✅ **90% less boilerplate code** - OpenAPI auto-generation  
- ✅ **Built-in validation** - Type safety and error handling
- ✅ **Automatic HTTP handling** - No manual request/response code
- ✅ **Streamlined development** - Focus on business logic

### API Coverage

| API Category | Endpoints Covered |
|-------------|-------------------|
| App Intelligence | `/v1/{os}/apps`, `/v1/{os}/ranking`, `/v1/{os}/downloads`, `/v1/{os}/revenue` |
| Store Intelligence | `/v1/ios/featured/apps`, `/v1/ios/featured/today/stories` |
| Usage Intelligence | `/v1/{os}/search_entities`, `/v1/{os}/apps/app_ids` |
| Connected Apps | `/v1/ios/sales_reports/analytics_metrics` |
| Ad Intelligence | `/v1/{os}/advertising/creatives` |

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
