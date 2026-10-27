# Actividad Grupal AG-09: Patrones de Diseño en RutaColca

**Universidad Nacional de San Agustín de Arequipa (UNSA)**  
**Facultad de Ingeniería de Producción y Servicios**  
**Escuela Profesional de Ingeniería de Sistemas**  
**Asignatura:** Construcción de Software (1703243) — Semestre 2026-B  
**Docente:** Mg. Antonio Arroyo Paz  
**Tema:** Tema 09: Patrones de Diseño (GoF) · Semana 09  

---

## 1. Equipo de Trabajo y Asignación de Roles

| Estudiante | Correo Institucional | Rol en la Actividad AG-09 | Responsabilidad Específica |
| :--- | :--- | :--- | :--- |
| **Emanuel Hilacondo Begazo** | `ehilacondob@unsa.edu.pe` | **Analista de Diseño** | Identificación de problemas de diseño en los 5 escenarios |
| **Mauro Snayder Sullca Mamani** | `msullcam@unsa.edu.pe` | **Evaluador de Arquitectura** | Análisis y justificación crítica del Reto de la "Paternite" |
| **German Arturo Chipana Jeronimo** | `gchipanaj@unsa.edu.pe` | **Diseñador de Modelos** | Elaboración y compilación de diagramas de clases PlantUML |
| **Leonardo Juan José Baca Calsin** | `lbacac@unsa.edu.pe` | **Líder Técnico y Auditor** | Bitácora de IA, implementación de código Java 21 y verificación |

---

## 2. Descripción del Caso de Crecimiento (RutaColca)

La plataforma **RutaColca** (diseñada a nivel arquitectónico C4 en el caso AG-08) entra a su fase de construcción y diseño detallado. El crecimiento del negocio introduce cinco nuevos requerimientos técnicos que demandan decisiones de diseño a nivel de objetos:
1. **Múltiples métodos de pago:** Aceptación simultánea de tarjetas de crédito/débito, transferencias móviles (Yape) y pasarelas internacionales (PayPal).
2. **Precios dinámicos:** Tarifas variables que se calculan en tiempo de ejecución según temporada alta, tamaño de grupo o condición de estudiante.
3. **Notificaciones concurrentes:** Confirmación de reserva que debe alertar automáticamente al turista (correo), al guía asignado (WhatsApp) y a la agencia aliada (panel web).
4. **Incompatibilidad de API gubernamental:** La interfaz del servicio de validación de AUTOCOLCA no coincide con el modelo de dominio interno.
5. **Alto volumen de consultas:** La disponibilidad de cupos de tours es consultada cientos de veces por minuto durante temporada alta.

---

## 3. Identificación y Selección de Patrones de Diseño (Paso 1)

A continuación se presenta la matriz analítica de los cinco escenarios, evaluando el problema de diseño, el principio subyacente y la decisión técnica de aplicar o rechazar un patrón:

| Escenario | Problema de Diseño Identificado | ¿Aplica Patrón? | Patrón Candidato | Principio de Diseño Justificativo |
| :---: | :--- | :---: | :---: | :--- |
| **1. Pagos** | Creación dispersa de clientes bancarios con `new` acoplados a clases concretas en `ReservaService`. | **SÍ** | **Factory Method + Adapter** | **Programar para interfaces / Abierto-Cerrado (OCP)** |
| **2. Tarifas** | Algoritmos de cálculo de precio cambiantes embebidos en condicionales `if/else` dentro de `Reserva`. | **SÍ** | **Strategy** | **Encapsular lo que varía / Composición sobre herencia** |
| **3. Notificaciones** | `ReservaService` fuertemente acoplado a múltiples canales de notificación que cambian con frecuencia. | **SÍ** | **Observer** | **Bajo acoplamiento / Abierto-Cerrado (OCP)** |
| **4. AUTOCOLCA** | Métodos y firmas del servicio externo de AUTOCOLCA incompatibles con la interfaz interna del dominio. | **SÍ** | **Adapter** | **Programar para interfaces / Inversión de Dependencias (DIP)** |
| **5. Disponibilidad** | Consultas masivas repetitivas sobre disponibilidad de cupos por salida. | **NO (Paternite)** | *Ninguno (Solución BD/HTTP)* | **Simple primero / No forzar patrones donde la tecnología base resuelve** |

---

## 4. Análisis Detallado Escenario por Escenario

### 4.1. Escenario 1: Procesamiento Multipasarela (Tarjeta, Yape, PayPal)
* **Problema Concreto:** Si `ReservaService` contiene bloques `if (metodo == YAPE) new YapeAdapter()... else if (metodo == PAYPAL)...`, cada nuevo medio de pago (ej. Plin, Apple Pay) obliga a modificar código ya testeado. Además, el servicio conoce clases concretas de infraestructura financiera.
* **Solución de Diseño:** 
  1. Se define la interfaz `PasarelaPago` con el método unificado `ResultadoPago cobrar(BigDecimal monto, DatosPago datos)`.
  2. Cada proveedor se encapsula en su propio adaptador (`TarjetaAdapter`, `YapeAdapter`, `PayPalAdapter`).
  3. La clase `PasarelaPagoFactory` centraliza la decisión de qué adaptador instanciar según el enum `MetodoPago`.
* **Beneficio Técnico:** El servicio de reservas depende exclusivamente de la abstracción `PasarelaPago`. Incorporar un método nuevo solo requiere crear una nueva clase adaptadora, respetando el principio Open/Closed.

