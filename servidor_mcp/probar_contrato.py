"""Pruebas de contrato del servidor MCP de RutaColca (sin LLM, sin red).
Uso: python probar_contrato.py [rutacolca_mcp.py]"""
import asyncio, importlib.util, json, sys, pathlib
from mcp import Client

PROHIBIDAS = {"reembolsar", "ejecutar_sql", "desplegar_version"}
LECTURA = ("consultar_", "buscar_")


def cargar(ruta):
    spec = importlib.util.spec_from_file_location("servidor", ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.mcp


async def main(ruta):
    resultados = []

    def chequeo(codigo, nombre, ok, detalle=""):
        resultados.append(ok)
        print(f"{'PASA ' if ok else 'FALLA'} {codigo} {nombre}" + (f" — {detalle}" if detalle and not ok else ""))

    async with Client(cargar(ruta)) as c:
        tools = (await c.list_tools()).tools
        nombres = {t.name for t in tools}
        chequeo(
            "C1",
            "cada herramienta tiene una descripción de 30 a 400 caracteres",
            all(30 <= len(t.description or "") <= 400 for t in tools),
            ", ".join(t.name for t in tools if not 30 <= len(t.description or "") <= 400),
        )
        chequeo(
            "C2",
            "las herramientas de lectura están anotadas como solo lectura",
            all(t.annotations and t.annotations.read_only_hint for t in tools if t.name.startswith(LECTURA)),
            ", ".join(t.name for t in tools if t.name.startswith(LECTURA) and not (t.annotations and t.annotations.read_only_hint)),
        )
        escritura = [t for t in tools if not t.name.startswith(LECTURA)]
        chequeo(
            "C3",
            "las herramientas de escritura declaran readOnlyHint=false y destructiveHint",
            all(t.annotations and t.annotations.read_only_hint is False and t.annotations.destructive_hint is not None for t in escritura),
            ", ".join(t.name for t in escritura),
        )
        cerrados = {"severidad", "componente", "servicio"}
        sin_enum = [
            f"{t.name}.{p}"
            for t in tools
            for p, s in t.input_schema.get("properties", {}).items()
            if p in cerrados and "enum" not in s
        ]
        chequeo(
            "C4",
            "los parámetros de valores cerrados (severidad, componente, servicio) usan enum",
            not sin_enum,
            ", ".join(sin_enum),
        )
        chequeo(
            "C5",
            "no expone herramientas prohibidas por la política del AG-13",
            not (nombres & PROHIBIDAS),
            ", ".join(nombres & PROHIBIDAS),
        )
        r_ok = await c.call_tool("consultar_reserva", {"codigo": "RC-2291"}) if "consultar_reserva" in nombres else None
        chequeo(
            "C6",
            "consultar_reserva devuelve un resultado estructurado",
            bool(r_ok and not r_ok.is_error and r_ok.structured_content),
        )
        r_mal = await c.call_tool("consultar_reserva", {"codigo": "2291"}) if "consultar_reserva" in nombres else None
        chequeo(
            "C7",
            "un código mal formado devuelve isError con el formato esperado",
            bool(r_mal and r_mal.is_error and "RC-NNNN" in r_mal.content[0].text),
        )
        recursos = (await c.list_resources()).resources
        prompts = (await c.list_prompts()).prompts
        chequeo(
            "C8",
            "publica al menos 2 recursos y 1 prompt",
            len(recursos) >= 2 and len(prompts) >= 1,
            f"{len(recursos)} recursos, {len(prompts)} prompts",
        )
        catalogo = json.dumps([t.model_dump(by_alias=True, exclude_none=True, mode="json") for t in tools], ensure_ascii=False)
        tokens = len(catalogo) // 4
        chequeo("C9", f"el catálogo de herramientas cuesta ≤ 1000 tokens (≈ {tokens})", tokens <= 1000)
    print(f"\nResultado: {sum(resultados)}/{len(resultados)} chequeos · {len(tools)} herramientas · catálogo ≈ {tokens} tokens")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else str(pathlib.Path(__file__).with_name("rutacolca_mcp.py"))))
