# Entregable E7: Bitácora de Uso y Gobernanza de Inteligencia Artificial (AG-10)

**Curso:** Construcción de Software (1703243) – Semestre 2026-B  
**Docente:** Mg. Antonio Arroyo Paz  
**Equipo Responsable:**
- Emanuel Hilacondo Begazo (`ehilacondob@unsa.edu.pe`) – Facilitador ADD
- German Arturo Chipana Jeronimo (`gchipanaj@unsa.edu.pe`) – Arquitecto
- Leonardo Juan José Baca Calsin (`lbacac@unsa.edu.pe`) – Redactor
- Mauro Snayder Sullca Mamani (`msullcam@unsa.edu.pe`) – Evaluador ATAM  
**Fecha:** 28 de octubre de 2026  
**Iteración:** ADD 3.0 – AG-10: RutaColca en Temporada Alta  

---

## 1. Política de Gobernanza de IA Aplicada

En estricto cumplimiento de las reglas del laboratorio AG-10:
1. **La IA propone, el equipo decide y verifica:** Ninguna sugerencia generada por el modelo de lenguaje se incorporó directamente al proyecto sin contrastación crítica, cálculo de factibilidad y ejecución empírica de pruebas de código.
2. **Protección de datos y credenciales:** Se verificó que ningún prompt incluyera datos personales, llaves privadas de pasarelas ni credenciales de bases de datos.
3. **Control de alucinaciones y sesgos:** Se rechazó enérgicamente cualquier intento de la IA de introducir patrones sobrecomplejos (como microservicios o brokers pesados) que violaran el [ADR-001](file:///docs/architecture/adr/ADR-001.md) o el presupuesto del consorcio.

---

## 2. Registro Sistemático de Prompts (P1 a P5)

### Registro 1 · Prompt P1: Cuestionar la Priorización del Árbol de Utilidad
* **Fase:** Parte A – Paso 1 (Árbol de Utilidad)
* **Integrante que ejecutó y verificó:** Emanuel Hilacondo Begazo (Facilitador ADD)
* **Texto del Prompt ejecutado:**
  ```text
  Actúa como evaluador de arquitectura con experiencia en ATAM.
  Contexto: [Sección 3 del caso RutaColca y nuestra tabla de prioridades: E1(A,M), E2(A,A), E3(A,M), E4(M,B), E5(A,M)].
  Tarea: para cada escenario, indica qué información nos falta para estimar su dificultad y si alguna calificación te parece inconsistente con la arquitectura actual. No cambies las calificaciones: solo haz preguntas y observaciones.
  ```
* **Respuesta de la IA (Resumen):**
  La IA cuestionó si la dificultad de E1 (Rendimiento) realmente era Media (M), advirtiendo que 2000 consultas concurrentes sobre un PostgreSQL sin caché podría exigir Alta (A). Asimismo, confirmó que calificar E2 (Disponibilidad) como (A, A) era plenamente consistente debido a que la pasarela es un sistema externo incontrolable y la arquitectura actual es síncrona.
* **Criterio de Aceptación / Rechazo del Equipo:**
  - **Aceptado:** La advertencia sobre la necesidad de justificar la dificultad de E1 y la confirmación de que E2 concentra el riesgo crítico del negocio.
  - **Rechazado/Ajustado:** La sugerencia de la IA de subir E1 a (A, A); el equipo mantuvo E1 en (A, M) dado que la consulta de disponibilidad es de solo lectura y se mitiga eficazmente con caché en memoria, mientras que E2 involucra transacciones financieras y estados de dinero real.

---

### Registro 2 · Prompt P2: Iteración de ADD Asistida
* **Fase:** Parte A – Paso 3 (Iteración de ADD)
* **Integrante que ejecutó y verificó:** German Arturo Chipana Jeronimo (Arquitecto)
* **Texto del Prompt ejecutado:**
  ```text
  Actúa como arquitecto de software y aplica ADD 3.0.
  Contexto: Drivers de RutaColca (Tabla 3.3: 4 desarrolladores, 3 semanas, mantener monolito modular ADR-001, sin costos operativos extra), Escenario E2 (pasarela no responde 15 min -> 0 reservas perdidas; confirmación <= 30 min) y arquitectura actual.
  Objetivo de la iteración: cumplir la medida de nuestro escenario.
  Tarea: 1) propone dos alternativas (tácticas + patrón); 2) compáralas en beneficios, costos y riesgos; 3) indica qué elementos del C4 cambian en cada una.
  Reglas: respeta el ADR-001 (monolito modular) y el plazo de 3 semanas; si propones infraestructura nueva, estima su costo de operación; si falta información, pregunta antes de responder.
  ```
* **Respuesta de la IA (Resumen):**
  Propuso la Alternativa A: Transactional Outbox Pattern en PostgreSQL + Circuit Breaker en Spring Boot ($0 costo adicional).
  Propuso la Alternativa B: Despliegue de un clúster Apache Kafka o RabbitMQ en AWS/GCP (costo estimado: $60-$120 USD/mes).
* **Criterio de Aceptación / Rechazo del Equipo:**
  - **Aceptado:** La formulación de las tácticas de disponibilidad de Bass et al. (timeout + reintentos + outbox) y el cálculo de la tasa de procesamiento por lotes ($< 2$ min para 200 reservas).
  - **Rechazado:** La IA inicialmente sugirió usar Debezium (Change Data Capture - CDC) para leer el outbox; el equipo rechazó Debezium por requerir Kafka Connect y Zookeeper/Kraft, decidiendo implementar un worker nativo programado en Spring Boot con `FOR UPDATE SKIP LOCKED`, mucho más simple y 100% integrable en 1.5 semanas.

---

### Registro 3 · Prompt P3: Auditoría y Revisión del ADR
* **Fase:** Parte A – Paso 4 (Registro en ADR)
* **Integrante que ejecutó y verificó:** Leonardo Juan José Baca Calsin (Redactor)
* **Texto del Prompt ejecutado:**
  ```text
  Actúa como revisor de decisiones de arquitectura.
  Contexto: [Borrador del ADR-003 y Escenario E2].
  Tarea: verifica que el ADR explique el contexto, la decisión, la alternativa descartada y las consecuencias negativas. Señala frases vagas ("mejora el rendimiento") y propone cómo hacerlas medibles. No reescribas la decisión.
  ```
* **Respuesta de la IA (Resumen):**
  Identificó dos ambigüedades en el borrador: la frase "el worker procesará rápidamente las transacciones" y "el circuit breaker se abrirá oportunamente". Recomendó parametrizar con métricas verificables: timeout de 3.0 s, umbral de fallo del 50% en ventana de 10 peticiones, y sondeo cada 15 segundos en lotes de 50 registros.
* **Criterio de Aceptación / Rechazo del Equipo:**
  - **Aceptado:** Se incorporaron todas las cuantificaciones numéricas exactas en el texto definitivo del ADR-003.
  - **Ajustado:** La IA sugirió alertar sobre consistencia eventual; el equipo redactó la mitigación formal en la UI (mensaje tranquilizador al turista en React con tracking de ticket).

---

### Registro 4 · Prompt P4: Evaluación Cruzada ATAM (Escenario E3 - Seguridad)
* **Fase:** Parte A – Paso 5 (Evaluación Cruzada)
* **Integrante que ejecutó y verificó:** Mauro Snayder Sullca Mamani (Evaluador ATAM)
* **Texto del Prompt ejecutado:**
  ```text
  Actúa como evaluador ATAM.
  Contexto: Cinco escenarios priorizados de RutaColca y la propuesta de ADR del grupo de Seguridad (Escenario E3: Operador intenta modificar tour de otra agencia -> 100% bloqueado y auditado).
  Tarea: identifica riesgos, puntos de sensibilidad y trade-offs de la decisión respecto de los cinco escenarios, no solo del que motivó el ADR.
  Formato: tabla Tipo | Descripción | Escenario afectado. Marca con "?" lo que no puedas afirmar sin más información.
  ```
* **Respuesta de la IA (Resumen):**
  Destacó el trade-off inherente entre Seguridad y Rendimiento (E3 vs. E1): insertar auditoría síncrona en PostgreSQL por cada fallo de acceso degrada el $p95 \le 1.5\text{ s}$ ante ataques de fuerza bruta. Asimismo, alertó del riesgo BOLA si la autorización solo se verifica en la URL.
* **Criterio de Aceptación / Rechazo del Equipo:**
  - **Aceptado:** Se incluyó íntegramente el análisis del riesgo BOLA (OWASP API 1) y el trade-off con E1 en el entregable E4 (`evaluacion-cruzada.md`).
  - **Aportado por el equipo:** El equipo diseñó la mitigación técnica con eventos asíncronos en memoria (`@Async`) para la auditoría, solución que la IA no había propuesto en primera instancia.

---

### Registro 5 · Prompt P5: Modelado C4 y Vista Dinámica en Structurizr DSL
* **Fase:** Parte B – Paso 6 (Actualización de C4)
* **Integrante que ejecutó y verificó:** Leonardo Juan José Baca Calsin (Redactor)
* **Texto del Prompt ejecutado:**
  ```text
  Actúa como experto en el modelo C4 y en Structurizr DSL.
  Contexto: [workspace.dsl base de AG-08 y ADR-003].
  Tarea: indica las líneas que hay que agregar o cambiar para reflejar el ADR, incluida una vista dynamic del escenario.
  Reglas: no cambies elementos que el ADR no menciona; cada paso de la vista dinámica debe corresponder a una relación del modelo.
  ```
* **Respuesta de la IA (Resumen):**
  Sugirió declarar una vista `dynamic ruta "DinamicoPagosResiliente"` con 11 pasos secuenciales detallando el fallo de la pasarela, la inserción local en `pagos_outbox`, el aviso al turista y la reconciliación posterior del worker.
* **Criterio de Aceptación / Rechazo del Equipo:**
  - **Aceptado:** La estructura y secuencia de relaciones para la vista dinámica.
  - **Corregido por el equipo:** La IA omitió declarar la relación de retorno hacia el `Turista` desde `whatsApp` en el bloque `model`, lo que provocaba un error de validación en Structurizr CLI. El equipo corrigió la gramática agregando `whatsApp -> turista "Entrega confirmaciones de reserva..."` en el modelo base antes de exportar.

---

## 3. Matriz de Síntesis de Gobernanza

| Prompt ID | Tarea | Modelo de IA | Integrante Verificador | Decisión del Equipo |
| :---: | :--- | :---: | :---: | :---: |
| **P1** | Cuestionar priorización del árbol de utilidad | Antigravity AI | Emanuel Hilacondo Begazo | Aceptado con ajuste de justificación en E1 |
| **P2** | Iteración ADD 3.0 (Outbox vs. Broker) | Antigravity AI | German Arturo Chipana Jeronimo | Aceptado Outbox, rechazado CDC/Debezium |
| **P3** | Auditoría y eliminación de frases vagas en ADR | Antigravity AI | Leonardo Juan José Baca Calsin | Aceptado; cuantificación de métricas |
| **P4** | Evaluación ATAM cruzada de Seguridad (BOLA) | Antigravity AI | Mauro Snayder Sullca Mamani | Aceptado; mitigación con eventos `@Async` |
| **P5** | Vista dinámica C4 en Structurizr DSL | Antigravity AI | Leonardo Juan José Baca Calsin | Corregidas relaciones antes de exportación |
