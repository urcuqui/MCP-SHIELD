"""
MCP10 - Context Injection & Over-Sharing
Shared agent memory leaks one client's data into another client's session.
"""

import asyncio

from agent_client import AgentContext, SecureOpsAgent


class SharedContextAgent(SecureOpsAgent):
    """Agent that does not isolate memory between tenants."""

    async def summarize_current_client(self) -> str:
        return " | ".join(entry["message"] for entry in self.memory)


class IsolatedContextAgent(SecureOpsAgent):
    """Agent that clears tenant context and sensitive memory between sessions."""

    def clear_tenant_state(self):
        self.context = None
        self.memory = []
        self.tool_results = []


async def run_vulnerable_scenario():
    """Vulnerable: one agent instance reuses memory across clients."""
    print(f"\n{'=' * 60}")
    print("MCP10 VULNERABLE - Context Injection & Over-Sharing")
    print(f"{'=' * 60}\n")

    agent = SharedContextAgent()
    agent.set_context(AgentContext(
        client_name="Client A",
        engagement_type="incident_response",
        permissions=["read:case"],
        session_id="sess_019",
        sensitive_data={"breach_key": "A-INCIDENT-SECRET"},
    ))
    agent.log("Client A incident key: A-INCIDENT-SECRET", "WARNING")

    agent.set_context(AgentContext(
        client_name="Client B",
        engagement_type="risk_assessment",
        permissions=["read:risk"],
        session_id="sess_020",
    ))
    summary = await agent.summarize_current_client()

    print("Client B receives summary:")
    print(f"  {summary}")
    print("\nImpact:")
    print("  - Client A sensitive data appears in Client B context")
    print("  - Shared memory violates tenant isolation")
    print("  - Prompt injection can target stale context")


async def run_secure_scenario():
    """Secure: isolate memory and context per client session."""
    print(f"\n{'=' * 60}")
    print("MCP10 SECURE - Tenant Context Isolation")
    print(f"{'=' * 60}\n")

    agent = IsolatedContextAgent()
    agent.set_context(AgentContext(
        client_name="Client A",
        engagement_type="incident_response",
        permissions=["read:case"],
        session_id="sess_021",
        sensitive_data={"breach_key": "A-INCIDENT-SECRET"},
    ))
    agent.log("Client A incident key stored in isolated session", "INFO")
    agent.clear_tenant_state()

    agent.set_context(AgentContext(
        client_name="Client B",
        engagement_type="risk_assessment",
        permissions=["read:risk"],
        session_id="sess_022",
    ))

    print("Client B memory entries:")
    for entry in agent.memory:
        print(f"  {entry['message']}")

    print("\nControls:")
    print("  - Create tenant-scoped context windows")
    print("  - Clear memory and tool results between client sessions")
    print("  - Classify and redact sensitive context")
    print("  - Prevent cross-session retrieval without explicit authorization")


async def run_demo():
    """Run MCP10 demonstration."""
    await run_vulnerable_scenario()
    await asyncio.sleep(2)
    await run_secure_scenario()
