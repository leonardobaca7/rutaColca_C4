# Entregable E2: Comparación de Alternativas de Diseño Arquitectónico (AG-10)

**Curso:** Construcción de Software (1703243) – Semestre 2026-B  
**Docente:** Mg. Antonio Arroyo Paz  
**Arquitecto de Software responsable:** German Arturo Chipana Jeronimo (`gchipanaj@unsa.edu.pe`)  
**Fecha:** 28 de octubre de 2026  
**Iteración:** ADD 3.0 – Paso 3: Iteración de Diseño Arquitectónico

---

## 1. Recorrido Metodológico ADD 3.0 (Pasos 2 a 5)

En conformidad con el método **Attribute-Driven Design (ADD 3.0)** de Cervantes y Kazman (2016), se recorrieron los pasos 2 a 5 para abordar el escenario crítico **E2 (Disponibilidad)**:

### Paso 2 · Objetivo de la iteración
Diseñar la arquitectura interna y mecanismos de integración del módulo de pagos para garantizar la **disponibilidad continua del flujo de reservas durante caídas de la pasarela de hasta 15 minutos**, asegurando **0 reservas perdidas** y **confirmación definitiva $\le 30\text{ minutos}$** tras el restablecimiento del servicio, sin romper la arquitectura de **Monolito Modular (ADR-001)** ni incrementar desproporcionadamente los costos operativos.

### Paso 3 · Elementos a refinar
Se refinan dos contenedores del modelo C4 base (AG-08):
1. **`API Backend` (Java 21 / Spring Boot 3):** Específicamente el módulo de dominio y aplicación de Pagos (`com.rutacolca.pagos`), introduciendo un componente de detección de fallas (*Circuit Breaker*) y un despachador en segundo plano (*Outbox Relay Worker*).
2. **`Base de Datos Principal` (PostgreSQL 16):** Introducción de la tabla transaccional `pagos_outbox` para registrar la intención de cobro de forma atómica junto a la entidad `Reserva`.

### Paso 4 · Conceptos de diseño elegidos
- **Tácticas arquitectónicas de Disponibilidad (Bass et al., 2021):**
  - *Detectar fallas:* Timeout controlado (3 segundos) y monitor de umbral de fallos (*Circuit Breaker*).
  - *Recuperarse de fallas:* Reintentos con retroceso exponencial (*Exponential Backoff*), degradación grácil (*Graceful Degradation* hacia estado `PENDIENTE_PAGO`) y cola de reintentos diferidos.
  - *Prevenir fallas:* Transacciones atómicas locales (ACID) mediante el patrón *Transactional Outbox*.
- **Patrones de Arquitectura:**
  - *Transactional Outbox Pattern* con sondeo transaccional (`SELECT ... FOR UPDATE SKIP LOCKED`).
  - *Circuit Breaker Pattern* implementado mediante Resilience4j / lógica integrada.
  - Desacoplamiento asíncrono con *Virtual Threads* (Java 21).

### Paso 5 · Instanciación de elementos y responsabilidades
- `ReservaService`: Orquesta la creación de la reserva en estado `PENDIENTE_PAGO`.
- `TransactionalOutboxManager`: Inserta el registro en `pagos_outbox` en la misma transacción de base de datos que la reserva.
- `OutboxRelayWorker`: Tarea programada (`@Scheduled`) que ejecuta la reconciliación periódica en lotes contra la pasarela externa cuando el circuito se encuentra cerrado o semiabierto.
- `PasarelaPagosCircuitBreaker`: Intercepta las llamadas salientes a la pasarela bancaria externa para cortar peticiones cuando la tasa de fallo supera el 50%.

---

## 2. Comparación Formal de Alternativas de Diseño (Tabla 9 de la guía)

Para evitar sesgos y no adoptar acríticamente la primera propuesta, se estructuraron y contrastaron dos alternativas de diseño diametralmente distintas:

### Tabla 1. Matriz de comparación de alternativas arquitectónicas

