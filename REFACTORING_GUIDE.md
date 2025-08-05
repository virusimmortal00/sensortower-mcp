# Sensor Tower MCP Server - Refactoring Guide

## Current Structure Issues

Your current `main.py` is 1957 lines and contains:
- All 40+ MCP tool definitions
- Configuration and argument parsing  
- HTTP client setup
- Server startup logic
- Documentation strings
- Utility functions

This makes it difficult to:
- Maintain and debug
- Add new features
- Test individual components
- Navigate the codebase

## Recommended New Structure

```
src/sensortower_mcp/
├── __init__.py                 # Package initialization
├── config.py                   # Configuration, args, HTTP client setup
├── base.py                     # Base classes and utilities  
├── server.py                   # Main server class and entry points
├── documentation.py            # MCP resources and docs
└── tools/                      # Tool modules organized by API category
    ├── __init__.py
    ├── app_analysis.py         # 14 app analysis tools
    ├── store_marketing.py      # 6 store marketing tools
    ├── market_analysis.py      # 8 market analysis tools
    ├── your_metrics.py         # 5 connected apps tools
    ├── search_discovery.py     # 4 search/discovery tools
    └── utilities.py            # 4 utility tools (countries, categories, etc.)
```

## Benefits of New Structure

### 1. **Separation of Concerns**
- Configuration in `config.py`
- Base classes in `base.py`
- Each API category in separate modules
- Server orchestration in `server.py`

### 2. **Maintainability**
- Easy to find and modify specific tools
- Clear module responsibilities
- Smaller, focused files (~150-200 lines each)

### 3. **Testability**
- Can test individual tool categories
- Mock dependencies more easily
- Isolated unit tests

### 4. **Extensibility**
- Add new API categories as separate modules
- Easy to add new tools to existing categories
- Clear patterns for new contributors

### 5. **Code Reuse**
- Base `SensorTowerTool` class eliminates duplication
- Shared utilities in `base.py`
- Consistent error handling

## Migration Steps

### Step 1: Create New Structure
```bash
mkdir -p src/sensortower_mcp/tools
# Create all the new files as shown above
```

### Step 2: Update pyproject.toml
```toml
[project.scripts]
sensortower-mcp = "sensortower_mcp.server:cli"

[tool.hatch.build.targets.wheel]
packages = ["src/sensortower_mcp"]
```

### Step 3: Test New Implementation
```bash
# Test with new structure
python -m src.sensortower_mcp.server --transport stdio

# Or install and test
pip install -e .
sensortower-mcp --transport http --port 8666
```

### Step 4: Update CI/CD and Tests
- Update test imports to use new modules
- Update any scripts that import from `main.py`

### Step 5: Remove Old Files
```bash
mv main.py main_old.py  # Backup first
rm main_old.py          # After confirming new version works
```

## Key Architectural Patterns

### 1. **Base Tool Class**
```python
class SensorTowerTool:
    def __init__(self, client: httpx.AsyncClient, token: str):
        self.client = client
        self.token = token
    
    async def make_request(self, endpoint: str, params: Dict[str, Any]):
        params["auth_token"] = self.token
        response = await self.client.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()
```

### 2. **Tool Registration Pattern**
```python
class AppAnalysisTools(SensorTowerTool):
    def register_tools(self, mcp: FastMCP):
        @mcp.tool
        def get_app_metadata(...):
            # Tool implementation
```

### 3. **Server Orchestration**
```python
class SensorTowerMCPServer:
    def register_all_tools(self, token: str):
        app_analysis = AppAnalysisTools(self.client, token)
        app_analysis.register_tools(self.mcp)
        # ... register other tool categories
```

## File Size Comparison

| File | Current | New Structure |
|------|---------|---------------|
| main.py | 1957 lines | N/A |
| config.py | N/A | ~80 lines |
| base.py | N/A | ~60 lines |
| server.py | N/A | ~150 lines |
| app_analysis.py | N/A | ~200 lines |
| store_marketing.py | N/A | ~120 lines |
| market_analysis.py | N/A | ~180 lines |
| your_metrics.py | N/A | ~100 lines |
| search_discovery.py | N/A | ~80 lines |
| utilities.py | N/A | ~90 lines |
| documentation.py | N/A | ~150 lines |

**Total: 1957 lines → ~1210 lines across 11 focused modules**

## Testing the New Structure

1. **Individual Tool Categories**:
   ```python
   # Test app analysis tools in isolation
   from src.sensortower_mcp.tools.app_analysis import AppAnalysisTools
   ```

2. **Configuration**:
   ```python
   # Test config parsing
   from src.sensortower_mcp.config import parse_args, validate_token
   ```

3. **Full Server**:
   ```python
   # Test complete server
   from src.sensortower_mcp.server import SensorTowerMCPServer
   ```

This refactoring transforms your monolithic 1957-line file into a clean, maintainable, pythonic package structure that follows best practices for larger Python projects.