### 4.2. Escenario 2: Cálculo Dinámico de Precios
* **Problema Concreto:** El precio final de un tour depende de múltiples reglas de negocio: recargo de temporada alta (+25%), descuento grupal (-15% para grupos ≥ 5 pasajeros), tarifa estudiantil (-30%) o tarifa estándar. Anidar estas reglas en métodos con `switch/case` genera explosión combinatoria y rigidez ante promociones temporales.
* **Solución de Diseño:**
  1. Se define la interfaz funcional `EstrategiaPrecio` con el contrato `BigDecimal calcularPrecio(Tour tour, ReservaDetalle detalle)`.
  2. Se implementan estrategias concretas: `PrecioEstandarStrategy`, `PrecioTemporadaAltaStrategy`, `PrecioGrupoStrategy` y `PrecioEstudianteStrategy`.
  3. El objeto `Reserva` mantiene una referencia a `EstrategiaPrecio` y delega en ella el cálculo (`total = estrategia.calcularPrecio(tour, detalle)`).
* **Beneficio Técnico:** Las fórmulas comerciales quedan desacopladas de la entidad `Reserva`. Se pueden intercambiar en caliente en tiempo de ejecución o componer dinámicamente sin tocar la lógica de negocio nuclear.

### 4.3. Escenario 3: Notificaciones Desacopladas a Múltiples Interesados
* **Problema Concreto:** Al confirmar una reserva, deben detonarse avisos a tres actores diferentes con requerimientos técnicos dispares: el turista necesita un correo con su voucher PDF; el guía requiere un mensaje WhatsApp con el itinerario; la agencia necesita que su tablero PWA descuente el cupo. Acoplar estas llamadas en `ReservaService` viola el Principio de Responsabilidad Única (SRP) y genera fragilidad si un canal falla.
* **Solución de Diseño:**
  1. Se aplica el patrón **Observer (Publicador-Suscriptor)**.
  2. La interfaz `ObservadorReserva` define el método `void onReservaConfirmada(EventoReserva evento)`.
  3. El sujeto `PublicadorReservas` administra la lista de suscriptores y los notifica en bucle o asíncronamente.
  4. Los observadores concretos (`NotificadorTuristaEmail`, `NotificadorGuiaWhatsApp`, `ActualizadorCuposAgencia`) reaccionan de forma autónoma.
* **Beneficio Técnico:** Si mañana la administración solicita enviar un SMS de respaldo o registrar la venta en un sistema contable, simplemente se suscribe un nuevo observador sin modificar una sola línea de `ReservaService`.

### 4.4. Escenario 4: Integración con la API Legada de AUTOCOLCA
* **Problema Concreto:** El servicio externo estatal de AUTOCOLCA expone una interfaz remota con firmas propietarias: `consultarVigenciaBoletoServicioPublico(String numSerie, String codigoVerif, String docIdent)`. Nuestro dominio interno exige un contrato limpio `ValidadorBoleto` con firma `ResultadoValidacion validar(BoletoTuristico boleto)`.
* **Solución de Diseño:**
  1. Se crea la interfaz del dominio `ValidadorBoleto`.
  2. La clase `AutocolcaAdapter` implementa `ValidadorBoleto` y mantiene internamente una instancia de `AutocolcaClient`.
  3. El adaptador extrae los datos del objeto de dominio `BoletoTuristico`, realiza la traducción de tipos, invoca al cliente externo y convierte la respuesta en un `ResultadoValidacion` fuertemente tipado.
* **Beneficio Técnico:** Aísla el núcleo de RutaColca de los cambios o caprichos en la API gubernamental externa (Capa Anticorrupción / ACL).

---

## 5. Resolución del Reto: Justificación de la "Paternite" en el Escenario 5

### 5.1. Definición del Criterio de Paternite
> *«El mayor riesgo de los patrones de diseño es su sobreaplicación: no fuerce un problema a encajar en un patrón cuando una solución tradicional funciona mejor»*  
> — John Ousterhout (2018), *A Philosophy of Software Design*, citado por Marco Tulio Valente (2020).

### 5.2. Escenario Elegido para NO Usar Patrón: Escenario 5 (Consultas de Disponibilidad)
En el Escenario 5, la tentación teórica recurrente inducida por los libros de texto es forzar un patrón estructural **Proxy de Caché** (`DisponibilidadProxy implements ConsultaDisponibilidad`) que intercepte las llamadas al servicio real y almacene un `HashMap` local.

**Razones contundentes por las cuales el equipo RECHAZA el patrón Proxy aquí:**
1. **Complejidad Accidental y Estado Mutable:** Un Proxy de caché implementado manualmente en Java introduce graves problemas de concurrencia multihilo (`ConcurrentHashMap`, bloqueos de lectura/escritura) y riesgo de *datos obsoletos* (overbooking por leer cupos desactualizados en memoria local de un nodo).
2. **La Base de Datos lo resuelve de forma nativa:** Un índice B-Tree relacional en PostgreSQL 16 sobre las columnas de búsqueda:
   ```sql
   CREATE INDEX idx_salidas_disponibilidad ON salidas (tour_id, fecha_salida) 
   WHERE cupos_disponibles > 0;
   ```
   permite al motor resolver cientos de consultas en **menos de 1 milisegundo** aprovechando el Buffer Pool de PostgreSQL, con coherencia transaccional ACID garantizada y cero clases adicionales que mantener.
3. **Caché Declarativa del Ecosistema:** En el marco de Spring Boot (ADR-001), la solución estándar de la industria es una anotación declarativa `@Cacheable(value="disponibilidad", ttl="30s")` o cabeceras HTTP estándar `Cache-Control: max-age=30` en el balanceador de carga Nginx/ALB. Crear clases Proxy artesanales solo añade indirección innecesaria (código espagueti y clases fantasma).
4. **Criterio de Ousterhout:** No hay variantes polimórficas en la consulta de disponibilidad; es una lectura directa. Diseñar un Proxy GoF aquí es un ejemplo clásico de **paternite**.
