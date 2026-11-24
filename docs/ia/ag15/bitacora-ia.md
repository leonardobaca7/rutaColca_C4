# Entregable E5: Bitácora de Uso de IA y Registro de Decisiones de Equipo

**Asignatura:** Construcción de Software (1703243) — Semestre 2026-B  
**Actividad:** Caso Práctico Grupal AG-15 — Revisar un Pull Request de la IA  
**Semana 15:** Desarrollo asistido por IA (23/11/2026 – 28/11/2026)  

---

## 1. Integrantes del Grupo y Distribución de Roles

| Estudiante | Rol Asumido (Tabla 2 de la Guía) | Responsabilidades Principales | Firma de Conformidad |
|:---|:---|:---|:---:|
| **Emanuel Hilacondo Begazo** | **Analista de la Especificación** | Redacción y extensión de la especificación HU-RC-21 con 6 escenarios Gherkin, vigilancia de casos borde de 24h, 72h y límite de supervisor. Autor del Entregable E1. | *E. Hilacondo B.* |
| **German Arturo Chipana Jeronimo** | **Revisor del Pull Request** | Auditoría del diff de la IA con la lista del Anexo A, redacción de la hoja de revisión con los 7 defectos y dictamen de solicitud de cambios. Autor del Entregable E2. | *G. Chipana J.* |
| **Leonardo Juan José Baca Calsin** | **Desarrollador y Responsable TDD** | Implementación de `rutacolca/reembolso.py` guiada por pruebas TDD, superación de 15/15 pruebas unitarias y 7/7 compuertas en `verificar.py`. Autor de E3. | *L. Baca C.* |
| **Mauro Snayder Sullca Mamani** | **Responsable de AGENTS.md y Calidad** | Redacción de las directivas en `AGENTS.md`, configuración del pipeline de CI/CD, diagramas PlantUML y consolidación de la bitácora. Autor de E4 y E5. | *M. Sullca M.* |

---

## 2. Registro de Interacción con Asistentes de IA

### 2.1 Metaprompt P1: La IA como Segunda Revisora
Se evaluó el borrador defectuoso de la IA (`borrador_ia/reembolso_v0.py`) empleando un LLM en modo revisor de código:

```text
Prompt P1 (Revisor Senior de Python):
"Actúa como revisor senior de Python en un equipo que usa TDD.
Contexto: [specs/hu-rc-21/spec.md, diff de borrador_ia/reembolso_v0.py y AGENTS.md].
Tarea: Lista los defectos del PR indicando archivo, línea y nivel de gravedad. No reescribas el código."
```

#### Comparativa y Hallazgos:
- **Aciertos de la IA:** Identificó rápidamente la llamada insegura a `subprocess.run` (CWE-78) y la alucinación del paquete `reembolsos_peru`.
- **Omisión Crítica (Falso Negativo):** La IA revisora dio por buenas las pruebas unitarias de `tests_ia/test_reembolso_ia.py` simplemente porque su ejecución arrojaba resultado verde (3 passed). No contrastó que la aserción `assert calcular_reembolso(100, 72, "cliente")["porcentaje"] == 50` contradecía flagrantemente la regla de negocio del 100 %.
- **Intervención del Equipo:** El equipo humano corrigió este sesgo, catalogando la prueba defectuosa como defecto crítico de la suite.

---

### 2.2 Desarrollo Guiado por Pruebas (TDD) en Modo Agente
Para la implementación oficial de `rutacolca/reembolso.py`, el equipo trabajó en un ciclo riguroso de TDD apoyado por un asistente en modo agente:

1. **Fase Roja (Red):** Con las 15 pruebas de `tests/test_reembolso.py` ya escritas a partir de la especificación Gherkin, se ejecutó `pytest` contra el borrador v0, constatando el fallo de 8 pruebas críticas.
2. **Instrucción al Asistente:**
   ```text
   Prompt de Implementación:
   "Implementa la función calcular_reembolso en rutacolca/reembolso.py de modo que pase las 15 pruebas de tests/test_reembolso.py y supere las 7 compuertas de calidad/verificar.py.
   Restricciones obligatorias:
   1. Usa decimal.Decimal y ROUND_HALF_UP para la moneda.
   2. Importa LIMITE_AGENTE desde rutacolca.politica; no quemes números literales.
   3. No uses subprocess ni librerías fuera de stdlib.
   4. Mantén longitud de líneas <= 88 caracteres para cumplir con ruff E501."
   ```
