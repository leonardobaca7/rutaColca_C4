package com.rutacolca.ag10.servicio;

public interface PasarelaPagosClient {
    boolean cobrar(String reservaId, double monto, String idempotencyKey) throws Exception;
}
