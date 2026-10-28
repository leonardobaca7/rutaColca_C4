# ADR-003: Resiliencia de Pagos en Temporada Alta mediante Transactional Outbox y Circuit Breaker

**Estado:** Aceptado  
**Fecha:** 28/10/2026  
**Escenario de Calidad:** E2 (Disponibilidad)  
**Autor (Redactor):** Leonardo Juan José Baca Calsin (`lbacac@unsa.edu.pe`)  
**Equipo Revisor:** Emanuel Hilacondo Begazo, German Arturo Chipana Jeronimo, Mauro Snayder Sullca Mamani  

---

## Contexto

Durante la temporada alta de turismo en el Valle del Colca (meses de julio y agosto), la plataforma RutaColca experimenta un incremento de demanda de reservas de diez veces ($\times 10$) respecto a la operación habitual. En este período, las pasarelas externas de pago bancario (Niubiz, Izipay y PayPal) experimentan cortes de servicio y picos de latencia que alcanzan ventanas de caída de hasta 15 minutos continuos.

En la arquitectura actual heredada de AG-08, la llamada a la pasarela de pagos desde el contenedor `API Backend` se realiza de manera síncrona mediante HTTPS. Esta condición genera dos fallas críticas cuando la pasarela colapsa:
1. **Pérdida de ventas y cobros huérfanos:** Solicitudes de reserva abortadas por timeout que cobran al turista pero no confirman la reserva en el sistema, o cancelaciones erróneas que dejan al visitante sin asiento.
2. **Saturación en cascada de hilos (*Thread Pool Starvation*):** Los hilos de ejecución de la API de Spring Boot permanecen bloqueados esperando respuestas de la pasarela caída, colapsando el servidor y degradando el resto de servicios de la plataforma.

