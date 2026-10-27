package com.rutacolca.patterns.notificaciones;

public class ActualizadorCuposAgencia implements ObservadorReserva {
    @Override
    public void onReservaConfirmada(EventoReservaConfirmada evento) {
        System.out.println("  [PWA AGENCIA] Sincronizando tablero en tiempo real para agencia " + evento.agenciaId() + ": Descontados " + evento.cupos() + " cupo(s).");
    }
}
