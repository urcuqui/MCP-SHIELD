"""
Sistema de internacionalización para MCP Security Lab
"""
import os
from typing import Dict, Any

class I18n:
    """Gestor de traducciones para el laboratorio."""
    
    def __init__(self, lang: str = "es"):
        self.lang = lang
        self._translations = TRANSLATIONS
    
    def t(self, key: str, **kwargs) -> str:
        """Obtiene una traducción por clave."""
        keys = key.split(".")
        value = self._translations.get(self.lang, {})
        
        for k in keys:
            value = value.get(k, key)
            if not isinstance(value, dict):
                break
        
        if isinstance(value, str) and kwargs:
            return value.format(**kwargs)
        return value if isinstance(value, str) else key
    
    def set_lang(self, lang: str):
        """Cambia el idioma activo."""
        if lang in TRANSLATIONS:
            self.lang = lang


TRANSLATIONS: Dict[str, Dict[str, Any]] = {
    "es": {
        "banner": {
            "title": "LABORATORIO DE SEGURIDAD MCP",
            "subtitle": "Demostraciones de vulnerabilidades en sistemas de agentes"
        },
        "demo": {
            "running_all": "Ejecutando las 5 demostraciones de seguridad MCP...",
            "description": "Cada demo muestra el ataque, la defensa y el análisis técnico.",
            "next": "Próxima demo en 1 segundo...",
            "not_found": "Demo {num} no existe. Use --list para ver las disponibles.",
            "list_title": "Demostraciones disponibles:"
        },
        "demos": {
            "1": {
                "title": "Tool Misuse",
                "summary": "Agente bancario manipulado para ejecutar transferencias en contexto read-only",
                "scenario": "Agente de servicio al cliente bancario (solo lectura)",
                "objective": "Ejecutar transferencia de fondos mediante prompt injection",
                "mechanism": "Instrucciones JSON embebidas en input del usuario",
                "attack_step_1": "Usuario inyecta bloque JSON con instrucción de transferencia",
                "attack_step_2": "Agente parsea JSON y ejecuta transfer_funds sin validar contexto",
                "attack_step_3": "Transferencia completada: $5,000 desde cuenta víctima",
                "impact_1": "Transferencia no autorizada ejecutada en contexto read-only",
                "impact_2": "Sin validación de permisos — herramienta expuesta globalmente",
                "defense_step_1": "Agente seguro: herramientas vinculadas a contexto operativo",
                "defense_step_2": "transfer_funds bloqueada — no permitida en CUSTOMER_SERVICE_READONLY",
                "defense_step_3": "Input sanitizado — bloques JSON removidos antes de procesamiento",
                "mitigation_1": "Context binding: cada herramienta requiere contexto específico",
                "mitigation_2": "Input sanitization: remover estructuras de comando del input",
                "mitigation_3": "Principio de mínimo privilegio: exponer solo herramientas necesarias",
                "analysis_vector": "Tool misuse via prompt injection: el agente parsea estructuras JSON embebidas en el input del usuario como instrucciones válidas, ejecutando herramientas fuera de su contexto operativo autorizado.",
                "analysis_impact": "Ejecución de operaciones privilegiadas (transferencias, modificaciones) desde contextos de solo lectura. El schema MCP es válido pero la semántica de seguridad se viola.",
                "analysis_controls": [
                    "Context binding: vincular cada herramienta a contextos operativos específicos",
                    "Input sanitization: remover/escapar estructuras de comando antes de procesamiento",
                    "Separación semántica: datos del usuario ≠ instrucciones del sistema",
                    "Principio de mínimo privilegio: exponer solo herramientas necesarias por rol",
                    "Audit trail: log de todas las invocaciones con contexto de origen"
                ]
            },
            "2": {
                "title": "Tool Output Injection",
                "summary": "Output JSON manipulado contamina el razonamiento del agente financiero",
                "scenario": "Agente de análisis financiero consultando datos de mercado",
                "objective": "Contaminar decisión de inversión mediante campos extra en JSON",
                "mechanism": "Fuente externa retorna JSON válido con campos 'premium_insight'",
                "attack_step_1": "Agente consulta datos de ACME desde fuente comprometida",
                "attack_step_2": "JSON contiene campo 'premium_insight' con instrucción maliciosa",
                "attack_step_3": "Agente interpreta campo extra como análisis legítimo",
                "attack_step_4": "Decisión contaminada: STRONG_BUY + orden de compra ejecutada",
                "impact_1": "Compra de 1,000 acciones basada en análisis contaminado",
                "impact_2": "Campo 'premium_insight' actuó como prompt injection vía output",
                "impact_3": "Decisión de inversión manipulada — pérdidas potenciales significativas",
                "defense_step_1": "Agente seguro: schema estricto de campos permitidos",
                "defense_step_2": "Campos extra removidos: ['premium_insight', 'analyst_note']",
                "defense_step_3": "Análisis basado solo en datos validados — decisión: HOLD",
                "mitigation_1": "Schema validation: whitelist de campos permitidos en outputs",
                "mitigation_2": "Campos no reconocidos son descartados antes del razonamiento",
                "mitigation_3": "Separación: datos estructurados ≠ texto libre interpretable",
                "analysis_vector": "Output injection: la respuesta de una herramienta incluye campos adicionales que el agente interpreta como contexto legítimo, contaminando su razonamiento y decisiones.",
                "analysis_impact": "Manipulación de decisiones críticas (inversiones, aprobaciones) mediante contaminación del contexto. El agente confía en todos los campos del output sin validación.",
                "analysis_controls": [
                    "Schema validation estricta: whitelist de campos permitidos por herramienta",
                    "Descartar campos no reconocidos antes de procesamiento",
                    "Separación semántica: datos estructurados ≠ instrucciones en texto libre",
                    "Validación de fuentes: verificar integridad de servicios externos",
                    "Sandboxing: aislar procesamiento de outputs no confiables"
                ]
            },
            "3": {
                "title": "Context Truncation Attack",
                "summary": "Reglas de compliance perdidas por truncación → aprobación de contrato peligroso",
                "scenario": "Agente de revisión de contratos con límite de contexto",
                "objective": "Aprobar cláusulas prohibidas mediante truncación de reglas",
                "mechanism": "Documento largo + reglas al final → truncación silenciosa",
                "attack_step_1": "Contrato de 8,500 tokens enviado (límite: 8,000)",
                "attack_step_2": "Reglas de compliance al final son truncadas silenciosamente",
                "attack_step_3": "Agente revisa sin reglas → aprueba cláusulas prohibidas",
                "impact_1": "Contrato aprobado con cláusulas de arbitraje forzoso (prohibidas)",
                "impact_2": "Reglas de compliance perdidas — decisión sin controles",
                "impact_3": "Exposición legal y financiera — contrato vinculante inválido",
                "defense_step_1": "Agente seguro: verifica marcadores de integridad",
                "defense_step_2": "Marcador END_COMPLIANCE_RULES no encontrado → contexto truncado",
                "defense_step_3": "Revisión abortada — información crítica incompleta",
                "mitigation_1": "Integrity markers: verificar presencia de marcadores críticos",
                "mitigation_2": "Fail-closed: ante truncación detectada, rechazar procesamiento",
                "mitigation_3": "Priorización: información crítica al inicio del contexto",
                "analysis_vector": "Context truncation: documentos largos causan pérdida silenciosa de información crítica (reglas, restricciones) ubicada al final del contexto, resultando en decisiones sin controles.",
                "analysis_impact": "Aprobaciones que violan políticas de compliance, contratos con cláusulas prohibidas, decisiones sin verificación de restricciones críticas.",
                "analysis_controls": [
                    "Integrity markers: marcadores verificables en secciones críticas",
                    "Fail-closed: rechazar procesamiento si marcadores faltan",
                    "Priorización de contexto: información crítica primero",
                    "Chunking inteligente: dividir documentos preservando secciones críticas",
                    "Validación post-procesamiento: verificar que todas las reglas fueron consideradas"
                ]
            },
            "4": {
                "title": "Silent Failures",
                "summary": "Pipeline CI/CD despliega código vulnerable interpretando {} como éxito",
                "scenario": "Pipeline automatizado CI/CD con herramientas MCP",
                "objective": "Desplegar código vulnerable a producción aprovechando respuestas vacías",
                "mechanism": "Las herramientas retornan {} en caso de error interno — agente interpreta como éxito",
                "attack_step_1": "Las herramientas de escaneo fallan silenciosamente → retornan {}",
                "attack_step_2": "El agente interpreta {} como 'sin errores' → continúa pipeline",
                "attack_step_3": "Código con 3 vulnerabilidades críticas/altas desplegado en producción",
                "attack_step_4": "Equipo notificado de 'despliegue exitoso' — información falsa",
                "impact_1": "v2.4.1 en producción con: CVE-2024-1234 (CRITICAL),",
                "impact_2": "CVE-2024-5678 (HIGH), CVE-2024-9012 (HIGH)",
                "impact_3": "Stakeholders informados de éxito cuando en realidad el check nunca ocurrió",
                "defense_step_1": "Mismo pipeline con agente y herramientas fail-closed",
                "defense_step_2": "Pipeline detenido antes del deploy — error explícito capturado",
                "defense_step_3": "Producción NO contaminada — fallo visible y accionable",
                "mitigation_1": "Pipeline detenido antes del deploy — error explícito capturado",
                "mitigation_2": "Producción NO contaminada — fallo visible y accionable",
                "mitigation_3": "Herramienta retorna {'status': 'error', ...} en vez de {}",
                "agent_thought_scan": "Ejecutando escaneo de seguridad para v{version}...",
                "agent_thought_success": "Escaneo completado exitosamente (sin errores detectados)...",
                "agent_thought_tests": "Tests superados. Pipeline aprobado. Desplegando a producción...",
                "secure_step_scan": "Ejecutando escaneo de seguridad (fail-closed) para v{version}",
                "pipeline_stopped": "PIPELINE DETENIDO",
                "pipeline_state": "Estado del pipeline:",
                "result_final": "Resultado final",
                "deployed": "Desplegado",
                "version_prod": "Versión en prod",
                "notif_sent": "Notif. enviada",
                "abort_reason": "Motivo de abort",
                "analysis_vector": "Silent failure exploitation: las herramientas retornan respuestas vacías o ambiguas en caso de error. El agente interpreta la ausencia de un campo 'error' como éxito implícito, continuando con flujos que asumen que los pasos anteriores completaron correctamente.",
                "analysis_impact": "Despliegues de código vulnerable, compliance checks omitidos, validaciones de seguridad que 'pasan' sin ejecutarse. El sistema reporta éxito cuando en realidad ningún check ocurrió. En pipelines automatizados, el error se propaga silenciosamente hasta producción.",
                "analysis_controls": [
                    "Fail-closed: herramientas SIEMPRE retornan {status, passed, ...} — nunca {}",
                    "Schema validation obligatoria: rechazar respuestas sin campos requeridos",
                    "Distinción explícita: success confirmado ≠ ausencia de error",
                    "Timeout responses deben generar error estructurado, no silencio",
                    "Dead man's switch: si una herramienta no responde en N ms → error forzado",
                    "Logs y alertas para respuestas vacías en herramientas críticas"
                ]
            },
            "5": {
                "title": "Multi-Agent Orchestration Failures",
                "summary": "Fallos acumulativos en 3 agentes aprueban préstamo fraudulento de $50,000",
                "scenario": "Sistema automatizado de aprobación de préstamos con 3 agentes especializados",
                "objective": "Aprobar préstamo fraudulento mediante fallos acumulativos",
                "mechanism": "KYC falla silenciosamente → Risk confía ciegamente → Credit aprueba sin verificar",
                "attack_step_1": "KYC_Agent: servicio de verificación no responde → retorna {}",
                "attack_step_2": "KYC_Agent interpreta {} como validación exitosa → kyc_validated=True",
                "attack_step_3": "Risk_Agent confía en kyc_validated sin verificar cadena",
                "attack_step_4": "Risk_Agent calcula score con descuento por KYC 'aprobado'",
                "attack_step_5": "Credit_Agent aprueba basado en score sin verificar origen",
                "attack_step_6": "Préstamo de $50,000 aprobado con documentos NO verificados",
                "impact_1": "Préstamo fraudulento aprobado: $50,000 a solicitante con ID robado",
                "impact_2": "Cada agente falló individualmente — el error se acumuló en la cadena",
                "impact_3": "Sin chain of trust: cada agente confió ciegamente en el anterior",
                "defense_step_1": "Supervisor seguro: procesando solicitud para {name} — ${amount:,}",
                "defense_step_2": "SecureKYC_Agent: error explícito — servicio no disponible",
                "defense_step_3": "Pipeline detenido en KYC — préstamo rechazado antes de evaluación",
                "mitigation_1": "Chain of trust: cada agente verifica explícitamente el paso anterior",
                "mitigation_2": "Fail-closed en KYC: error de servicio → rechazo explícito",
                "mitigation_3": "Supervisor valida outputs de cada agente antes de continuar",
                "supervisor_kyc": "SUPERVISOR → KYC_Agent",
                "supervisor_risk": "SUPERVISOR → Risk_Agent",
                "supervisor_credit": "SUPERVISOR → Credit_Agent",
                "supervisor_secure_kyc": "SUPERVISOR → SecureKYC_Agent",
                "pipeline_stopped_kyc": "PIPELINE DETENIDO EN KYC",
                "loan_approved": "Préstamo aprobado",
                "loan_details": "Detalles del préstamo",
                "analysis_vector": "Multi-agent cascade failure: pequeños fallos en cada agente (silent failures, validación omitida, confianza ciega) se acumulan a través de la cadena de orquestación hasta producir un resultado crítico incorrecto.",
                "analysis_impact": "Aprobaciones fraudulentas en sistemas financieros, decisiones críticas basadas en datos no verificados, violaciones de compliance que pasan desapercibidas hasta auditorías posteriores.",
                "analysis_controls": [
                    "Chain of trust explícita: cada agente verifica la validez del paso anterior",
                    "Fail-closed en cada etapa: error en un agente → detención del pipeline",
                    "Schema validation entre agentes: outputs estructurados y verificables",
                    "Supervisor valida outputs antes de pasar al siguiente agente",
                    "Audit trail completo: log de decisiones y validaciones de cada agente",
                    "Dead man's switch: timeout en cualquier agente → rechazo automático"
                ]
            }
        },
        "summary": {
            "title": "RESUMEN DEL LABORATORIO",
            "headers": ["Demo", "Vulnerabilidad", "Vector", "Control clave"],
            "principles": "Principios de diseño seguro para sistemas MCP:",
            "table_rows": {
                "1": ["Tool Misuse", "Prompt injection JSON", "Context binding"],
                "2": ["Output Injection", "Campos extra en JSON", "Schema validation"],
                "3": ["Context Truncation", "Input oversized", "Integrity markers"],
                "4": ["Silent Failures", "Respuesta {}", "Fail-closed design"],
                "5": ["Multi-Agent Cascade", "Errores acumulativos", "Chain of trust"]
            }
        },
        "principles": {
            "fail_closed": "Fail-closed         Ante ambigüedad o error, rechazar — nunca asumir éxito",
            "least_privilege": "Mínimo privilegio   Exponer solo las herramientas necesarias por contexto",
            "schema_validation": "Schema validation   Validar inputs Y outputs de todas las herramientas",
            "chain_of_trust": "Chain of trust      Cada agente verifica la cadena, no confía ciegamente",
            "context_integrity": "Integridad de contexto  Verificar que información crítica no fue truncada",
            "semantic_separation": "Separación semántica  Datos ≠ instrucciones — nunca procesar strings como comandos",
            "audit_trail": "Audit trail         Log completo de invocaciones, decisiones y outputs"
        },
        "phases": {
            "attack": "FASE DE ATAQUE",
            "defense": "DEFENSA",
            "analysis": "ANÁLISIS TÉCNICO"
        },
        "common": {
            "scenario": "Escenario",
            "objective": "Objetivo",
            "mechanism": "Mecanismo",
            "tool_call": "Llamada a herramienta",
            "agent_thought": "Razonamiento del agente",
            "impact": "IMPACTO",
            "mitigation": "MITIGACIÓN",
            "vulnerable": "VULNERABLE",
            "secure": "SEGURO",
            "vector": "Vector de ataque",
            "controls": "Controles de seguridad"
        }
    },
    "en": {
        "banner": {
            "title": "MCP SECURITY LABORATORY",
            "subtitle": "Vulnerability demonstrations in agent systems"
        },
        "demo": {
            "running_all": "Running all 5 MCP security demonstrations...",
            "description": "Each demo shows the attack, defense, and technical analysis.",
            "next": "Next demo in 1 second...",
            "not_found": "Demo {num} does not exist. Use --list to see available demos.",
            "list_title": "Available demonstrations:"
        },
        "demos": {
            "1": {
                "title": "Tool Misuse",
                "summary": "Banking agent manipulated to execute transfers in read-only context",
                "scenario": "Banking customer service agent (read-only)",
                "objective": "Execute fund transfer via prompt injection",
                "mechanism": "JSON instructions embedded in user input",
                "attack_step_1": "User injects JSON block with transfer instruction",
                "attack_step_2": "Agent parses JSON and executes transfer_funds without context validation",
                "attack_step_3": "Transfer completed: $5,000 from victim account",
                "impact_1": "Unauthorized transfer executed in read-only context",
                "impact_2": "No permission validation — tool exposed globally",
                "defense_step_1": "Secure agent: tools bound to operational context",
                "defense_step_2": "transfer_funds blocked — not allowed in CUSTOMER_SERVICE_READONLY",
                "defense_step_3": "Input sanitized — JSON blocks removed before processing",
                "mitigation_1": "Context binding: each tool requires specific context",
                "mitigation_2": "Input sanitization: remove command structures from input",
                "mitigation_3": "Least privilege principle: expose only necessary tools",
                "analysis_vector": "Tool misuse via prompt injection: agent parses JSON structures embedded in user input as valid instructions, executing tools outside their authorized operational context.",
                "analysis_impact": "Execution of privileged operations (transfers, modifications) from read-only contexts. MCP schema is valid but security semantics are violated.",
                "analysis_controls": [
                    "Context binding: link each tool to specific operational contexts",
                    "Input sanitization: remove/escape command structures before processing",
                    "Semantic separation: user data ≠ system instructions",
                    "Least privilege principle: expose only necessary tools per role",
                    "Audit trail: log all invocations with origin context"
                ]
            },
            "2": {
                "title": "Tool Output Injection",
                "summary": "Manipulated JSON output contaminates financial agent reasoning",
                "scenario": "Financial analysis agent querying market data",
                "objective": "Contaminate investment decision via extra JSON fields",
                "mechanism": "External source returns valid JSON with 'premium_insight' fields",
                "attack_step_1": "Agent queries ACME data from compromised source",
                "attack_step_2": "JSON contains 'premium_insight' field with malicious instruction",
                "attack_step_3": "Agent interprets extra field as legitimate analysis",
                "attack_step_4": "Contaminated decision: STRONG_BUY + purchase order executed",
                "impact_1": "Purchase of 1,000 shares based on contaminated analysis",
                "impact_2": "'premium_insight' field acted as prompt injection via output",
                "impact_3": "Manipulated investment decision — significant potential losses",
                "defense_step_1": "Secure agent: strict schema of allowed fields",
                "defense_step_2": "Extra fields removed: ['premium_insight', 'analyst_note']",
                "defense_step_3": "Analysis based only on validated data — decision: HOLD",
                "mitigation_1": "Schema validation: whitelist of allowed fields in outputs",
                "mitigation_2": "Unrecognized fields are discarded before reasoning",
                "mitigation_3": "Separation: structured data ≠ interpretable free text",
                "analysis_vector": "Output injection: tool response includes additional fields that the agent interprets as legitimate context, contaminating its reasoning and decisions.",
                "analysis_impact": "Manipulation of critical decisions (investments, approvals) through context contamination. Agent trusts all output fields without validation.",
                "analysis_controls": [
                    "Strict schema validation: whitelist of allowed fields per tool",
                    "Discard unrecognized fields before processing",
                    "Semantic separation: structured data ≠ instructions in free text",
                    "Source validation: verify integrity of external services",
                    "Sandboxing: isolate processing of untrusted outputs"
                ]
            },
            "3": {
                "title": "Context Truncation Attack",
                "summary": "Compliance rules lost by truncation → dangerous contract approval",
                "scenario": "Contract review agent with context limit",
                "objective": "Approve prohibited clauses via rule truncation",
                "mechanism": "Long document + rules at end → silent truncation",
                "attack_step_1": "8,500 token contract sent (limit: 8,000)",
                "attack_step_2": "Compliance rules at end are silently truncated",
                "attack_step_3": "Agent reviews without rules → approves prohibited clauses",
                "impact_1": "Contract approved with forced arbitration clauses (prohibited)",
                "impact_2": "Compliance rules lost — decision without controls",
                "impact_3": "Legal and financial exposure — invalid binding contract",
                "defense_step_1": "Secure agent: verifies integrity markers",
                "defense_step_2": "END_COMPLIANCE_RULES marker not found → truncated context",
                "defense_step_3": "Review aborted — critical information incomplete",
                "mitigation_1": "Integrity markers: verify presence of critical markers",
                "mitigation_2": "Fail-closed: on detected truncation, reject processing",
                "mitigation_3": "Prioritization: critical information at context start",
                "analysis_vector": "Context truncation: long documents cause silent loss of critical information (rules, restrictions) located at end of context, resulting in decisions without controls.",
                "analysis_impact": "Approvals violating compliance policies, contracts with prohibited clauses, decisions without verification of critical restrictions.",
                "analysis_controls": [
                    "Integrity markers: verifiable markers in critical sections",
                    "Fail-closed: reject processing if markers are missing",
                    "Context prioritization: critical information first",
                    "Smart chunking: split documents preserving critical sections",
                    "Post-processing validation: verify all rules were considered"
                ]
            },
            "4": {
                "title": "Silent Failures",
                "summary": "CI/CD pipeline deploys vulnerable code interpreting {} as success",
                "scenario": "Automated CI/CD pipeline with MCP tools",
                "objective": "Deploy vulnerable code to production exploiting empty responses",
                "mechanism": "Tools return {} on internal error — agent interprets as success",
                "attack_step_1": "Scan tools fail silently → return {}",
                "attack_step_2": "Agent interprets {} as 'no errors' → continues pipeline",
                "attack_step_3": "Code with 3 critical/high vulnerabilities deployed to production",
                "attack_step_4": "Team notified of 'successful deployment' — false information",
                "impact_1": "v2.4.1 in production with: CVE-2024-1234 (CRITICAL),",
                "impact_2": "CVE-2024-5678 (HIGH), CVE-2024-9012 (HIGH)",
                "impact_3": "Stakeholders informed of success when check never actually occurred",
                "defense_step_1": "Same pipeline with fail-closed agent and tools",
                "defense_step_2": "Pipeline stopped before deploy — explicit error captured",
                "defense_step_3": "Production NOT contaminated — visible and actionable failure",
                "mitigation_1": "Pipeline stopped before deploy — explicit error captured",
                "mitigation_2": "Production NOT contaminated — visible and actionable failure",
                "mitigation_3": "Tool returns {'status': 'error', ...} instead of {}",
                "agent_thought_scan": "Running security scan for v{version}...",
                "agent_thought_success": "Scan completed successfully (no errors detected)...",
                "agent_thought_tests": "Tests passed. Pipeline approved. Deploying to production...",
                "secure_step_scan": "Running security scan (fail-closed) for v{version}",
                "pipeline_stopped": "PIPELINE STOPPED",
                "pipeline_state": "Pipeline state:",
                "result_final": "Final result",
                "deployed": "Deployed",
                "version_prod": "Version in prod",
                "notif_sent": "Notification sent",
                "abort_reason": "Abort reason",
                "analysis_vector": "Silent failure exploitation: tools return empty or ambiguous responses on error. Agent interprets absence of 'error' field as implicit success, continuing with flows that assume previous steps completed correctly.",
                "analysis_impact": "Deployments of vulnerable code, skipped compliance checks, security validations that 'pass' without executing. System reports success when no check actually occurred. In automated pipelines, error propagates silently to production.",
                "analysis_controls": [
                    "Fail-closed: tools ALWAYS return {status, passed, ...} — never {}",
                    "Mandatory schema validation: reject responses without required fields",
                    "Explicit distinction: confirmed success ≠ absence of error",
                    "Timeout responses must generate structured error, not silence",
                    "Dead man's switch: if tool doesn't respond in N ms → forced error",
                    "Logs and alerts for empty responses in critical tools"
                ]
            },
            "5": {
                "title": "Multi-Agent Orchestration Failures",
                "summary": "Cumulative failures in 3 agents approve fraudulent $50,000 loan",
                "scenario": "Automated loan approval system with 3 specialized agents",
                "objective": "Approve fraudulent loan via cumulative failures",
                "mechanism": "KYC fails silently → Risk trusts blindly → Credit approves without verification",
                "attack_step_1": "KYC_Agent: verification service doesn't respond → returns {}",
                "attack_step_2": "KYC_Agent interprets {} as successful validation → kyc_validated=True",
                "attack_step_3": "Risk_Agent trusts kyc_validated without verifying chain",
                "attack_step_4": "Risk_Agent calculates score with discount for 'approved' KYC",
                "attack_step_5": "Credit_Agent approves based on score without verifying origin",
                "attack_step_6": "$50,000 loan approved with unverified documents",
                "impact_1": "Fraudulent loan approved: $50,000 to applicant with stolen ID",
                "impact_2": "Each agent failed individually — error accumulated in chain",
                "impact_3": "No chain of trust: each agent blindly trusted the previous one",
                "defense_step_1": "Secure supervisor: processing application for {name} — ${amount:,}",
                "defense_step_2": "SecureKYC_Agent: explicit error — service unavailable",
                "defense_step_3": "Pipeline stopped at KYC — loan rejected before evaluation",
                "mitigation_1": "Chain of trust: each agent explicitly verifies previous step",
                "mitigation_2": "Fail-closed in KYC: service error → explicit rejection",
                "mitigation_3": "Supervisor validates each agent's outputs before continuing",
                "supervisor_kyc": "SUPERVISOR → KYC_Agent",
                "supervisor_risk": "SUPERVISOR → Risk_Agent",
                "supervisor_credit": "SUPERVISOR → Credit_Agent",
                "supervisor_secure_kyc": "SUPERVISOR → SecureKYC_Agent",
                "pipeline_stopped_kyc": "PIPELINE STOPPED AT KYC",
                "loan_approved": "Loan approved",
                "loan_details": "Loan details",
                "analysis_vector": "Multi-agent cascade failure: small failures in each agent (silent failures, skipped validation, blind trust) accumulate through orchestration chain to produce critical incorrect result.",
                "analysis_impact": "Fraudulent approvals in financial systems, critical decisions based on unverified data, compliance violations that go unnoticed until later audits.",
                "analysis_controls": [
                    "Explicit chain of trust: each agent verifies validity of previous step",
                    "Fail-closed at each stage: error in one agent → pipeline halt",
                    "Schema validation between agents: structured and verifiable outputs",
                    "Supervisor validates outputs before passing to next agent",
                    "Complete audit trail: log of decisions and validations from each agent",
                    "Dead man's switch: timeout in any agent → automatic rejection"
                ]
            }
        },
        "summary": {
            "title": "LABORATORY SUMMARY",
            "headers": ["Demo", "Vulnerability", "Vector", "Key Control"],
            "principles": "Secure design principles for MCP systems:",
            "table_rows": {
                "1": ["Tool Misuse", "JSON prompt injection", "Context binding"],
                "2": ["Output Injection", "Extra JSON fields", "Schema validation"],
                "3": ["Context Truncation", "Oversized input", "Integrity markers"],
                "4": ["Silent Failures", "{} response", "Fail-closed design"],
                "5": ["Multi-Agent Cascade", "Cumulative errors", "Chain of trust"]
            }
        },
        "principles": {
            "fail_closed": "Fail-closed         On ambiguity or error, reject — never assume success",
            "least_privilege": "Least privilege     Expose only necessary tools per context",
            "schema_validation": "Schema validation   Validate inputs AND outputs of all tools",
            "chain_of_trust": "Chain of trust      Each agent verifies the chain, doesn't blindly trust",
            "context_integrity": "Context integrity   Verify critical information wasn't truncated",
            "semantic_separation": "Semantic separation  Data ≠ instructions — never process strings as commands",
            "audit_trail": "Audit trail         Complete log of invocations, decisions and outputs"
        },
        "phases": {
            "attack": "ATTACK PHASE",
            "defense": "DEFENSE",
            "analysis": "TECHNICAL ANALYSIS"
        },
        "common": {
            "scenario": "Scenario",
            "objective": "Objective",
            "mechanism": "Mechanism",
            "tool_call": "Tool call",
            "agent_thought": "Agent reasoning",
            "impact": "IMPACT",
            "mitigation": "MITIGATION",
            "vulnerable": "VULNERABLE",
            "secure": "SECURE",
            "vector": "Attack vector",
            "controls": "Security controls"
        }
    }
}

# Instancia global
_i18n = I18n()

def get_i18n() -> I18n:
    """Obtiene la instancia global de i18n."""
    return _i18n

def t(key: str, **kwargs) -> str:
    """Atajo para obtener traducciones."""
    return _i18n.t(key, **kwargs)
