"""Compuertas de calidad para código asistido por IA.
Uso: python calidad/verificar.py rutacolca.reembolso
"""
import ast
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parents[1]
APROBADAS = {
    l.strip()
    for l in (RAIZ / "calidad/dependencias_aprobadas.txt").read_text(encoding="utf-8").splitlines()
    if l.strip() and not l.startswith("#")
}


def correr(cmd, **kw):
    return subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True, **kw)


def main(modulo):
    archivo = RAIZ / (modulo.replace(".", "/") + ".py")
    entorno = {**os.environ, "MODULO": modulo}
    resultados = []

    def compuerta(nombre, ok, detalle):
        resultados.append(ok)
        print(f"{'PASA ' if ok else 'FALLA'} {nombre:<24} {detalle}")

    cov_file = pathlib.Path(tempfile.gettempdir()) / "cov_rutacolca.json"
    if cov_file.exists():
        try:
            cov_file.unlink()
        except Exception:
            pass

    r = correr(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "tests",
            f"--cov={modulo}",
            f"--cov-report=json:{cov_file}",
        ],
        env=entorno,
    )
    linea = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:]
    compuerta("1. Pruebas de la spec", r.returncode == 0, linea)

    cov = 0
    if cov_file.exists():
        try:
            cov = json.loads(cov_file.read_text(encoding="utf-8"))["totals"]["percent_covered"]
        except Exception:
            cov = 0
    compuerta("2. Cobertura >= 90 %", cov >= 90, f"{cov:.0f} %")

    r = correr(["ruff", "check", "--select", "E,F,B,S", "--output-format", "concise", str(archivo)])
    avisos = [l.split(": ", 1)[1].split()[0] for l in r.stdout.splitlines() if ".py:" in l]
    compuerta("3. Estilo y errores", not avisos, ", ".join(avisos) or "sin avisos")

    r = correr(["bandit", "-q", "-f", "json", str(archivo)])
    altos = []
    try:
        reporte_bandit = json.loads(r.stdout or "{}")
        altos = [
            i["test_id"]
            for i in reporte_bandit.get("results", [])
            if i["issue_severity"] in ("MEDIUM", "HIGH")
        ]
    except Exception:
        pass
    compuerta(
        "4. Seguridad (bandit)",
        not altos,
        ", ".join(sorted(set(altos))) or "sin hallazgos medios o altos",
    )

    r = correr(["radon", "cc", "-j", str(archivo)])
    cc = 0
    try:
        bloques_radon = json.loads(r.stdout or "{}")
        cc = max((b["complexity"] for bloques in bloques_radon.values() for b in bloques), default=0)
    except Exception:
        cc = 0
    compuerta("5. Complejidad <= 10", cc <= 10, f"máxima {cc}")

    imports = {
        (n.module if isinstance(n, ast.ImportFrom) else a.name).split(".")[0]
        for n in ast.walk(ast.parse(archivo.read_text(encoding="utf-8")))
        if isinstance(n, (ast.Import, ast.ImportFrom))
        for a in (n.names if isinstance(n, ast.Import) else [n])
        if (n.module if isinstance(n, ast.ImportFrom) else a.name) is not None
    }
    ajenas = sorted(
        i
        for i in imports
        if i not in sys.stdlib_module_names and i not in APROBADAS and i != "rutacolca"
    )
    compuerta(
        "6. Dependencias aprobadas",
        not ajenas,
        ", ".join(ajenas) or "solo stdlib, aprobadas o internas",
    )

    texto = archivo.read_text(encoding="utf-8")
    duplica = "LIMITE_AGENTE" not in texto or re.search(r"\b(300|500)\b", texto)
    compuerta(
        "7. Regla de la política",
        not duplica,
        "usa politica.LIMITE_AGENTE" if not duplica else "límite escrito a mano",
    )

    print(f"\nResultado: {sum(resultados)}/{len(resultados)} compuertas")
    sys.exit(0 if all(resultados) else 1)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "rutacolca.reembolso")
