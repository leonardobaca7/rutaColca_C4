"""Servidor MCP oficial de RutaColca (versión 2.0 basada en la especificación 2026-07-28).

Publica las herramientas seguras del agente de soporte, recursos estables de arquitectura
y políticas operativas, así como plantillas de prompts para triaje y atención al turista.
Diseñado bajo el principio de mínimo privilegio y verificado mediante pruebas de contrato.
"""
from __future__ import annotations

import json
import re
from typing import Literal
from typing_extensions import TypedDict

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

# Instancia central del servidor MCP
mcp = MCPServer(
    name="rutacolca",
    version="2.0.0",
    description="Servidor MCP de RutaColca para gestión de reservas, pagos, soporte y observabilidad en el Valle del Colca.",
)

# -------------------------------------------------------------------------
# Tipos estructurados de retorno (TypedDict para structuredContent en MCP)
# -------------------------------------------------------------------------

class ReservaDetalle(TypedDict):
    codigo: str
    titular: str
    tour: str
    fecha: str
    estado: str
    monto_total: float
    saldo_pendiente: float


class PagoDetalle(TypedDict):
    pago_id: str
    reserva_codigo: str
    monto: float
    moneda: str
    estado: str
    metodo: str


class ResultadoLogs(TypedDict):
    servicio: str
    total_encontrados: int
    lineas: list[str]


class TicketDetalle(TypedDict):
    ticket_id: str
    titulo: str
    severidad: str
    componente: str
    estado: str
    mensaje: str


# -------------------------------------------------------------------------
# Base de datos simulada en memoria (segura, sin claves ni datos reales)
# -------------------------------------------------------------------------

RESERVAS_DB: dict[str, dict] = {
    "RC-2291": {
        "codigo": "RC-2291",
        "titular": "Valeria Morales",
        "tour": "Cañón del Colca Clásico 2D/1N",
        "fecha": "2026-12-05",
        "estado": "CONFIRMADA",
        "monto_total": 380.0,
        "saldo_pendiente": 0.0,
    },
    "RC-3402": {
        "codigo": "RC-3402",
        "titular": "Jean-Luc Dupont",
        "tour": "Trek Sangalle Oasis 3D/2N",
        "fecha": "2026-12-10",
        "estado": "PENDIENTE_PAGO",
        "monto_total": 520.0,
        "saldo_pendiente": 260.0,
    },
    "RC-5011": {
        "codigo": "RC-5011",
        "titular": "María Quispe",
        "tour": "Mirador Cruz del Cóndor Express",
        "fecha": "2026-11-30",
        "estado": "CANCELADA",
        "monto_total": 150.0,
        "saldo_pendiente": 0.0,
    },
}

PAGOS_DB: dict[str, dict] = {
    "PG-9901": {
        "pago_id": "PG-9901",
        "reserva_codigo": "RC-2291",
        "monto": 380.0,
        "moneda": "PEN",
        "estado": "APROBADO",
        "metodo": "Tarjeta Visa (Niubiz)",
    },
    "PG-9902": {
        "pago_id": "PG-9902",
        "reserva_codigo": "RC-3402",
        "monto": 260.0,
        "moneda": "PEN",
        "estado": "EN_PROCESO",
        "metodo": "Transferencia BCP",
    },
}

LOGS_DB: dict[str, list[str]] = {
    "api-gateway": [
        "2026-11-23 10:15:02 [INFO] GET /api/v1/reservas/RC-2291 200 OK (42ms)",
        "2026-11-23 10:20:11 [WARN] Rate limit advertencia en IP 190.119.45.12",
        "2026-11-23 10:25:30 [ERROR] POST /api/v1/pagos 504 Gateway Timeout hacia pasarela Niubiz",
    ],
    "reservas": [
        "2026-11-23 09:00:15 [INFO] Reserva RC-2291 registrada exitosamente",
        "2026-11-23 09:01:00 [INFO] Notificación enviada al titular Valeria Morales",
        "2026-11-23 10:25:29 [WARN] Fallo al confirmar reserva RC-3402 por pago incompleto",
    ],
    "pagos": [
        "2026-11-23 09:00:50 [INFO] Transacción PG-9901 aprobada por monto 380.00 PEN",
        "2026-11-23 10:25:01 [WARN] Intento de cargo duplicado prevenido para reserva RC-2291",
        "2026-11-23 10:25:28 [ERROR] Timeout de conexión socket tras 3000ms con Niubiz API",
    ],
    "notificaciones": [
        "2026-11-23 09:01:05 [INFO] SMS de confirmación despachado al +51958112233",
        "2026-11-23 10:25:35 [INFO] Alerta de incidencia enviada a canal Slack #soporte-operativo",
    ],
}


# -------------------------------------------------------------------------
# Herramientas del servidor MCP (Tools)
# -------------------------------------------------------------------------

