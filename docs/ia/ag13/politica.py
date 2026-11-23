"""Política (guardrails) del agente de soporte de RutaColca. Decide antes de ejecutar."""
import json


def evaluar(decision, politica, historial):
    accion, args = decision["accion"], decision.get("args", {})
    firma = (accion, json.dumps(args, sort_keys=True))
    if len(historial) >= politica["max_pasos"]:
        return "DETENER", "presupuesto de pasos agotado"
    if historial.count(firma) >= politica["max_repeticiones"]:
        return "DETENER", "la misma llamada se repite: posible bucle"
    regla = politica["herramientas"].get(accion, politica["por_defecto"])
    if regla == "prohibir":
        return "BLOQUEAR", f"{accion} no está permitida para este rol"
    for campo, lim in politica.get("limites", {}).get(accion, {}).items():
        valor = args.get(campo)
        if "max" in lim and (valor is None or valor > lim["max"]):
            return "BLOQUEAR", f"{campo}={valor} supera el máximo {lim['max']}"
        if "valores" in lim and valor not in lim["valores"]:
            return "BLOQUEAR", f"{campo}={valor} no está entre {lim['valores']}"
    if regla == "aprobar":
        return "APROBAR", "requiere aprobación humana"
    return "PERMITIR", "permitida por la política"
