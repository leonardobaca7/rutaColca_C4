package com.rutacolca.patterns.tarifas;

import java.math.BigDecimal;

public class PrecioTemporadaAltaStrategy implements EstrategiaPrecio {
    private static final BigDecimal FACTOR_TEMPORADA_ALTA = new BigDecimal("1.25"); // +25%

    @Override
    public BigDecimal calcular(BigDecimal precioBase, int cantidadPasajeros) {
        BigDecimal subtotal = precioBase.multiply(BigDecimal.valueOf(cantidadPasajeros));
        return subtotal.multiply(FACTOR_TEMPORADA_ALTA);
    }
}
