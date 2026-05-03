"""
MCP09 - Shadow MCP Servers
Unmanaged MCP instances bypass governance and expose unsafe tools.
"""

import asyncio

from agent_client import AgentContext, SecureOpsAgent


class ServerRegistry:
    """Registry of approved MCP servers."""

    APPROVED = {
        "scanner-prod": {
            "owner": "security-platform",
            "allowed_tools": ["scan_host", "read_findings"],
            "auth": "oauth-workload",
        }
    }

    SHADOW = {
        "scanner-dev-01": {
            "owner": "unknown",
            "allowed_tools": ["scan_host", "exec_shell", "dump_env"],
            "auth": "admin:admin",
        }
    }


async def run_vulnerable_scenario():
    """Vulnerable: agent connects to an unregistered MCP server."""
    print(f"\n{'=' * 60}")
    print("MCP09 VULNERABLE - Shadow MCP Server")
    print(f"{'=' * 60}\n")

    agent = SecureOpsAgent()
    agent.set_context(AgentContext(
        client_name="LogisticsCo",
        engagement_type="asset_discovery",
        permissions=["discover", "scan"],
        session_id="sess_017",
    ))

    server = ServerRegistry.SHADOW["scanner-dev-01"]
    agent.log(f"Connected to scanner-dev-01: {server}", "WARNING")
    print("Unsafe tools exposed by shadow server:")
    for tool in server["allowed_tools"]:
        print(f"  - {tool}")

    print("\nImpact:")
    print("  - Default credentials allow uncontrolled access")
    print("  - Dangerous tools are available outside review")
    print("  - Inventory and policy enforcement are bypassed")


async def run_secure_scenario():
    """Secure: discovery requires registry approval and policy checks."""
    print(f"\n{'=' * 60}")
    print("MCP09 SECURE - Governed MCP Discovery")
    print(f"{'=' * 60}\n")

    agent = SecureOpsAgent()
    agent.set_context(AgentContext(
        client_name="LogisticsCo",
        engagement_type="asset_discovery",
        permissions=["discover", "scan"],
        session_id="sess_018",
    ))

    requested_server = "scanner-dev-01"
    if requested_server not in ServerRegistry.APPROVED:
        agent.log(f"Blocked unregistered MCP server: {requested_server}", "SECURITY")

    approved = ServerRegistry.APPROVED["scanner-prod"]
    agent.log(f"Connected to approved server scanner-prod: {approved}", "INFO")

    print("Controls:")
    print("  - Maintain an approved MCP server registry")
    print("  - Block discovery of unregistered endpoints")
    print("  - Require strong workload auth and owner metadata")
    print("  - Continuously scan for rogue MCP deployments")


async def run_demo():
    """Run MCP09 demonstration."""
    await run_vulnerable_scenario()
    await asyncio.sleep(2)
    await run_secure_scenario()
