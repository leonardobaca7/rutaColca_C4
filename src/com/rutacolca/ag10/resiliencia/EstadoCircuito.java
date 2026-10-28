package com.rutacolca.ag10.resiliencia;

public enum EstadoCircuito {
    CLOSED,      // Operación normal: llamadas pasan a la pasarela
    OPEN,        // Falla detectada: llamadas cortadas inmediatamente para proteger recursos
    HALF_OPEN    // Prueba de recuperación: se permiten llamadas piloto para verificar restablecimiento
}
