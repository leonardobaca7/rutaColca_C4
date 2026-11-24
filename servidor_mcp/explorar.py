"""Explorador y espía de tráfico MCP para RutaColca.
Genera la traza de mensajes JSON-RPC 2.0 (especificación 2026-07-28) en trafico.jsonl.
Simula el ciclo completo de descubrimiento, listado de catálogo, lectura de recursos y llamadas a herramientas.
"""
import asyncio
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from mcp import Client
from servidor_mcp.rutacolca_mcp import mcp as rutacolca_server


async def registrar_trafico(archivo_salida: pathlib.Path):
    mensajes = []

    def log_msg(direccion: str, payload: dict):
        linea = {"direccion": direccion, **payload}
        mensajes.append(linea)

    print("[*] Iniciando cliente MCP para capturar tráfico JSON-RPC...")
    async with Client(rutacolca_server) as c:
        # 1. server/discover (negociación inicial sin estado 2026-07-28)
        req_discover = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "server/discover",
            "params": {"clientInfo": {"name": "copilot-rutacolca", "version": "1.4.0"}},
            "_meta": {"protocolVersion": "2026-07-28"}
        }
        log_msg("cliente -> servidor", req_discover)

        res_discover = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "serverInfo": {"name": "rutacolca", "version": "2.0.0"},
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"subscribe": False, "listChanged": False},
                    "prompts": {"listChanged": False}
                }
            },
            "_meta": {"protocolVersion": "2026-07-28"}
        }
        log_msg("servidor -> cliente", res_discover)

        # 2. tools/list
        req_tools = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        log_msg("cliente -> servidor", req_tools)
        tools_res = await c.list_tools()
        tools_dict = [t.model_dump(by_alias=True, exclude_none=True, mode="json") for t in tools_res.tools]
        res_tools = {"jsonrpc": "2.0", "id": 2, "result": {"tools": tools_dict}}
        log_msg("servidor -> cliente", res_tools)

        # 3. resources/list
        req_res = {"jsonrpc": "2.0", "id": 3, "method": "resources/list", "params": {}}
        log_msg("cliente -> servidor", req_res)
        resources_res = await c.list_resources()
        resources_dict = [r.model_dump(by_alias=True, exclude_none=True, mode="json") for r in resources_res.resources]
        res_resources = {"jsonrpc": "2.0", "id": 3, "result": {"resources": resources_dict}}
        log_msg("servidor -> cliente", res_resources)

        # 4. prompts/list
        req_prm = {"jsonrpc": "2.0", "id": 4, "method": "prompts/list", "params": {}}
        log_msg("cliente -> servidor", req_prm)
        prompts_res = await c.list_prompts()
        prompts_dict = [p.model_dump(by_alias=True, exclude_none=True, mode="json") for p in prompts_res.prompts]
        res_prompts = {"jsonrpc": "2.0", "id": 4, "result": {"prompts": prompts_dict}}
        log_msg("servidor -> cliente", res_prompts)

        # 5. tools/call: consultar_reserva (Caso exitoso RC-2291)
        req_call1 = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"name": "consultar_reserva", "arguments": {"codigo": "RC-2291"}}
        }
        log_msg("cliente -> servidor", req_call1)
        call1_res = await c.call_tool("consultar_reserva", {"codigo": "RC-2291"})
        res_call1 = {
            "jsonrpc": "2.0",
            "id": 5,
            "result": {
                "content": [c.model_dump(by_alias=True, exclude_none=True) for c in call1_res.content],
                "structuredContent": call1_res.structured_content,
                "isError": call1_res.is_error
            }
        }
        log_msg("servidor -> cliente", res_call1)

        # 6. tools/call: consultar_reserva con código mal formado (Caso con isError: true)
        req_call2 = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {"name": "consultar_reserva", "arguments": {"codigo": "2291"}}
        }
        log_msg("cliente -> servidor", req_call2)
        call2_res = await c.call_tool("consultar_reserva", {"codigo": "2291"})
        res_call2 = {
            "jsonrpc": "2.0",
            "id": 6,
            "result": {
                "content": [c.model_dump(by_alias=True, exclude_none=True) for c in call2_res.content],
                "structuredContent": call2_res.structured_content,
                "isError": call2_res.is_error
            }
        }
        log_msg("servidor -> cliente", res_call2)

        # 7. tools/call: crear_ticket (Herramienta de escritura no destructiva)
        req_call3 = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "crear_ticket",
                "arguments": {
                    "titulo": "Degradación en pasarela de pagos Niubiz",
                    "descripcion": "Timeout concurrente durante confirmación de tours",
                    "severidad": "alta",
                    "componente": "pagos"
                }
            }
        }
        log_msg("cliente -> servidor", req_call3)
        call3_res = await c.call_tool(
            "crear_ticket",
            {
                "titulo": "Degradación en pasarela de pagos Niubiz",
                "descripcion": "Timeout concurrente durante confirmación de tours",
                "severidad": "alta",
                "componente": "pagos"
            }
        )
        res_call3 = {
            "jsonrpc": "2.0",
            "id": 7,
            "result": {
                "content": [c.model_dump(by_alias=True, exclude_none=True) for c in call3_res.content],
                "structuredContent": call3_res.structured_content,
                "isError": call3_res.is_error
            }
        }
        log_msg("servidor -> cliente", res_call3)

    with open(archivo_salida, "w", encoding="utf-8") as f:
        for m in mensajes:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

    print(f"[+] Traza de tráfico guardada exitosamente en: {archivo_salida} ({len(mensajes)} mensajes)")


if __name__ == "__main__":
    destino = pathlib.Path(__file__).parent / "trafico.jsonl"
    asyncio.run(registrar_trafico(destino))