**Restricciones obligatorias del proyecto:**
- Mantener la arquitectura de **Monolito Modular** establecida en el [ADR-001](file:///docs/architecture/adr/ADR-001.md).
- El equipo está conformado por 4 desarrolladores con un plazo máximo de implementación de 3 semanas.
- Toda nueva infraestructura requiere justificar explícitamente su costo operativo mensual ante la administración de la cooperativa.

---

## Alternativas Consideradas

- **Alternativa A (Elegida):** **Transactional Outbox Pattern sobre PostgreSQL 16 con Circuit Breaker integrado en Spring Boot 3.**
  - *Tácticas:* Detección rápida de falla mediante *Circuit Breaker* (timeout de 3 s) + Recuperación mediante reintentos asíncronos programados con *Virtual Threads* y degradación temporal al estado `PENDIENTE_PAGO` + Prevención mediante transacción local atómica ACID en PostgreSQL.
- **Alternativa B (Descartada):** **Broker de Mensajería Distribuido Externo (RabbitMQ / Apache Kafka) con Dead Letter Queue (DLQ).**
  - *Tácticas:* Detección por *heartbeat* + Recuperación mediante colas de reintento y DLQ + Prevención por confirmación del productor (*Publisher Confirms*).

---

## Decisión

Se decide implementar la **Alternativa A**: **Transactional Outbox Pattern sobre PostgreSQL 16 complementado con Circuit Breaker en el backend Spring Boot**.

### Mecanismo de Funcionamiento Arquitectónico:
1. **Detección y Aislamiento:** Las llamadas HTTP salientes a la pasarela de pagos se protegen con un *Circuit Breaker* (timeout configurado en 3.0 segundos y umbral de fallo del 50% sobre una ventana deslizante de 10 peticiones). Si la pasarela falla o el circuito pasa a estado `OPEN`, la API interrumpe de inmediato los intentos de red síncronos para proteger el pool de hilos de la aplicación.
2. **Atomicidad Local (Transactional Outbox):** En lugar de abortar la operación, la API inserta la `Reserva` con estado `PENDIENTE_PAGO` y simultáneamente registra la intención de transacción en la tabla `pagos_outbox` dentro de la **misma transacción relacional ACID** en PostgreSQL 16. La respuesta al cliente es inmediata ($\le 1.2\text{ s}$), notificándole que su cupo está pre-reservado y que el pago está siendo procesado de forma diferida.
3. **Reconciliación Asíncrona:** Un componente en segundo plano (`OutboxRelayWorker`) consulta periódicamente la tabla `pagos_outbox` mediante la cláusula no bloqueante `SELECT ... FOR UPDATE SKIP LOCKED` (ejecutado cada 15 segundos en hilos virtuales ligeros de Java 21). Al recuperar conectividad con la pasarela, el worker envía los cobros pendientes, actualiza el estado de la reserva a `CONFIRMADA_PAGADA` y dispara la confirmación al turista vía WhatsApp Business.

### Cumplimiento estricto de la Medida del Escenario E2:
- **0 reservas pagadas perdidas:** La transacción ACID garantiza que si el registro de reserva existe, la intención de pago está almacenada de manera durable en PostgreSQL, eliminando cualquier discrepancia de datos.
- **Confirmación $\le 30\text{ minutos}$ tras recuperación:** Con lotes de 50 registros cada 15 segundos, un acumulado de 200 reservas pendientes durante los 15 minutos de caída se procesa y confirma en menos de 2 minutos tras restablecerse la pasarela, holgadamente por debajo del objetivo de 30 minutos.
- **Cero costo de infraestructura adicional:** Se ejecuta sobre el clúster de cómputo y la base de datos gestionada ya existentes en la nube, demandando **\$0 USD** de gasto operativo mensual.

---

## Consecuencias

### Consecuencias Positivas (Beneficios)
- **Máxima Resiliencia Operativa:** El sistema no interrumpe la admisión de reservas aunque la red bancaria externa sufra cortes intermitentes de hasta 15 minutos.
- **Protección contra Fallos en Cascada:** El *Circuit Breaker* libera los recursos de la API en $< 3\text{ s}$, impidiendo la degradación de otros módulos (catálogo, itinerarios, autenticación).
- **Concurrencia Segura sin Bloqueos:** El uso de `FOR UPDATE SKIP LOCKED` en PostgreSQL permite que múltiples réplicas de la API en producción procesen la cola de pagos concurrentemente sin colisiones de bloqueo ni condiciones de carrera.
- **Alineación con el Monolito Modular (ADR-001):** Toda la lógica queda contenida en el módulo `com.rutacolca.pagos`, sin agregar servicios distribuidos externos que compliquen el ciclo de vida del software.

### Consecuencias Negativas y Mitigaciones
- **Consistencia Eventual en la Experiencia de Usuario:** El turista no recibe una confirmación bancaria instantánea en milisegundos cuando la pasarela está caída, sino una confirmación diferida.
  - *Mitigación:* Se implementa un mensaje transparente en la interfaz web React: *"Tu solicitud de reserva está asegurada. Estamos procesando tu pago de manera diferida debido a alta congestión bancaria. Te enviaremos el voucher a WhatsApp y correo en breve."*
- **Crecimiento de la tabla `pagos_outbox` en la Base de Datos:**
  - *Mitigación:* Se añade un índice parcial optimizado `CREATE INDEX idx_outbox_pendientes ON pagos_outbox(estado, proximo_intento) WHERE estado = 'PENDIENTE'` y se programa un job de purga que archiva transacciones exitosas con antigüedad mayor a 30 días.
- **Riesgo de Doble Cobro ante Reintentos de Red:** Si la pasarela procesó el cargo original pero la respuesta se perdió por timeout de red, el worker podría intentar cobrar de nuevo.
  - *Mitigación:* Se envía obligatoriamente una clave de idempotencia única (*Idempotency Key* basada en UUID de la reserva) en cada petición hacia la pasarela de pagos.
