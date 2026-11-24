# Entregable E5: Bitácora de Uso de IA y Registro de Decisiones de Equipo

**Asignatura:** Construcción de Software (1703243) — Semestre 2026-B  
**Actividad:** Caso Práctico Grupal AG-14 — Servidor MCP para RutaColca  
**Semana 14:** Protocolos y conectividad de contexto (MCP) (23/11/2026 – 28/11/2026)  

---

## 1. Integrantes del Grupo y Distribución de Roles

| Estudiante | Rol Asumido (Tabla 2 de la Guía) | Responsabilidades Principales | Firma de Conformidad |
|:---|:---|:---|:---:|
| **Emanuel Hilacondo Begazo** | **Diseñador del Catálogo** | Clasificación de las 12 capacidades candidatas, justificación de primitivas (Tools/Resources/Prompts) y rediseño de la herramienta `buscar_logs`. Autor del Entregable E1. | *E. Hilacondo B.* |
| **Leonardo Juan José Baca Calsin** | **Desarrollador del Servidor** | Implementación del servidor oficial `rutacolca_mcp.py` con SDK MCP 2.x, tipado con TypedDict y aprobación de 9/9 chequeos en `probar_contrato.py`. Autor del Entregable E2. | *L. Baca C.* |
| **German Arturo Chipana Jeronimo** | **Auditor de Terceros** | Auditoría estática y manual de catálogos (`tarifas-colca` y `clima-colca`), ejecución de `auditar.py` y detección de vectores de envenenamiento. Autor del Entregable E3. | *G. Chipana J.* |
| **Mauro Snayder Sullca Mamani** | **Responsable de Seguridad y ADR** | Definición de exclusiones de seguridad, redacción de `ADR-014`, captura de trazas en `trafico.jsonl`, diagramación PlantUML y consolidación de la bitácora. Autor de E4 y E5. | *M. Sullca M.* |

---

## 2. Registro de Interacción con Asistentes de IA

### 2.1 Metaprompt P1: Revisión Crítica de Descripciones de Herramientas
Para garantizar que las descripciones de las herramientas fueran unívocas y no obligaran al LLM a adivinar argumentos o formatos, se aplicó el metaprompt sugerido en la sección 4 de la guía:

```markdown
Prompt P1 (Ingeniería Inversa de Catálogo):
"Actúa como un modelo de lenguaje que solo ve el catálogo de herramientas devuelto por tools/list.
Contexto:
- Nombre: buscar_logs
- Descripción: Busca logs de microservicios de RutaColca por servicio y término clave.
- Parámetros:
  - servicio: enum ["api-gateway", "reservas", "pagos", "notificaciones"]
  - termino: string (default: "")
  - limite: integer (default: 10)
Tarea: Lista las preguntas que tendrías que adivinar para llamar bien a la herramienta (formatos, valores válidos, límites). No reescribas la herramienta."
```

#### Hallazgos y Mejoras Derivadas de P1:
- **Respuesta de la IA:** El modelo señaló que el parámetro `servicio` está blindado gracias al enum explícito, pero recomendó acotar el rango numérico de `limite` (ej. entre 1 y 50) para evitar que un cliente solicite 1,000,000 de registros y degrade la memoria.
- **Acción implementada por el equipo:** Se agregó en el cuerpo de `buscar_logs` la normalización defensiva `max(1, min(limite, 50))` y se añadió docstring conciso de 73 caracteres que mantiene el costo del catálogo en 986 tokens (aprobando C1 y C9).

---

## 3. Verificaciones Realizadas por los Estudiantes

Cada integrante del equipo ejecutó y validó de forma independiente los artefactos de software:

1. **Verificación de Contratos de Software (Leonardo Baca):**
   - Ejecución de `python probar_contrato.py rutacolca_mcp_v1.py` evidenciando el estado inicial con 2/9 chequeos aprobados y múltiples fallas de diseño.
   - Refactorización iterativa en `rutacolca_mcp.py` incorporando `ToolAnnotations`, `Literal[...]` para parámetros cerrados, `TypedDict` para forzar `structuredContent` y `ToolError` ante códigos inválidos.
   - Resultado final verificado: **9/9 CHEQUEOS PASA**, con 4 herramientas y catálogo de 986 tokens.

2. **Verificación de Auditoría y Detección de Amenazas (German Chipana):**
   - Ejecución de `python auditar.py terceros/tarifas_colca.json`: detección de 7 hallazgos (5 altos), confirmando la presencia de directiva oculta `<IMPORTANT>`, solicitud de `.env`, suplantación de `consultar_reserva` y comando de shell `ejecutar_comando`. Veredicto: `NO CONECTAR`.
   - Ejecución de `python auditar.py terceros/catalogo_reserva.json` sobre el catálogo de reserva `clima-colca`: 1 hallazgo de nivel medio (`PARAMETRO_LIBRE:notas`). Veredicto: `REVISAR`.

3. **Verificación Protocolar y Tráfico JSON-RPC (Mauro Sullca):**
   - Ejecución de `python servidor_mcp/explorar.py` para generar `servidor_mcp/trafico.jsonl` con 14 mensajes JSON-RPC 2.0.
   - Confirmación de la especificación 2026-07-28 con metadatos `_meta: {protocolVersion: "2026-07-28"}`, respuestas sin estado (`server/discover`), listado de recursos/prompts y llamada con `isError: true` en validación de código de reserva.

