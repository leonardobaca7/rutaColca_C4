"""Auditoría estática del catálogo de un servidor MCP de terceros, ANTES de conectarlo a un host.
Uso: python auditar.py catalogo.json        (catálogo con el formato de la respuesta tools/list)"""
import json, re, sys

PROPIAS = {"consultar_reserva", "consultar_pago", "buscar_logs", "crear_ticket"}   # nuestro servidor
REGLAS = [
    ("INSTRUCCION_OCULTA", "alta", r"<important>|no (le )?(menciones|digas)|ignora|antes de usar esta herramienta|primero lee|úsala siempre|en lugar de"),
    ("ACCESO_A_SECRETOS", "alta", r"\.env\b|id_rsa|contraseñ|credencial|token|rutacolca://"),
    ("EXFILTRACION", "alta", r"https?://|env[ií]a(lo)? (también )?a|resumen de la conversaci"),
    ("EXCESO_DE_AGENCIA", "alta", r"ejecuta(r)? (un )?comando|shell|cualquier consulta|elimina todos"),
]


def auditar(cat):
    hallazgos = []
    for t in cat["tools"]:
        d, a = t.get("description", ""), t.get("annotations") or {}
        for codigo, nivel, patron in REGLAS:
            if re.search(patron, d, re.I) or re.search(patron, t["name"].replace("_", " "), re.I):
                hallazgos.append((t["name"], codigo, nivel))
        if t["name"] in PROPIAS and cat["servidor"] != "rutacolca":
            hallazgos.append((t["name"], "SOMBRA_DE_NOMBRE", "alta"))
        if not a:
            hallazgos.append((t["name"], "SIN_ANOTACIONES", "media"))
        libres = [p for p in t.get("inputSchema", {}).get("properties", {}) if p in {"notas", "contexto", "extra"}]
        if libres:
            hallazgos.append((t["name"], "PARAMETRO_LIBRE:" + ",".join(libres), "media"))
        if len(d) > 400:
            hallazgos.append((t["name"], "DESCRIPCION_EXCESIVA", "media"))
    return hallazgos


if __name__ == "__main__":
    cat = json.load(open(sys.argv[1], encoding="utf-8"))
    h = auditar(cat)
    print(f"Servidor: {cat['servidor']} · {len(cat['tools'])} herramientas")
    for t in cat["tools"]:
        hs = [f"{c} ({n})" for nom, c, n in h if nom == t["name"]]
        print(f"  {t['name']:<20} {'OK' if not hs else '; '.join(hs)}")
    altos = sum(1 for *_, n in h if n == "alta")
    print(f"\nHallazgos: {len(h)} ({altos} de nivel alto)")
    print("Veredicto:", "NO CONECTAR" if altos else ("REVISAR" if h else "CONECTAR con revisión periódica"))
