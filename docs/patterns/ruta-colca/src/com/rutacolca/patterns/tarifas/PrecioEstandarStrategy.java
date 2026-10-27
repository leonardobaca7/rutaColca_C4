package com.rutacolca.patterns.tarifas;

import java.math.BigDecimal;

public class PrecioEstandarStrategy implements EstrategiaPrecio {
    @Override
    public BigDecimal calcular(BigDecimal precioBase, int cantidadPasajeros) {
        return precioBase.multiply(BigDecimal.valueOf(cantidadPasajeros));
    }
}
