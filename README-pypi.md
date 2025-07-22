# Sensor Tower MCP Server

Access Sensor Tower's mobile app intelligence APIs through the Model Context Protocol (MCP). Get app store data, rankings, downloads, revenue estimates, and competitor intelligence directly in MCP-compatible tools like Cursor.

## Features

- **📱 App Intelligence** - Metadata, rankings, downloads, revenue estimates
- **🔍 Search & Discovery** - Find apps and publishers by name or description  
- **📊 Market Analysis** - Category rankings, featured apps, competitor insights
- **🛠️ Developer Tools** - Access your own app analytics and metrics

## Quick Start

```bash
# Install with uvx (recommended)
uvx sensortower-mcp

# Or install with pip
pip install sensortower-mcp
```

### MCP Configuration

Add to your MCP settings (e.g., Cursor):

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

## API Token

Get your API token from [Sensor Tower Account Settings](https://app.sensortower.com/users/edit/api-settings).

## Available Tools

| Tool | Description |
|------|-------------|
| `get_app_metadata` | App details, ratings, categories |
| `search_entities` | Search apps and publishers |
| `get_category_rankings` | Top apps by category |
| `get_download_estimates` | Download trends and estimates |
| `get_revenue_estimates` | Revenue data and forecasts |
| `get_country_codes` | Available country codes |
| `get_category_ids` | Platform category IDs |

## Example Usage

```python
# Search for social media apps
search_entities(os="ios", entity_type="app", term="social media", limit=10)

# Get app metadata
get_app_metadata(os="ios", app_ids="284882215", country="US")

# Get top free apps in Social category
get_category_rankings(
    os="ios", 
    category="6005", 
    chart_type="topfreeapplications", 
    country="US", 
    date="2024-01-15"
)
```

## Requirements

- Python 3.10+
- Sensor Tower API token
- MCP-compatible client (Cursor, etc.)

## Docker

```bash
# Run with Docker
docker run -e SENSOR_TOWER_API_TOKEN="your_token" -p 8666:8666 \
  bobbysayers492/sensortower-mcp sensortower-mcp --transport http --port 8666
```

## Links

- [Docker Hub](https://hub.docker.com/r/bobbysayers492/sensortower-mcp)
- [Full Documentation](https://github.com/sensortower/sensortower-mcp)
- [Sensor Tower API](https://docs.sensortower.com/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## License

MIT License 