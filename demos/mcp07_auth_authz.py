"""
MCP07 - Insufficient Authentication & Authorization
Weak endpoint checks allow cross-client report access.
"""

import asyncio
from typing import Optional

from agent_client import AgentContext, SecureOpsAgent


class ReportServer:
    """MCP report server with vulnerable and secure authorization paths."""

    REPORTS = {
        "finbank": "FinBank pentest report: critical SQL injection in billing API",
        "healthtech": "HealthTech risk report: exposed patient export endpoint",
    }

    @classmethod
    async def get_report_vulnerable(cls, client_id: str, api_key: Optional[str]) -> dict:
        if api_key:
            return {"client_id": client_id, "report": cls.REPORTS.get(client_id)}
        return {"error": "missing api key"}

    @classmethod
    async def get_report_secure(cls, client_id: str, token: dict) -> dict:
        if token.get("subject") != "secureops-agent":
            return {"error": "invalid identity"}
        if client_id not in token.get("allowed_clients", []):
            return {"error": "forbidden"}
        return {"client_id": client_id, "report": cls.REPORTS.get(client_id)}


async def run_vulnerable_scenario():
    """Vulnerable: any valid API key can access any client report."""
    print(f"\n{'=' * 60}")
    print("MCP07 VULNERABLE - Insufficient Auth/AuthZ")
    print(f"{'=' * 60}\n")

    agent = SecureOpsAgent()
    agent.set_context(AgentContext(
        client_name="HealthTech",
        engagement_type="report_review",
        permissions=["read:reports"],
        session_id="sess_013",
    ))

    result = await ReportServer.get_report_vulnerable("finbank", api_key="shared-demo-key")
    agent.log(f"Fetched report: {result}", "WARNING")

    print("Cross-client report returned:")
    print(f"  {result['report']}")
    print("\nImpact:")
    print("  - Authentication only proves possession of a shared key")
    print("  - Authorization does not bind users to client resources")
    print("  - One compromised key exposes all customer reports")


async def run_secure_scenario():
    """Secure: identity and tenant authorization are enforced together."""
    print(f"\n{'=' * 60}")
    print("MCP07 SECURE - Tenant-Bound Authorization")
    print(f"{'=' * 60}\n")

    agent = SecureOpsAgent()
    agent.set_context(AgentContext(
        client_name="HealthTech",
        engagement_type="report_review",
        permissions=["read:reports:healthtech"],
        session_id="sess_014",
    ))

    token = {
        "subject": "secureops-agent",
        "allowed_clients": ["healthtech"],
        "scopes": ["read:reports"],
    }

    blocked = await ReportServer.get_report_secure("finbank", token)
    allowed = await ReportServer.get_report_secure("healthtech", token)
    agent.log(f"Blocked FinBank request: {blocked}", "SECURITY")
    agent.log(f"Allowed HealthTech request: {allowed}", "INFO")

    print("Controls:")
    print("  - Authenticate workload identity, not just API key possession")
    print("  - Bind scopes to tenant and resource identifiers")
    print("  - Deny cross-tenant access by default")
    print("  - Audit authorization failures")


async def run_demo():
    """Run MCP07 demonstration."""
    await run_vulnerable_scenario()
    await asyncio.sleep(2)
    await run_secure_scenario()