3. **Fase Verde (Green):** La primera propuesta generada pasó 15/15 pruebas unitarias y 6/7 compuertas, fallando únicamente en la compuerta 3 por una línea de 91 caracteres (Ruff `E501`).
4. **Fase de Refactorización (Refactor):** El equipo dividió el string de excepción en dos líneas, alcanzando **7/7 compuertas PASA**, 100 % de cobertura y complejidad máxima de 8.

---

## 3. Respuestas del Grupo a las Preguntas de Socialización (Sección 6.2)

### Pregunta 1: ¿Por qué las 3 pruebas del PR no demuestran que el código cumple la historia?
> **Respuesta del Grupo:**  
> Porque las pruebas del PR sufren de **sesgo de confirmación retrospectivo**: fueron redactadas por el mismo agente para confirmar lo que el código defectuoso ya hacía, en lugar de derivarse de la especificación funcional. El ejemplo paradigmático es `test_reembolso_medio`, que evalúa 72 horas esperando un 50 %: la prueba pasa exitosamente y da una ilusión de corrección, pero en realidad está blindando un error de negocio que despoja al turista del 100 % de su reembolso. Una prueba solo tiene valor verificador si proviene de los criterios de aceptación independientes de la especificación (TDD).

### Pregunta 2: ¿Qué defecto no habría detectado ninguna compuerta automática y solo una persona?
> **Respuesta del Grupo:**  
> **La prueba cómplice que valida el propio bug (`test_reembolso_ia.py` línea 10).**  
> Ninguna compuerta automática (linter, analizador de cobertura, escáner de seguridad o verificador de tipos) puede detectar que una aserción unitaria está verificando un valor de negocio equivocado. Para `pytest`, la prueba corre y pasa; para `coverage`, la línea está cubierta al 100 %; para `bandit`, no hay riesgos de seguridad; y para `radon`, la complejidad es baja. Solo un revisor humano consciente de las reglas contractuales de RutaColca puede contrastar la prueba contra la especificación y percatarse de que el test fue diseñado para encubrir la falla.

### Pregunta 3: La cobertura del borrador es 94 %. ¿Qué dice eso de la cobertura como medida de calidad?
> **Respuesta del Grupo:**  
> **Demuestra que la cobertura de código es una métrica de ejecución sintáctica, jamás de corrección semántica ni de suficiencia funcional.**  
> El borrador v0 alcanzó un deslumbrante 94 % de cobertura a pesar de tener 7 defectos graves: ejecutaba casi todas sus líneas, pero calculaba mal los bordes, redondear con pérdidas contables, permitía inyección de comandos en shell y procesaba montos negativos sin validación. Como bien señala la literatura de ingeniería de software, *«un código 100 % cubierto puede seguir estando 100 % equivocado»*. La cobertura solo cobra sentido si está precedida por pruebas TDD rigurosas que exploren exhaustivamente las clases de equivalencia y los casos borde.

### Pregunta 4: ¿Qué medirían para saber si la IA realmente acelera a su equipo?
> **Respuesta del Grupo:**  
> Mediríamos métricas de entrega y estabilidad basadas en el estándar **DORA** (*DevOps Research and Assessment*), complementadas con indicadores de deuda técnica asistida:
> 1. **Tasa de Rechazo en Revisión (*PR Rework Rate*):** Porcentaje de líneas de IA modificadas o devueltas por defectos en revisión humana.
> 2. **Tiempo de Ciclo de Especificación a Producción (*Lead Time for Changes*):** Tiempo total que toma desde la redacción de la spec Gherkin hasta el merge con 7/7 compuertas aprobadas.
> 3. **Tasa de Fallos en Cambios (*Change Failure Rate*):** Cantidad de incidentes o regresiones que escapan a producción originados en código generado por IA.
> 4. **Frecuencia de Alucinaciones en Dependencias:** Incidencia de paquetes inexistentes detectados por la compuerta de dependencias antes de llegar a ramas productivas.

---

## 4. Declaración de Integridad y Aprobación Grupal

Los 4 integrantes declaramos haber participado activamente en la discusión conceptual, auditoría del diff, configuración de compuertas y redacción del informe técnico. Ningún código fue promovido sin comprender plenamente su funcionamiento y validar su conformidad contra las 7 compuertas de calidad.

Arequipa, 24 de noviembre de 2026.
