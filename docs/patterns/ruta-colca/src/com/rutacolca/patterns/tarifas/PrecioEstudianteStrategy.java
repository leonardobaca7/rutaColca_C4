package com.rutacolca.patterns.tarifas;

import java.math.BigDecimal;

public class PrecioEstudianteStrategy implements EstrategiaPrecio {
    private static final BigDecimal FACTOR_ESTUDIANTE = new BigDecimal("0.70"); // -30%

    @Override
    public BigDecimal calcular(BigDecimal precioBase, int cantidadPasajeros) {
        BigDecimal subtotal = precioBase.multiply(BigDecimal.valueOf(cantidadPasajeros));
        return subtotal.multiply(FACTOR_ESTUDIANTE);
    }
}
