# ADR-013: Gobernanza de Autonomía y Guardrails para el Agente de Soporte de RutaColca

- **Estado:** Aceptado
- **Fecha:** 2026-11-20
- **Decisores:** Emanuel Hilacondo Begazo, Leonardo Juan José Baca Calsin, German Arturo Chipana Jeronimo, Mauro Snayder Sullca Mamani
- **Contexto Técnico:** Arquitectura de Sistemas Agénticos en Construcción de Software (2026-B)
- **Proyecto:** RutaColca — Plataforma de Gestión Turística del Cañón del Colca

---

## 1. Contexto y Planteamiento del Problema

Tras la automatización del triaje de incidencias en el Caso Práctico AG-12, el equipo de ingeniería de RutaColca diseñó un **Agente de Soporte Técnico Autónomo** capaz no solo de clasificar reportes, sino de ejecutar tareas de resolución operativa: inspeccionar transacciones en pasarelas bancarias, consultar reservas, examinar logs de contenedores C4, registrar tickets de defectos, proponer reprogramaciones de tours, emitir reembolsos y notificar a los clientes vía WhatsApp o correo electrónico.

A diferencia de una canalización determinista (*workflow*) o un prompt de clasificación estático, un agente basado en el bucle **ReAct (Reasoning + Acting)** decide dinámicamente sus propios pasos de ejecución. Esta capacidad agéntica introduce riesgos operacionales y de seguridad de primer orden:
1. **Exceso de Agencia (OWASP LLM06):** Asignación de herramientas de excesivo poder o privilegios no acotados (como acceso DDL/DML directo a base de datos de producción o permisos de despliegue de software).
2. **Inyección Indirecta de Prompts (OWASP LLM01):** Cargas útiles maliciosas incrustadas en datos externos (como notas de reservas redactadas por clientes o agencias) que manipulan las decisiones del modelo hacia acciones lesivas (por ejemplo, desvío de reembolsos no autorizados).
3. **Bucles Infinitos y Consumo Excesivo de Tokens:** Reintentos estocásticos de llamadas idénticas causados por respuestas imprevistas de APIs.
4. **Efectos Colaterales Irreversibles:** Ejecución autónoma de transacciones financieras o comunicaciones oficiales no auditadas.

Por consiguiente, la decisión arquitectónica central no es «qué puede hacer el agente», sino **«qué le permitimos hacer de manera autónoma, qué restringimos por completo y en qué punto exigimos la intervención de un operador humano»**.

---

## 2. Opciones Consideradas

### Opción 1: Autonomía Completa sin Restricciones (Todo Permitido - Nivel 4)
- **Descripción:** El agente dispone de las nueve herramientas del catálogo y ejecuta cualquier acción que proponga sin mediación de políticas ni confirmación humana (`politica_v1.json`).
- **Ventajas:** Máxima velocidad de respuesta desatendida; cero requerimiento de personal de soporte para aprobar acciones.
- **Desventajas:** Riesgo inaceptable de fraude financiero y corrupción de datos. En las pruebas de laboratorio sobre 20 pasos grabados, provocó **9 FUGAS críticas (45% de fallo)**, incluyendo ejecución de comandos SQL destructivos (`ejecutar_sql`), despliegue de hotfixes sin control (`desplegar_version`), reembolsos fraudulentos hacia cuentas de atacantes (caso T3) y bucles infinitos de consumo de tokens (caso T4).

### Opción 2: Autonomía Cero con Aprobación Total (Todo con Aprobación - Nivel 1)
- **Descripción:** Toda herramienta propuesta por el agente (incluso lecturas idempotentes como `consultar_reserva` o `buscar_logs`) queda en estado `Esperando aprobación` hasta que un operador humano la valide manualmente.
- **Ventajas:** Eliminación teórica de fugas automatizadas.
- **Desventajas:** Tasa de fricción inaceptable (100%). Genera **fatiga severa de alertas** en los operadores humanos, quienes ante un flujo constante de solicitudes triviales de lectura terminan aprobando ciegamente (*click-through habituation*), perdiendo la capacidad real de detectar anomalías y anulando los beneficios de eficiencia de la IA.

