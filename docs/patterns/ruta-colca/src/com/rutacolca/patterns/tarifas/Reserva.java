package com.rutacolca.patterns.tarifas;

import java.math.BigDecimal;

public class Reserva {
    private final String id;
    private final String nombreTour;
    private final BigDecimal precioBase;
    private final int cantidadPasajeros;
    private EstrategiaPrecio estrategiaPrecio;

    public Reserva(String id, String nombreTour, BigDecimal precioBase, int cantidadPasajeros, EstrategiaPrecio estrategiaInicial) {
        this.id = id;
        this.nombreTour = nombreTour;
        this.precioBase = precioBase;
        this.cantidadPasajeros = cantidadPasajeros;
        this.estrategiaPrecio = estrategiaInicial;
    }

    public void setEstrategiaPrecio(EstrategiaPrecio nuevaEstrategia) {
        this.estrategiaPrecio = nuevaEstrategia;
    }

    public BigDecimal calcularTotal() {
        return this.estrategiaPrecio.calcular(this.precioBase, this.cantidadPasajeros);
    }

    public String getId() { return id; }
    public String getNombreTour() { return nombreTour; }
    public int getCantidadPasajeros() { return cantidadPasajeros; }
}
