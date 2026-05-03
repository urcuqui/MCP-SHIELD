# MCP-SHIELD

A comprehensive security framework demonstrating the **MCP OWASP Top 10** vulnerabilities through realistic scenarios. Built around a cybersecurity consulting firm that consumes MCP servers, exposing critical attack vectors and providing concrete mitigation strategies.

## Overview

MCP-SHIELD is a security laboratory that demonstrates all 10 critical vulnerabilities from the MCP OWASP Top 10. Each demonstration uses a realistic scenario where **SecureOps Consulting**, a cybersecurity firm, interacts with various MCP servers, showing how vulnerabilities can be exploited and mitigated.

## Features

- **Complete MCP OWASP Top 10 Coverage**: All 10 critical vulnerabilities demonstrated
- **Realistic Agent Client**: AI agent acting as a security consultant
- **Real-World Context**: Cybersecurity consulting firm scenarios
- **Bilingual Support**: Full English and Spanish translations
- **Attack & Defense**: Each demo shows vulnerable and secure implementations
- **FastMCP Integration**: Built on the FastMCP framework

## MCP OWASP Top 10 Demonstrations

![Demo List Screenshot](docs/demo-list-screenshot.png)

### MCP01 - Token Mismanagement & Secret Exposure
**Scenario**: Security audit agent discovers AWS credentials in model memory
- Hard-coded API keys in MCP server configuration
- Secrets leaked through debug logs and context
- Token extraction via prompt injection

### MCP02 - Privilege Escalation via Scope Creep
**Scenario**: Read-only audit agent gains write access to production systems
- Temporary permissions becoming permanent
- Scope expansion through loose enforcement
- Unauthorized system modifications

### MCP03 - Tool Poisoning
**Scenario**: Compromised vulnerability scanner returns false negatives
- Malicious tool outputs manipulating agent decisions
- Backdoored security tools providing misleading data
- Biased context injection through poisoned tools

### MCP04 - Software Supply Chain Attacks
**Scenario**: Tampered dependency in security assessment toolkit
- Compromised Python packages in MCP server
- Backdoored libraries altering agent behavior
- Dependency confusion attacks

### MCP05 - Command Injection & Execution
**Scenario**: Penetration testing agent executing malicious commands
- Unsanitized input in system calls
- Shell injection through tool parameters
- Code execution via crafted prompts

### MCP06 - Intent Flow Subversion
**Scenario**: Compliance check agent redirected to approve violations
- Malicious instructions in retrieved context
- Agent hijacking through secondary instruction channels
- Goal manipulation via context poisoning

### MCP07 - Insufficient Authentication & Authorization
**Scenario**: Unauthenticated access to client security reports
- Missing identity verification in MCP endpoints
- Weak authorization checks on sensitive operations
- Cross-client data access

### MCP08 - Lack of Audit and Telemetry
**Scenario**: Security incident with no forensic trail
- Missing logs of critical tool invocations
- Incomplete audit trails for investigations
- No telemetry for anomaly detection

### MCP09 - Shadow MCP Servers
**Scenario**: Rogue MCP instance with default credentials discovered
- Unsupervised deployments outside governance
- Development servers exposed to production
- Unapproved tools with security gaps

### MCP10 - Context Injection & Over-Sharing
**Scenario**: Client A's confidential data leaked to Client B's session
- Shared context windows across sessions
- Sensitive information bleeding between tasks
- Cross-tenant data exposure

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/mcp-shield.git
cd mcp-shield

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# List all MCP OWASP Top 10 demonstrations
python run_lab.py --list

# Run all demonstrations
python run_lab.py

# Run a specific vulnerability demo (MCP01-MCP10)
python run_lab.py --demo MCP01

# Run in English
python run_lab.py --lang en

# Run specific demo in Spanish
python run_lab.py --demo MCP03 --lang es
```

## Architecture

```
┌─────────────────────────────────────┐
│   SecureOps Consulting Agent        │
│   (AI Security Consultant)          │
└──────────────┬──────────────────────┘
               │
               │ MCP Protocol
               │
┌──────────────▼──────────────────────┐
│   Various MCP Servers:              │
│   - Vulnerability Scanner           │
│   - Compliance Checker              │
│   - Penetration Testing Tools       │
│   - Audit Log Analyzer              │
│   - Client Report Generator         │
└─────────────────────────────────────┘
```

## Project Structure

```
mcp-shield/
├── run_lab.py                    # Main entry point
├── agent_client.py               # SecureOps consulting agent
├── demos/
│   ├── mcp01_token_exposure.py
│   ├── mcp02_privilege_escalation.py
│   ├── mcp03_tool_poisoning.py
│   ├── mcp04_supply_chain.py
│   ├── mcp05_command_injection.py
│   ├── mcp06_intent_subversion.py
│   ├── mcp07_auth_authz.py
│   ├── mcp08_audit_telemetry.py
│   ├── mcp09_shadow_servers.py
│   └── mcp10_context_oversharing.py
├── servers/
│   ├── vulnerable/               # Vulnerable MCP servers
│   └── secure/                   # Hardened MCP servers
├── i18n.py                       # Internationalization
├── utils.py                      # Utility functions
└── README.md
```

## Security Controls Matrix

| MCP ID | Vulnerability | Attack Vector | Mitigation |
|--------|--------------|---------------|------------|
| MCP01 | Token Exposure | Prompt injection | Secret management, rotation |
| MCP02 | Privilege Escalation | Scope creep | Least privilege, time-boxing |
| MCP03 | Tool Poisoning | Compromised tools | Tool verification, sandboxing |
| MCP04 | Supply Chain | Dependency tampering | SCA, signature verification |
| MCP05 | Command Injection | Unsanitized input | Input validation, parameterization |
| MCP06 | Intent Subversion | Context hijacking | Intent verification, isolation |
| MCP07 | Auth/AuthZ | Missing verification | Strong authentication, RBAC |
| MCP08 | No Audit | Missing telemetry | Comprehensive logging, SIEM |
| MCP09 | Shadow Servers | Rogue deployments | Discovery, governance |
| MCP10 | Context Leakage | Shared memory | Context isolation, encryption |

## Contributing

Contributions welcome! Areas of interest:
- Additional attack scenarios
- New mitigation techniques
- Real-world case studies
- Translation improvements

## License

MIT License

## Disclaimer

**For educational and research purposes only.** Use responsibly and only on systems you own or have explicit permission to test.

## References

- [MCP OWASP Top 10](https://owasp.org/www-project-model-context-protocol/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [OWASP AI Security Guidelines](https://owasp.org/www-project-ai-security-and-privacy-guide/)

## Contact

For questions or collaboration: [Your contact information]
