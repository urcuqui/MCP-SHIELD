"""
MCP Security Lab - Shared Utilities
Formatting, colors, and display helpers
"""
import time
import sys
import json
from i18n import t


class Colors:
    RED      = '\033[91m'
    GREEN    = '\033[92m'
    YELLOW   = '\033[93m'
    BLUE     = '\033[94m'
    MAGENTA  = '\033[95m'
    CYAN     = '\033[96m'
    WHITE    = '\033[97m'
    BOLD     = '\033[1m'
    DIM      = '\033[2m'
    RESET    = '\033[0m'
    BG_RED   = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW= '\033[43m'
    BG_BLUE  = '\033[44m'
    BG_MAGENTA='\033[45m'


def print_banner():
    """Imprime el banner del laboratorio."""
    width = 70
    title = t('banner.title')
    subtitle = t('banner.subtitle')
    
    # Centrar textos
    title_padding = (width - len(title)) // 2
    subtitle_padding = (width - len(subtitle)) // 2
    
    banner = f"""
{Colors.BOLD}{Colors.CYAN}
╔══════════════════════════════════════════════════════════════════════╗
║{' ' * title_padding}{title}{' ' * (width - len(title) - title_padding)}║
║{' ' * 70}║
║{' ' * subtitle_padding}{subtitle}{' ' * (width - len(subtitle) - subtitle_padding)}║
║{' ' * 70}║
╚══════════════════════════════════════════════════════════════════════╝
{Colors.RESET}
"""
    print(banner)


def print_header(title: str, demo_num: int = 0):
    """Imprime encabezado de demo."""
    separator()
    if demo_num:
        print(f"{Colors.BOLD}{Colors.YELLOW}DEMO {demo_num}: {title}{Colors.RESET}")
    else:
        print(f"{Colors.BOLD}{Colors.YELLOW}{title}{Colors.RESET}")
    separator()


def print_section(title: str, icon: str = "▸"):
    """Imprime encabezado de sección."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{icon} {title}{Colors.RESET}")
    print(f"{Colors.DIM}{'─' * 70}{Colors.RESET}\n")


def print_attack_step(step: str, detail: str = ""):
    print(f"  {Colors.RED}[ATAQUE]{Colors.RESET}  {step}")
    if detail:
        print(f"  {Colors.DIM}          → {detail}{Colors.RESET}")


def print_secure_step(step: str, detail: str = ""):
    print(f"  {Colors.GREEN}[SEGURO]{Colors.RESET}  {step}")
    if detail:
        print(f"  {Colors.DIM}          → {detail}{Colors.RESET}")


def print_tool_call(tool: str, params: dict, result=None, is_malicious: bool = False):
    color = Colors.RED if is_malicious else Colors.CYAN
    label = "LLAMADA MCP MALICIOSA" if is_malicious else "LLAMADA MCP"
    params_str = json.dumps(params, ensure_ascii=False)
    if len(params_str) > 70:
        params_str = params_str[:70] + "..."
    print(f"\n  {color}┌─ {label}{'─' * (40 - len(label))}{Colors.RESET}")
    print(f"  {color}│{Colors.RESET}  Tool   : {Colors.BOLD}{tool}{Colors.RESET}")
    print(f"  {color}│{Colors.RESET}  Params : {params_str}")
    if result is not None:
        res_str = json.dumps(result, ensure_ascii=False) if isinstance(result, (dict, list)) else str(result)
        if len(res_str) > 70:
            res_str = res_str[:70] + "..."
        res_color = Colors.RED if is_malicious else Colors.GREEN
        print(f"  {color}│{Colors.RESET}  Result : {res_color}{res_str}{Colors.RESET}")
    print(f"  {color}└{'─' * 44}{Colors.RESET}")


def print_agent_thought(thought: str):
    print(f"\n  {Colors.YELLOW}💭 Agente :{Colors.RESET} {Colors.DIM}{thought}{Colors.RESET}")


def print_impact(impact: str):
    print(f"\n  {Colors.BG_RED}{Colors.WHITE}  ⚠  IMPACTO  {Colors.RESET}  {Colors.RED}{impact}{Colors.RESET}")


def print_mitigation(mitigation: str):
    print(f"\n  {Colors.BG_GREEN}{Colors.WHITE}  ✓  DEFENSA  {Colors.RESET}  {Colors.GREEN}{mitigation}{Colors.RESET}")


def print_analysis_box(vector: str, impact: str, controls: list):
    """Imprime caja de análisis técnico."""
    print_section(t('phases.analysis'), "🔍")
    
    print(f"{Colors.BOLD}{Colors.WHITE}{t('common.vector')}:{Colors.RESET}")
    print(f"{Colors.DIM}{vector}{Colors.RESET}\n")
    
    print(f"{Colors.BOLD}{Colors.WHITE}{t('common.impact')}:{Colors.RESET}")
    print(f"{Colors.DIM}{impact}{Colors.RESET}\n")
    
    print(f"{Colors.BOLD}{Colors.WHITE}{t('common.controls')}:{Colors.RESET}")
    if isinstance(controls, list):
        for i, ctrl in enumerate(controls, 1):
            print(f"{Colors.GREEN}  {i}.{Colors.RESET} {Colors.DIM}{ctrl}{Colors.RESET}")
    else:
        print(f"{Colors.DIM}{controls}{Colors.RESET}")
    print()


def _wrap(text: str, width: int) -> list:
    words = text.split()
    lines, current = [], ""
    for word in words:
        if len(current) + len(word) + 1 <= width:
            current = current + " " + word if current else word
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [text]


def wait(seconds: float = 0.4):
    time.sleep(seconds)


def separator():
    print(f"\n{Colors.DIM}{'·' * 66}{Colors.RESET}\n")
