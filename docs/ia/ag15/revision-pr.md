# Entregable E2: Hoja de Revisión Humana del Pull Request de la IA y Decisión Fundada

**Asignatura:** Construcción de Software (1703243) — Semestre 2026-B  
**Actividad:** Caso Práctico Grupal AG-15 — Revisar un Pull Request de la IA  
**Historia de Usuario:** HU-RC-21: Calcular el reembolso por cancelación  
**Pull Request Auditado:** PR #42 — *«Implementa calcular_reembolso según la historia HU-RC-21»*  
**Autor del PR:** Asistente de IA (Código en `borrador_ia/reembolso_v0.py` y `tests_ia/test_reembolso_ia.py`)  
**Grupo Revisor:**
- German Arturo Chipana Jeronimo (Revisor Principal del PR)
- Emanuel Hilacondo Begazo (Analista de Especificación)
- Leonardo Juan José Baca Calsin (Desarrollador y TDD)
- Mauro Snayder Sullca Mamani (Responsable de Calidad y AGENTS.md)

---

## 1. Hoja de Revisión del Pull Request (Tabla 5 de la Guía)

El equipo revisó minuciosamente el diff del PR generado por la IA utilizando la lista de verificación del Anexo A, identificando **7 defectos estructurales** (6 en el código fuente y 1 en la suite de pruebas adjunta).

### Tabla 1: Hoja de Revisión de Defectos en el PR de la IA

| N.º | Archivo y Línea(s) | Defecto Técnico Identificado | Riesgo e Impacto Operacional | Compuerta que lo Detecta |
|:---:|:---|:---|:---|:---|
| **1** | `borrador_ia/reembolso_v0.py`<br>Líneas 5–8 | **Alucinación de Paquete Externo (`reembolsos_peru`):** El asistente inventa una dependencia que no existe en PyPI ni está autorizada en el repositorio, usando un bloque `try/except ImportError` como parche frágil. | **Crítico:** Riesgo de ataque a la cadena de suministro (*Dependency Confusion* / *Package Hallucination* - Spracklen et al., 2025) si un atacante registra un paquete malicioso con ese nombre en PyPI. | **Compuerta 6**<br>(Dependencias aprobadas) |
| **2** | `borrador_ia/reembolso_v0.py`<br>Línea 14 | **Borde Incorrecto de Anticipación:** Escribe `elif horas_antes > 72:` en lugar del operador inclusivo `>= 72` estipulado en la regla de negocio. | **Alto:** Un turista que cancela con exactamente 72 horas de anticipación recibe arbitrariamente un 50 % de reembolso en lugar del 100 % que le corresponde por contrato, generando quejas legales y reclamos ante INDECOPI. | **Compuerta 1**<br>(Pruebas de la spec) |
| **3** | `borrador_ia/reembolso_v0.py`<br>Línea 20 | **Aritmética en Coma Flotante y Redondeo Inadecuado:** Emplea `float` y la función `round(..., 2)` nativa de Python (redondeo bancario *round-to-even*) en lugar de redondeo formal hacia arriba (`ROUND_HALF_UP`). | **Alto:** Pérdidas contables y descuadre de caja. Por ejemplo, S/ 120.25 al 50 % resulta en 60.125, que `round()` trunca hacia el número par más cercano (S/ 60.12), violando la regla explícita de redondear a S/ 60.13. | **Compuerta 1**<br>(Pruebas de la spec) |
| **4** | `borrador_ia/reembolso_v0.py`<br>Línea 21 | **Valor Quemado en Código Duro (*Hardcoded*):** Escribe `monto > 500` para determinar la derivación a supervisor, ignorando el límite real de S/ 300 establecido en `politica.LIMITE_AGENTE`. | **Crítico:** Brecha de gobernanza financiera. Reembolsos entre S/ 301.00 y S/ 500.00 se procesarían de forma 100 % autónoma sin autorización humana, violando la política del agente del AG-13 y AG-14. | **Compuerta 7**<br>(Regla de la política) |
| **5** | `borrador_ia/reembolso_v0.py`<br>Líneas 22–23 | **Vulnerabilidad de Inyección de Comandos (CWE-78) y Efecto Secundario No Solicitado:** Ejecuta `subprocess.run(f"echo ... | mail {correo_cliente}", shell=True)`. | **Crítico:** Ejecución remota de código (RCE). Si un atacante ingresa `correo_cliente = "turista@mail.com; rm -rf /"`, toma control del host. Además, la HU jamás solicitó enviar correos (violación del principio de responsabilidad única). | **Compuerta 3** (Ruff S602)<br>**Compuerta 4** (Bandit B602) |
| **6** | `borrador_ia/reembolso_v0.py`<br>Líneas 11–19 | **Ausencia Total de Validación Defensiva de Entradas:** No valida montos negativos, montos que superen el límite operativo ($> 10\,000$), horas negativas ni motivos desconocidos (ej. `"lluvia"`). | **Alto:** El sistema procesa reembolsos con montos ilógicos o negativos sin lanzar la excepción `ValueError` requerida por la especificación, corrompiendo la base de datos de pagos. | **Compuerta 1**<br>(Pruebas de la spec) |
| **7** | `tests_ia/test_reembolso_ia.py`<br>Línea 10 | **Prueba Unitaria Cómplice del Defecto (Sesgo de Confirmación):** En `test_reembolso_medio` afirma: `assert calcular_reembolso(100, 72, "cliente")["porcentaje"] == 50`. | **Crítico:** La prueba de la IA valida que con 72 horas dé 50 % para «hacer pasar» su propio código con bug. Crea una falsa sensación de seguridad («todas las pruebas pasan ✅») enmascarando el error de negocio. | **Compuerta 1**<br>(Pruebas de la spec) |

