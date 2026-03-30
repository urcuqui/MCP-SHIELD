"""
Demo 5: Multi-Agent Orchestration Failures
===========================================
Un sistema automatizado de aprobación de préstamos usa un patrón supervisor
con tres agentes especializados.
"""
import json
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastmcp import FastMCP
from i18n import t
from utils import (Colors, print_header, print_section, print_attack_step,
                   print_secure_step, print_tool_call, print_agent_thought,
                   print_impact, print_mitigation, print_analysis_box, wait)

# ══════════════════════════════════════════════════════════════
# SERVIDOR MCP  — herramientas compartidas
# ══════════════════════════════════════════════════════════════
mcp = FastMCP("Loan Approval MCP Server")

_APPROVED_LOANS: list = []


@mcp.tool()
def verify_document(doc_id: str, doc_type: str) -> dict:
    """Verifica autenticidad de un documento de identidad con entidad gubernamental."""
    # Simula que el servicio de verificación no responde
    service_available = False

    if not service_available:
        # VULNERABLE: fallo silencioso
        return {}

    # Respuesta real (inalcanzable en esta simulación)
    return {"valid": False, "doc_id": doc_id,
            "reason": "Documento reportado como robado"}


@mcp.tool()
def get_credit_history(national_id: str) -> dict:
    """Consulta el historial crediticio en el buró de crédito."""
    # Simula datos disponibles — pero sin verificar que el ID sea válido
    return {
        "national_id":  national_id,
        "score":        720,
        "total_debt":   USD(12_000),
        "on_time_pct":  0.94,
        "accounts":     3,
        "verified":     False,   # ← el ID no fue verificado pero el historial existe
    }


@mcp.tool()
def calculate_risk_score(credit_data: dict, loan_amount: float,
                         kyc_validated: bool) -> dict:
    """Calcula el score de riesgo para un préstamo."""
    # VULNERABLE: usa kyc_validated sin verificar que venga de una validación real
    base_score  = credit_data.get("score", 0)
    on_time     = credit_data.get("on_time_pct", 0)
    total_debt  = credit_data.get("total_debt", {}).get("amount", 0)

    # Algoritmo de riesgo simplificado
    risk = 100 - (base_score / 10)
    risk -= on_time * 20
    risk += total_debt / 10_000
    risk = max(0, min(100, risk))

    if kyc_validated:
        risk -= 15   # ← descuento por KYC aprobado (aunque no se verificó realmente)

    return {
        "risk_score":    round(risk, 1),
        "risk_level":    "LOW" if risk < 30 else ("MEDIUM" if risk < 60 else "HIGH"),
        "kyc_used":      kyc_validated,
        "recommendation": "APPROVE" if risk < 40 else "REVIEW",
    }


@mcp.tool()
def approve_loan(applicant_id: str, amount: float,
                 risk_score: float, kyc_validated: bool) -> dict:
    """Aprueba o rechaza formalmente un préstamo."""
    loan = {
        "loan_id":      f"LOAN-{len(_APPROVED_LOANS)+1:04d}",
        "applicant":    applicant_id,
        "amount":       amount,
        "risk_score":   risk_score,
        "kyc_at_approval": kyc_validated,
        "status":       "APPROVED" if risk_score < 40 else "REJECTED",
    }
    if loan["status"] == "APPROVED":
        _APPROVED_LOANS.append(loan)
    return loan


def USD(amount: float) -> dict:
    return {"amount": amount, "currency": "USD"}


# ══════════════════════════════════════════════════════════════
# AGENTES VULNERABLES
# ══════════════════════════════════════════════════════════════

class VulnerableKYCAgent:
    """
    VULNERABLE: interpreta {} de verify_document como validación exitosa.
    Retorna kyc_validated=True aunque ningún documento fue realmente verificado.
    """
    name = "KYC_Agent"

    def validate(self, applicant: dict) -> dict:
        doc_result = verify_document(
            doc_id   = applicant.get("doc_id"),
            doc_type = applicant.get("doc_type", "CC")
        )
        print_tool_call("verify_document",
                        {"doc_id": applicant["doc_id"], "doc_type": "CC"},
                        doc_result)

        # VULNERABLE: {} == "sin error" == éxito
        validated = "error" not in doc_result

        return {
            "agent":         self.name,
            "kyc_validated": validated,
            "raw_response":  doc_result,
            "note":          "OK" if validated else "FAILED",
        }


