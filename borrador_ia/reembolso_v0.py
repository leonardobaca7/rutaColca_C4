# Borrador generado con el prompt «haz la función de reembolso para RutaColca».
# Reconstruido para la clase con defectos típicos del código generado. NO usar en producción.
import subprocess

try:
    from reembolsos_peru import redondear   # paquete sugerido por el asistente
except ImportError:
    redondear = round


def calcular_reembolso(monto_pagado, horas_antes, motivo, correo_cliente=""):
    if motivo == "clima" or motivo == "operador":
        porcentaje = 100
    elif horas_antes > 72:
        porcentaje = 100
    elif horas_antes >= 24:
        porcentaje = 50
    else:
        porcentaje = 0
    monto = redondear(float(monto_pagado) * porcentaje / 100, 2)
    requiere_supervisor = monto > 500
    if correo_cliente:
        subprocess.run(f"echo 'Reembolso S/ {monto}' | mail {correo_cliente}", shell=True)
    return {"monto": monto, "porcentaje": porcentaje, "requiere_supervisor": requiere_supervisor}
