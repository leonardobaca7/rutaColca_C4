package com.rutacolca.patterns.autocolca;

public interface ValidadorBoleto {
    ResultadoValidacion validar(String codigoBoleto, String dni);
}