---

## 2. Decisión del Revisor en GitHub (Paso 3)

### Dictamen Oficial: **SOLICITAR CAMBIOS (REQUEST CHANGES)**

A continuación se transcribe el comentario formal que el equipo dejó en el Pull Request de la plataforma:

```markdown
### ❌ Solicitud de Cambios Requerida (Pull Request #42)

Hola @asistente-ia. Hemos completado la revisión técnica humana y la verificación automatizada mediante compuertas de calidad sobre tu propuesta de implementación para **HU-RC-21**.

Aunque tu descripción indica que *"Todas las pruebas pasan ✅ (3/3)"*, hemos comprobado que tus pruebas fueron redactadas para confirmar los propios errores del código y no para validar la especificación. Al ejecutar la suite de pruebas oficial de la historia, **8 de las 15 pruebas fallan** y tu código solo supera **2 de las 7 compuertas de calidad**.

Solicitamos corregir los siguientes defectos ordenados por nivel de severidad antes de poder considerar la fusión:

#### 1. Defectos de Severidad Crítica (Seguridad y Gobernanza):
- **[Línea 23] Vulnerabilidad Crítica de Inyección de Comandos (Bandit B602 / Ruff S602):**
  Elimina de inmediato la llamada `subprocess.run(..., shell=True)`. La historia de usuario HU-RC-21 es una función pura de cálculo y no solicita el envío de correos electrónicos.
- **[Línea 21] Incumplimiento de Política Financiera (Compuerta 7):**
  Elimina el límite quemado `> 500`. Debes importar y utilizar obligatoriamente `from rutacolca.politica import LIMITE_AGENTE` (S/ 300).
- **[Línea 6] Alucinación de Dependencias (Compuerta 6):**
  Elimina la referencia al paquete inexistente `reembolsos_peru`. Utiliza el módulo estándar `decimal.Decimal` con `ROUND_HALF_UP`.
- **[Tests Línea 10] Falso Positivo en Pruebas:**
  Corrige `test_reembolso_medio`: con 72 horas de anticipación le corresponde el 100 % de reembolso, no el 50 %.

#### 2. Defectos de Severidad Alta (Lógica de Negocio y Validación):
- **[Línea 14] Corrección de Condición de Borde:**
  Cambia `elif horas_antes > 72:` por `elif horas_antes >= 72:`.
- **[Línea 20] Redondeo Financiero:**
  Implementa cuantización con `Decimal('0.01')` y redondeo de mitad hacia arriba (`ROUND_HALF_UP`).
- **[Líneas 11-19] Validación de Entradas:**
  Valida que `monto_pagado > 0` y `<= 10000`, `horas_antes >= 0` y `motivo in {'clima', 'operador', 'cliente'}`, levantando `ValueError` ante cualquier anomalía.

Por favor, consulta las reglas vigentes en `AGENTS.md` para guiar tu refactorización.
```

---

## 3. Comparación con la Revisión de la IA (Metaprompt P1)

En cumplimiento del **Paso 3 y Paso 8**, se ejecutó el Metaprompt P1 configurando a un modelo de IA como segundo revisor técnico senior:

```text
Prompt P1: "Actúa como revisor senior de Python en un equipo que usa TDD.
Contexto: [spec.md, diff del PR, AGENTS.md]. Tarea: lista los defectos del PR con su línea y gravedad."
```

### Tabla 2: Matriz Comparativa: Revisión Humana vs. Revisión con Asistente de IA (P1)

| Aspecto Evaluado | Detección Humana (Grupo de Estudiantes) | Detección por IA (Metaprompt P1) | Análisis Crítico de la Diferencia |
|:---|:---:|:---:|:---|
| **Inyección de Comandos (`subprocess`)** | Detectado (Línea 23) | Detectado (Línea 23) | **Coincidencia:** Ambos identificaron el riesgo crítico de RCE (CWE-78). |
| **Alucinación de Paquete (`reembolsos_peru`)** | Detectado (Línea 6) | Detectado (Línea 6) | **Coincidencia:** La IA reconoció que el paquete no es estándar y sugirió usar `decimal`. |
| **Borde de 72 horas (`>` vs `>=`)** | Detectado (Línea 14) | Detectado (Línea 14) | **Coincidencia:** Ambos señalaron que 72 horas exactas cae en el bloque erróneo. |
| **Falla en las pruebas del PR (`test_reembolso_ia`)** | **Detectado (Línea 10)** | **OMITIDO (Falso Negativo)** | **Ventaja Humana:** La IA revisora se enfocó exclusivamente en el archivo `.py` de lógica y asumió ciegamente que las pruebas del PR eran correctas porque pasaban. No detectó que la prueba confirmaba el bug. |
| **Límite Quemado (`> 500` vs `LIMITE_AGENTE`)** | Detectado (Línea 21) | Detectado parcialmente | La IA notó que 500 no cuadraba con la spec, pero no enfatizó la importación desde `rutacolca.politica`. |
| **Falsos Positivos de la IA** | Ninguno | Sugirió refactorizar con `typing.Protocol` | **Alucinación de Requisitos:** La IA sugirió introducir sobre-ingeniería innecesaria que aumentaba la complejidad ciclomática sin aportar valor a la HU. |

### Conclusión del Ejercicio Comparativo
La IA funciona eficazmente como un **analizador estático acelerado** para capturar errores sintácticos obvios y vulnerabilidades conocidas de seguridad. Sin embargo, sufre de **sesgo de complacencia** y pasa por alto fallas metodológicas críticas, como pruebas unitarias contaminadas que confirman el propio error. La revisión humana apoyada en compuertas automáticas sigue siendo insustituible para garantizar la corrección y la gobernanza del software empresarial.
