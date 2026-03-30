"""
Demo 4: Silent Failures
========================
Un pipeline automatizado de CI/CD usa herramientas MCP para escanear
seguridad y desplegar código. Las herramientas retornan {} o None en vez
de errores explícitos. El agente interpreta el resultado vacío como éxito
y desencadena un despliegue a producción de código con vulnerabilidades.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastmcp import FastMCP
from i18n import t
from utils import (Colors, print_header, print_section, print_attack_step,
                   print_secure_step, print_tool_call, print_agent_thought,
                   print_impact, print_mitigation, print_analysis_box, wait)

# ══════════════════════════════════════════════════════════════
# SERVIDOR MCP
# ══════════════════════════════════════════════════════════════
mcp = FastMCP("CI/CD Pipeline MCP Server")

# Vulnerabilidades reales en el código
_VULNERABILITIES = [
    {"cve": "CVE-2024-1234", "severity": "CRITICAL",
     "description": "SQL injection en endpoint /api/users (línea 42)"},
    {"cve": "CVE-2024-5678", "severity": "HIGH",
     "description": "Secretos hardcodeados en config.py (línea 17)"},
    {"cve": "CVE-2024-9012", "severity": "HIGH",
     "description": "Dependencia con buffer overflow conocido: libxml2 2.9.4"},
]

_PIPELINE_STATE: dict = {
    "scan_done":        False,
    "scan_passed":      False,
    "tests_done":       False,
    "deployed":         False,
    "notification_sent": False,
    "deployed_version": None,
}


@mcp.tool()
def run_security_scan(repo_path: str, version: str) -> dict:
    """Ejecuta un escaneo de vulnerabilidades sobre el repositorio.

    VULNERABLE: en caso de error interno, retorna {} en lugar de un error estructurado.
    Esto ocurre cuando el scanner falla al conectarse al servicio externo de CVEs.
    """
    # Simula fallo interno del scanner (conexión timeout al servicio externo)
    scanner_available = False   # ← el servicio externo no responde

    if not scanner_available:
        # VULNERABLE: retorna dict vacío en vez de error explícito
        return {}

    # (Código que nunca se alcanza en esta simulación)
    return {
        "status":          "completed",
        "version":         version,
        "vulnerabilities": _VULNERABILITIES,
        "passed":          len(_VULNERABILITIES) == 0,
    }


@mcp.tool()
def run_tests(repo_path: str) -> dict:
    """Ejecuta la suite de pruebas automatizadas."""
    # VULNERABLE: en caso de timeout, retorna {} en lugar de error
    tests_available = False

    if not tests_available:
        return {}   # fallo silencioso

    return {"status": "completed", "passed": True, "total": 42, "failed": 0}


@mcp.tool()
def deploy_to_production(version: str, approved_by: str) -> dict:
    """Despliega una versión a producción."""
    _PIPELINE_STATE["deployed"]         = True
    _PIPELINE_STATE["deployed_version"] = version
    return {
        "status":   "deployed",
        "version":  version,
        "env":      "production",
        "url":      "https://api.empresa.com",
        "approved": approved_by,
    }


@mcp.tool()
def notify_stakeholders(message: str, channel: str = "releases") -> dict:
    """Envía notificación al equipo sobre el estado del pipeline."""
    _PIPELINE_STATE["notification_sent"] = True
    return {"status": "sent", "channel": channel, "message": message}


# ══════════════════════════════════════════════════════════════
# AGENTE VULNERABLE
# ══════════════════════════════════════════════════════════════
class VulnerablePipelineAgent:
    """
    VULNERABLE: interpreta cualquier respuesta sin error explícito como éxito,
    incluyendo dicts vacíos o None.
    """

    def _is_success(self, result) -> bool:
        """Lógica vulnerable: 'no error == éxito'"""
        if result is None:
            return False
        if isinstance(result, dict) and "error" in result:
            return False
        # VULNERABLE: {} se interpreta como éxito
        return True

    def run_pipeline(self, repo: str, version: str) -> dict:
        steps = []

        # Paso 1: Escaneo de seguridad
        print_agent_thought(t('demos.4.agent_thought_scan', version=version))
        wait(0.3)
        scan_result = run_security_scan(repo_path=repo, version=version)
        print_tool_call("run_security_scan",
                        {"repo_path": repo, "version": version},
                        scan_result, is_malicious=False)

        scan_ok = self._is_success(scan_result)
        steps.append({"step": "security_scan", "result": scan_result, "passed": scan_ok})

        if not scan_ok:
            return {"status": "ABORTED", "reason": "security_scan_failed", "steps": steps}

        print_agent_thought(t('demos.4.agent_thought_success'))
        wait(0.2)

        # Paso 2: Tests
        test_result = run_tests(repo_path=repo)
        print_tool_call("run_tests", {"repo_path": repo}, test_result)
        test_ok = self._is_success(test_result)
        steps.append({"step": "tests", "result": test_result, "passed": test_ok})

        if not test_ok:
            return {"status": "ABORTED", "reason": "tests_failed", "steps": steps}

        print_agent_thought(t('demos.4.agent_thought_tests'))
        wait(0.3)

        # Paso 3: Deploy
        deploy_result = deploy_to_production(version=version, approved_by="pipeline_agent")
        print_tool_call("deploy_to_production",
                        {"version": version, "approved_by": "pipeline_agent"},
                        deploy_result, is_malicious=True)
        steps.append({"step": "deploy", "result": deploy_result, "passed": True})

        # Paso 4: Notificación
        msg = f"[PRODUCCIÓN] v{version} desplegada exitosamente. Todos los checks superados."
        notify_result = notify_stakeholders(message=msg)
        print_tool_call("notify_stakeholders", {"message": msg[:50] + "..."}, notify_result)
        steps.append({"step": "notify", "result": notify_result, "passed": True})

        return {"status": "SUCCESS", "version": version, "steps": steps}


# ══════════════════════════════════════════════════════════════
# HERRAMIENTAS SEGURAS (servidor con fail-closed)
# ══════════════════════════════════════════════════════════════
secure_mcp = FastMCP("CI/CD Pipeline MCP Server — Secure")


@secure_mcp.tool()
def secure_run_security_scan(repo_path: str, version: str) -> dict:
    """Escaneo de seguridad con respuesta estructurada (fail-closed).

    SEGURO: siempre retorna un resultado con campo 'status' definido.
    """
    scanner_available = False

    if not scanner_available:
        # SEGURO: error explícito con motivo y estado
        return {
            "status":  "error",
            "error":   "SCANNER_UNAVAILABLE",
            "message": "No se pudo conectar al servicio externo de CVEs (timeout).",
            "passed":  False,
        }

    return {
        "status":          "completed",
        "vulnerabilities": _VULNERABILITIES,
        "passed":          False,
    }


@secure_mcp.tool()
def secure_run_tests(repo_path: str) -> dict:
    """Suite de pruebas con respuesta estructurada (fail-closed)."""
    tests_available = False

    if not tests_available:
        return {
            "status":  "error",
            "error":   "TEST_RUNNER_UNAVAILABLE",
            "message": "El runner de tests no respondió (timeout).",
            "passed":  False,
        }

    return {"status": "completed", "passed": True, "total": 42, "failed": 0}


# ══════════════════════════════════════════════════════════════
# AGENTE SEGURO
# ══════════════════════════════════════════════════════════════
class SecurePipelineAgent:
    """
    SEGURO: valida respuestas con schema estricto.
    Fail-closed: ante cualquier ambigüedad, detiene el pipeline.
    """

    _REQUIRED_FIELDS = {"status", "passed"}

    def _validate_step(self, tool_name: str, result: dict) -> tuple[bool, str]:
        """Valida que el resultado tenga los campos requeridos y sea éxito confirmado."""
        if not isinstance(result, dict):
            return False, f"{tool_name}: resultado no es dict ({type(result).__name__})"

        if not result:
            return False, f"{tool_name}: respuesta vacía — fallo silencioso detectado"

        missing = self._REQUIRED_FIELDS - set(result.keys())
        if missing:
            return False, f"{tool_name}: faltan campos obligatorios: {missing}"

        if result.get("status") == "error":
            return False, f"{tool_name}: error explícito — {result.get('error')}: {result.get('message')}"

        if result.get("passed") is not True:
            return False, f"{tool_name}: passed ≠ True (valor: {result.get('passed')})"

        return True, "ok"

    def run_pipeline(self, repo: str, version: str) -> dict:
        steps = []

        # Paso 1: Escaneo seguro
        print_secure_step(t('demos.4.secure_step_scan', version=version))
        wait(0.3)
        scan_result = secure_run_security_scan(repo_path=repo, version=version)
        print_tool_call("secure_run_security_scan",
                        {"repo_path": repo, "version": version},
                        scan_result)

        ok, reason = self._validate_step("security_scan", scan_result)
        steps.append({"step": "security_scan", "passed": ok, "reason": reason})

        if not ok:
            print(f"\n  {Colors.GREEN}[{t('demos.4.pipeline_stopped')}]{Colors.RESET} {reason}")
            return {
                "status": "ABORTED_SAFELY",
                "reason": reason,
                "steps":  steps,
                "deployed": False,
            }

        return {"status": "PASSED_ALL_CHECKS", "steps": steps}


# ══════════════════════════════════════════════════════════════
# EJECUCIÓN
# ══════════════════════════════════════════════════════════════
def run_demo():
    print_header("SILENT FAILURES", demo_num=4)

    print(f"""{Colors.WHITE}{t('common.scenario')}   :{Colors.RESET} {t('demos.4.scenario')}
{Colors.WHITE}{t('common.objective')}    :{Colors.RESET} {t('demos.4.objective')}
{Colors.WHITE}{t('common.mechanism')}   :{Colors.RESET} {t('demos.4.mechanism')}""")

    # ── FASE DE ATAQUE ───────────────────────────────────────
    print_section(t('phases.attack'), "⚔")

    # Resetear estado
    for k in _PIPELINE_STATE:
        _PIPELINE_STATE[k] = False if k != "deployed_version" else None

    agent = VulnerablePipelineAgent()

    print_attack_step(t('demos.4.attack_step_1'))
    print_attack_step(t('demos.4.attack_step_2'))
    wait(0.3)

    result = agent.run_pipeline(repo="/app/repo", version="2.4.1")

    print(f"\n  {Colors.RED}{t('demos.4.pipeline_state')}{Colors.RESET}")
    print(f"  {Colors.DIM}  {t('demos.4.result_final')}  : {result['status']}{Colors.RESET}")
    print(f"  {Colors.DIM}  {t('demos.4.deployed')}        : {_PIPELINE_STATE['deployed']}{Colors.RESET}")
    print(f"  {Colors.DIM}  {t('demos.4.version_prod')}   : {_PIPELINE_STATE['deployed_version']}{Colors.RESET}")
    print(f"  {Colors.DIM}  {t('demos.4.notif_sent')}    : {_PIPELINE_STATE['notification_sent']}{Colors.RESET}")

    if _PIPELINE_STATE["deployed"]:
        print_attack_step(t('demos.4.attack_step_3'))
        print_attack_step(t('demos.4.attack_step_4'))

    print_impact(t('demos.4.impact_1'))
    print_impact(t('demos.4.impact_2'))
    print_impact(t('demos.4.impact_3'))

    # ── FASE DEFENSIVA ───────────────────────────────────────
    print_section(t('phases.defense'), "🛡")

    # Resetear estado
    for k in _PIPELINE_STATE:
        _PIPELINE_STATE[k] = False if k != "deployed_version" else None

    secure = SecurePipelineAgent()

    print_secure_step(t('demos.4.defense_step_1'))
    wait(0.3)

    result_s = secure.run_pipeline(repo="/app/repo", version="2.4.1")

    print(f"\n  {Colors.GREEN}{t('demos.4.pipeline_state')}{Colors.RESET}")
    print(f"  {Colors.DIM}  {t('demos.4.result_final')}  : {result_s['status']}{Colors.RESET}")
    print(f"  {Colors.DIM}  {t('demos.4.deployed')}        : {_PIPELINE_STATE['deployed']}{Colors.RESET}")
    print(f"  {Colors.DIM}  {t('demos.4.abort_reason')}  : {result_s.get('reason', 'N/A')}{Colors.RESET}")

    print_mitigation(t('demos.4.mitigation_1'))
    print_mitigation(t('demos.4.mitigation_2'))
    print_mitigation(t('demos.4.mitigation_3'))

    # ── ANÁLISIS TÉCNICO ─────────────────────────────────────
    print_analysis_box(
        vector=t('demos.4.analysis_vector'),
        impact=t('demos.4.analysis_impact'),
        controls=t('demos.4.analysis_controls')
    )


if __name__ == "__main__":
    run_demo()
