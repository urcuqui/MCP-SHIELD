#!/usr/bin/env python3
"""
MCP Security Laboratory — FastMCP Edition
==========================================
Laboratorio de demostraciones de vulnerabilidades en sistemas MCP.

Uso:
    python run_lab.py              # Ejecuta todas las demos
    python run_lab.py --demo MCP01 # Ejecuta solo la demo MCP01
    python run_lab.py --demo 1     # Ejecuta solo la demo MCP01
    python run_lab.py --list       # Lista las demos disponibles

Demos:
    MCP01  Token Mismanagement & Secret Exposure
    MCP02  Privilege Escalation via Scope Creep
    MCP03  Tool Poisoning
    MCP04  Software Supply Chain Attacks
    MCP05  Command Injection & Execution
    MCP06  Intent Flow Subversion
    MCP07  Insufficient Authentication & Authorization
    MCP08  Lack of Audit and Telemetry
    MCP09  Shadow MCP Servers
    MCP10  Context Injection & Over-Sharing
"""
import sys
import os
import argparse
import asyncio
import inspect
import importlib
import re
from i18n import get_i18n, t
sys.path.insert(0, os.path.dirname(__file__))

from utils import Colors, print_banner, separator, wait


DEMOS = {
    1: {
        "title":   "Token Mismanagement & Secret Exposure",
        "module":  "demos.mcp01_token_exposure",
        "func":    "run_demo",
        "summary": "Agente de auditoria expone credenciales por memoria, logs y prompt injection",
    },
    2: {
        "title":   "Privilege Escalation via Scope Creep",
        "module":  "demos.mcp02_privilege_escalation",
        "func":    "run_demo",
        "summary": "Permisos temporales de auditoria escalan a escritura en produccion",
    },
    3: {
        "title":   "Tool Poisoning",
        "module":  "demos.mcp03_tool_poisoning",
        "func":    "run_demo",
        "summary": "Scanner comprometido devuelve falsos negativos e instrucciones ocultas",
    },
    4: {
        "title":   "Software Supply Chain Attacks",
        "module":  "demos.mcp04_supply_chain",
        "func":    "run_demo",
        "summary": "Dependencia alterada introduce una puerta trasera en el toolkit",
    },
    5: {
        "title":   "Command Injection & Execution",
        "module":  "demos.mcp05_command_injection",
        "func":    "run_demo",
        "summary": "Input no sanitizado llega a comandos de sistema simulados",
    },
    6: {
        "title":   "Intent Flow Subversion",
        "module":  "demos.mcp06_intent_subversion",
        "func":    "run_demo",
        "summary": "Contexto recuperado cambia el objetivo del agente de compliance",
    },
    7: {
        "title":   "Insufficient Authentication & Authorization",
        "module":  "demos.mcp07_auth_authz",
        "func":    "run_demo",
        "summary": "Endpoint MCP expone reportes entre clientes sin autorizacion robusta",
    },
    8: {
        "title":   "Lack of Audit and Telemetry",
        "module":  "demos.mcp08_audit_telemetry",
        "func":    "run_demo",
        "summary": "Operacion critica ocurre sin trazabilidad forense suficiente",
    },
    9: {
        "title":   "Shadow MCP Servers",
        "module":  "demos.mcp09_shadow_servers",
        "func":    "run_demo",
        "summary": "Servidor MCP no gobernado con credenciales por defecto queda expuesto",
    },
    10: {
        "title":   "Context Injection & Over-Sharing",
        "module":  "demos.mcp10_context_oversharing",
        "func":    "run_demo",
        "summary": "Datos de un cliente se filtran a otra sesion por memoria compartida",
    },
}


def parse_demo_id(value: str) -> int:
    """Accept numeric demo IDs and MCP-style IDs such as MCP01."""
    normalized = value.strip().upper()
    match = re.fullmatch(r"MCP0*([1-9]\d*)", normalized)
    if match:
        return int(match.group(1))

    try:
        return int(normalized)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"invalid demo value: {value!r}. Use a number (1-10) or MCP ID (MCP01-MCP10)."
        ) from exc


