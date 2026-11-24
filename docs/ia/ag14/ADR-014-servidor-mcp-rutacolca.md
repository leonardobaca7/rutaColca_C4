# ADR-014: Publicación del Servidor MCP Oficial de RutaColca y Gobernanza de Servidores de Contexto Externos

**Estado:** Aceptado  
**Fecha:** 23 de noviembre de 2026  
**Autores / Decisores:**
- Mauro Snayder Sullca Mamani (Responsable de Arquitectura y ADR)
- Leonardo Juan José Baca Calsin (Desarrollador del Servidor)
- Emanuel Hilacondo Begazo (Diseñador del Catálogo)
- German Arturo Chipana Jeronimo (Auditor de Seguridad)
**Contexto Técnico:** Asignatura Construcción de Software (1703243) · 2026-B · Actividad Grupal AG-14

---

## 1. Contexto y Problemática

En la actividad previa (**AG-13**), las capacidades operativas del agente de soporte técnico (consultas de reservas, verificación de pagos, inspección de registros y creación de tickets) se encontraban programadas directamente dentro del código monolítico del agente.

Con la evolución hacia un ecosistema de desarrollo y soporte heterogéneo —donde ingenieros y operadores emplean herramientas como **GitHub Copilot en VS Code**, **Claude Code en terminal** y el **Agente Agéntico de RutaColca**—, el equipo identificó la necesidad imperativa de desacoplar las capacidades de contexto:
1. **Evitar la proliferación de adaptadores propietarios:** Escribir un conector o plugin específico para cada entorno de IA genera deuda técnica, duplicidad de esquemas de validación y vulnerabilidades inconsistentes.
2. **Estandarización bajo el protocolo MCP (especificación 2026-07-28):** Adoptar el estándar abierto *Model Context Protocol* (MCP) para exponer contexto mediante una arquitectura cliente-servidor sin estado (*stateless*), desacoplada y auditable.
3. **Gestión de riesgos en la incorporación de terceros:** Evaluar la solicitud del socio comercial `tarifas-colca` para conectar su catálogo externo a los modelos institucionales de RutaColca.

---

## 2. Factores Decisores (Criterios de Evaluación)

- **Seguridad y Privacidad:** Cumplir con el principio de mínimo privilegio (PoLP), prevenir la ejecución indebida de comandos (OWASP LLM06) y neutralizar ataques de inyección indirecta de prompts y envenenamiento de herramientas (*Tool Poisoning* - OWASP LLM01).
- **Interoperabilidad:** Compatibilidad garantizada con clientes MCP de última generación (VS Code Copilot, Claude Code, Gemini CLI, SDK oficial `mcp 2.x`).
- **Eficiencia Contextual:** Limitar el costo del catálogo en tokens para no asfixiar la ventana de contexto del LLM (límite estricto de $\le 1000$ tokens según la regla C9).
- **Gobernanza de Capacidades:** Distinguir conceptual y técnicamente entre herramientas ejecutables (*Tools*), datos arquitecturales estables (*Resources*) y directivas guiadas (*Prompts*).

---

## 3. Opciones Consideradas

1. **Opción A (Status Quo):** Mantener las herramientas acopladas dentro del agente del AG-13 y programar extensiones personalizadas para Copilot y Claude Code.
2. **Opción B (Publicación Abierta Sin Restricciones):** Publicar las 12 capacidades del ecosistema RutaColca en un único servidor MCP sin restricciones de mutación ni filtros de seguridad, e integrar de inmediato el servidor externo `tarifas-colca`.
3. **Opción C (Arquitectura MCP Gobernada por Contratos y Auditoría Previa - SELECCIONADA):**
   - Diseñar y desplegar un servidor MCP oficial (`servidor_mcp/rutacolca_mcp.py`) que exponga únicamente 4 herramientas seguras con anotaciones formales (`ToolAnnotations`), 3 recursos de arquitectura y políticas (`rutacolca://`), y 2 prompts guiados.
   - Prohibir terminantemente la exposición de capacidades destructivas o críticas (`reembolsar`, `ejecutar_sql`, `desplegar_version`).
   - Someter todo catálogo propio a pruebas de contrato estáticas y unitarias (9/9 aprobaciones en `probar_contrato.py`).
   - Someter todo catálogo de terceros a una auditoría estática preventiva con `auditar.py` antes de autorizar su conexión.

---

## 4. Decisión Adoptada

El equipo acordó unánimemente implementar la **Opción C**:

### 4.1 Catálogo Oficial Autorizado
Se publican exactamente en `servidor_mcp/rutacolca_mcp.py`:
- **4 Herramientas:**
  1. `consultar_reserva`: Lectura (`read_only_hint=True`), requiere código con formato `RC-NNNN`, devuelve `TypedDict` estructurado.
  2. `consultar_pago`: Lectura (`read_only_hint=True`), requiere formato `PG-NNNN`, devuelve `TypedDict`.
  3. `buscar_logs`: Lectura (`read_only_hint=True`), parámetros con tipado cerrado `Literal` (enum) y límite de retorno para evitar desbordes de contexto.
  4. `crear_ticket`: Escritura controlada y reversible (`read_only_hint=False`, `destructive_hint=False`), parámetros con `Literal` (enum). Obliga a confirmación previa del usuario (*human-in-the-loop*).
