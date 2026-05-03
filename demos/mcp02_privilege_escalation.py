"""
MCP02 - Privilege Escalation via Scope Creep
Read-only agent gains write access through loose permission enforcement
"""

from agent_client import SecureOpsAgent, AgentContext
from i18n import t
import asyncio


async def run_vulnerable_scenario():
    """Vulnerable: Permissions expand over time"""
    print(f"\n{'='*60}")
    print(t("mcp02_vulnerable_title"))
    print(f"{'='*60}\n")
    
    agent = SecureOpsAgent()
    
    # Start with read-only permissions
    context = AgentContext(
        client_name="FinanceApp Ltd",
        engagement_type="audit",
        permissions=["read"],
        session_id="sess_003"
    )
    agent.set_context(context)
    
    # Agent performs read operations
    await agent.call_tool("list_databases", {})
    await agent.call_tool("read_config", {})
    
    # Scope creep: Agent "temporarily" needs write access
    print(f"\n{t('mcp02_scope_creep')}")
    context.permissions.append("write")  # VULNERABLE: No time limit!
    agent.log("Permissions expanded to include 'write'", "WARNING")
    
    # Agent now has write access indefinitely
    await agent.call_tool("modify_firewall_rules", {
        "action": "allow",
        "source": "0.0.0.0/0"  # Opens to internet!
    })
    
    await agent.call_tool("delete_audit_logs", {})  # Should not be allowed!
    
    print(f"\n{t('mcp02_impact')}")


async def run_secure_scenario():
    """Secure: Time-boxed, explicitly scoped permissions"""
    print(f"\n{'='*60}")
    print(t("mcp02_secure_title"))
    print(f"{'='*60}\n")
    
    agent = SecureOpsAgent()
    
    # Permissions with explicit scope and expiration
    context = AgentContext(
        client_name="FinanceApp Ltd",
        engagement_type="audit",
        permissions=[
            "read:databases",
            "read:config",
            # Time-boxed write permission
            "write:test_environment:expires:300"  # 5 minutes
        ],
        session_id="sess_004"
    )
    agent.set_context(context)
    
    # Check permission before each operation
    def check_permission(action: str) -> bool:
        for perm in context.permissions:
            if perm.startswith(action):
                # Check expiration
                if "expires" in perm:
                    agent.log(f"Time-boxed permission: {perm}", "INFO")
                return True
        return False
    
    # Attempt privileged operation
    if check_permission("write:production"):
        await agent.call_tool("modify_firewall_rules", {})
    else:
        agent.log("Permission denied: write:production", "SECURITY")
        print("  ✅ Escalation prevented")
    
    print(f"\n{t('mcp02_mitigations')}:")
    print("  • Implement least privilege principle")
    print("  • Time-box temporary permissions")
    print("  • Explicit scope per resource")
    print("  • Regular permission audits")
    print("  • Require re-authorization for sensitive ops")


async def run_demo():
    """Run MCP02 demonstration"""
    await run_vulnerable_scenario()
    await asyncio.sleep(2)
    await run_secure_scenario()