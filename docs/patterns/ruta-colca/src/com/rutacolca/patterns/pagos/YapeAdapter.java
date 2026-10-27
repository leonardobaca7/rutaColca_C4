package com.rutacolca.patterns.pagos;

import java.math.BigDecimal;
import java.util.UUID;

public class YapeAdapter implements PasarelaPago {
    @Override
    public ResultadoPago cobrar(BigDecimal monto, String cuentaOrigen) {
        String txId = "TX-YAPE-" + UUID.randomUUID().toString().substring(0, 8);
        return new ResultadoPago(true, txId, "Transferencia Yape confirmada para el número " + cuentaOrigen + " por S/ " + monto);
    }
}
