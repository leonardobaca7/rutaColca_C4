package com.rutacolca.patterns.autocolca;

import java.time.LocalDate;

public class AutocolcaApiAdapter implements ValidadorBoleto {
    private final AutocolcaLegacyClient legacyClient;

    public AutocolcaApiAdapter(AutocolcaLegacyClient legacyClient) {
        this.legacyClient = legacyClient;
    }

    @Override
    public ResultadoValidacion validar(String codigoBoleto, String dni) {
        String hashControl = "AUTH-" + (dni != null ? dni.hashCode() : 0);
        String respuestaRaw = legacyClient.consultarVigenciaBoletoServicioPublico(codigoBoleto, hashControl);

        if (respuestaRaw.contains("STATUS:OK")) {
            return new ResultadoValidacion(true, codigoBoleto, LocalDate.of(2026, 12, 31), "Boleto verificado satisfactoriamente ante AUTOCOLCA");
        }
        return new ResultadoValidacion(false, codigoBoleto, null, "Boleto no vigente o no emitido por AUTOCOLCA");
    }
}
