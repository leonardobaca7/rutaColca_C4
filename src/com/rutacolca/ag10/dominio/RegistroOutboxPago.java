package com.rutacolca.ag10.dominio;

import java.time.LocalDateTime;

public class RegistroOutboxPago {
    private final String outboxId;
    private final String reservaId;
    private final double monto;
    private final String idempotencyKey;
    private EstadoPagoOutbox estado;
    private int intentos;
    private String ultimoError;
    private final LocalDateTime fechaCreacion;
    private LocalDateTime proximoIntento;

    public RegistroOutboxPago(String outboxId, String reservaId, double monto, String idempotencyKey) {
        this.outboxId = outboxId;
        this.reservaId = reservaId;
        this.monto = monto;
        this.idempotencyKey = idempotencyKey;
        this.estado = EstadoPagoOutbox.PENDIENTE;
        this.intentos = 0;
        this.ultimoError = null;
        this.fechaCreacion = LocalDateTime.now();
        this.proximoIntento = LocalDateTime.now();
    }

    public String getOutboxId() { return outboxId; }
    public String getReservaId() { return reservaId; }
    public double getMonto() { return monto; }
    public String getIdempotencyKey() { return idempotencyKey; }
    public EstadoPagoOutbox getEstado() { return estado; }
    public void setEstado(EstadoPagoOutbox estado) { this.estado = estado; }
    public int getIntentos() { return intentos; }
    public void incrementarIntentos() { this.intentos++; }
    public String getUltimoError() { return ultimoError; }
    public void setUltimoError(String error) { this.ultimoError = error; }
    public LocalDateTime getFechaCreacion() { return fechaCreacion; }
    public LocalDateTime getProximoIntento() { return proximoIntento; }

    public void programarProximoIntento(long delaySeconds) {
        this.proximoIntento = LocalDateTime.now().plusSeconds(delaySeconds);
    }

    @Override
    public String toString() {
        return "RegistroOutboxPago{outboxId='" + outboxId + "', reservaId='" + reservaId + "', monto=" + monto + ", estado=" + estado + ", intentos=" + intentos + "}";
    }
}
