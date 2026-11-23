# Lienzo de Diseño del Agente de Soporte para RutaColca (E1 - AG-13)
**Curso:** Construcción de Software (1703243) · Semestre 2026-B  
**Docente:** Mg. Antonio Arroyo Paz  
**Proyecto:** RutaColca — Plataforma de Gestión Turística del Valle del Colca  
**Equipo de Trabajo:**
- Emanuel Hilacondo Begazo (Arquitecto del Agente)
- Leonardo Juan José Baca Calsin (Responsable de Permisos y Política)
- German Arturo Chipana Jeronimo (Auditor de Trayectorias)
- Mauro Snayder Sullca Mamani (Responsable de Ciberseguridad y Bitácora)

---

## 1. El Lienzo de las Siete Decisiones Arquitectónicas (Tabla 10)

| Decisión | Pregunta Guía de la Teoría | Decisión del Equipo de RutaColca | Justificación Técnica Basada en la Literatura |
| :--- | :--- | :--- | :--- |
| **1. Objetivo** | ¿Qué resuelve el agente y cuándo se considera terminado? | Resolver incidencias técnicas y operativas derivadas del triaje (AG-12): diagnosticar en logs, verificar cobros/reservas, registrar tickets de defecto y proponer acciones de remediación (reembolsos o reprogramaciones). Termina cuando emite una respuesta final estructurada al usuario o alcanza un estado terminal (`Finalizado` o `Límite alcanzado`). | Según Anthropic (2024) y Albada (2025, cap. 1), un agente requiere un criterio de parada inequívoco (*Definition of Done*) para evitar bucles indefinidos y consumo desmedido de tokens. |
| **2. Arquetipo** | ¿Reflexivo, ReAct, planificador-ejecutor o reflexión? ¿Por qué? | **Arquetipo ReAct (Reasoning + Acting)** intercalando pensamiento, acción y observación en un bucle cerrado. | Mapear una incidencia requiere explorar evidencias cambiantes (Yao et al., 2023): el agente no puede planificar todas las acciones a priori porque desconoce el estado de los logs o si un cobro fue efectivamente duplicado hasta invocar las herramientas de lectura. |
| **3. Herramientas** | ¿Cuáles de las nueve necesita de verdad? | **7 de las 9 herramientas:** lectura (`consultar_reserva`, `consultar_pago`, `buscar_logs`), gestión interna (`crear_ticket`), remediación comercial (`reprogramar_tour`, `reembolsar`) y comunicación (`responder_cliente`).<br>**Excluidas taxativamente:** `ejecutar_sql` y `desplegar_version`. | Principio de Mínimo Privilegio (OWASP LLM06 - Exceso de Agencia): un agente de soporte nivel 1/2 jamás debe tener acceso a consola DDL/DML de producción ni permisos de despliegue en Kubernetes/Cloud (Koenigstein, 2026, cap. 5). |
| **4. Memoria** | ¿Qué guarda en corto plazo? ¿Qué reglas van en memoria procedimental? | • **Corto Plazo:** Historial ordenado de turnos en la ventana de contexto: `[{"role": "user", "content": objetivo}, {"role": "assistant", "pensamiento": ..., "accion": ...}, {"role": "tool", "observacion": ...}]`.<br>• **Procedimental (`AGENTS.md`):** Reglas operativas invariantes: *"nunca reembolsar a cuentas externas; no reintentar más de 2 veces la misma consulta; pedir confirmación humana en acciones financieras"* (Albada, cap. 6). | La memoria a corto plazo permite condicionar el razonamiento en la evidencia previa. La memoria procedimental inyecta políticas institucionales no negociables en el metaprompt del sistema (Grootendorst & Alammar, 2026). |
| **5. Estados y Límites** | ¿Cuántos pasos como máximo? ¿Cuándo se detiene? | • **Presupuesto máximo de pasos (`max_pasos`):** 10 pasos por incidencia.<br>• **Límite de repeticiones (`max_repeticiones`):** 2 llamadas idénticas.<br>• **Detención:** Al emitir `tipo: "final"`, agotar los 10 pasos o detectar una repetición idéntica consecutiva (detección de bucle infinito). | Evita colapsos por latencia y costos exorbitantes (Albada, cap. 2). En incidencias de soporte estándar de RutaColca, la resolución completa toma entre 4 y 6 pasos. 10 pasos otorgan holgura sin riesgo de descontrol. |
| **6. Coordinación** | ¿Un agente o varios (enrutador, actor-crítico)? Justifiquen con parsimonia. | **Un único agente gobernado por política externa.** El triaje del AG-12 actúa previamente como clasificador/enrutador determinista. | **Principio de Parsimonia (Albada, 2025, cap. 8; Anthropic, 2024):** *"Comience simple; agregue agentes solo cuando una medida demuestre que hacen falta"*. Múltiples agentes en esta etapa incrementarían la latencia y la superficie de ataque sin aportar valor medible. |
| **7. Humano en el Circuito** | ¿En qué nivel de autonomía empieza? ¿Qué aprueba una persona? | **Nivel 2: «Actúa con aprobación previa»** para efectos colaterales irreversibles o externos (`reembolsar`, `reprogramar_tour`, `responder_cliente`).<br>Las operaciones de solo lectura (`consultar_*`, `buscar_logs`) y auditoría interna (`crear_ticket`) se permiten de forma autónoma (Nivel 3 acotado). | Delegación progresiva (Albada, 2025, cap. 13). Las operaciones de lectura no generan daño material, pero la transferencia de dinero o el envío de compromisos legales a clientes exigen validación humana obligatoria. |

