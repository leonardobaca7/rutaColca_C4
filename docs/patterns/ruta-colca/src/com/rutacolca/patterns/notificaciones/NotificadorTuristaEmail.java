package com.rutacolca.patterns.notificaciones;

public class NotificadorTuristaEmail implements ObservadorReserva {
    @Override
    public void onReservaConfirmada(EventoReservaConfirmada evento) {
        System.out.println("  [EMAIL] Enviando voucher digital a " + evento.emailTurista() + " para tour " + evento.tourNombre());
    }
}
