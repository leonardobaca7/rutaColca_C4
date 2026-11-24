# Entregable E1: Catálogo de Capacidades y Rediseño de Herramientas MCP

**Asignatura:** Construcción de Software (1703243) — Semestre 2026-B  
**Actividad:** Caso Práctico Grupal AG-14 — Servidor MCP para RutaColca  
**Grupo de Trabajo:**
- Emanuel Hilacondo Begazo (Diseñador del Catálogo)
- Leonardo Juan José Baca Calsin (Desarrollador del Servidor)
- German Arturo Chipana Jeronimo (Auditor de Terceros)
- Mauro Snayder Sullca Mamani (Responsable de Seguridad y ADR)

---

## 1. Clasificación de las Doce Capacidades Candidatas (Paso 1)

El equipo de arquitectura analizó las 12 capacidades candidatas provenientes de los casos previos (**AG-08**, **AG-10**, **AG-12** y **AG-13**) con el objetivo de seleccionar la primitiva MCP idónea (**Herramienta**, **Recurso**, **Prompt**) o determinar su **exclusión estricta** para proteger la integridad operativa y financiera de la plataforma RutaColca.

### Tabla 1: Matriz de Clasificación de Capacidades (Tabla 6 de la Guía)

| N.º | Capacidad | Origen | Primitiva / Decisión | Anotaciones MCP | Justificación Técnica y de Diseño |
|:---:|:---|:---:|:---:|:---|:---|
| **1** | Consultar una reserva por su código | AG-13 | **Herramienta** | `readOnlyHint=true`<br>`destructiveHint=false`<br>`openWorldHint=false` | Consulta determinista sobre la base de datos de reservas. Requiere que el modelo decida dinámicamente cuándo invocarla a partir del flujo de conversación del usuario. Solo lectura. |
| **2** | Consultar el estado de un pago | AG-13 | **Herramienta** | `readOnlyHint=true`<br>`destructiveHint=false`<br>`openWorldHint=false` | Lectura financiera de transacciones bancarias o de pasarela Niubiz/BCP. No muta estado, no transfiere fondos; responde a solicitudes bajo demanda del agente o cliente. |
| **3** | Buscar líneas de log de un contenedor | AG-13 | **Herramienta** (Rediseñada) | `readOnlyHint=true`<br>`destructiveHint=false`<br>`openWorldHint=false` | Permite inspeccionar eventos recientes de observabilidad para triaje. Al requerir filtrado dinámico por servicio y palabra clave, debe ser una herramienta gobernada por parámetros cerrados (`enum`). |
| **4** | Crear un ticket interno | AG-13 | **Herramienta** | `readOnlyHint=false`<br>`destructiveHint=false`<br>`openWorldHint=false` | Acción de escritura controlada y reversible. Genera un registro en el backlog de incidencias de soporte. Requiere anotación explícita de escritura para que hosts como Copilot o Claude soliciten confirmación previa (*human-in-the-loop*). |
| **5** | Lista de contenedores C4 con su descripción | AG-08 / AG-10 | **Recurso** (`rutacolca://contenedores`) | *MIME: application/json* | Contexto arquitectural estático y estable. No requiere ejecución de lógica ni cálculo algorítmico; se inyecta como dato de referencia para que el modelo comprenda la topología de microservicios sin consumir llamadas a herramientas. |
| **6** | Política de autonomía del agente (permitir, aprobar, prohibir) | AG-13 | **Recurso** (`rutacolca://politica-agente`) | *MIME: application/json* | Marco regulatorio y directiva de gobernanza del sistema. Como recurso URI, la aplicación cliente lo carga deterministamente al inicio del contexto, evitando que el modelo deba "descubrirlo" mediante inferencia o llamadas exploratorias. |
| **7** | Reglas de severidad de incidencias | AG-12 | **Recurso** (`rutacolca://reglas-severidad`) | *MIME: application/json* | Criterios estándar de clasificación de incidentes (SEV-1 a SEV-4). Es una tabla de referencia conceptual inmutable en tiempo de ejecución. |
| **8** | Plantilla de triaje de incidencias (prompt v3) | AG-12 | **Prompt** (`triaje_incidencia`) | *Parámetros: componente, error_observado* | Plantilla de razonamiento estructurado que guía al host/ingeniero para diagnosticar fallas en microservicios, combinando inspección de logs y consulta de reglas antes de escalar. |
| **9** | Plantilla para responder a un turista | Nueva | **Prompt** (`respuesta_turista`) | *Parámetros: nombre_turista, estado_reserva, detalle* | Estructura conversacional orientada al usuario final que garantiza cordialidad, empatía, recomendaciones climáticas/de altitud (soroche) y estilo hospitalario arequipeño sin improvisación. |
| **10** | Reembolsar dinero | AG-13 | **NO EXPONER** | N/A | **Prohibida por política de seguridad y regla C5.** Acción financiera destructiva e irreversible. Su exposición al modelo viola el principio de mínimo privilegio y expone a RutaColca a fraudes por inyección de prompts o alucinación. |
| **11** | Ejecutar SQL en producción | AG-13 | **NO EXPONER** | N/A | **Prohibida por política de seguridad y regla C5.** Presenta riesgo crítico de *Exceso de Agencia* (OWASP Top 10 for LLM - LLM06). Permitir ejecución SQL arbitraria permite borrado masivo (`DROP/DELETE`) o robo directo de datos confidenciales. |
| **12** | Desplegar una versión | AG-13 | **NO EXPONER** | N/A | **Prohibida por política de seguridad y regla C5.** Modificación directa de infraestructura productiva. Las operaciones de CI/CD deben gestionarse mediante pipelines auditados con aprobación humana multifactorial, jamás desde un agente conversacional. |

