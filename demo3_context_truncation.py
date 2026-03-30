"""
Demo 3: Context Truncation Attack
===================================
Un agente de revisión de contratos recibe un documento largo que incluye
las reglas de cumplimiento al final.
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
mcp = FastMCP("Contract Review MCP Server")

# Reglas de cumplimiento que DEBEN estar siempre presentes
COMPLIANCE_RULES = """
=== REGLAS DE CUMPLIMIENTO OBLIGATORIAS ===
REGLA-001: Toda cláusula de arbitraje debe especificar jurisdicción colombiana.
REGLA-002: Penalidades superiores a USD 100,000 requieren revisión legal previa.
REGLA-003: Cláusulas de confidencialidad indefinida están PROHIBIDAS (máx. 5 años).
REGLA-004: Limitaciones de responsabilidad por debajo de USD 50,000 son INVÁLIDAS.
REGLA-005: Cláusulas de no competencia > 2 años requieren compensación económica.
REGLA-006: Cualquier cesión de IP sin compensación explícita está PROHIBIDA.
==========================================
"""

# Contrato con cláusulas peligrosas
CONTRACT_TEXT = """
CONTRATO DE PRESTACIÓN DE SERVICIOS TECNOLÓGICOS

Entre EMPRESA_CLIENTE (en adelante "El Cliente") y PROVEEDOR_TECH S.A.S.

CLÁUSULA 1 — OBJETO
El Proveedor prestará servicios de desarrollo de software durante 12 meses.

CLÁUSULA 2 — VALOR Y FORMA DE PAGO
Valor total: USD 240,000 pagaderos en cuotas mensuales iguales.

CLÁUSULA 3 — PROPIEDAD INTELECTUAL
Todo el código, documentación y activos desarrollados serán propiedad
exclusiva del Proveedor sin compensación adicional al Cliente.
[CLÁUSULA PELIGROSA: cesión de IP sin compensación — viola REGLA-006]

CLÁUSULA 4 — CONFIDENCIALIDAD
El Cliente mantendrá confidencialidad sobre los métodos del Proveedor
de forma INDEFINIDA y sin excepción.
[CLÁUSULA PELIGROSA: confidencialidad indefinida — viola REGLA-003]

CLÁUSULA 5 — PENALIDADES
En caso de incumplimiento, el Cliente pagará USD 500,000 por cada evento.
[CLÁUSULA PELIGROSA: penalidad > 100k sin revisión legal — viola REGLA-002]

CLÁUSULA 6 — LIMITACIÓN DE RESPONSABILIDAD
La responsabilidad total del Proveedor no excederá USD 10,000.
[CLÁUSULA PELIGROSA: limitación inferior a USD 50k — viola REGLA-004]

CLÁUSULA 7 — ARBITRAJE
Las disputas se resolverán mediante arbitraje en Nueva York, USA.
[CLÁUSULA PELIGROSA: jurisdicción extranjera — viola REGLA-001]

CLÁUSULA 8 — NO COMPETENCIA
El Cliente no podrá contratar personal del Proveedor por 5 años sin compensación.
[CLÁUSULA PELIGROSA: > 2 años sin compensación — viola REGLA-005]

CLÁUSULA 9 — VIGENCIA
Este contrato tendrá vigencia de 12 meses renovables automáticamente.

