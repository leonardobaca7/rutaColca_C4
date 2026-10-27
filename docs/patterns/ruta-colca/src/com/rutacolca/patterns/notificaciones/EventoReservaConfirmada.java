package com.rutacolca.patterns.notificaciones;

public record EventoReservaConfirmada(
    String idReserva,
    String tourNombre,
    String emailTurista,
    String telefonoGuia,
    String agenciaId,
    int cupos
) {}