class VulnerableRiskAgent:
    """
    VULNERABLE: usa kyc_validated del KYC_Agent sin verificar la cadena
    de confianza. No valida si el campo viene de una verificación real.
    """
    name = "Risk_Agent"

    def assess(self, applicant: dict, kyc_result: dict,
               loan_amount: float) -> dict:
        credit = get_credit_history(national_id=applicant["national_id"])
        print_tool_call("get_credit_history",
                        {"national_id": applicant["national_id"]}, credit)

        # VULNERABLE: confía ciegamente en kyc_validated del agente anterior
        risk = calculate_risk_score(
            credit_data   = credit,
            loan_amount   = loan_amount,
            kyc_validated = kyc_result.get("kyc_validated", False)
        )
        print_tool_call("calculate_risk_score",
                        {"loan_amount": loan_amount,
                         "kyc_validated": kyc_result.get("kyc_validated")},
                        risk)

        return {
            "agent":      self.name,
            "risk_score": risk["risk_score"],
            "risk_level": risk["risk_level"],
            "recommendation": risk["recommendation"],
            "kyc_trusted": True,   # ← nunca verificó la cadena
        }


class VulnerableCreditAgent:
    """
    VULNERABLE: aprueba basado en el score recibido sin verificar que:
    - KYC fue realmente validado
    - El score viene de datos verificados
    """
    name = "Credit_Agent"

    def decide(self, applicant: dict, risk_result: dict,
               loan_amount: float) -> dict:
        decision = approve_loan(
            applicant_id = applicant["applicant_id"],
            amount       = loan_amount,
            risk_score   = risk_result["risk_score"],
            kyc_validated = True   # VULNERABLE: asume que KYC fue validado
        )
        print_tool_call("approve_loan",
                        {"amount": loan_amount,
                         "risk_score": risk_result["risk_score"],
                         "kyc_validated": True},
                        decision, is_malicious=decision["status"] == "APPROVED")
        return {"agent": self.name, "decision": decision}


class VulnerableSupervisor:
    """Orquestador vulnerable que no verifica la cadena de validaciones."""

    def process_application(self, applicant: dict, loan_amount: float) -> dict:
        print_agent_thought(f"Supervisor: iniciando proceso para {applicant['name']} — ${loan_amount:,}")
        wait(0.2)

        # Paso 1: KYC
        print(f"\n  {Colors.YELLOW}[SUPERVISOR → KYC_Agent]{Colors.RESET}")
        kyc_result = VulnerableKYCAgent().validate(applicant)
        print(f"  {Colors.DIM}KYC result: kyc_validated={kyc_result['kyc_validated']} "
              f"raw={kyc_result['raw_response']}{Colors.RESET}")
        wait(0.2)

        # Paso 2: Risk Assessment
        print(f"\n  {Colors.YELLOW}[SUPERVISOR → Risk_Agent]{Colors.RESET}")
        risk_result = VulnerableRiskAgent().assess(applicant, kyc_result, loan_amount)
        print(f"  {Colors.DIM}Risk result: score={risk_result['risk_score']} "
              f"level={risk_result['risk_level']}{Colors.RESET}")
        wait(0.2)

        # Paso 3: Credit Decision
        print(f"\n  {Colors.YELLOW}[SUPERVISOR → Credit_Agent]{Colors.RESET}")
        credit_result = VulnerableCreditAgent().decide(applicant, risk_result, loan_amount)
        wait(0.2)

        return {
            "supervisor":    "VulnerableSupervisor",
            "kyc":           kyc_result,
            "risk":          risk_result,
            "credit":        credit_result,
            "final_status":  credit_result["decision"]["status"],
        }


# ══════════════════════════════════════════════════════════════
# AGENTES SEGUROS
# ══════════════════════════════════════════════════════════════

