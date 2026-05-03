"""
MCP08 - Lack of Audit and Telemetry
Critical tool invocations cannot be reconstructed after an incident.
"""

import asyncio

from agent_client import AgentContext, SecureOpsAgent


class AuditLog:
    """Small telemetry collector for the secure scenario."""

    def __init__(self):
        self.events: list[dict] = []

    def record(self, event: dict):
        self.events.append(event)


async def delete_security_group(rule_id: str) -> dict:
    return {"status": "deleted", "rule_id": rule_id}


async def run_vulnerable_scenario():
    """Vulnerable: critical action has no durable audit trail."""
    print(f"\n{'=' * 60}")
    print("MCP08 VULNERABLE - Lack of Audit and Telemetry")
    print(f"{'=' * 60}\n")

    agent = SecureOpsAgent()
    agent.set_context(AgentContext(
        client_name="RetailChain",
        engagement_type="incident_response",
        permissions=["network:write"],
        session_id="sess_015",
    ))

    result = await delete_security_group("prod-ingress-deny-all")
    print(f"Critical operation result: {result}")
    print("Telemetry available after incident: []")
    print("\nImpact:")
    print("  - No actor, session, input, or approval record")
    print("  - Incident responders cannot prove what happened")
    print("  - Detection rules have no signal to alert on")


async def run_secure_scenario():
    """Secure: every privileged tool call emits structured telemetry."""
    print(f"\n{'=' * 60}")
    print("MCP08 SECURE - Structured Audit Trail")
    print(f"{'=' * 60}\n")

    audit = AuditLog()
    agent = SecureOpsAgent()
    context = AgentContext(
        client_name="RetailChain",
        engagement_type="incident_response",
        permissions=["network:write"],
        session_id="sess_016",
    )
    agent.set_context(context)

    event = {
        "session_id": context.session_id,
        "client": context.client_name,
        "tool": "delete_security_group",
        "params": {"rule_id": "prod-ingress-deny-all"},
        "approval_id": "CHG-2026-0142",
    }
    audit.record({**event, "phase": "before"})
    result = await delete_security_group("prod-ingress-deny-all")
    audit.record({**event, "phase": "after", "result": result})

    print("Telemetry emitted:")
    for item in audit.events:
        print(f"  {item}")

    print("\nControls:")
    print("  - Log before and after privileged tool calls")
    print("  - Include session, actor, tenant, parameters, and approval ID")
    print("  - Send audit events to append-only storage")
    print("  - Alert on risky tools and missing telemetry")


async def run_demo():
    """Run MCP08 demonstration."""
    await run_vulnerable_scenario()
    await asyncio.sleep(2)
    await run_secure_scenario()
