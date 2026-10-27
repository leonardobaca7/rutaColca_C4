package com.rutacolca.patterns.tarifas;

import java.math.BigDecimal;

public class PrecioGrupoStrategy implements EstrategiaPrecio {
    private static final BigDecimal FACTOR_DESCUENTO = new BigDecimal("0.85"); // -15%

    @Override
    public BigDecimal calcular(BigDecimal precioBase, int cantidadPasajeros) {
        BigDecimal subtotal = precioBase.multiply(BigDecimal.valueOf(cantidadPasajeros));
        if (cantidadPasajeros >= 5) {
            return subtotal.multiply(FACTOR_DESCUENTO);
        }
        return subtotal;
    }
}
