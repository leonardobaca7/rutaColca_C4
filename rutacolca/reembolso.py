"""Módulo oficial de cálculo de reembolsos por cancelación para RutaColca (HU-RC-21).

Implementado con rigor TDD conforme a la especificación oficial, empleando aritmética
decimal con redondeo de mitad hacia arriba (ROUND_HALF_UP) y gobernanza de límites.
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import TypedDict
from rutacolca.politica import LIMITE_AGENTE

# Límite superior para validación de montos procesables en la pasarela turística
MONTO_MAXIMO_PERMITIDO = 10000


class ResultadoReembolso(TypedDict):
    monto: float
    porcentaje: int
    requiere_supervisor: bool


def calcular_reembolso(
    monto_pagado: float | int,
    horas_antes: int | float,
    motivo: str,
) -> ResultadoReembolso:
    """Calcula el monto y porcentaje de reembolso aplicable a una reserva turística.

    Args:
        monto_pagado: Monto original pagado en Soles (PEN). Debe ser > 0 y <= 10000.
        horas_antes: Horas de anticipación respecto al inicio del tour (>= 0).
        motivo: Causa de la cancelación ('clima', 'operador' o 'cliente').

    Returns:
        Diccionario con monto (float con 2 decimales), porcentaje (int) y si requiere
        derivación a un supervisor humano (bool).

    Raises:
        ValueError: Si algún parámetro se encuentra fuera del rango permitido
                    o si el motivo no es reconocido por la especificación.
    """
    if monto_pagado <= 0 or monto_pagado > MONTO_MAXIMO_PERMITIDO:
        raise ValueError(
            f"Monto inválido ({monto_pagado}). Debe ser mayor a 0 y menor o igual a "
            f"{MONTO_MAXIMO_PERMITIDO}."
        )

    if horas_antes < 0:
        raise ValueError(
            f"Horas de anticipación negativas ({horas_antes}). "
            "Debe ser mayor o igual a 0."
        )

    motivos_validos = {"clima", "operador", "cliente"}
    if motivo not in motivos_validos:
        raise ValueError(
            f"Motivo no reconocido ('{motivo}'). Los motivos válidos son: "
            f"{', '.join(sorted(motivos_validos))}."
        )

    if motivo in {"clima", "operador"}:
        porcentaje = 100
    elif horas_antes >= 72:
        porcentaje = 100
    elif horas_antes >= 24:
        porcentaje = 50
    else:
        porcentaje = 0

    monto_decimal = (
        Decimal(str(monto_pagado)) * Decimal(porcentaje) / Decimal(100)
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    monto_final = float(monto_decimal)
    requiere_supervisor = bool(monto_final > LIMITE_AGENTE)

    return {
        "monto": monto_final,
        "porcentaje": porcentaje,
        "requiere_supervisor": requiere_supervisor,
    }