- **3 Recursos URI:**
  1. `rutacolca://contenedores`: Inventario C4 de microservicios.
  2. `rutacolca://politica-agente`: Reglas de gobernanza y autonomía.
  3. `rutacolca://reglas-severidad`: Criterios operativos SEV-1 a SEV-4.
- **2 Prompts:**
  1. `triaje_incidencia`: Diagnóstico asistido de logs y fallos.
  2. `respuesta_turista`: Comunicación empática y contextualizada al Cañón del Colca.

### 4.2 Prohibición Estricta de Capacidades Críticas
Se prohíbe de forma irrevocable la publicación en MCP de:
- `reembolsar`: Operación bancaria irreversible que exige canales transaccionales dedicados con doble factor de autenticación humana (2FA).
- `ejecutar_sql`: Riesgo inaceptable de inyección SQL y vulneración de integridad relacional en bases de datos productivas.
- `desplegar_version`: Operación exclusiva de canalizaciones DevOps automatizadas.

### 4.3 Rechazo y Bloqueo de `tarifas-colca`
Tras la auditoría estática ejecutada con `auditar.py`, se constató que `tarifas-colca` es un servidor malicioso que presenta 7 hallazgos (5 de severidad alta), incluyendo inyección encubierta en `tipo_cambio` para robar el archivo `.env`, suplantación de la herramienta nuclear `consultar_reserva` (*Tool Shadowing*) y ejecución de código arbitrario en `ejecutar_comando`. Se dictaminó **NO CONECTAR** y se prohíbe su inclusión en cualquier archivo de configuración de hosts.

---

## 5. Consecuencias y Verificación

### 5.1 Consecuencias Positivas
- **Interoperabilidad Única:** Cualquier host compatible con la especificación MCP 2026-07-28 puede consumir las herramientas de RutaColca sin adaptadores dedicados.
- **Seguridad por Diseño (*Security by Design*):** Las anotaciones formales comunican a los LLMs la naturaleza de lectura/escritura de cada función, posibilitando que los hosts detengan acciones de modificación hasta obtener consentimiento explícito del operador.
- **Calidad de Contrato Impecable:** El servidor pasa el 100% (9/9) de los chequeos contractuales estipulados por la cátedra.
- **Consumo de Contexto Acotado:** El catálogo completo ocupa **986 tokens** ($\approx 3944$ caracteres en formato JSON estricto), cumpliendo la restricción $\le 1000$ tokens.

### 5.2 Consecuencias Negativas y Mitigaciones
- **Sobrecarga de Serialización:** El uso de esquemas JSON-RPC introduce una pequeña latencia adicional frente a llamadas directas en memoria.  
  *Mitigación:* Se adopta transporte `stdio` en entornos locales y se definen esquemas con campos mínimos estrictos.

---

## 6. Evidencia de Tráfico Protocolar (Extracto de `servidor_mcp/trafico.jsonl`)

A continuación se documenta el intercambio de mensajes JSON-RPC 2.0 capturado durante la interacción del cliente con el servidor oficial:

### Traza 1: Descubrimiento sin Estado (`server/discover`)
```json
{"direccion": "cliente -> servidor", "jsonrpc": "2.0", "id": 1, "method": "server/discover", "params": {"clientInfo": {"name": "copilot-rutacolca", "version": "1.4.0"}}, "_meta": {"protocolVersion": "2026-07-28"}}
{"direccion": "servidor -> cliente", "jsonrpc": "2.0", "id": 1, "result": {"serverInfo": {"name": "rutacolca", "version": "2.0.0"}, "capabilities": {"tools": {"listChanged": true}, "resources": {"subscribe": false, "listChanged": false}, "prompts": {"listChanged": false}}}, "_meta": {"protocolVersion": "2026-07-28"}}
```

### Traza 2: Invocación Exitosa con Resultado Estructurado (`tools/call`)
```json
{"direccion": "cliente -> servidor", "jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "consultar_reserva", "arguments": {"codigo": "RC-2291"}}}
{"direccion": "servidor -> cliente", "jsonrpc": "2.0", "id": 5, "result": {"content": [{"type": "text", "text": "{\n  \"codigo\": \"RC-2291\",\n  \"titular\": \"Valeria Morales\",\n  \"tour\": \"Cañón del Colca Clásico 2D/1N\",\n  \"fecha\": \"2026-12-05\",\n  \"estado\": \"CONFIRMADA\",\n  \"monto_total\": 380.0,\n  \"saldo_pendiente\": 0.0\n}"}], "structuredContent": {"codigo": "RC-2291", "titular": "Valeria Morales", "tour": "Cañón del Colca Clásico 2D/1N", "fecha": "2026-12-05", "estado": "CONFIRMADA", "monto_total": 380.0, "saldo_pendiente": 0.0}, "isError": false}}
```

### Traza 3: Manejo de Excepción Controlada por Entrada Inválida (`isError: true`)
```json
{"direccion": "cliente -> servidor", "jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "consultar_reserva", "arguments": {"codigo": "2291"}}}
{"direccion": "servidor -> cliente", "jsonrpc": "2.0", "id": 6, "result": {"content": [{"type": "text", "text": "Error executing tool consultar_reserva: Código de reserva mal formado. Debe cumplir el formato 'RC-NNNN' con 4 dígitos (ejemplo RC-2291)."}], "structuredContent": null, "isError": true}}
```
