package com.rutacolca.ag10.servicio;

import java.util.concurrent.atomic.AtomicBoolean;

public class SimuladorPasarelaPagos implements PasarelaPagosClient {
    private final AtomicBoolean servicioCaido = new AtomicBoolean(false);
    private long latenciaSimuladaMs = 30;

    public void simularCaida(boolean caida) {
        this.servicioCaido.set(caida);
        if (caida) {
            System.err.println(">>> [SIMULADOR PASARELA] Servicio externo CAÍDO (simulando corte de 15 min / HTTP 504) <<<");
        } else {
            System.out.println(">>> [SIMULADOR PASARELA] Servicio externo RESTABLECIDO (red operativa) <<<");
        }
    }

    public boolean estaCaido() {
        return servicioCaido.get();
    }

    public void setLatenciaSimuladaMs(long latenciaMs) {
        this.latenciaSimuladaMs = latenciaMs;
    }

    @Override
    public boolean cobrar(String reservaId, double monto, String idempotencyKey) throws Exception {
        if (latenciaSimuladaMs > 0) {
            Thread.sleep(latenciaSimuladaMs);
        }
        if (servicioCaido.get()) {
            throw new java.net.SocketTimeoutException("HTTP 504 Gateway Timeout: La pasarela bancaria externa no responde");
        }
        return true;
    }
}
