# Pruebas que el asistente generó junto con su borrador (incluidas en el mismo Pull Request).
from borrador_ia.reembolso_v0 import calcular_reembolso


def test_reembolso_completo():
    assert calcular_reembolso(100, 100, "cliente")["porcentaje"] == 100


def test_reembolso_medio():
    assert calcular_reembolso(100, 72, "cliente")["porcentaje"] == 50


def test_clima():
    assert calcular_reembolso(100, 1, "clima")["monto"] == 100
