package com.rutacolca.patterns.pagos;

public class PasarelaPagoFactory {
    public static PasarelaPago crear(MetodoPago metodo) {
        return switch (metodo) {
            case TARJETA -> new TarjetaAdapter();
            case YAPE -> new YapeAdapter();
            case PAYPAL -> new PayPalAdapter();
        };
    }
}
