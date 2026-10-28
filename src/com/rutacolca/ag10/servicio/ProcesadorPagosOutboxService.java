package com.rutacolca.ag10.servicio;

import com.rutacolca.ag10.dominio.*;
import com.rutacolca.ag10.resiliencia.CircuitBreaker;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.atomic.AtomicLong;

public class ProcesadorPagosOutboxService {
    private final PasarelaPagosClient pasarelaClient;
    private final CircuitBreaker circuitBreaker;

    // Simulación de almacenamiento transaccional PostgreSQL 16
    private final Map<String, Reserva> tablaReservas = new ConcurrentHashMap<>();
    private final List<RegistroOutboxPago> tablaOutboxPagos = new CopyOnWriteArrayList<>();
    private final AtomicLong secId = new AtomicLong(1000);

    public ProcesadorPagosOutboxService(PasarelaPagosClient pasarelaClient, CircuitBreaker circuitBreaker) {
        this.pasarelaClient = pasarelaClient;
        this.circuitBreaker = circuitBreaker;
    }

    /**
     * Transacción atómica de reserva:
     * Si la pasarela está activa, intenta cobro directo.
     * Si la pasarela falla o el circuit breaker está abierto, se persiste la reserva
     * y el registro outbox atómicamente en estado PENDIENTE_PAGO. Cero pérdida de reservas.
     */
    public Reserva procesarSolicitudReserva(String turista, String tourId, double monto) {
        String reservaId = "RES-" + secId.incrementAndGet();
        String idempotencyKey = UUID.randomUUID().toString();
        Reserva reserva = new Reserva(reservaId, turista, tourId, monto);

        boolean cobroInmediatoExitoso = false;

        if (circuitBreaker.permiteEjecucion()) {
            try {
                cobroInmediatoExitoso = pasarelaClient.cobrar(reservaId, monto, idempotencyKey);
                circuitBreaker.registrarExito();
            } catch (Exception e) {
                circuitBreaker.registrarFallo(e.getMessage());
            }
        } else {
            System.out.println("[API BACKEND] Petición interceptada por Circuit Breaker (OPEN). Enrutando directamente a Transactional Outbox.");
        }

        if (cobroInmediatoExitoso) {
            reserva.setEstado(EstadoReserva.CONFIRMADA_PAGADA);
            tablaReservas.put(reservaId, reserva);
            System.out.println("[API BACKEND] Cobro síncrono exitoso para " + reservaId + " (Confirmación inmediata)");
        } else {
            // DEGRADACIÓN GRÁCIL + TRANSACTIONAL OUTBOX ATÓMICO (ACID LOCAL)
            reserva.setEstado(EstadoReserva.PENDIENTE_PAGO);
            tablaReservas.put(reservaId, reserva);

            String outboxId = "OUT-" + UUID.randomUUID().toString().substring(0, 8);
            RegistroOutboxPago outbox = new RegistroOutboxPago(outboxId, reservaId, monto, idempotencyKey);
            tablaOutboxPagos.add(outbox);

            System.out.println("[TRANSACTIONAL OUTBOX] Reserva " + reservaId + " asegurada en BD con estado PENDIENTE_PAGO. Registro Outbox: " + outboxId);
        }

        return reserva;
    }

    /**
     * Simulación del Outbox Relay Worker (Spring Boot @Scheduled con Virtual Threads).
     * Sondea la tabla 'pagos_outbox' con SELECT ... FOR UPDATE SKIP LOCKED.
     */
    public int ejecutarReconciliacionOutbox() {
        int procesados = 0;
        for (RegistroOutboxPago outbox : tablaOutboxPagos) {
            if (outbox.getEstado() == EstadoPagoOutbox.PENDIENTE) {
                if (!circuitBreaker.permiteEjecucion()) {
                    System.out.println("[OUTBOX WORKER] Reintento pausado: Circuit Breaker sigue ABIERTO.");
                    break;
                }

                outbox.incrementarIntentos();
                try {
                    boolean cobrado = pasarelaClient.cobrar(outbox.getReservaId(), outbox.getMonto(), outbox.getIdempotencyKey());
                    if (cobrado) {
                        circuitBreaker.registrarExito();
                        outbox.setEstado(EstadoPagoOutbox.PROCESADO_EXITOSO);

                        Reserva r = tablaReservas.get(outbox.getReservaId());
                        if (r != null) {
                            r.setEstado(EstadoReserva.CONFIRMADA_PAGADA);
                        }
                        procesados++;
                        System.out.println("[OUTBOX WORKER] ¡Pago conciliado exitosamente! Reserva: " + outbox.getReservaId() + " -> CONFIRMADA_PAGADA (Intento #" + outbox.getIntentos() + ")");
                    }
                } catch (Exception e) {
                    circuitBreaker.registrarFallo(e.getMessage());
                    outbox.setUltimoError(e.getMessage());
                    long delay = (long) Math.pow(2, Math.min(outbox.getIntentos(), 5));
                    outbox.programarProximoIntento(delay);
                    System.err.println("[OUTBOX WORKER] Fallo al reintentar reserva " + outbox.getReservaId() + ". Próximo intento en " + delay + "s");
                }
            }
        }
        return procesados;
    }

    public Map<String, Reserva> getTablaReservas() { return tablaReservas; }
    public List<RegistroOutboxPago> getTablaOutboxPagos() { return tablaOutboxPagos; }
}
