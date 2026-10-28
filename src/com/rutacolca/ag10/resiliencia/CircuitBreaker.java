package com.rutacolca.ag10.resiliencia;

import java.util.concurrent.atomic.AtomicInteger;

public class CircuitBreaker {
    private final String nombre;
    private final int umbralFallosConsecutivos;
    private final long tiempoEsperaEnfriamientoMs;
    private EstadoCircuito estado;
    private final AtomicInteger fallosConsecutivos;
    private long timestampAperturaMs;

    public CircuitBreaker(String nombre, int umbralFallosConsecutivos, long tiempoEsperaEnfriamientoMs) {
        this.nombre = nombre;
        this.umbralFallosConsecutivos = umbralFallosConsecutivos;
        this.tiempoEsperaEnfriamientoMs = tiempoEsperaEnfriamientoMs;
        this.estado = EstadoCircuito.CLOSED;
        this.fallosConsecutivos = new AtomicInteger(0);
        this.timestampAperturaMs = 0;
    }

    public synchronized boolean permiteEjecucion() {
        if (estado == EstadoCircuito.CLOSED) {
            return true;
        }
        if (estado == EstadoCircuito.OPEN) {
            long ahora = System.currentTimeMillis();
            if (ahora - timestampAperturaMs >= tiempoEsperaEnfriamientoMs) {
                estado = EstadoCircuito.HALF_OPEN;
                System.out.println("[CIRCUIT BREAKER: " + nombre + "] Transición de OPEN a HALF_OPEN (probando recuperación tras " + (ahora - timestampAperturaMs) + " ms)");
                return true;
            }
            return false;
        }
        // HALF_OPEN: permite llamadas piloto
        return true;
    }

    public synchronized void registrarExito() {
        if (estado == EstadoCircuito.HALF_OPEN || estado == EstadoCircuito.OPEN) {
            System.out.println("[CIRCUIT BREAKER: " + nombre + "] Éxito confirmado. Transición de " + estado + " a CLOSED (servicio externo restablecido)");
        }
        estado = EstadoCircuito.CLOSED;
        fallosConsecutivos.set(0);
    }

    public synchronized void registrarFallo(String causa) {
        int fallos = fallosConsecutivos.incrementAndGet();
        System.err.println("[CIRCUIT BREAKER: " + nombre + "] Fallo detectado (" + fallos + "/" + umbralFallosConsecutivos + "): " + causa);
        if (fallos >= umbralFallosConsecutivos) {
            estado = EstadoCircuito.OPEN;
            timestampAperturaMs = System.currentTimeMillis();
            System.err.println("[CIRCUIT BREAKER: " + nombre + "] ¡Circuito ABIERTO (OPEN)! Interrumpiendo llamadas salientes para evitar pool starvation.");
        }
    }

    public EstadoCircuito getEstado() { return estado; }
    public String getNombre() { return nombre; }
}
