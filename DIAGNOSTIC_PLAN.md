# Systematic Diagnostic Plan for Sensor Tower MCP Issues

## Overview
This document outlines a systematic approach to diagnose and resolve the 7 tools with issues found in comprehensive testing.

## 🎯 Issues to Diagnose

### Critical Issues (7 tools)
1. **Usage Intelligence Tools (3 tools)** - 404 errors
   - `mcp_sensortower_get_usage_active_users`
   - `mcp_sensortower_app_analysis_retention` 
   - `mcp_sensortower_app_analysis_demographics`

2. **Advertising Intelligence Tools (3 tools)** - 422 errors
   - `mcp_sensortower_get_creatives`
   - `mcp_sensortower_get_impressions`
   - `mcp_sensortower_impressions_rank`

3. **Implementation Issues (1 tool)** - Format error
   - `mcp_sensortower_get_publisher_apps` (returns list instead of dict)

## 🔍 Diagnostic Phases

### Phase 1: Endpoint Availability 
**Objective**: Determine if problematic endpoints still exist

**Method**:
- Use OPTIONS/HEAD requests to test endpoint existence
- Test without authentication first to isolate connectivity issues
- Compare with known working endpoints

**Expected Outcomes**:
- 404 endpoints: Likely deprecated or moved
- 422 endpoints: Exist but have parameter issues

### Phase 2: Parameter Validation
**Objective**: Identify correct parameter formats and requirements

**Method**:
- Test minimal parameter sets vs full parameter sets
- Validate date formats, app ID formats, country codes
- Test different combinations systematically
- Parse 422 error responses for specific validation messages

**Expected Outcomes**:
- Identify specific parameter issues
- Find working parameter combinations
- Understand validation requirements

### Phase 3: Implementation Analysis
**Objective**: Fix code-level implementation issues

**Method**:
- Analyze `get_publisher_apps` response format
- Compare with working tools like `search_entities`
- Design consistent response format
- Test format conversion logic

**Expected Outcomes**:
- Clear fix for implementation error
- Consistent response format across all tools

### Phase 4: Access Level Investigation  
**Objective**: Determine if issues are access/permission related

**Method**:
- Test token validity with known working endpoints
- Check for 401/403/402 status codes indicating access issues
- Compare free vs premium endpoint requirements
- Validate current API plan capabilities

**Expected Outcomes**:
- Confirm token validity
- Identify premium-only endpoints
- Understand access limitations

## 🛠️ Implementation Steps

### Step 1: Run Diagnostic Script
```bash
cd tests/
python diagnostic_tests.py
```

### Step 2: Analyze Results
Review diagnostic output for:
- Endpoint availability status
- Parameter validation errors  
- Implementation issues
- Access level restrictions

### Step 3: Apply Fixes Based on Findings

#### For 404 Errors (Usage Intelligence):
- **If endpoints are deprecated**: Update to new endpoints or remove tools
- **If endpoints moved**: Update endpoint URLs in main.py
- **If access-restricted**: Document premium requirements

#### For 422 Errors (Advertising Intelligence):
- **If parameter format issues**: Fix parameter formatting in main.py
- **If missing required parameters**: Add required parameters
- **If invalid values**: Update parameter validation

#### For Implementation Errors:
- **Fix `get_publisher_apps`**: Wrap list response in dict format
- **Follow existing patterns**: Use same structure as `search_entities` fix

### Step 4: Validation Testing
After applying fixes:
- Re-run comprehensive tool testing
- Verify fixes don't break working tools
- Test edge cases and error handling

## 📋 Diagnostic Tools Created

### 1. `tests/diagnostic_tests.py`
Comprehensive diagnostic script with:
- Endpoint availability testing
- Parameter validation testing
- Implementation error analysis
- Access level checking
- Detailed reporting

### 2. Running Diagnostics
```bash
# Run full diagnostic suite
python tests/diagnostic_tests.py

# Expected output:
# - Phase 1: Endpoint availability results
# - Phase 2: Parameter validation results
# - Phase 3: Implementation analysis
# - Phase 4: Access level investigation
# - Comprehensive report with recommendations
```

## 🎯 Success Criteria

### Immediate Goals
- [ ] Identify root cause for each of the 7 failing tools
- [ ] Determine which issues are fixable vs require API access changes
- [ ] Create specific fix plan for each issue type

### Resolution Goals  
- [ ] Fix `get_publisher_apps` implementation error
- [ ] Resolve or document 422 parameter errors
- [ ] Resolve or document 404 endpoint errors
- [ ] Achieve >90% tool success rate

### Long-term Goals
- [ ] Establish monitoring for API endpoint changes
- [ ] Create parameter validation guidelines
- [ ] Document premium vs free API feature differences

## 🔄 Iterative Process

### Cycle 1: Quick Wins
1. Fix implementation error (get_publisher_apps)
2. Test basic parameter fixes for 422 errors
3. Verify endpoint URLs for 404 errors

### Cycle 2: Deep Investigation
1. API documentation research
2. Contact Sensor Tower support if needed
3. Test alternative approaches

### Cycle 3: Documentation & Monitoring
1. Document known limitations
2. Set up monitoring for future issues
3. Create troubleshooting guide

## 📞 Escalation Path

### Internal Resolution
1. Fix obvious implementation issues
2. Research API documentation
3. Test alternative parameter combinations

### External Support
If internal resolution fails:
1. Contact Sensor Tower API support
2. Check community forums/documentation
3. Verify API plan includes required features

### Documentation & Workarounds
For unresolvable issues:
1. Document known limitations
2. Provide alternative tools where possible
3. Update user guidance

---

## Next Steps

1. **Run the diagnostic script**: `python tests/diagnostic_tests.py`
2. **Analyze results**: Review each phase's findings
3. **Apply quick fixes**: Start with implementation errors
4. **Iterate**: Re-test and refine based on results

This systematic approach ensures we understand the root causes before applying fixes, leading to more reliable and maintainable solutions.