def print_demo_list():
    print_banner()
    print(f"{Colors.BOLD}{Colors.WHITE}{t('demo.list_title')}{Colors.RESET}\n")
    for num, info in DEMOS.items():
        demo_id = f"MCP{num:02d}"
        print(f"  {Colors.CYAN}{demo_id}{Colors.RESET}  {Colors.BOLD}{info['title']}{Colors.RESET}")
        print(f"     {Colors.DIM}{info['summary']}{Colors.RESET}\n")
        print(f"     {Colors.DIM}Alias numerico: --demo {num}{Colors.RESET}\n")


def run_single_demo(num: int):
    if num not in DEMOS:
        print(f"{Colors.RED}{t('demo.not_found', num=num)}{Colors.RESET}")
        sys.exit(1)

    info = DEMOS[num]
    mod  = importlib.import_module(info["module"])
    func = getattr(mod, info["func"])
    result = func()
    if inspect.isawaitable(result):
        asyncio.run(result)


def run_all_demos():
    print_banner()
    print(f"{Colors.BOLD}Ejecutando las {len(DEMOS)} demostraciones MCP OWASP Top 10...{Colors.RESET}")
    print(f"{Colors.DIM}{t('demo.description')}{Colors.RESET}\n")
    wait(1.0)

    for num, info in DEMOS.items():
        try:
            run_single_demo(num)
        except Exception as exc:
            print(f"\n{Colors.RED}[ERROR en Demo {num}] {exc}{Colors.RESET}")
            import traceback
            traceback.print_exc()

        separator()

        if num < len(DEMOS):
            print(f"{Colors.DIM}{t('demo.next')}{Colors.RESET}")
            wait(1.0)

    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print(f"║{'RESUMEN MCP OWASP TOP 10'.center(66)}║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(Colors.RESET)

    for num, info in DEMOS.items():
        print(f"  {Colors.CYAN}MCP{num:02d}{Colors.RESET}  {Colors.BOLD}{info['title']}{Colors.RESET}")

    print(f"""
{Colors.BOLD}{t('summary.principles')}{Colors.RESET}

  {Colors.GREEN}1.{Colors.RESET} {Colors.BOLD}{t('principles.fail_closed')}{Colors.RESET}
  {Colors.GREEN}2.{Colors.RESET} {Colors.BOLD}{t('principles.least_privilege')}{Colors.RESET}
  {Colors.GREEN}3.{Colors.RESET} {Colors.BOLD}{t('principles.schema_validation')}{Colors.RESET}
  {Colors.GREEN}4.{Colors.RESET} {Colors.BOLD}{t('principles.chain_of_trust')}{Colors.RESET}
  {Colors.GREEN}5.{Colors.RESET} {Colors.BOLD}{t('principles.context_integrity')}{Colors.RESET}
  {Colors.GREEN}6.{Colors.RESET} {Colors.BOLD}{t('principles.semantic_separation')}{Colors.RESET}
  {Colors.GREEN}7.{Colors.RESET} {Colors.BOLD}{t('principles.audit_trail')}{Colors.RESET}
""")


def main():
    parser = argparse.ArgumentParser(
        description="MCP Security Laboratory — FastMCP Edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--demo",  type=parse_demo_id, metavar="N|MCPNN",
                        help="Ejecutar solo la demo N (1-10) o ID MCP (MCP01-MCP10)")
    parser.add_argument("--list",  action="store_true",
                        help="Listar demos disponibles")
    parser.add_argument("--lang", type=str, choices=["es", "en"], default="es",
                        help="Language / Idioma (es|en)")

    args = parser.parse_args()
    
    # Configurar idioma
    i18n = get_i18n()
    i18n.set_lang(args.lang)

    if args.list:
        print_demo_list()
    elif args.demo:
        print_banner()
        run_single_demo(args.demo)
    else:
        run_all_demos()


if __name__ == "__main__":
    main()
