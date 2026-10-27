# Bitácora de Uso Crítico de IA: Patrones de Diseño en RutaColca (AG-09)

**Asignatura:** Construcción de Software (1703243) — Semestre 2026-B  
**Docente:** Mg. Antonio Arroyo Paz  
**Caso Práctico:** AG-09 · Patrones de Diseño (GoF) en RutaColca  
**Regla de Oro:** *«La IA propone, el equipo decide y verifica».* Toda propuesta generada por el asistente fue contrastada críticamente contra los principios de diseño de software (SOLID, Ousterhout, Valente) y evaluada para evitar la sobreaplicación de patrones (*paternite*).

---

## 1. Plantilla Oficial de Prompt Utilizada (Basada en Slide 31)

```text
Actúa como diseñador de software experto en patrones GoF.
Contexto: [Código de RutaColca y escenario de negocio correspondiente].
Problema: [Descripción de la variación o acoplamiento del requerimiento].
Tarea:
1. Identifica el problema de diseño.
2. Propón UN patrón y justifica con un principio.
3. Dibuja el diagrama de clases en PlantUML.
4. Explica qué pasa si NO usamos el patrón.
Reglas: Java 21; sin dependencias nuevas.
Si el problema no justifica un patrón, dilo explícitamente.
```

---

## 2. Registro de Contrastación y Decisiones por Escenario

| Escenario | Propuesta Generada por la IA | Evaluación Crítica del Equipo | Decisión Final del Equipo | Estudiante Responsable |
| :---: | :--- | :--- | :--- | :--- |
| **Escenario 1<br>(Pagos)** | Propuso implementar un **Abstract Factory** completo con familias para web y móvil, más Adaptadores para cada pasarela. | **Sobrediseño innecesario:** RutaColca solo requiere instanciar la pasarela correcta según el método elegido; no hay múltiples familias de productos abstractos. Un Abstract Factory agrega 6 interfaces artificiales sin valor real. | **Ajustado a Factory Method + Adapter.** La fábrica simple desacopla la creación y el cliente solo conoce `PasarelaPago`. | Emanuel Hilacondo Begazo |
| **Escenario 2<br>(Tarifas)** | Propuso el patrón **Chain of Responsibility** para encadenar las reglas de descuento una tras otra. | **Inadecuado para el modelo de negocio:** Los descuentos de tours (estudiante, temporada alta, grupo) son tarifas mutuamente excluyentes o calculadas bajo fórmulas prioritarias de negocio, no una cadena de filtros donde la petición viaja de eslabón en eslabón. | **Rechazado.** Se seleccionó **Strategy**, que permite seleccionar el algoritmo de tarificación exacto en tiempo de ejecución de acuerdo a la reserva. | German Arturo Chipana Jeronimo |
| **Escenario 3<br>(Notificaciones)** | Propuso el patrón **Mediator** para coordinar a los componentes de mensajería (email, WhatsApp, portal). | **Falso acoplamiento cruzado:** Los notificadores no se comunican entre sí; no necesitan arbitraje bidireccional. Solo reaccionan unidireccionalmente ante el hecho consumado del pago. | **Rechazado.** Se seleccionó **Observer (Publisher/Subscriber)** con el evento inmutable `EventoReservaConfirmada`. | Leonardo Juan José Baca Calsin |
| **Escenario 4<br>(AUTOCOLCA)** | Propuso el patrón **Facade** para ocultar el servicio de AUTOCOLCA. | **Confusión conceptual:** Facade simplifica una interfaz compleja de un subsistema propio de muchas clases. El problema de AUTOCOLCA no es la multiplicidad de clases, sino la **incompatibilidad de firmas** de un sistema externo. | **Corregido a Adapter (Object Adapter).** Adapta la interfaz foránea hacia el contrato propio `ValidadorBoleto` (Capa Anticorrupción). | German Arturo Chipana Jeronimo |
| **Escenario 5<br>(Disponibilidad)** | **CASO EMBLEMÁTICO DE PATERNITE:** La IA propuso implementar el patrón **Proxy de Caché** (`DisponibilidadProxy implements ConsultaDisponibilidad`) con un mapa en memoria concurrente. | **ALERTA DE PATERNITE:** El equipo detectó que un Proxy en memoria en un entorno cloud con dos réplicas de VM causa desincronización de cupos e introduce sobrecarga de clases para una simple consulta de lectura. | **RECHAZO TOTAL DEL PATRÓN.** Se optó por la solución simple primero: índice relacional B-Tree en PostgreSQL 16 y cabeceras HTTP `Cache-Control` en el balanceador. | Mauro Snayder Sullca Mamani |

---

## 3. Síntesis de Aprendizaje: Dónde Fallan los LLM en Patrones de Diseño

1. **Sesgo hacia la complejidad:** La IA tiende a sugerir el patrón más complejo de la jerarquía (ej. Abstract Factory en lugar de Factory Method, o Chain of Responsibility donde Strategy es mucho más intuitivo).
2. **Dificultad para decir "No use un patrón":** En el Escenario 5, la IA intentó obligatoriamente encajar un patrón GoF (Proxy) a pesar de que el problema se resuelve con infraestructura de base de datos o HTTP. El rol crítico del ingeniero de software consiste en frenar la *paternite* y elegir la solución más simple y mantenible.
