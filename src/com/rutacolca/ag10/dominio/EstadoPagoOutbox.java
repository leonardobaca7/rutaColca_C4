package com.rutacolca.ag10.dominio;

public enum EstadoPagoOutbox {
    PENDIENTE,
    PROCESANDO,
    PROCESADO_EXITOSO,
    DEAD_LETTER_FALLIDO
}
