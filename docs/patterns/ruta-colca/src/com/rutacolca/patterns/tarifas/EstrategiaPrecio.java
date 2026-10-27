package com.rutacolca.patterns.tarifas;

import java.math.BigDecimal;

public interface EstrategiaPrecio {
    BigDecimal calcular(BigDecimal precioBase, int cantidadPasajeros);
}
