package com.rutacolca.patterns.pagos;

import java.math.BigDecimal;

public interface PasarelaPago {
    ResultadoPago cobrar(BigDecimal monto, String cuentaOrigen);
}
