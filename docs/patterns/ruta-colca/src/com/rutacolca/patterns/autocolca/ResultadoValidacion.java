package com.rutacolca.patterns.autocolca;

import java.time.LocalDate;

public record ResultadoValidacion(boolean esValido, String codigo, LocalDate fechaExpiracion, String mensaje) {}
