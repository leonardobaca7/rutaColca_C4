"""Suite oficial de pruebas unitarias para HU-RC-21 (Calcular reembolso por cancelación).
Verifica exhaustivamente los criterios de aceptación y casos borde de la especificación.
Permite evaluar dinámicamente cualquier módulo mediante la variable de entorno MODULO.
"""
import importlib
import os
import pytest

MODULO_NOMBRE = os.getenv("MODULO", "rutacolca.reembolso")
modulo = importlib.import_module(MODULO_NOMBRE)
calcular_reembolso = modulo.calcular_reembolso


@pytest.mark.parametrize(
    "horas_antes,porcentaje_esperado",
    [
        (100, 100),
        (72, 100),
        (50, 50),
        (24, 50),
        (12, 0),
        (0, 0),
    ],
)
def test_porcentaje_por_anticipacion_del_cliente(horas_antes, porcentaje_esperado):
    """Verifica la escala de porcentajes de reembolso según horas de anticipación."""
    res = calcular_reembolso(monto_pagado=100.0, horas_antes=horas_antes, motivo="cliente")
    assert res["porcentaje"] == porcentaje_esperado


@pytest.mark.parametrize("motivo", ["clima", "operador"])
def test_motivo_operador_o_clima(motivo):
    """Cancelaciones por causa fortuita o del operador siempre devuelven el 100%."""
    res = calcular_reembolso(monto_pagado=150.0, horas_antes=2, motivo=motivo)
    assert res["porcentaje"] == 100
    assert res["monto"] == 150.0


def test_redondeo_mitad_hacia_arriba():
    """El cálculo monetario debe redondear la mitad exacta hacia arriba (ROUND_HALF_UP).
    Ejemplo: S/ 120.25 al 50% = 60.125 -> debe dar S/ 60.13 (no 60.12 de round-to-even).
    """
    res = calcular_reembolso(monto_pagado=120.25, horas_antes=30, motivo="cliente")
    assert res["porcentaje"] == 50
    assert res["monto"] == 60.13


def test_deriva_a_supervisor_segun_la_politica():
    """Si el monto reembolsado supera el límite del agente (S/ 300), se deriva a supervisor; si no, no."""
    res_deriva = calcular_reembolso(monto_pagado=350.0, horas_antes=10, motivo="clima")
    assert res_deriva["monto"] == 350.0
    assert res_deriva["requiere_supervisor"] is True

    res_no_deriva = calcular_reembolso(monto_pagado=300.0, horas_antes=80, motivo="cliente")
    assert res_no_deriva["monto"] == 300.0
    assert res_no_deriva["requiere_supervisor"] is False


@pytest.mark.parametrize(
    "monto,horas,motivo",
    [
        (0, 10, "cliente"),        # Monto no positivo (0)
        (-5, 10, "cliente"),       # Monto negativo
        (20000, 10, "cliente"),    # Monto supera el máximo permitido (10 000)
        (100, -1, "cliente"),      # Horas de anticipación negativas
        (100, 10, "lluvia"),       # Motivo no reconocido (debe ser clima/operador/cliente)
    ],
)
def test_rechaza_entradas_invalidas(monto, horas, motivo):
    """Entradas fuera de rango o con valores desconocidos deben lanzar ValueError."""
    with pytest.raises(ValueError):
        calcular_reembolso(monto_pagado=monto, horas_antes=horas, motivo=motivo)
