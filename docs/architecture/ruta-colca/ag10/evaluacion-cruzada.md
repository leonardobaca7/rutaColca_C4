# Entregable E4: Evaluación Cruzada al Estilo ATAM Ligero (AG-10)

**Curso:** Construcción de Software (1703243) – Semestre 2026-B  
**Docente:** Mg. Antonio Arroyo Paz  
**Evaluador ATAM responsable:** Mauro Snayder Sullca Mamani (`msullcam@unsa.edu.pe`)  
**Fecha:** 28 de octubre de 2026  
**Iteración:** ADD 3.0 – Paso 5: Evaluación Cruzada de Arquitectura  

---

## 1. Contexto de la Evaluación Cruzada

Siguiendo la regla de rotación de escenarios establecida por la cátedra ($E_i \rightarrow E_{i+1}$), a nuestro equipo (responsable del escenario **E2: Disponibilidad**) le correspondió evaluar el diseño arquitectónico y el ADR del equipo a cargo del escenario subsiguiente:

> **Escenario Evaluado · E3: Seguridad (Control de Acceso / BOLA)**  
> *"Un operador de agencia intenta consultar o modificar un tour registrado por otra agencia aliada. Medida esperada: 100% de los intentos bloqueados con HTTP 403 y registrados en el log de auditoría."*

El grupo evaluado propuso en su ADR implementar una validación de autorización en el API Gateway / Controller de Spring Security mediante claims en tokens JWT, complementado con un interceptor que inserta registros en una tabla de auditoría `seguridad_auditoria`.

---

## 2. Matriz de Evaluación ATAM Ligero (Tabla 10 de la guía)

Se identificaron de forma rigurosa los **Riesgos**, **Puntos de Sensibilidad** y **Trade-offs** del diseño presentado, analizando su impacto integral sobre los cinco escenarios de calidad del sistema:

### Tabla 1. Matriz de hallazgos arquitectónicos de evaluación cruzada

| Tipo de Hallazgo | Definición Teórica (Kazman et al., 2000) | Hallazgo Concreto en el Diseño del Grupo Evaluado (Escenario E3) | Escenario Afectado | Recomendación de Mitigación del Evaluador |
| :--- | :--- | :--- | :---: | :--- |
| **Riesgo 1** | Decisión de diseño que puede comprometer o impedir el cumplimiento de un escenario de calidad. | **Vulnerabilidad BOLA (*Broken Object Level Authorization* - OWASP API 1):** El grupo propone validar la autorización verificando únicamente el rol `OPERADOR` en el token JWT dentro del Controller. Si un operador legítimo de la "Agencia Chivay Tours" manipula el identificador `{tourId}` en la URL (`PUT /api/tours/842`) perteneciente a "Colca Expeditions", el rol es válido pero el recurso no le pertenece, permitiendo la modificación no autorizada. | **E3 (Seguridad)** | Implementar autorización mandatoria a nivel de entidad/método en el dominio mediante `@PreAuthorize("@permisosService.esPropietarioTour(principal, #tourId)")` o en el repositorio antes de cualquier mutación de datos. |
| **Riesgo 2** | Decisión de diseño que puede comprometer o impedir el cumplimiento de un escenario de calidad. | **Escritura síncrona y bloqueante de auditoría:** Cada intento de acceso bloqueado ejecuta un `INSERT` síncrono en la tabla de auditoría de PostgreSQL. Ante un ataque de denegación de servicio (DoS) con miles de intentos deliberados de acceso a IDs ajenos, la base de datos colapsará por contención de escrituras. | **E1 (Rendimiento)** | Desacoplar el registro de auditoría utilizando eventos asíncronos internos de Spring (`ApplicationEventPublisher` con `@Async`) con volcado en lotes hacia la base de datos. |
| **Punto de Sensibilidad 1** | Parámetro o variable de configuración de la que depende críticamente el valor de una medida de calidad. | **Tiempo de expiración (*Time-To-Live* - TTL) de los tokens JWT:** Un TTL muy extenso (ej. 8 horas) permite que un operador despedido continúe manipulando datos. Un TTL muy corto (ej. 5 minutos) genera sobrecarga de re-autenticación y consultas frecuentes a la base de datos. | **E3 (Seguridad) / E1 (Rendimiento)** | Fijar un TTL de 15 minutos para tokens de acceso, complementado con *Refresh Tokens* rotativos de un solo uso y revocación mediante lista negra ligera en memoria. |
| **Punto de Sensibilidad 2** | Parámetro o variable de configuración de la que depende críticamente el valor de una medida de calidad. | **Índices en la consulta de pertenencia:** La verificación de titularidad `WHERE tour_id = ? AND agencia_id = ?` debe resolverse en $< 10\text{ ms}$ para no penalizar la latencia total de la API. | **E1 (Rendimiento)** | Crear un índice compuesto único `CREATE UNIQUE INDEX idx_tours_agencia ON tours(id, agencia_id);`. |
| **Trade-off 1** | Decisión arquitectónica que beneficia directamente un atributo de calidad pero perjudica a otro. | **Seguridad Estricta vs. Latencia de Rendimiento (E3 vs. E1):** La doble verificación (inspección de token + consulta de pertenencia en BD + inserción de log de auditoría) incrementa la seguridad al 100%, pero introduce una penalización de entre 25 ms a 60 ms por cada petición HTTP, lo que podría poner en riesgo la meta de $p95 \le 1.5\text{ s}$ del escenario E1 bajo carga de 2000 usuarios concurrentes. | **E3 (Seguridad) $\leftrightarrow$ E1 (Rendimiento)** | Almacenar en caché en memoria (Caffeine o Redis local) la tupla de pertenencia `(tour_id, agencia_propietaria)` con invalidación únicamente al modificarse la titularidad del tour. |
| **Trade-off 2** | Decisión arquitectónica que beneficia directamente un atributo de calidad pero perjudica a otro. | **Seguridad vs. Modificabilidad (E3 vs. E4):** Agregar reglas de autorización dispersas en múltiples controladores y servicios acopla el código de negocio con las políticas de seguridad de agencias. | **E3 (Seguridad) $\leftrightarrow$ E4 (Modificabilidad)** | Encapsular las reglas de autorización en un aspecto transversal (*Aspect-Oriented Programming* - AOP) mediante una anotación personalizada `@VerificarPropietario(tipo = Recurso.TOUR)`. |

---

## 3. Dictamen y Conclusiones de la Evaluación Cruzada

1. **Aceptación Condicionada del Diseño:** La propuesta del grupo para el escenario E3 atiende el requerimiento de negocio, pero debe subsanar el riesgo de vulnerabilidad BOLA trasladando la verificación de permisos desde la capa perimetral (Gateway/URL) hacia la capa de aplicación/dominio.
2. **Impacto Sistémico:** La seguridad no puede diseñarse de forma aislada; las escrituras de auditoría síncronas representan una amenaza directa contra el rendimiento (E1) y la disponibilidad global del sistema en temporada alta.
3. **Alineación con el Monolito Modular:** Se felicita al equipo evaluado por no haber propuesto microservicios de autenticación separados (como servidores OAuth/Keycloak externos que violarían los costos y plazos de 3 semanas), manteniendo la solución dentro de los límites del monolito modular (ADR-001).
