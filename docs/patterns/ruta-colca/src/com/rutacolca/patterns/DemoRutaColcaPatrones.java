package com.rutacolca.patterns;

import com.rutacolca.patterns.autocolca.*;
import com.rutacolca.patterns.notificaciones.*;
import com.rutacolca.patterns.pagos.*;
import com.rutacolca.patterns.tarifas.*;

import java.math.BigDecimal;

public class DemoRutaColcaPatrones {
    public static void main(String[] args) {
        System.out.println("======================================================================");
        System.out.println("  RutaColca · Demostración de Patrones de Diseño GoF (Java 21)");
        System.out.println("======================================================================\n");

        // 1. ESCENARIO 4: ADAPTER (Validación de Boleto con AUTOCOLCA)
        System.out.println("[1] Validación de Boleto Turístico con Adapter:");
        ValidadorBoleto validador = new AutocolcaApiAdapter(new AutocolcaLegacyClient());
        ResultadoValidacion resBoleto = validador.validar("BTC-2026-9941", "72849102");
        System.out.println("  -> Código: " + resBoleto.codigo() + " | Válido: " + resBoleto.esValido() + " | " + resBoleto.mensaje());

        // 2. ESCENARIO 2: STRATEGY (Cálculo de Precios Dinámicos)
        System.out.println("\n[2] Cálculo de Tarifas con Strategy:");
        BigDecimal precioBase = new BigDecimal("120.00"); // S/ 120 por persona
        Reserva reserva = new Reserva("RES-701", "Cañón del Colca Clásico 2D/1N", precioBase, 6, new PrecioEstandarStrategy());
        System.out.println("  -> Tarifa Estándar (6 pasajeros): S/ " + reserva.calcularTotal());

        reserva.setEstrategiaPrecio(new PrecioTemporadaAltaStrategy());
        System.out.println("  -> Tarifa Temporada Alta (+25%): S/ " + reserva.calcularTotal());

        reserva.setEstrategiaPrecio(new PrecioGrupoStrategy());
        System.out.println("  -> Tarifa Grupo (>=5 pax, -15%): S/ " + reserva.calcularTotal());

        // 3. ESCENARIO 1: FACTORY METHOD + ADAPTER (Cobro en Pasarela de Pagos)
        System.out.println("\n[3] Procesamiento Multipasarela con Factory + Adapter:");
        BigDecimal montoACobrar = reserva.calcularTotal();
        PasarelaPago pasarelaYape = PasarelaPagoFactory.crear(MetodoPago.YAPE);
        ResultadoPago resPagoYape = pasarelaYape.cobrar(montoACobrar, "959123456");
        System.out.println("  -> " + resPagoYape.mensaje() + " (TX: " + resPagoYape.idTransaccion() + ")");

        PasarelaPago pasarelaCard = PasarelaPagoFactory.crear(MetodoPago.TARJETA);
        ResultadoPago resPagoCard = pasarelaCard.cobrar(montoACobrar, "4111-XXXX-XXXX-1111");
        System.out.println("  -> " + resPagoCard.mensaje() + " (TX: " + resPagoCard.idTransaccion() + ")");

        // 4. ESCENARIO 3: OBSERVER (Notificaciones Concurrentes)
        System.out.println("\n[4] Notificaciones Desacopladas con Observer:");
        PublicadorReservas publicador = new PublicadorReservas();
        publicador.suscribir(new NotificadorTuristaEmail());
        publicador.suscribir(new NotificadorGuiaWhatsApp());
        publicador.suscribir(new ActualizadorCuposAgencia());

        EventoReservaConfirmada evento = new EventoReservaConfirmada(
            reserva.getId(),
            reserva.getNombreTour(),
            "turista.aventura@gmail.com",
            "+51958774411",
            "AGENCIA-COLCA-TOURS-CHIVAY",
            reserva.getCantidadPasajeros()
        );
        publicador.notificarTodos(evento);

        System.out.println("\n======================================================================");
        System.out.println("  Demostración ejecutada exitosamente sin 'paternite'.");
        System.out.println("======================================================================");
    }
}