### Opción 3: Política de Gobernanza por Niveles con Guardrails en Código (Nivel 2 con Mínimo Privilegio) — *Elegida*
- **Descripción:** Arquitectura de control basada en la regla de oro: **«El agente propone, la política filtra, el humano aprueba»**.
  - **Mínimo Privilegio y Denegación por Defecto (`por_defecto: "prohibir"`):** Herramientas de alto impacto como `ejecutar_sql` y `desplegar_version` quedan bloqueadas de forma taxativa para el rol de soporte.
  - **Operaciones de Lectura e Internas Reversibles (`PERMITIR`):** `consultar_reserva`, `consultar_pago`, `buscar_logs` y `crear_ticket` se ejecutan de forma autónoma sin fricción.
  - **Operaciones Externas e Irreversibles (`APROBAR`):** `reprogramar_tour` y `responder_cliente` requieren aprobación humana previa.
  - **Límites de Dominio en Código (`BLOQUEAR` condicional):** `reembolsar` impone un tope estricto de S/ 500 y destino exclusivo `medio_original`. Si la llamada cumple estos límites, pasa a aprobación humana; si viola alguno, la política la **bloquea en código** antes de molestar al humano.
  - **Presupuesto y Detección de Bucles (`DETENER`):** Tope de 10 pasos por caso y corte automático tras 2 repeticiones idénticas consecutivas.

---

## 3. Decisión Adoptada

El equipo acordó unánimemente adoptar la **Opción 3**, formalizada en el motor de políticas [politica.py](file:///c:/Leonardo%20Baca%20Calsin%20UNSA/S%C3%ADlabos/3er%20a%C3%B1o/2026%20B/Construcci%C3%B3n%20de%20Software/RutaColca_Practice/docs/ia/ag13/politica.py) y en la especificación declarativa [politica.json](file:///c:/Leonardo%20Baca%20Calsin%20UNSA/S%C3%ADlabos/3er%20a%C3%B1o/2026%20B/Construcci%C3%B3n%20de%20Software/RutaColca_Practice/docs/ia/ag13/politica.json).

```json
{
  "max_pasos": 10,
  "max_repeticiones": 2,
  "por_defecto": "prohibir",
  "herramientas": {
    "consultar_reserva": "permitir",
    "consultar_pago": "permitir",
    "buscar_logs": "permitir",
    "crear_ticket": "permitir",
    "responder_cliente": "aprobar",
    "reprogramar_tour": "aprobar",
    "reembolsar": "aprobar",
    "ejecutar_sql": "prohibir",
    "desplegar_version": "prohibir"
  },
  "limites": {
    "reembolsar": {
      "monto": { "max": 500 },
      "destino": { "valores": ["medio_original"] }
    }
  }
}
```

---

## 4. Consecuencias y Validación Empírica

### Consecuencias Positivas:
1. **Erradicación de Fugas Críticas:** Se redujeron las fugas de 9 en la línea base a **0 fugas** en la política gobernada (100% de aciertos en control).
2. **Neutralización Determinista de Inyecciones (Caso T3):** Cuando el LLM fue engañado por una inyección indirecta en las notas de la reserva para transferir S/ 1500 a una cuenta fraudulenta, la política bloqueó la llamada en código determinista (`monto=1500 supera el maximo 500`), evitando transferir el riesgo al operador humano.
3. **Prevención de Bucles Infinitos (Caso T4):** La política detuvo al agente tras 2 repeticiones idénticas consecutivas, impidiendo el agotamiento del presupuesto.
4. **Cero Fricción en Tareas Normales:** Las lecturas y la generación de tickets avanzaron a velocidad de máquina sin interrupciones innecesarias.
5. **Carga Humana Sostenible:** Se requirieron únicamente 4 aprobaciones humanas a lo largo de 20 decisiones complejas, focalizando la atención del personal exclusivamente en transferencias de dinero legítimas y compromisos formales con clientes.

### Consecuencias Negativas y Mitigaciones:
- **Latencia Adicional por Aprobación Humana:** Los casos que exigen reprogramación o reembolso quedan en estado `Esperando aprobación`. *Mitigación:* Se implementa un panel de control con timeouts y SLAs configurables para que un supervisor atienda las solicitudes pendientes en menos de 15 minutos.

---

## 5. Referencias
- [1] OWASP Foundation, “OWASP Top 10 for LLM Applications 2025,” 2025.
- [2] Anthropic, “Building effective agents,” 2024.
- [3] M. Albada, *Desarrollo de aplicaciones con agentes de IA*, O’Reilly Media, 2025.
- [4] N. Koenigstein, *Agentes de IA: la guía definitiva*, O’Reilly Media, 2026.
