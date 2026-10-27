package com.rutacolca.patterns.notificaciones;

import java.util.ArrayList;
import java.util.List;

public class PublicadorReservas {
    private final List<ObservadorReserva> suscriptores = new ArrayList<>();

    public void suscribir(ObservadorReserva observador) {
        suscriptores.add(observador);
    }

    public void desuscribir(ObservadorReserva observador) {
        suscriptores.remove(observador);
    }

    public void notificarTodos(EventoReservaConfirmada evento) {
        for (ObservadorReserva observador : suscriptores) {
            observador.onReservaConfirmada(evento);
        }
    }
}
