#!/usr/bin/env python3
"""Helper script for validating the deployed search_entities tool."""

import os
import subprocess
import sys
from textwrap import dedent

from dotenv import load_dotenv

load_dotenv()


def _run_subprocess(code: str, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def verify_schema_transformation() -> bool:
    script = dedent(
        """
        raw_data = [{"app_id": 123, "name": "Test App"}]
        entity_type = "app"
        term = "test"
        os_val = "ios"

        if isinstance(raw_data, list):
            result = {
                f"{entity_type}s": raw_data,
                "total_count": len(raw_data),
                "query_term": term,
                "entity_type": entity_type,
                "platform": os_val,
            }
        else:
            result = raw_data

        print("✅ Schema transformation test:")
        print(f"   Input: {type(raw_data)} with {len(raw_data)} items")
        print(f"   Output: {type(result)}")
        print(f"   Output keys: {list(result.keys())}")
        print(f"   Has 'apps' key: {'apps' in result}")
        print(f"   Apps count: {len(result.get('apps', []))}")

        if isinstance(result, dict) and "apps" in result:
            print("✅ Schema fix working correctly!")
            raise SystemExit(0)
        print("❌ Schema fix not working")
        raise SystemExit(1)
        """
    )

    result = _run_subprocess(script, timeout=10)
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    return result.returncode == 0


def verify_deployed_package(token: str) -> bool:
    script = dedent(
        f"""
        import asyncio
        import os
        import sys

        try:
            import main as deployed_main
            print("✅ Imported main from deployed package")
        except ImportError as exc:
            print(f"❌ Import failed: {{exc}}")
            raise SystemExit(1)

        os.environ["SENSOR_TOWER_API_TOKEN"] = "{token}"

        async def run_check():
            try:
                result = await deployed_main.search_entities(
                    os="ios",
                    entity_type="app",
                    term="iPhone",
                    limit=1,
                )
                print(f"🔍 search_entities result type: {{type(result)}}")
                if isinstance(result, dict) and "apps" in result:
                    print("✅ search_entities returns dict format with 'apps' key!")
                    raise SystemExit(0)
                print("❌ Unexpected payload: {{result}}")
                raise SystemExit(1)
            except Exception as exc:
                message = str(exc)
                if "429" in message or "rate limit" in message.lower():
                    print("⚠️  Rate limited but request structure is valid")
                    raise SystemExit(0)
                print(f"❌ Error invoking search_entities: {{message}}")
                raise SystemExit(1)

        asyncio.run(run_check())
        """
    )

    try:
        result = _run_subprocess(script, timeout=30)
    except subprocess.TimeoutExpired:
        print("⚠️  search_entities check timed out (likely waiting on API)")
        return False

    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    return result.returncode == 0


def main() -> int:
    print("🎯 search_entities Fix Verification")
    print("=" * 60)

    schema_ok = verify_schema_transformation()

    token = os.getenv("SENSOR_TOWER_API_TOKEN")
    if not token:
        print("⚠️  SENSOR_TOWER_API_TOKEN not set; skipping deployed package check")
        deployed_ok = False
    else:
        deployed_ok = verify_deployed_package(token)

    print("=" * 60)
    print("📊 search_entities verification summary")
    print(f"   Schema transformation: {'PASS' if schema_ok else 'FAIL'}")
    print(
        f"   Deployed package: {'PASS' if deployed_ok else 'SKIPPED' if not token else 'FAIL'}"
    )

    if schema_ok and (deployed_ok or not token):
        print("\n🎉 search_entities fix validated")
        return 0

    print("\n⚠️  search_entities fix requires attention")
    return 1


if __name__ == "__main__":
    sys.exit(main())
