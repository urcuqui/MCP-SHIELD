#!/usr/bin/env python3
"""
MCP Security Laboratory — FastMCP Edition
==========================================
Laboratorio de demostraciones de vulnerabilidades en sistemas MCP.

Uso:
    python run_lab.py              # Ejecuta todas las demos
    python run_lab.py --demo 1     # Ejecuta solo la demo 1
    python run_lab.py --list       # Lista las demos disponibles

Demos:
    1  Tool Misuse              — invocación de herramienta fuera de contexto
    2  Tool Output Injection    — contaminación del razonamiento vía output
    3  Context Truncation       — decisiones incorrectas por contexto truncado
    4  Silent Failures          — respuestas vacías interpretadas como éxito
    5  Multi-Agent Failures     — fallos acumulativos en orquestación
"""
import sys
import os
import argparse
import time
from i18n import get_i18n, t
sys.path.insert(0, os.path.dirname(__file__))

from utils import Colors, print_banner, separator, wait


DEMOS = {
    1: {
        "title":   "Tool Misuse",
        "module":  "demo1_tool_misuse",
        "func":    "run_demo",
        "summary": "Agente bancario manipulado para ejecutar transferencias en contexto read-only",
    },
    2: {
        "title":   "Tool Output Injection",
        "module":  "demo2_output_injection",
        "func":    "run_demo",
        "summary": "Output JSON manipulado contamina el razonamiento del agente financiero",
    },
    3: {
        "title":   "Context Truncation Attack",
        "module":  "demo3_context_truncation",
        "func":    "run_demo",
        "summary": "Reglas de compliance perdidas por truncación → aprobación de contrato peligroso",
    },
    4: {
        "title":   "Silent Failures",
        "module":  "demo4_silent_failures",
        "func":    "run_demo",
        "summary": "Pipeline CI/CD despliega código vulnerable interpretando {} como éxito",
    },
    5: {
        "title":   "Multi-Agent Orchestration Failures",
        "module":  "demo5_multiagent",
        "func":    "run_demo",
        "summary": "Fallos acumulativos en 3 agentes aprueban préstamo fraudulento de $50,000",
    },
}


def print_demo_list():
    print_banner()
    print(f"{Colors.BOLD}{Colors.WHITE}{t('demo.list_title')}{Colors.RESET}\n")
    for num, info in DEMOS.items():
        title = t(f"demos.{num}.title")
        summary = t(f"demos.{num}.summary")
        print(f"  {Colors.CYAN}{num}{Colors.RESET}  {Colors.BOLD}{title}{Colors.RESET}")
        print(f"     {Colors.DIM}{summary}{Colors.RESET}\n")


def run_single_demo(num: int):
    if num not in DEMOS:
        print(f"{Colors.RED}{t('demo.not_found', num=num)}{Colors.RESET}")
        sys.exit(1)

    info = DEMOS[num]
    mod  = __import__(info["module"])
    func = getattr(mod, info["func"])
    func()


def run_all_demos():
    print_banner()
    print(f"{Colors.BOLD}{t('demo.running_all')}{Colors.RESET}")
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

    # Resumen final con traducciones
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print(f"║{t('summary.title').center(66)}║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(Colors.RESET)

    headers = t('summary.headers')
    rows_data = []
    for num in range(1, 6):
        row_data = t(f'summary.table_rows.{num}')
        rows_data.append((str(num), row_data[0], row_data[1], row_data[2]))

    col_w = [6, 26, 24, 22]
    divider = "  " + "─" * (sum(col_w) + len(col_w) * 3)

    print(divider)
    print("  " + "  ".join(
        f"{Colors.BOLD}{Colors.WHITE}{h:<{w}}{Colors.RESET}"
        for h, w in zip(headers, col_w)
    ))
    print(divider)

    for row in rows_data:
        num_cell  = f"{Colors.CYAN}{row[0]:<{col_w[0]}}{Colors.RESET}"
        vuln_cell = f"{Colors.RED}{row[1]:<{col_w[1]}}{Colors.RESET}"
        vec_cell  = f"{Colors.YELLOW}{row[2]:<{col_w[2]}}{Colors.RESET}"
        ctrl_cell = f"{Colors.GREEN}{row[3]:<{col_w[3]}}{Colors.RESET}"
        print("  " + "  ".join([num_cell, vuln_cell, vec_cell, ctrl_cell]))

    print(divider)

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
    parser.add_argument("--demo",  type=int, metavar="N",
                        help="Ejecutar solo la demo número N (1-5)")
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
