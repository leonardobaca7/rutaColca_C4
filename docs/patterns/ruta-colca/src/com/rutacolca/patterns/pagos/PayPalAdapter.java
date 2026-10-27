package com.rutacolca.patterns.pagos;

import java.math.BigDecimal;
import java.util.UUID;

public class PayPalAdapter implements PasarelaPago {
    @Override
    public ResultadoPago cobrar(BigDecimal monto, String cuentaOrigen) {
        String txId = "TX-PAYPAL-" + UUID.randomUUID().toString().substring(0, 8);
        return new ResultadoPago(true, txId, "Captura internacional PayPal procesada para la cuenta " + cuentaOrigen + " por S/ " + monto);
    }
}