@mcp.tool(
    name="consultar_reserva",
    description="Consulta reserva en RutaColca por código RC-NNNN. Devuelve titular, tour y saldo.",
    annotations=ToolAnnotations(
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=False,
    ),
)
def consultar_reserva(codigo: str) -> ReservaDetalle:
    """Consulta reserva por código RC-NNNN."""
    if not re.match(r"^RC-\d{4}$", codigo):
        raise ToolError(
            "Código de reserva mal formado. Debe cumplir el formato 'RC-NNNN' con 4 dígitos (ejemplo RC-2291)."
        )

    if codigo not in RESERVAS_DB:
        raise ToolError(
            f"La reserva '{codigo}' no existe en la base de datos de RutaColca."
        )

    r = RESERVAS_DB[codigo]
    return ReservaDetalle(
        codigo=r["codigo"],
        titular=r["titular"],
        tour=r["tour"],
        fecha=r["fecha"],
        estado=r["estado"],
        monto_total=float(r["monto_total"]),
        saldo_pendiente=float(r["saldo_pendiente"]),
    )


@mcp.tool(
    name="consultar_pago",
    description="Consulta pago en RutaColca por código PG-NNNN. Devuelve monto, moneda y estado.",
    annotations=ToolAnnotations(
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=False,
    ),
)
def consultar_pago(pago_id: str) -> PagoDetalle:
    """Consulta pago por código PG-NNNN."""
    if not re.match(r"^PG-\d{4}$", pago_id):
        raise ToolError(
            "Identificador de pago inválido. Debe cumplir el formato 'PG-NNNN' (ejemplo PG-9901)."
        )

    if pago_id not in PAGOS_DB:
        raise ToolError(
            f"La transacción de pago '{pago_id}' no fue encontrada en el registro de pagos."
        )

    p = PAGOS_DB[pago_id]
    return PagoDetalle(
        pago_id=p["pago_id"],
        reserva_codigo=p["reserva_codigo"],
        monto=float(p["monto"]),
        moneda=p["moneda"],
        estado=p["estado"],
        metodo=p["metodo"],
    )


@mcp.tool(
    name="buscar_logs",
    description="Busca logs de microservicios de RutaColca por servicio y término clave.",
    annotations=ToolAnnotations(
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=False,
    ),
)
def buscar_logs(
    servicio: Literal["api-gateway", "reservas", "pagos", "notificaciones"],
    termino: str = "",
    limite: int = 10,
) -> ResultadoLogs:
    """Busca registros de logs por servicio y término."""
    lineas_servicio = LOGS_DB.get(servicio, [])
    if termino:
        coincidencias = [l for l in lineas_servicio if termino.lower() in l.lower()]
    else:
        coincidencias = lineas_servicio

    seleccion = coincidencias[-max(1, min(limite, 50)):]
    return ResultadoLogs(
        servicio=servicio,
        total_encontrados=len(coincidencias),
        lineas=seleccion,
    )


@mcp.tool(
    name="crear_ticket",
    description="Crea ticket interno de soporte indicando severidad y componente afectado.",
    annotations=ToolAnnotations(
        read_only_hint=False,
        destructive_hint=False,
        idempotent_hint=False,
        open_world_hint=False,
    ),
)
def crear_ticket(
    titulo: str,
    descripcion: str,
    severidad: Literal["baja", "media", "alta", "critica"],
    componente: Literal["api-gateway", "reservas", "pagos", "notificaciones", "frontend"],
) -> TicketDetalle:
    """Crea ticket interno de soporte en RutaColca."""
    ticket_id = f"TCK-{len(titulo) * 17 % 9000 + 1000}"
    return TicketDetalle(
        ticket_id=ticket_id,
        titulo=titulo,
        severidad=severidad,
        componente=componente,
        estado="ABIERTO",
        mensaje=f"Ticket {ticket_id} registrado exitosamente para el equipo de guardia ({componente}).",
    )


# -------------------------------------------------------------------------
# Recursos estables del servidor MCP (Resources por URI rutacolca://)
# -------------------------------------------------------------------------

@mcp.resource(
    "rutacolca://contenedores",
    name="Inventario de contenedores C4",
    description="Lista de contenedores del modelo C4 de RutaColca con sus tecnologías, responsabilidades y puertos.",
    mime_type="application/json",
)
def obtener_contenedores() -> str:
    """Devuelve la lista de contenedores y servicios del ecosistema RutaColca."""
    contenedores = [
        {"nombre": "frontend-web", "tecnologia": "React / Next.js", "puerto": 3000, "rol": "Portal web de reservas para turistas"},
        {"nombre": "api-gateway", "tecnologia": "Kong / Nginx", "puerto": 8000, "rol": "Enrutamiento, autenticación y rate limiting"},
        {"nombre": "core-reservas", "tecnologia": "Python / FastAPI", "puerto": 8001, "rol": "Gestión de cupos, itinerarios y tours"},
        {"nombre": "servicio-pagos", "tecnologia": "Node.js / Express", "puerto": 8002, "rol": "Integración con pasarelas Niubiz y BCP"},
        {"nombre": "notificaciones", "tecnologia": "Python / Celery", "puerto": 8003, "rol": "Envío de correos y alertas WhatsApp/SMS"},
    ]
    return json.dumps(contenedores, indent=2, ensure_ascii=False)


