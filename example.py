#!/usr/bin/env python3
"""
Example script showing how to test the Sensor Tower MCP server (FastMCP)
"""

import asyncio
import os
import sys

async def test_fastmcp_tools():
    """Test basic functionality by calling the main server directly"""
    
    # Check if API token is set
    if not os.getenv("SENSOR_TOWER_API_TOKEN"):
        print("❌ Error: Please set SENSOR_TOWER_API_TOKEN environment variable")
        print("🔑 Get your token from: https://app.sensortower.com/users/edit/api-settings")
        return False
        
    try:
        # Import the main server module to test tools
        from main import mcp, get_country_codes, get_category_ids, get_chart_types
        
        print("🚀 Testing Sensor Tower MCP Server (FastMCP)")
        print("=" * 50)
        
        # Test utility tools
        print("\n📍 Testing utility tools:")
        
        countries = get_country_codes()
        print(f"✅ Country codes: Found {len(countries['countries'])} countries")
        
        ios_categories = get_category_ids("ios")
        print(f"✅ iOS categories: Found {len(ios_categories['categories'])} categories")
        
        android_categories = get_category_ids("android") 
        print(f"✅ Android categories: Found {len(android_categories['categories'])} categories")
        
        chart_types = get_chart_types()
        print(f"✅ Chart types: Found {len(chart_types['chart_types'])} chart types")
        
        # List available tools
        print(f"\n🔧 Available tools: {len(mcp._tools)} total")
        tool_names = list(mcp._tools.keys())
        
        print("\n📋 Tool inventory:")
        for i, tool_name in enumerate(sorted(tool_names), 1):
            print(f"  {i:2d}. {tool_name}")
            
        print("\n📖 Resources available:")
        resource_names = list(mcp._resources.keys()) if hasattr(mcp, '_resources') else []
        for resource in resource_names:
            print(f"  • {resource}")
            
        print("\n✅ All tests passed! Server is ready to use.")
        print("\n💡 Usage examples:")
        print("   # Get iOS app metadata")
        print('   get_app_metadata(os="ios", app_ids="284882215", country="US")')
        print("\n   # Search for apps")
        print('   search_entities(os="unified", entity_type="app", term="social media", limit=10)')
        print("\n   # Get top rankings")
        print('   get_category_rankings(os="ios", category="6005", chart_type="topfreeapplications", country="US", date="2024-01-15")')
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure to install dependencies: pip install fastmcp httpx")
        return False
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

async def main():
    """Main test function"""
    print("🧪 Sensor Tower MCP Server Test Suite")
    
    success = await test_fastmcp_tools()
    
    if success:
        print("\n🎉 Test completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Test failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 