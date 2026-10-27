package com.rutacolca.patterns.autocolca;

public class AutocolcaLegacyClient {
    public String consultarVigenciaBoletoServicioPublico(String serieNumero, String hashControl) {
        // Simulación del servicio SOAP/legado con formato estructurado propietario: "STATUS:OK|EXP:2026-12-31|MSG:VALIDO"
        if (serieNumero != null && serieNumero.startsWith("BTC-")) {
            return "STATUS:OK|EXP:2026-12-31|MSG:BOLETO_TURISTICO_AUTORIZADO";
        }
        return "STATUS:ERR|EXP:NONE|MSG:NUMERO_NO_ENCONTRADO";
    }
}
