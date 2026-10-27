package com.rutacolca.patterns.notificaciones;

public class NotificadorGuiaWhatsApp implements ObservadorReserva {
    @Override
    public void onReservaConfirmada(EventoReservaConfirmada evento) {
        System.out.println("  [WHATSAPP] Notificando al guía (" + evento.telefonoGuia() + "): Manifiesto actualizado con " + evento.cupos() + " cupo(s) nuevo(s).");
    }
}
