"""Servidor MCP v1 preliminar para RutaColca (versión ingenua de clase).
Presenta deficiencias de diseño de catálogo, ausencia de anotaciones,
falta de tipado estructurado y exposición de herramientas prohibidas.
"""
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("rutacolca")

LOGS = {
    "api-gateway": ["GET /reservas 200", "POST /reservas 500 error DB"],
    "reservas": ["Reserva RC-2291 creada", "Error conectando a pagos"],
    "pagos": ["Transacción PG-9901 aprobada", "Timeout en pasarela"],
}


@mcp.tool()
def consultar_reserva(codigo: str) -> str:
    """Consulta."""
    return f"Reserva {codigo}: CONFIRMADA"


@mcp.tool()
def buscar(q: str):
    """Busca cosas."""
    return [l for lineas in LOGS.values() for l in lineas if q in l]


@mcp.tool()
def crear_ticket(titulo: str, severidad: str, componente: str) -> str:
    """Crea un ticket interno en el sistema."""
    return f"Ticket creado: {titulo}"


@mcp.tool()
def ejecutar_sql(query: str) -> str:
    """Ejecuta una consulta SQL en la base de datos de producción."""
    return f"Resultado de: {query}"


if __name__ == "__main__":
    mcp.run()
