# AGENTS.md · Directivas de Gobernanza para Asistentes y Agentes de IA

**Proyecto:** RutaColca Practice — Ecosistema de Microservicios Turísticos  
**Alcance:** Aplica a GitHub Copilot, Claude Code, Cursor, Gemini CLI y cualquier agente autónomo o asistente que genere código, pruebas o documentación en este repositorio.  
**Versión:** 2026-B.15  
**Fecha de Aprobación:** 24 de noviembre de 2026  

---

## 1. Principio Fundamental
> **«La IA propone; la especificación define el comportamiento; las pruebas y compuertas verifican; el ingeniero humano entiende, valida y aprueba.»**  
> Ningún fragmento de código generado por un agente se fusionará a la rama principal (`main`) basándose únicamente en la afirmación de que «parece que funciona» o porque «las pruebas autogeneradas pasan».

---

## 2. Reglas Obligatorias de Codificación y Seguridad

### Regla 1: Integridad de la Cadena de Suministro y Cero Alucinación de Dependencias
- **Prohibición:** Queda terminantemente prohibido importar paquetes externos no verificados o sugeridos especulativamente por el modelo (prevención de *package hallucinations* / *dependency confusion* - Spracklen et al., USENIX Security 2025).
- **Mandato:** Todo módulo debe utilizar exclusivamente la biblioteca estándar de Python (`sys.stdlib_module_names`), paquetes internos del namespace `rutacolca` o dependencias explícitamente aprobadas en `calidad/dependencias_aprobadas.txt`.
- **Verificación:** Compuerta 6 de calidad (`calidad/verificar.py`).

### Regla 2: Seguridad en Ejecución y Prohibición de Efectos Secundarios No Especificados
- **Prohibición:** Queda estrictamente prohibida la invocación de shells del sistema operativo mediante `subprocess.run(..., shell=True)`, `os.system()`, `eval()` o `exec()` (mitigación de CWE-78 e inyección de comandos - Pearce et al., IEEE S&P 2022).
- **Mandato:** Las funciones de cálculo o procesamiento de datos deben ser funciones puras o con efectos colaterales estrictamente delimitados por la Historia de Usuario. Queda prohibido añadir llamadas de red, despacho de correos electrónicos o escrituras en disco no solicitadas en la especificación.
- **Verificación:** Compuerta 3 (Ruff `S602`) y Compuerta 4 (Bandit `B602`).

### Regla 3: Precisión Aritmética Financiera y Redondeo Formal
- **Prohibición:** Queda terminantemente prohibido el uso de tipos de coma flotante binaria (`float`) y de la función nativa `round()` de Python para cálculos que involucren dinero en Soles (PEN). El redondeo bancario por defecto (*round-to-even*) produce inconsistencias contables inaceptables (ej. redondea `60.125` hacia abajo a `60.12`).
- **Mandato:** Los cálculos monetarios deben realizarse obligatoriamente mediante el módulo `decimal.Decimal` con cuantización explícita a dos decimales y política de redondeo de mitad hacia arriba (`ROUND_HALF_UP`).
- **Verificación:** Compuerta 1 (Pruebas de la especificación Gherkin).

### Regla 4: Gobernanza de Políticas y Prohibición de Valores Quemados (*Hardcoding*)
- **Prohibición:** Queda prohibido quemar constantes de negocio, umbrales de supervisión o montos límite como valores literales directos en el código (ej. escribir `monto > 300` o `monto > 500`).
- **Mandato:** Todo parámetro de gobernanza y límite de autonomía debe importarse desde el módulo central `rutacolca.politica` (ejemplo: `from rutacolca.politica import LIMITE_AGENTE`).
- **Verificación:** Compuerta 7 de calidad (`calidad/verificar.py`).

### Regla 5: Desarrollo Guiado por Pruebas (TDD) Derivadas de Especificación
- **Mandato:** Todo desarrollo debe iniciar formalmente por la lectura de los criterios de aceptación Gherkin en `specs/hu-rc-XX/spec.md`. Las pruebas unitarias deben escribirse y fallar antes de generar la implementación (*Red-Green-Refactor*).
- **Prohibición:** Los agentes no deben redactar pruebas que validen su propio código preliminar sin contrastar los casos borde de la especificación (evitando el sesgo de confirmación donde la prueba valida el bug).
- **Verificación:** Compuerta 1 (100 % pruebas aprobadas) y Compuerta 2 (Cobertura $\ge 90\%$).

### Regla 6: Complejidad Ciclomática y Estilo Limpio
- **Mandato:** Toda función debe mantener una complejidad ciclomática $\le 10$ según la métrica de McCabe calculada por `radon`.
- **Formato:** Líneas de código con longitud máxima de 88 caracteres, cumpliendo las reglas de estilo de `ruff`.
- **Verificación:** Compuerta 5 (Radon) y Compuerta 3 (Ruff).