| Criterio de Comparación | Alternativa A: Outbox Transaccional en PostgreSQL + Circuit Breaker (Elegida) | Alternativa B: Broker de Mensajería Externo RabbitMQ/Kafka + Dead Letter Queue (Descartada) |
| :--- | :--- | :--- |
| **Tácticas de Calidad (Bass et al., 2021)** | **Detectar:** Timeout de 3 s + Circuit Breaker (Resilience4j).<br/>**Recuperar:** Reintentos asíncronos programados con *Virtual Threads* + degradación a estado `PENDIENTE_CONFIRMACION`.<br/>**Prevenir:** Transacción local ACID en PostgreSQL que garantiza consistencia absoluta entre reserva y registro de cobro. | **Detectar:** Heartbeat con el broker de mensajería.<br/>**Recuperar:** Enrutamiento a colas de reintento diferido (*Retry Exchange*) y cola de mensajes muertos (*Dead Letter Queue* - DLQ).<br/>**Prevenir:** Confirmaciones de entrega del productor (*Publisher Confirms*). |
| **Patrón o Tecnología** | **Transactional Outbox Pattern** sobre PostgreSQL 16 con `SELECT ... FOR UPDATE SKIP LOCKED` + Spring Boot 3 Scheduler en hilos virtuales de Java 21. | **Message Broker distribuido (RabbitMQ o clúster Apache Kafka)** con colas durables y consumidores asíncronos dedicados. |
| **Cómo logra la medida del escenario** | 1. Si la pasarela cae, el intento de cobro se guarda en `pagos_outbox` atómicamente con la reserva ($\mathbf{0}$ pagos perdidos).<br/>2. Al recuperarse la pasarela, el *Outbox Relay Worker* procesa la cola cada 15 segundos en lotes de 50 registros; 200 reservas pendientes se concilian en menos de **2 minutos**, cumpliendo holgadamente el límite de $\mathbf{\le 30\text{ min}}$. | Los mensajes se encolan en RabbitMQ inmediatamente. Si la pasarela cae, el consumidor reintenta con política de *exponential backoff* hasta lograr el cobro. También garantiza 0 pagos perdidos y confirmación en minutos. |
| **Costo (Desarrollo y Operación)** | **Operación:** **\$0 USD/mes adicionales** (aprovecha la base de datos PostgreSQL 16 gestionada ya existente en la arquitectura de producción).<br/>**Desarrollo:** **1.5 semanas-persona** para el equipo de 4 ingenieros. Curva de aprendizaje mínima sobre Spring Boot. | **Operación:** **+\$45 a +\$120 USD/mes** por instancia administrada de RabbitMQ en AWS/GCP (superando el presupuesto aprobado).<br/>**Desarrollo:** **3 a 4 semanas-persona** (configuración de red VPC, listeners, serialización JSON, monitoreo de colas y gestión de clustering). |
| **Riesgos Técnicos** | - Posible contención o saturación en PostgreSQL si la tabla outbox crece descontroladamente.<br/>*Mitigación:* Índice parcial en `(estado, proximo_reintento)` y empleo estricto de `FOR UPDATE SKIP LOCKED`. Purga automática nocturna de transacciones resueltas $> 30$ días. | - Mayor complejidad de red: si se cae la conexión entre la API y RabbitMQ, se pierde la garantía de entrega a menos que se use outbox igualmente (problema de dual-write).<br/>- Sobrecarga operativa de monitoreo para un equipo pequeño de 4 ingenieros. |
| **¿Respeta las restricciones del proyecto?** | **SÍ, 100% COMPATIBLE.**<br/>- Preserva el **Monolito Modular (ADR-001)**.<br/>- Plazo de entrega $\le 3$ semanas.<br/>- Sin nuevos costos de infraestructura que justificar ante la gerencia. | **NO CUMPLE LAS RESTRICCIONES.**<br/>- Introduce un nuevo contenedor de infraestructura distribuida innecesario.<br/>- Requiere justificar costo operativo mensual.<br/>- Riesgo elevado de exceder el plazo de 3 semanas debido a complejidad operacional. |

---

## 3. Justificación de la Elección y Rechazo

### Por qué se descarta la Alternativa B (Broker Externo RabbitMQ/Kafka):
La Alternativa B incurre en el clásico antipatrón de diseño de **sobreingeniería (*over-engineering*)**, intentando solucionar un problema local de un solo módulo mediante la introducción de infraestructura distribuida compleja. Además:
1. **El problema del *Dual Write*:** Si la API intenta guardar la reserva en PostgreSQL y luego enviar el evento a RabbitMQ, una caída entre ambas operaciones deja los datos inconsistentes (reserva sin mensaje en cola o mensaje en cola sin reserva en BD). Para solucionar esto en RabbitMQ, se tendría que implementar de todas maneras un *Transactional Outbox* local en la base de datos relacional. Por ende, incorporar RabbitMQ duplica la infraestructura sin eliminar el problema de fondo.
2. **Violación de restricciones presupuestarias y de tiempo:** Exige un costo adicional de hasta \$120 USD mensuales y un tiempo de despliegue que coparía las 3 semanas de plazo del sprint, poniendo en riesgo la entrega.

### Por qué se aprueba la Alternativa A (Transactional Outbox en PostgreSQL):
1. **Garantía ACID absoluta:** El registro de la reserva y el registro en `pagos_outbox` se ejecutan en la misma transacción local de base de datos (`@Transactional`). No existe ninguna ventana de tiempo en la que la reserva exista sin su registro de pago asociado.
2. **Eficiencia en recursos:** Aprovecha el motor relacional PostgreSQL 16 ya desplegado en la nube de RutaColca. Con la sintaxis `FOR UPDATE SKIP LOCKED`, múltiples réplicas de la API pueden consumir registros de la cola en paralelo sin bloqueos ni condiciones de carrera.
3. **Mantenibilidad:** El código reside íntegramente dentro del módulo `pagos` del monolito modular en Spring Boot, facilitando pruebas unitarias e integración continua sin dependencias externas pesadas.