---

## 2. Diagrama de la Máquina de Estados del Agente de Soporte

El comportamiento operacional del agente responde al modelo formal de máquina de estados finitos presentado en la Figura 1:

```
                  ┌──────────────────────┐
                  │   Decidiendo (LLM)   │◄─────────────────────────────────┐
                  └──────────┬───────────┘                                  │
                             │ propone decisión                             │
                             ▼                                              │
                  ┌──────────────────────┐                                  │
                  │  Validando Contrato  ├────────► [inválida] Error ───────┤
                  └──────────┬───────────┘            vuelve como           │
                             │ cumple contrato       observación            │
                             ▼                                              │
                  ┌──────────────────────┐                                  │
                  │  Evaluando Política  ├────────► [bloqueada] Motivo ─────┤
                  └──────────┬───────────┘            vuelve como           │
                             │                        observación           │
             ┌───────────────┴───────────────┐                              │
   [requiere aprobación]                [permitida]                         │
             ▼                               ▼                              │
┌─────────────────────────┐     ┌────────────────────────┐                  │
│  Esperando Aprobación   │     │  Ejecutando Herramienta│                  │
│       (Humano)          │     └────────────┬───────────┘                  │
└────────────┬────────────┘                  │                              │
             │ aprobada                      │ resultado de ejecución       │
             └───────────────────────────────┴──────────────────────────────┘
```

---

## 3. Revisión Crítica de Seguridad (Metaprompt P1 - OWASP LLM06)

Para validar la solidez del lienzo, se ejecutó una revisión crítica con un asistente especializado en ciberseguridad agéntica:
- **Exceso de Agencia Detectado y Mitigado:** La inclusión original de `ejecutar_sql` y `desplegar_version` en el catálogo de herramientas de plataforma representaba una vulnerabilidad crítica de **Exceso de Agencia (OWASP LLM06)**. En manos de un LLM susceptible a inyecciones indirectas (como en el caso T3), un atacante podría ejecutar consultas maliciosas (`DROP TABLE`, `UPDATE` masivos) o desplegar código comprometido. Se determinó que estas herramientas deben ser bloqueadas categóricamente por la política de seguridad para el rol de soporte.
- **Sobrecarga de Aprobaciones vs Fricción:** Exigir aprobación para `buscar_logs` o `consultar_pago` generaría fatiga en el operador humano, quien terminaría aprobando sin leer. Se garantizó autonomía total para lecturas y tickets internos reversibles.