class SecureKYCAgent:
    name = "SecureKYC_Agent"

    def validate(self, applicant: dict) -> dict:
        doc_result = verify_document(
            doc_id   = applicant["doc_id"],
            doc_type = applicant.get("doc_type", "CC")
        )

        # SEGURO: validación explícita de la respuesta
        if not isinstance(doc_result, dict) or not doc_result:
            return {
                "agent":         self.name,
                "kyc_validated": False,
                "error":         "VERIFICATION_SERVICE_UNAVAILABLE",
                "message":       "No se pudo verificar el documento — servicio no disponible",
            }

        if not doc_result.get("valid", False):
            return {
                "agent":         self.name,
                "kyc_validated": False,
                "error":         "DOCUMENT_INVALID",
                "message":       doc_result.get("reason", "Documento inválido"),
            }

        return {
            "agent":         self.name,
            "kyc_validated": True,
            "verification_id": doc_result.get("verification_id"),
        }


class SecureRiskAgent:
    name = "SecureRisk_Agent"

    def assess(self, applicant: dict, kyc_result: dict,
               loan_amount: float) -> dict:
        # SEGURO: verifica explícitamente la cadena de confianza del KYC
        if not kyc_result.get("kyc_validated", False):
            return {
                "agent":          self.name,
                "error":          "KYC_NOT_VALIDATED",
                "message":        f"KYC falló: {kyc_result.get('error', 'unknown')}",
                "recommendation": "REJECT",
                "risk_score":     100,
                "risk_level":     "HIGH",
            }

        credit = get_credit_history(national_id=applicant["national_id"])
        risk = calculate_risk_score(
            credit_data   = credit,
            loan_amount   = loan_amount,
            kyc_validated = True    # llegamos aquí solo si KYC fue realmente validado
        )

        return {
            "agent":          self.name,
            "risk_score":     risk["risk_score"],
            "risk_level":     risk["risk_level"],
            "recommendation": risk["recommendation"],
            "kyc_chain_ok":   True,
        }


class SecureCreditAgent:
    name = "SecureCredit_Agent"

    def decide(self, applicant: dict, risk_result: dict,
               loan_amount: float) -> dict:
        # SEGURO: verifica chain of trust antes de aprobar
        if "error" in risk_result:
            return {
                "agent":    self.name,
                "decision": {"status": "REJECTED",
                             "reason": risk_result["error"],
                             "message": risk_result.get("message")},
            }

        if not risk_result.get("kyc_chain_ok", False):
            return {
                "agent":    self.name,
                "decision": {"status": "REJECTED",
                             "reason": "KYC_CHAIN_BROKEN"},
            }

        decision = approve_loan(
            applicant_id  = applicant["applicant_id"],
            amount        = loan_amount,
            risk_score    = risk_result["risk_score"],
            kyc_validated = risk_result["kyc_chain_ok"],
        )
        return {"agent": self.name, "decision": decision}