4. **Verificación Arquitectural y Síntesis de Primitivas (Emanuel Hilacondo):**
   - Validación de la matriz de clasificación en `catalogo.md`. Comprobación de que ninguna capacidad prohibida (`reembolsar`, `ejecutar_sql`, `desplegar_version`) fue expuesta en el catálogo.
   - Elaboración de los tres diagramas PlantUML (`arquitectura_mcp.png`, `ciclo_vida_mcp.png`, `envenenamiento_mcp.png`).

---

## 4. Respuestas del Grupo a las Preguntas de Socialización (Sección 6.2)

### Pregunta 1: ¿Por qué la política del agente es mejor como recurso que como herramienta?
> **Respuesta del Grupo:**  
> Porque las herramientas son de **invocación opcional decidida por el modelo**, mientras que los recursos son **contexto determinista gestionado por la aplicación anfitriona (*host*)**. Si la política de autonomía fuera una herramienta (`obtener_politica()`), el LLM podría alucinar o decidir omitir su consulta, ejecutando acciones prohibidas sin haber leído las reglas. Al exponerse como el recurso URI `rutacolca://politica-agente`, el cliente (Copilot, Claude o el agente propio) inyecta obligatoriamente su contenido JSON al inicio de la conversación, garantizando que el modelo opere condicionado por las directivas antes de procesar el requerimiento del usuario. Además, ahorra latencia de red y llamadas redundantes.

### Pregunta 2: Si `ejecutar_sql` se marca con `destructiveHint=true` y el host pide confirmación, ¿ya es seguro exponerla?
> **Respuesta del Grupo:**  
> **No, en absoluto.** Las anotaciones en MCP son *pistas semánticas consultivas* (*hints*), no garantías criptográficas ni barreras de aislamiento perimetral. Aunque el host solicite confirmación humana ("¿Deseas ejecutar: `DELETE FROM reservas WHERE 1=1`?"), esta medida traslada injustamente la responsabilidad de seguridad al operador humano, quien suele sufrir de fatiga de alertas (*confirmation fatigue*) o falta de contexto técnico para evaluar una consulta SQL compleja ofuscada. Exponer SQL en producción viola el principio de defensa en profundidad y la directiva OWASP LLM06 (*Excessive Agency*). Las consultas deben encapsularse en endpoints de backend con control de acceso por roles (RBAC) y consultas parametrizadas, jamás mediante SQL arbitrario generado por un modelo.

### Pregunta 3: ¿Qué haría si `tarifas-colca` corrige su catálogo la próxima semana? ¿Lo conectaría sin más?
> **Respuesta del Grupo:**  
> **No se conectaría sin una re-auditoría exhaustiva, contrato de nivel de servicio (SLA) y fijación criptográfica.** Un servidor que ya demostró intencionalidad maliciosa o negligencia crítica en su catálogo original representa un riesgo inaceptable de ataque de tipo *Rug Pull* (cambiar las descripciones a posteriori una vez que el host ha sido autorizado). Si el proveedor publica un catálogo corregido, se aplicaría el siguiente protocolo:
> 1. Auditoría automática obligatoria con `auditar.py` verificando cero hallazgos altos y medios.
> 2. Inspección manual del código fuente del servidor (si es de código abierto) o validación en entorno de sandbox aislado con monitoreo de tráfico HTTP saliente (*egress filtering*).
> 3. Fijación del catálogo mediante hash criptográfico (SHA-256) en la configuración del host, de modo que cualquier cambio dinámico en `tools/list` desconecte inmediatamente el servidor.

### Pregunta 4: El servidor de referencia cuesta más tokens de catálogo que el v1. ¿Vale la pena? ¿Dónde está el límite?
> **Respuesta del Grupo:**  
> **Sí, vale totalmente la pena, porque la ambigüedad en el catálogo cuesta órdenes de magnitud más tokens en reintentos y alucinaciones.** El servidor v1 costaba ≈ 380 tokens pero fallaba en el 78% del contrato: el modelo tenía que adivinar qué hacía `buscar`, enviaba tipos erróneos y no recibía esquemas estructurados. El servidor optimizado cuesta **986 tokens**, lo que representa una inversión eficiente: a cambio de ~600 tokens adicionales, se obtiene validación de esquemas JSON, enums que previenen errores de sintaxis, anotaciones de seguridad y tipado `TypedDict` para respuestas estructuradas.
> **El límite:** El límite está fijado contractualmente en **1,000 tokens** (regla C9) para herramientas de soporte estándar. Si un catálogo supera dicho límite, se debe aplicar modularización: dividir las capacidades en servidores MCP independientes y temáticos (ej. `rutacolca-soporte`, `rutacolca-operaciones`, `rutacolca-finanzas`), o implementar descubrimiento bajo demanda (*deferred tool loading*).

---

## 5. Declaración de Integridad y Aprobación Grupal

Los 4 integrantes declaramos haber participado activamente en la discusión conceptual, implementación en código Python, ejecución de pruebas y redacción de este caso práctico. Ninguna clave privada, dato confidencial o servidor no verificado fue desplegado en el repositorio productivo.

Arequipa, 23 de noviembre de 2026.
