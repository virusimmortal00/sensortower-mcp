# Sensor Tower MCP Server - Bug Report

## Summary
Multiple issues found in sensortower-mcp server during OpenAI Agents SDK integration testing. Server has schema validation errors and API access restrictions that prevent advertising intelligence queries from working.

## Environment
- **sensortower-mcp version**: 1.1.0 (via `uvx sensortower-mcp`)
- **OpenAI Agents SDK**: 0.9.0
- **Transport**: stdio
- **API**: Sensor Tower API v1
- **Test Date**: 2025-07-24

## Issues Found

### 🚨 **Critical Issue 1: `search_entities` Schema Validation Error**

**Problem**: Tool returns a list but MCP framework expects dictionary structure.

**Error Message**:
```
Error calling tool 'search_entities': structured_content must be a dict or None. 
Got list: [{'app_id': 'com.mistplay.mistplay', 'canonical_country': 'US', ...}]
Tools should wrap non-dict values based on their output_schema.
```

**Reproduction**:
```bash
# Any search_entities call fails with schema error
uvx sensortower-mcp search_entities --os android --entity_type app --term "Mistplay" --limit 3
```

**Expected**: Dictionary wrapper around the app list
**Actual**: Raw list causing MCP validation failure

**Impact**: Breaks all app discovery workflows

---

### 🚨 **Critical Issue 2: Advertising Intel APIs Return 422 Errors**

**Problem**: All advertising intelligence endpoints return `422 Unprocessable Content`

**Affected Tools**:
- `get_creatives` 
- `get_impressions`

**Error Examples**:
```
HTTPStatusError: Client error '422 Unprocessable Content' for url 
'https://api.sensortower.com/v1/android/ad_intel/creatives?app_ids=com.mistplay.mistplay&start_date=2024-01-01&countries=US&networks=facebook&auth_token=ST0_usKmuVU4_gUANJDtgUrwLJv'

HTTPStatusError: Client error '422 Unprocessable Content' for url 
'https://api.sensortower.com/v1/android/ad_intel/impressions?app_ids=com.mistplay.mistplay&start_date=2023-09-01&end_date=2023-09-30&countries=US&networks=all&date_granularity=daily&auth_token=ST0_usKmuVU4_gUANJDtgUrwLJv'
```

**Reproduction**:
```bash
# Both calls fail for multiple apps tested
uvx sensortower-mcp get_creatives --os android --app_ids "com.mistplay.mistplay" --start_date "2024-01-01" --countries "US" --networks "facebook"
uvx sensortower-mcp get_creatives --os android --app_ids "com.netflix.mediaclient" --start_date "2024-01-01" --countries "US" --networks "facebook"
```

**Impact**: Makes advertising network analysis impossible - this is a core use case

---

### 🚨 **Issue 3: `get_download_estimates` Returns 404**

**Problem**: Basic download estimates endpoint not accessible

**Error**:
```
HTTPStatusError: Client error '404 Not Found' for url 
'https://api.sensortower.com/v1/android/downloads?app_ids=com.mistplay.mistplay&auth_token=ST0_usKmuVU4_gUANJDtgUrwLJv'
```

**Impact**: Prevents download performance analysis

---

## ✅ What Works Correctly

These tools function properly:
- ✅ `health_check` - Returns 39 available tools
- ✅ `get_app_metadata` - Returns proper app details
- ✅ `get_category_ids` - Returns category mappings  
- ✅ `get_country_codes` - Returns country mappings

## Root Cause Analysis

### Schema Issue (`search_entities`)
The MCP framework requires tools to return dictionary structures. The `search_entities` tool is returning a raw list which violates the MCP protocol specification.

**Fix Needed**: Wrap the list in a dictionary structure like:
```json
{
  "apps": [
    {"app_id": "com.mistplay.mistplay", ...},
    {"app_id": "...", ...}
  ],
  "total_count": 3
}
```

### API Access Issues (Advertising Intel)
The 422 errors suggest either:
1. **API Tier Restrictions**: The API key doesn't have access to advertising intelligence endpoints
2. **Parameter Validation**: Required parameters are missing or formatted incorrectly  
3. **Endpoint Changes**: API endpoints may have changed since MCP server implementation

**Investigation Needed**:
- Verify API key has advertising intel permissions
- Check if additional parameters are required
- Validate endpoint URLs against current Sensor Tower API documentation

## Impact on OpenAI Agents SDK Integration

The core issue reported was: *"I encountered an issue retrieving the advertising network data for Mistplay"*

Our OpenAI Agents SDK integration is **working correctly** - it:
- ✅ Discovers MCP tools automatically
- ✅ Calls tools with proper parameters  
- ✅ Handles errors gracefully with detailed messages
- ✅ Provides actionable feedback to users

The SDK integration correctly identified these as **server-side MCP issues** rather than failing silently.

## Suggested Fixes

### Priority 1: Fix `search_entities` Schema
```python
# Current (broken)
return search_results_list

# Fixed
return {
    "apps": search_results_list,
    "total_count": len(search_results_list),
    "query": original_query
}
```

### Priority 2: Debug Advertising Intel APIs
1. Test API endpoints directly with curl/httpx
2. Verify API key permissions with Sensor Tower support
3. Check current API documentation for parameter requirements
4. Add better error handling with specific error messages

### Priority 3: Validate All Endpoint URLs
Review all API endpoints against current Sensor Tower documentation to ensure they haven't changed.

## Test Case for Validation

Once fixed, this should work:
```bash
# Test basic app search (schema fix)
uvx sensortower-mcp search_entities --os android --entity_type app --term "Mistplay" --limit 3

# Test advertising analysis (API access fix)  
uvx sensortower-mcp get_creatives --os android --app_ids "com.mistplay.mistplay" --start_date "2024-01-01" --countries "US" --networks "facebook"
```

Expected result: Clean execution with proper JSON responses that enable advertising network analysis.

---

**Reporter**: Via OpenAI Agents SDK integration testing  
**Priority**: High (blocks core advertising intelligence workflows)  
**Availability**: Happy to test fixes or provide additional debugging information 