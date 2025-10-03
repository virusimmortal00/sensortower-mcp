#!/usr/bin/env python3
"""Manual MCP protocol smoke test for the search_entities tool."""

import asyncio
import json
import os
import subprocess
import sys

from dotenv import load_dotenv

load_dotenv()


async def verify_search_entities_via_mcp(token: str) -> bool:
    process = subprocess.Popen(
        ["sensortower-mcp", "--transport", "stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, "SENSOR_TOWER_API_TOKEN": token},
    )

    await asyncio.sleep(2)
    if process.poll() is not None:
        stdout, stderr = process.communicate()
        print("❌ MCP server failed to start")
        print(stderr)
        return False

    assert process.stdin and process.stdout

    def send(payload: dict) -> None:
        process.stdin.write(json.dumps(payload) + "\n")
        process.stdin.flush()

    send(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "manual-smoke", "version": "1.0"},
            },
        }
    )
    send({"jsonrpc": "2.0", "method": "notifications/initialized"})
    send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    await asyncio.sleep(1)
    send(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "search_entities",
                "arguments": {
                    "os": "ios",
                    "entity_type": "app",
                    "term": "iPhone",
                    "limit": 1,
                },
            },
        }
    )

    await asyncio.sleep(3)
    success = False
    for _ in range(20):
        line = process.stdout.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        try:
            response = json.loads(line)
        except json.JSONDecodeError:
            continue
        if response.get("id") == 3:
            result = response.get("result", {})
            content = result.get("content", [])
            if content:
                text_block = content[0].get("text", "")
                print("🔍 search_entities response:")
                print(text_block[:500])
                success = "\"apps\"" in text_block
            break

    process.terminate()
    await asyncio.sleep(1)
    if process.poll() is None:
        process.kill()

    return success


def main() -> int:
    print("🎯 search_entities MCP Protocol Smoke Test")
    print("=" * 60)

    token = os.getenv("SENSOR_TOWER_API_TOKEN")
    if not token:
        print("⚠️  SENSOR_TOWER_API_TOKEN not configured; skipping MCP smoke test")
        return 0

    try:
        success = asyncio.run(verify_search_entities_via_mcp(token))
    except Exception as exc:  # pragma: no cover - manual script
        print(f"❌ MCP smoke test exception: {exc}")
        return 1

    if success:
        print("\n🎉 MCP smoke test succeeded")
        return 0

    print("\n⚠️  MCP smoke test did not detect expected 'apps' payload")
    return 1


if __name__ == "__main__":
    sys.exit(main())