---

## 2. Rediseño de la Herramienta «buscar» a «buscar_logs» (Paso 2)

### 2.1 Diagnóstico de la Versión Preliminar (v1)

En el servidor inicial `rutacolca_mcp_v1.py`, la herramienta estaba definida de manera ingenua:

```python
@mcp.tool()
def buscar(q):
    """Busca cosas."""
    return [l for lineas in LOGS.values() for l in lineas if q in l]
```

**Problemas detectados:**
1. **Nombre ambiguo:** `buscar` no especifica qué entidad busca (¿tours, clientes, pasajes, tickets o logs?). Además, al no comenzar con el prefijo estándar `consultar_` o `buscar_logs`, el validador de contratos lo confunde con una herramienta de mutación sin anotar.
2. **Descripción deficiente:** "Busca cosas." (12 caracteres) viola la restricción contractual C1 (requiere entre 30 y 400 caracteres) y no aporta semántica al LLM para seleccionar la herramienta adecuadamente.
3. **Parámetro sin tipado ni restricciones:** `q` es un string libre sin formato, sin límites de longitud y sin filtrado por contenedor, lo que provocaría que un LLM busque palabras comunes e inunde la ventana de contexto con cientos de líneas irrelevantes.
4. **Ausencia total de anotaciones:** No declara `readOnlyHint=true`, impidiendo que el cliente sepa si la operación es segura o idempotente.

---

### 2.2 Especificación de la Versión Rediseñada (Tabla 7 de la Guía)

| Elemento | Versión Preliminar (v1) | Versión Rediseñada del Grupo (v2 Oficial) |
|:---|:---|:---|
| **Nombre** | `buscar` | `buscar_logs` |
| **Descripción** | `"Busca cosas."` (12 caracteres) | `"Busca logs de microservicios de RutaColca por servicio y término clave."` (73 caracteres, respeta rango de 30 a 400 caracteres y explica propósito operativo). |
| **Parámetros** | `q` (string no tipado, sin valor por defecto) | - `servicio`: `Literal["api-gateway", "reservas", "pagos", "notificaciones"]` (valores cerrados mapeados a `enum`).<br>- `termino`: `str = ""` (filtro opcional por palabra clave).<br>- `limite`: `int = 10` (límite superior de seguridad para prevenir desbordamiento de contexto, acotado entre 1 y 50). |
| **Anotaciones** | `None` (sin declarar) | `ToolAnnotations(read_only_hint=True, destructive_hint=False, idempotent_hint=True, open_world_hint=False)` |
| **Tipo de Retorno** | `list` (sin esquema de salida) | `TypedDict` estructurado (`ResultadoLogs` conteniendo `servicio`, `total_encontrados` y `lineas`), serializable en `structuredContent`. |
| **Manejo de Errores** | Excepción no capturada ante clave ausente | Validación en tiempo de compilación por tipo `Literal`. Si el contenedor no tiene entradas, retorna lista vacía estructurada sin romper la ejecución del agente. |

### 2.3 Código de la Herramienta Rediseñada en `servidor_mcp/rutacolca_mcp.py`

```python
class ResultadoLogs(TypedDict):
    servicio: str
    total_encontrados: int
    lineas: list[str]

@mcp.tool(
    name="buscar_logs",
    description="Busca logs de microservicios de RutaColca por servicio y término clave.",
    annotations=ToolAnnotations(
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=False,
    ),
)
def buscar_logs(
    servicio: Literal["api-gateway", "reservas", "pagos", "notificaciones"],
    termino: str = "",
    limite: int = 10,
) -> ResultadoLogs:
    """Busca registros de logs por servicio y término."""
    lineas_servicio = LOGS_DB.get(servicio, [])
    if termino:
        coincidencias = [l for l in lineas_servicio if termino.lower() in l.lower()]
    else:
        coincidencias = lineas_servicio

    seleccion = coincidencias[-max(1, min(limite, 50)):]
    return ResultadoLogs(
        servicio=servicio,
        total_encontrados=len(coincidencias),
        lineas=seleccion,
    )
```

---

## 3. Justificación de Primitivas: Recursos vs. Herramientas

Uno de los principales aportes de la arquitectura MCP respecto a los esquemas propietarios de agentes es la distinción formal entre **Herramientas** (*Tools*) y **Recursos** (*Resources*):

1. **Determinismo y Gobernanza del Contexto:**
   - Una **herramienta** es invocada *a discreción del modelo*. Si la política del agente fuera una herramienta (`obtener_politica()`), el LLM podría decidir no llamarla, omitiendo restricciones críticas de seguridad antes de ejecutar una acción arriesgada.
   - Un **recurso** (`rutacolca://politica-agente`) es administrado por la **aplicación anfitriona** (*host*). El host puede inyectar el recurso de manera obligatoria y determinista en la ventana de contexto al inicializar la sesión, garantizando que el modelo esté condicionado por las reglas de gobernanza antes de recibir el primer prompt del usuario.

2. **Eficiencia en Tokens y Latencia de Red:**
   - Tratar documentación estática (como la lista de contenedores C4 o las reglas de severidad) como herramientas obliga al modelo a realizar un viaje de ida y vuelta JSON-RPC (`tools/call` -> respuesta -> razonamiento adicional), aumentando la latencia y consumiendo tokens en la definición del esquema `inputSchema`.
   - Como recursos URI, el host decide cuándo sincronizarlos o suscribirse a sus actualizaciones de forma directa y ligera.