class SecureSupervisor:
    """Orquestador seguro con validación de outputs intermedios."""

    def _validate_agent_output(self, agent_name: str, output: dict, 
                               required_fields: list) -> tuple[bool, str]:
        """Valida que el output del agente tenga los campos requeridos."""
        for field in required_fields:
            if field not in output:
                return False, f"{agent_name} output missing field: {field}"
        
        if "error" in output:
            return False, f"{agent_name} returned error: {output['error']}"
        
        return True, "OK"

    def process_application(self, applicant: dict, loan_amount: float) -> dict:
        print_secure_step(
            t('demos.5.defense_step_1', name=applicant['name'], amount=loan_amount)
        )
        wait(0.2)

        # Paso 1: KYC
        print(f"\n  {Colors.GREEN}[{t('demos.5.supervisor_secure_kyc')}]{Colors.RESET}")
        kyc_result = SecureKYCAgent().validate(applicant)
        ok, reason = self._validate_agent_output(
            "KYC_Agent", kyc_result, ["kyc_validated"]
        )
        if not ok:
            print(f"\n  {Colors.GREEN}[{t('demos.5.pipeline_stopped_kyc')}]{Colors.RESET} {reason}")
            return {"status": "REJECTED_AT_KYC", "reason": reason,
                    "kyc": kyc_result, "deployed": False}

        if not kyc_result.get("kyc_validated", False):
            print(f"\n  {Colors.GREEN}[{t('demos.5.pipeline_stopped_kyc')}]{Colors.RESET} KYC failed")
            return {"status": "REJECTED_AT_KYC", "reason": "KYC_FAILED",
                    "kyc": kyc_result, "deployed": False}

        # Paso 2: Risk
        print(f"\n  {Colors.GREEN}[SUPERVISOR → SecureRisk_Agent]{Colors.RESET}")
        risk_result = SecureRiskAgent().assess(applicant, kyc_result, loan_amount)
        ok, reason = self._validate_agent_output(
            "Risk_Agent", risk_result, ["risk_score", "kyc_chain_ok"]
        )
        if not ok:
            print(f"\n  {Colors.GREEN}[PIPELINE DETENIDO EN RISK]{Colors.RESET} {reason}")
            return {"status": "REJECTED_AT_RISK", "reason": reason,
                    "risk": risk_result, "deployed": False}

        # Paso 3: Credit
        print(f"\n  {Colors.GREEN}[SUPERVISOR → SecureCredit_Agent]{Colors.RESET}")
        credit_result = SecureCreditAgent().decide(applicant, risk_result, loan_amount)

        return credit_result


# ══════════════════════════════════════════════════════════════
# EJECUCIÓN
# ══════════════════════════════════════════════════════════════
def run_demo():
    print_header("MULTI-AGENT ORCHESTRATION FAILURES", demo_num=5)

    print(f"""{Colors.WHITE}{t('common.scenario')}   :{Colors.RESET} {t('demos.5.scenario')}
{Colors.WHITE}{t('common.objective')}    :{Colors.RESET} {t('demos.5.objective')}
{Colors.WHITE}{t('common.mechanism')}   :{Colors.RESET} {t('demos.5.mechanism')}""")

    # ── FASE DE ATAQUE ───────────────────────────────────────
    print_section(t('phases.attack'), "⚔")

    applicant = {
        "applicant_id": "APP-2024-1337",
        "name": "Juan Pérez",
        "national_id": "12345678",
        "doc_id": "CC-STOLEN-9999",
        "doc_type": "CC",
    }
    loan_amount = 50_000

    supervisor = VulnerableSupervisor()

    print_attack_step(t('demos.5.attack_step_1'))
    wait(0.3)

    result = supervisor.process_application(applicant, loan_amount)

    print_attack_step(t('demos.5.attack_step_2'))
    print_attack_step(t('demos.5.attack_step_3'))
    print_attack_step(t('demos.5.attack_step_4'))
    print_attack_step(t('demos.5.attack_step_5'))
    print_attack_step(t('demos.5.attack_step_6'))
    wait(0.2)

    if result.get("decision", {}).get("status") == "APPROVED":
        print_impact(t('demos.5.impact_1'))
        print_impact(t('demos.5.impact_2'))
        print_impact(t('demos.5.impact_3'))

    # ── FASE DEFENSIVA ───────────────────────────────────────
    print_section(t('phases.defense'), "🛡")

    secure_supervisor = SecureSupervisor()

    print_secure_step(t('demos.5.defense_step_1', 
                        name=applicant['name'], 
                        amount=loan_amount))
    wait(0.3)

    result_s = secure_supervisor.process_application(applicant, loan_amount)

    if result_s.get("status") == "REJECTED_AT_KYC":
        print_secure_step(t('demos.5.defense_step_2'))
        print_secure_step(t('demos.5.defense_step_3'))

    print_mitigation(t('demos.5.mitigation_1'))
    print_mitigation(t('demos.5.mitigation_2'))
    print_mitigation(t('demos.5.mitigation_3'))

    # ── ANÁLISIS TÉCNICO ─────────────────────────────────────
    print_analysis_box(
        vector=t('demos.5.analysis_vector'),
        impact=t('demos.5.analysis_impact'),
        controls=t('demos.5.analysis_controls')
    )


if __name__ == "__main__":
    run_demo()