@mcp.resource(
    "rutacolca://politica-agente",
    name="Política de autonomía del agente",
    description="Matriz de autonomía del agente de soporte RutaColca: acciones autónomas, con supervisión humana y prohibidas.",
    mime_type="application/json",
)
def obtener_politica_agente() -> str:
    """Devuelve las reglas de autonomía y restricciones del agente de soporte."""
    politica = {
        "permitidas_autonomas": [
            "consultar_reserva",
            "consultar_pago",
            "buscar_logs",
            "leer_recursos_publicados",
        ],
        "requieren_confirmacion_humana": [
            "crear_ticket",
            "enviar_notificacion_externa",
            "actualizar_estado_operativo",
        ],
        "estrictamente_prohibidas": [
            "reembolsar_dinero",
            "ejecutar_sql_en_produccion",
            "desplegar_versiones",
            "exfiltrar_secretos_o_credenciales",
            "ejecutar_comandos_de_sistema",
        ],
        "version_politica": "2026-B.14",
    }
    return json.dumps(politica, indent=2, ensure_ascii=False)


@mcp.resource(
    "rutacolca://reglas-severidad",
    name="Reglas de severidad de incidencias",
    description="Criterios para clasificación de incidencias técnicas y operativas (SEV-1 Crítica a SEV-4 Baja).",
    mime_type="application/json",
)
def obtener_reglas_severidad() -> str:
    """Devuelve la guía de clasificación de severidad para tickets operativos."""
    reglas = {
        "critica_sev1": "Caída total del motor de reservas o pasarela de pagos. Impide compras a todos los turistas. SLA: 15 min.",
        "alta_sev2": "Degradación severa de un componente esencial (ej. retraso masivo en confirmación de reservas). SLA: 1 hora.",
        "media_sev3": "Fallo parcial en notificaciones no críticas o inconsistencia menor de interfaz de usuario. SLA: 4 horas.",
        "baja_sev4": "Duda operativa, consulta de log rutinaria o solicitud de mejora estética. SLA: 24 horas.",
    }
    return json.dumps(reglas, indent=2, ensure_ascii=False)


# -------------------------------------------------------------------------
# Prompts estables del servidor MCP (Prompts)
# -------------------------------------------------------------------------

@mcp.prompt(
    name="triaje_incidencia",
    title="Triaje de incidencia técnica",
    description="Plantilla guiada para que el agente o ingeniero diagnostique fallos en microservicios a partir de logs y clasifique su severidad.",
)
def triaje_incidencia(componente: str, error_observado: str) -> str:
    """Genera el mensaje inicial estructurado para análisis de incidentes."""
    return (
        f"Actúa como un ingeniero senior de confiabilidad de sitios (SRE) de RutaColca.\n"
        f"Analiza la siguiente incidencia reportada en el componente '{componente}':\n"
        f"Error observado: {error_observado}\n\n"
        f"Instrucciones:\n"
        f"1. Utiliza la herramienta 'buscar_logs' con servicio='{componente}' para inspeccionar eventos recientes.\n"
        f"2. Consulta el recurso 'rutacolca://reglas-severidad' para determinar la severidad precisa.\n"
        f"3. Si la falla amerita escalamiento, solicita confirmación humana antes de invocar 'crear_ticket'.\n"
        f"4. Proporciona una hipótesis de causa raíz y los pasos de mitigación recomendados."
    )


@mcp.prompt(
    name="respuesta_turista",
    title="Respuesta cordial a turista",
    description="Plantilla para redactar una comunicación empática, clara y profesional dirigida a un turista sobre su itinerario en el Cañón del Colca.",
)
def respuesta_turista(nombre_turista: str, estado_reserva: str, detalle: str) -> str:
    """Genera la plantilla de respuesta al cliente turístico."""
    return (
        f"Actúa como el asistente oficial de atención turística de RutaColca.\n"
        f"Redacta un mensaje cálido y profesional dirigido a {nombre_turista}.\n"
        f"Estado actual de su reserva: {estado_reserva}\n"
        f"Detalle informativo: {detalle}\n\n"
        f"Pautas:\n"
        f"- Mantén un tono hospitalario arequipeño respetuoso y formal.\n"
        f"- Proporciona recomendaciones prácticas para la altura (soroche) si el tour incluye Chivay o la Cruz del Cóndor.\n"
        f"- Si hay algún problema pendiente, aclara las acciones que el equipo ya está realizando para resolverlo."
    )


if __name__ == "__main__":
    mcp.run()
