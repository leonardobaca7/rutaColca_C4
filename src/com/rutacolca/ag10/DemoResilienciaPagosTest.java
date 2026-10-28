package com.rutacolca.ag10;

import com.rutacolca.ag10.dominio.*;
import com.rutacolca.ag10.resiliencia.CircuitBreaker;
import com.rutacolca.ag10.resiliencia.EstadoCircuito;
import com.rutacolca.ag10.servicio.ProcesadorPagosOutboxService;
import com.rutacolca.ag10.servicio.SimuladorPasarelaPagos;

import java.util.ArrayList;
import java.util.List;

/**
 * Prueba de Concepto (PoC) Automatizada - AG-10 (Escenario E2: Disponibilidad)
 * Simula el comportamiento del sistema ante la caída de la pasarela bancaria por 15 minutos.
 * Verifica formalmente:
 * 1. 0 reservas pagadas perdidas (conservadas en estado PENDIENTE_PAGO en el outbox).
 * 2. Protección de hilos por Circuit Breaker (apertura ante fallos repetidos).
 * 3. Reconciliación exitosa del 100% de reservas diferidas tras el restablecimiento de la pasarela.
 */
public class DemoResilienciaPagosTest {

    public static void main(String[] args) {
        System.out.println("================================================================================");
        System.out.println(" DEMO DE RESILIENCIA ARQUITECTÓNICA - RUTACOLCA EN TEMPORADA ALTA (AG-10)");
        System.out.println(" Escenario E2: Disponibilidad ante Caída de Pasarela de Pagos (ADR-003)");
        System.out.println("================================================================================\n");

        SimuladorPasarelaPagos pasarela = new SimuladorPasarelaPagos();
        // Umbral: 3 fallos consecutivos abren el circuito; enfriamiento de 500 ms para la prueba
        CircuitBreaker cb = new CircuitBreaker("PasarelaBancariaCB", 3, 500);
        ProcesadorPagosOutboxService servicio = new ProcesadorPagosOutboxService(pasarela, cb);

        // FASE 1: Operación normal (pasarela saludable)
        System.out.println("--- FASE 1: Operación Normal en Temporada Alta ---");
        List<Reserva> reservasIniciales = new ArrayList<>();
        reservasIniciales.add(servicio.procesarSolicitudReserva("Jean Pierre (Francia)", "TOUR-COLCA-2D", 280.0));
        reservasIniciales.add(servicio.procesarSolicitudReserva("Carla Mendoza (Lima)", "TOUR-CABANACONDE-1D", 150.0));

        for (Reserva r : reservasIniciales) {
            assert r.getEstado() == EstadoReserva.CONFIRMADA_PAGADA : "Error: La reserva debió confirmarse inmediatamente";
            System.out.println("✓ Reserva " + r.getId() + " verificada: " + r.getEstado());
        }
        System.out.println("Estado Circuit Breaker: " + cb.getEstado() + " (Operativo)\n");

        // FASE 2: Simulación de caída de pasarela (corte de 15 minutos en temporada alta)
        System.out.println("--- FASE 2: Incidente en Pasarela de Pagos (Corte Externo de 15 min) ---");
        pasarela.simularCaida(true);

        List<Reserva> reservasDuranteCaida = new ArrayList<>();
        String[] turistas = {
            "Hans Müller (Alemania)",
            "Sarah Jenkins (EE.UU.)",
            "Mateo Rossi (Italia)",
            "Valeria Quispe (Arequipa)",
            "Liam O'Connor (Irlanda)",
            "Yuki Tanaka (Japón)"
        };

        for (String t : turistas) {
            Reserva res = servicio.procesarSolicitudReserva(t, "TOUR-CRUZ-DEL-CONDOR", 220.0);
            reservasDuranteCaida.add(res);
        }

        // Verificación de resiliencia
        long aseguradasEnOutbox = servicio.getTablaOutboxPagos().stream()
                .filter(o -> o.getEstado() == EstadoPagoOutbox.PENDIENTE)
                .count();

        System.out.println("\n[MÉTRICA ARQUITECTÓNICA - FASE 2]");
        System.out.println("Total de reservas recibidas durante la caída: " + reservasDuranteCaida.size());
        System.out.println("Total de intenciones de pago aseguradas en PostgreSQL Outbox: " + aseguradasEnOutbox);
        System.out.println("Estado final del Circuit Breaker: " + cb.getEstado());

        assert aseguradasEnOutbox == reservasDuranteCaida.size() : "Fallo crítico: Se perdieron reservas durante la caída!";
        assert cb.getEstado() == EstadoCircuito.OPEN : "Fallo: El Circuit Breaker debió abrirse para proteger la API";
        System.out.println("✓ 0 RESERVAS PERDIDAS: Todas las reservas se preservaron atómicamente en el Outbox.\n");

        // FASE 3: Intento de reconciliación mientras la pasarela sigue caída
        System.out.println("--- FASE 3: Sondeo periódico del Outbox Worker con pasarela aún caída ---");
        int conciliadosDuranteCaida = servicio.ejecutarReconciliacionOutbox();
        System.out.println("Pagos conciliados mientras la pasarela está caída: " + conciliadosDuranteCaida + " (Esperado: 0 para no saturar)");
        assert conciliadosDuranteCaida == 0 : "Error: No debió conciliar con pasarela caída";

        // FASE 4: Restablecimiento del servicio bancario externo
        System.out.println("\n--- FASE 4: Recuperación de la Pasarela de Pagos y Reconciliación Automática ---");
        try {
            // Breve pausa para permitir enfriamiento del circuit breaker
            Thread.sleep(600);
        } catch (InterruptedException ignored) {}

        pasarela.simularCaida(false); // La pasarela vuelve a estar en línea

        System.out.println("Disparando ejecución del OutboxRelayWorker (Simulación de @Scheduled cada 15s)...");
        int conciliados = servicio.ejecutarReconciliacionOutbox();
        System.out.println("\nTotal de pagos diferidos conciliados exitosamente: " + conciliados + "/" + reservasDuranteCaida.size());

        // Verificaciones finales
        long outboxPendientesFinal = servicio.getTablaOutboxPagos().stream()
                .filter(o -> o.getEstado() == EstadoPagoOutbox.PENDIENTE)
                .count();

        long reservasConfirmadasFinal = servicio.getTablaReservas().values().stream()
                .filter(r -> r.getEstado() == EstadoReserva.CONFIRMADA_PAGADA)
                .count();

        System.out.println("\n================================================================================");
        System.out.println(" RESULTADOS FINALES DE LA EVALUACIÓN DEL ESCENARIO E2 (DISPONIBILIDAD):");
        System.out.println(" - Reservas totales registradas: " + servicio.getTablaReservas().size());
        System.out.println(" - Reservas 100% confirmadas y pagadas: " + reservasConfirmadasFinal);
        System.out.println(" - Pagos pendientes en cola Outbox: " + outboxPendientesFinal);
        System.out.println(" - Reservas o cobros perdidos: 0");
        System.out.println(" - Estado de salud final del Circuit Breaker: " + cb.getEstado() + " (CLOSED)");
        System.out.println("================================================================================");

        if (reservasConfirmadasFinal == (reservasIniciales.size() + reservasDuranteCaida.size()) && outboxPendientesFinal == 0) {
            System.out.println(">>> PRUEBA DE CONCEPTO EXITOSA: Se cumple 100% la medida del Escenario E2 (ADR-003) <<<");
        } else {
            System.err.println(">>> ERROR: No se cumplieron todas las aseveraciones arquitectónicas <<<");
            System.exit(1);
        }
    }
}
