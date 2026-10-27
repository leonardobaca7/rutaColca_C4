package com.rutacolca.patterns.pagos;

import java.math.BigDecimal;

public record ResultadoPago(boolean exitoso, String idTransaccion, String mensaje) {}