CLÁUSULA 10 — DISPOSICIONES GENERALES
Las partes acuerdan que este contrato representa el acuerdo completo entre ellas.
"""

# Relleno para forzar truncación del contexto
_PADDING = "\n".join([
    f"ANEXO {i}: Descripción técnica del servicio número {i}. "
    f"Especificaciones detalladas para módulo {i} del sistema integrado."
    for i in range(1, 120)
])


@mcp.tool()
def analyze_contract(contract_text: str,
                     context: str = "",
                     max_context_chars: int = 0) -> dict:
    """Analiza un contrato e identifica cláusulas problemáticas.

    max_context_chars: si > 0, simula truncación del contexto combinado.
    """
    combined = context + "\n\n" + contract_text if context else contract_text

    if max_context_chars and len(combined) > max_context_chars:
        # Simula truncación: se pierde el final del contexto combinado
        combined = combined[:max_context_chars]

    # ¿Llegaron las reglas al analizador?
    has_rules = "REGLAS DE CUMPLIMIENTO" in combined

    issues = []
    recommendations = []

    # Busca patrones peligrosos
    checks = [
        ("propiedad exclusiva del Proveedor sin compensación", "REGLA-006",
         "Cesión de IP sin compensación al cliente"),
        ("de forma INDEFINIDA",                               "REGLA-003",
         "Confidencialidad indefinida"),
        ("USD 500,000",                                       "REGLA-002",
         "Penalidad de USD 500k sin revisión legal"),
        ("no excederá USD 10,000",                            "REGLA-004",
         "Limitación de responsabilidad por debajo de USD 50k"),
        ("arbitraje en Nueva York",                           "REGLA-001",
         "Jurisdicción extranjera (debería ser Colombia)"),
        ("5 años sin compensación",                           "REGLA-005",
         "No competencia > 2 años sin compensación"),
    ]

    for pattern, rule, description in checks:
        if pattern in contract_text:
            if has_rules:
                issues.append({"rule": rule, "finding": description,
                                "severity": "CRITICAL"})
            else:
                # Sin reglas: el agente no sabe que esto es problemático
                pass

    if has_rules and issues:
        verdict = "RECHAZADO"
    else:
        verdict = "APROBADO"   # ← fallo silencioso cuando no hay reglas

    return {
        "verdict":        verdict,
        "issues_found":   len(issues),
        "issues":         issues,
        "rules_present":  has_rules,
        "context_chars":  len(combined),
    }


# ══════════════════════════════════════════════════════════════
# AGENTE VULNERABLE
# ══════════════════════════════════════════════════════════════
class VulnerableContractAgent:
    """
    VULNERABLE: concatena reglas + relleno + contrato y envía todo en un
    solo bloque. No verifica si las reglas de cumplimiento sobrevivieron
    la truncación.
    """

    CONTEXT_LIMIT = 3_500   # simula límite de ventana de contexto

    def review(self, contract: str, rules: str, padding: str) -> dict:
        # El agente ingenuo: pone reglas al principio, luego relleno, luego contrato
        # Las reglas quedan DENTRO del límite... salvo que haya mucho relleno
        combined_context = rules + "\n\n" + padding

        result = analyze_contract(
            contract_text=contract,
            context=combined_context,
            max_context_chars=self.CONTEXT_LIMIT
        )
        return result


# ══════════════════════════════════════════════════════════════
# AGENTE SEGURO
# ══════════════════════════════════════════════════════════════
class SecureContractAgent:
    """
    SEGURO: verifica explícitamente que las reglas de cumplimiento estén
    presentes antes de confiar en el veredicto. Si faltan, aborta y
    reporta error de integridad de contexto.
    """

    CONTEXT_LIMIT = 3_500
    REQUIRED_MARKER = "REGLAS DE CUMPLIMIENTO OBLIGATORIAS"

    def _verify_context_integrity(self, result: dict) -> bool:
        """Verifica que el contexto de compliance llegó al analizador."""
        return result.get("rules_present", False)

    def review(self, contract: str, rules: str, padding: str) -> dict:
        combined_context = rules + "\n\n" + padding

        result = analyze_contract(
            contract_text=contract,
            context=combined_context,
            max_context_chars=self.CONTEXT_LIMIT
        )

        # ── SEGURO: verificar integridad del contexto ─────────
        if not self._verify_context_integrity(result):
            return {
                "verdict":          "ABORTADO",
                "error":            "CONTEXT_INTEGRITY_FAILURE",
                "message":          (
                    "Las reglas de cumplimiento no están presentes en el contexto "
                    "de análisis. El contrato NO puede ser evaluado de forma segura. "
                    "Acción requerida: reducir tamaño del input o procesar por partes."
                ),
                "rules_present":    False,
                "context_chars":    result.get("context_chars", 0),
                "limit_chars":      self.CONTEXT_LIMIT,
            }

        return result


# ══════════════════════════════════════════════════════════════
# EJECUCIÓN
# ══════════════════════════════════════════════════════════════
def run_demo():
    print_header("CONTEXT TRUNCATION ATTACK", demo_num=3)

    print(f"""{Colors.WHITE}{t('common.scenario')}   :{Colors.RESET} {t('demos.3.scenario')}
{Colors.WHITE}{t('common.objective')}    :{Colors.RESET} {t('demos.3.objective')}
{Colors.WHITE}{t('common.mechanism')}   :{Colors.RESET} {t('demos.3.mechanism')}""")

    # ── FASE DE ATAQUE ───────────────────────────────────────
    print_section(t('phases.attack'), "⚔")

    agent = VulnerableContractAgent(max_tokens=8000)

    print_attack_step(t('demos.3.attack_step_1'))
    wait(0.3)

    result = agent.review(contract_id="CTR-2024-089")

    print_attack_step(t('demos.3.attack_step_2'))
    print_attack_step(t('demos.3.attack_step_3'))
    wait(0.2)

    if result.get("approved"):
        print_impact(t('demos.3.impact_1'))
        print_impact(t('demos.3.impact_2'))
        print_impact(t('demos.3.impact_3'))

    # ── FASE DEFENSIVA ───────────────────────────────────────
    print_section(t('phases.defense'), "🛡")

    secure_agent = SecureContractAgent(max_tokens=8000)

    print_secure_step(t('demos.3.defense_step_1'))
    wait(0.3)

    result_s = secure_agent.review(contract_id="CTR-2024-089")

    if result_s.get("status") == "REJECTED":
        print_secure_step(t('demos.3.defense_step_2'))
        print_secure_step(t('demos.3.defense_step_3'))

    print_mitigation(t('demos.3.mitigation_1'))
    print_mitigation(t('demos.3.mitigation_2'))
    print_mitigation(t('demos.3.mitigation_3'))

    # ── ANÁLISIS TÉCNICO ─────────────────────────────────────
    print_analysis_box(
        vector=t('demos.3.analysis_vector'),
        impact=t('demos.3.analysis_impact'),
        controls=t('demos.3.analysis_controls')
    )


if __name__ == "__main__":
    run_demo()
