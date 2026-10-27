package com.rutacolca.patterns.pagos;

import java.math.BigDecimal;
import java.util.UUID;

public class TarjetaAdapter implements PasarelaPago {
    @Override
    public ResultadoPago cobrar(BigDecimal monto, String cuentaOrigen) {
        String txId = "TX-CARD-" + UUID.randomUUID().toString().substring(0, 8);
        return new ResultadoPago(true, txId, "Cargo exitoso de S/ " + monto + " a tarjeta terminada en " + cuentaOrigen);
    }
}
