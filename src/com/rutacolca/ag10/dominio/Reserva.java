package com.rutacolca.ag10.dominio;

import java.time.LocalDateTime;

public class Reserva {
    private final String id;
    private final String turistaNombre;
    private final String tourId;
    private final double montoTotal;
    private EstadoReserva estado;
    private final LocalDateTime fechaCreacion;
    private LocalDateTime fechaActualizacion;

    public Reserva(String id, String turistaNombre, String tourId, double montoTotal) {
        this.id = id;
        this.turistaNombre = turistaNombre;
        this.tourId = tourId;
        this.montoTotal = montoTotal;
        this.estado = EstadoReserva.SOLICITADA;
        this.fechaCreacion = LocalDateTime.now();
        this.fechaActualizacion = LocalDateTime.now();
    }

    public String getId() { return id; }
    public String getTuristaNombre() { return turistaNombre; }
    public String getTourId() { return tourId; }
    public double getMontoTotal() { return montoTotal; }
    public EstadoReserva getEstado() { return estado; }

    public void setEstado(EstadoReserva estado) {
        this.estado = estado;
        this.fechaActualizacion = LocalDateTime.now();
    }

    public LocalDateTime getFechaCreacion() { return fechaCreacion; }
    public LocalDateTime getFechaActualizacion() { return fechaActualizacion; }

    @Override
    public String toString() {
        return "Reserva{id='" + id + "', turista='" + turistaNombre + "', tour='" + tourId + "', monto=S/." + montoTotal + ", estado=" + estado + "}";
    }
}
