# INFORME TÉCNICO DE INGENIERÍA DE SOFTWARE
## ARQUITECTURA DE SOFTWARE C4 Y PATRONES DE DISEÑO GOF EN LA PLATAFORMA INTEGRAL «RUTACOLCA»
### Casos Prácticos AG-08 y AG-09 (Semanas 08 y 09)

---

**UNIVERSIDAD NACIONAL DE SAN AGUSTÍN DE AREQUIPA**  
**Facultad de Ingeniería de Producción y Servicios**  
**Escuela Profesional de Ingeniería de Sistemas**  

* **Asignatura:** Construcción de Software (Código: 1703243) — Semestre 2026-B
* **Docente:** Mg. Antonio Arroyo Paz (`aarroyop@unsa.edu.pe`)
* **Competencias ABET:** C.c (Diseño con restricciones realistas) · C.d (Trabajo en equipo) · C.g (Comunicación efectiva)
* **Repositorio Oficial en GitHub:** [https://github.com/leonardobaca7/rutaColca_C4.git](https://github.com/leonardobaca7/rutaColca_C4.git)
* **Lugar y Fecha:** Arequipa, Octubre de 2026

---

### Autores e Integrantes del Equipo

| Estudiante | Correo Institucional | Rol AG-08 (Modelo C4) | Rol AG-09 (Patrones GoF) |
| :--- | :--- | :--- | :--- |
| **Emanuel Hilacondo Begazo** | `ehilacondob@unsa.edu.pe` | Modelador / Revisor | Analista de Diseño (Identificación y principios) |
| **Leonardo Juan José Baca Calsin** | `lbacac@unsa.edu.pe` | Redactor DSL / Vocero | Líder Técnico e Implementación Java 21 |
| **Mauro Snayder Sullca Mamani** | `msullcam@unsa.edu.pe` | Revisor / Redactor DSL | Evaluador de Arquitectura (Reto de Paternite) |
| **German Arturo Chipana Jeronimo** | `gchipanaj@unsa.edu.pe` | Vocero / Modelador | Diseñador de Modelos UML (PlantUML) |

---

## Resumen Ejecutivo

El presente informe consolida el trabajo arquitectónico y de diseño orientado a objetos desarrollado durante las Semanas 08 y 09 para la plataforma «RutaColca», sistema concebido para optimizar la coordinación y venta de tours turísticos hacia el Cañón del Colca (Arequipa y Chivay). En una primera fase (AG-08), se aplicó el modelo C4 de Simon Brown junto con la filosofía de Diagramas como Código (DaC) sobre Structurizr DSL, modelando cuatro vistas canónicas: Contexto, Contenedores Lógicos, Dinámico y Topología de Despliegue en Producción, complementado con el registro del ADR-002 para trabajo sin conexión mediante IndexedDB y mitigación de sobreventa.

En la segunda fase (AG-09), el diseño se profundizó hacia el nivel de componentes de software orientados a objetos, abordando cinco escenarios de crecimiento comercial. Se aplicaron cuatro patrones de diseño GoF: Factory Method y Adapter (para cobros multipasarela con Tarjeta, Yape y PayPal), Strategy (para tarifas dinámicas de temporada, estudiantes y grupos), Observer (para notificaciones concurrentes a turistas, guías y agencias) y Adapter (para integrar la API legada de AUTOCOLCA). Crucialmente, el equipo resolvió el reto de la «paternite» en el quinto escenario demostrando con criterio de ingeniería por qué NO debe forzarse un patrón Proxy artesanal cuando un índice B-Tree relacional en PostgreSQL 16 y cabeceras de caché HTTP resuelven el problema con mayor confiabilidad y menor costo de mantenimiento.

---

## 1. Introducción y Contexto del Caso RutaColca

El Valle del Colca recibe anualmente a miles de visitantes nacionales y extranjeros atraídos por atractivos como la Cruz del Cóndor, los baños termales y rutas de trekking. A pesar de este dinamismo, las agencias de turismo locales en Arequipa y Chivay gestionan sus operaciones mediante canales informales: llamadas telefónicas, mensajes no coordinados en WhatsApp y anotaciones físicas en cuadernos de ventanilla. Esta operativa manual genera descoordinación logística con los guías, sobreventa de cupos en temporada alta y dificultades para validar los boletos turísticos obligatorios de AUTOCOLCA.

Para transformar este ecosistema, un consorcio de agencias solicitó el diseño integral de RutaColca. El sistema debe responder a seis historias de usuario clave en su MVP (HU-01 a HU-06), respetando las restricciones de tiempo y tecnología del ADR-001 (React SPA, React PWA, Spring Boot en Java 21, PostgreSQL 16 y Docker en la nube, entregado en 1 mes por un equipo de 4 personas).

---

## 2. Inventario Arquitectónico y Clasificación C4

| Elemento del Caso | Tipo C4 Formal | Justificación Arquitectónica |
| :--- | :--- | :--- |
| **Turista** | Persona | Usuario final que busca tours, selecciona fechas, reserva y paga en línea. |
| **Operador de agencia** | Persona | Personal de ventanilla en Arequipa o Chivay que publica itinerarios y gestiona cupos. |
| **Guía de turismo** | Persona | Profesional de campo que recibe listas e itinerarios por mensajería sin entrar a la web. |
| **Administrador** | Persona | Auditor interno que autoriza nuevas agencias y monitorea reportes financieros. |
| **RutaColca** | Sistema de Software (Propio) | Núcleo de software en estudio que centraliza catálogo, reservas, pagos y validación. |
| **Pasarela de pagos** | Sistema de Software (Externo) | Proveedor financiero (Niubiz/Stripe) que procesa pagos con tarjeta y billeteras móviles. |
| **Sistema de AUTOCOLCA** | Sistema de Software (Externo) | Servicio gubernamental externo consultado vía HTTPS para autenticar boletos turísticos. |
| **WhatsApp Business** | Sistema de Software (Externo) | Plataforma de mensajería empresarial para entrega automatizada de manifiestos. |
| **Web del turista** | Contenedor (Aplicación) | Single Page Application (React) para consulta de catálogo, reserva y pago digital. |
| **Portal de agencias** | Contenedor (Aplicación) | Progressive Web App (React PWA) para gestión operativa y ventas con o sin conexión. |
| **API Backend** | Contenedor (Aplicación) | Servicio REST central (Java 21, Spring Boot) que orquesta lógica y datos. |
| **Base de Datos Principal** | Contenedor (Almacén de Datos) | Motor relacional PostgreSQL 16 para persistencia ACID de transacciones. |
| **Almacén Local de Reservas** | Contenedor (Almacén de Datos) | Base de datos IndexedDB en el navegador para registrar ventas offline en Chivay. |

> **Decisión Crítica:** El Guía de Turismo se modela como Persona receptora del servicio en el diagrama de contexto. Asimismo, Docker y los balanceadores de carga son infraestructura de despliegue y se excluyen rigurosamente del diagrama de contenedores lógicos.

---

## 3. Modelado Arquitectónico C4 de RutaColca (AG-08)

### 3.1. Diagrama de Contexto del Sistema (Nivel 1)
Delimita las fronteras del sistema, identificando a los cuatro actores humanos y los tres sistemas externos.

![Figura 1. Diagrama de Contexto](architecture/c4/ruta-colca/export/structurizr-Contexto.png)

### 3.2. Diagrama de Contenedores (Nivel 2 · Operación Estándar)
Zoom interno a RutaColca según las especificaciones técnicas del ADR-001 con protocolos `JSON/HTTPS` y `JDBC`.

![Figura 2. Diagrama de Contenedores](architecture/c4/ruta-colca/export/structurizr-Contenedores.png)

### 3.3. Diagrama Dinámico: Reservar y Pagar un Tour (HU-02 y HU-03)
Flujo temporal de 8 pasos. La validación con AUTOCOLCA se antepone al cobro para evitar comisiones de reversión bancaria.

![Figura 3. Diagrama Dinámico](architecture/c4/ruta-colca/export/structurizr-Dinamico.png)

### 3.4. Diagrama de Despliegue en Producción
Topología de infraestructura cloud con balanceador TLS, clúster de 2 VMs Ubuntu con Docker y PostgreSQL gestionado.

![Figura 4. Diagrama de Despliegue](architecture/c4/ruta-colca/export/structurizr-DespliegueProduccion.png)

---

## 4. Resolución del Reto Sin Conexión en Chivay (HU-05) y ADR-002

Para garantizar ventas presenciales sin internet en Chivay, se incorporó un almacén local en `IndexedDB` y la política de **Partición de Cupos Garantizados (*Quota Partitioning*)** para erradicar la sobreventa (*overbooking*):

![Figura 5. Diagrama Contenedores con Reto Offline](architecture/c4/ruta-colca/export/structurizr-ContenedoresReto.png)

---

## 5. Diseño Orientado a Objetos: Patrones de Diseño GoF (AG-09)

### 5.1. Escenario 1: Procesamiento Multipasarela (Factory Method + Adapter)
`PasarelaPagoFactory` desacopla la instanciación de pasarelas (Tarjeta, Yape, PayPal) y el cliente solo depende de la abstracción `PasarelaPago`:

![Figura 6. Patrón Pagos Factory y Adapter](patterns/ruta-colca/diagramas/patron-pagos-factory-adapter.png)

### 5.2. Escenario 2: Tarifas Dinámicas (Strategy)
La clase `Reserva` delega el cálculo de precios a la interfaz `EstrategiaPrecio`, permitiendo intercambiar fórmulas (temporada alta, grupos, estudiantes) en tiempo de ejecución:

![Figura 7. Patrón Tarifas Strategy](patterns/ruta-colca/diagramas/patron-tarifas-strategy.png)

### 5.3. Escenario 3: Notificaciones Concurrentes Desacopladas (Observer)
`PublicadorReservas` emite el evento inmutable `EventoReservaConfirmada` hacia suscriptores independientes (email, WhatsApp, tablero PWA):

![Figura 8. Patrón Notificaciones Observer](patterns/ruta-colca/diagramas/patron-notificaciones-observer.png)

### 5.4. Escenario 4: Integración con la API Legada de AUTOCOLCA (Adapter)
`AutocolcaApiAdapter` actúa como Capa Anticorrupción (ACL), aislando el dominio interno de las firmas legadas del servicio estatal:

![Figura 9. Patrón AUTOCOLCA Adapter](patterns/ruta-colca/diagramas/patron-autocolca-adapter.png)

### 5.5. Escenario 5: El Reto de la «Paternite» (Consultas de Disponibilidad)
* **Dictamen:** **NO USAR PATRÓN PROXY.**
* **Justificación de ingeniería:** En un entorno con dos réplicas cloud, una caché en memoria en un Proxy artesanal genera desincronización y riesgo de sobreventa. Un índice relacional B-Tree en PostgreSQL 16 sobre `(tour_id, fecha_salida)` resuelve lecturas en <1 ms, y cabeceras HTTP `Cache-Control` en el balanceador absorben el tráfico repetido sin agregar clases innecesarias.

---

## 6. Gobernanza de Inteligencia Artificial y Auditoría Cruzada

| Actividad | Propuesta de la IA | Evaluación Crítica del Equipo | Decisión Final |
| :--- | :--- | :--- | :--- |
| **AG-08 · Paso 1** | Incluir Docker como contenedor lógico C4. | Violación conceptual grave de la regla de oro C4. | Rechazado. Reubicado en despliegue. |
| **AG-08 · Paso 3** | Incorporar Kafka y Redis al backend. | Sobrediseño que excede el plazo del MVP de 1 mes. | Rechazado. Se mantuvo el stack del ADR-001. |
| **AG-08 · Paso 4** | Cobrar antes de validar con AUTOCOLCA. | Riesgo financiero severo de contracargos bancarios. | Reordenado. Validación previa obligatoria. |
| **AG-09 · Paso 1** | Usar Abstract Factory en pasarelas de pago. | No existen múltiples familias abstractas. | Ajustado a Factory Method + Adapter. |
| **AG-09 · Reto** | Crear Proxy de caché en memoria para cupos. | Caso clásico de paternite; riesgo de sobreventa. | Rechazado. Resuelto con índice en BD y HTTP Cache. |

---

## 7. Respuestas Argumentadas para la Evaluación Docente

1. **¿Por qué RutaColca aparece como una sola caja en el contexto y como un límite con contenedores en el siguiente nivel?**  
   Porque atienden a propósitos y audiencias diferentes. El contexto oculta los detalles técnicos para dialogar con gerentes de agencias y autoridades de turismo. El diagrama de contenedores hace un zoom in para el equipo técnico, mostrando las piezas ejecutables (SPA, PWA, API Spring Boot, PostgreSQL) y los protocolos de integración.
2. **¿Qué diagrama le mostrarían a la gerente de una agencia y cuál al equipo de operaciones?**  
   A la gerente le mostraríamos el Diagrama de Contexto (Nivel 1), que explica qué servicios ofrece la plataforma y cómo se conecta sin jerga técnica. Al equipo de operaciones le mostraríamos el Diagrama de Despliegue, que detalla las máquinas virtuales, balanceadores y base de datos gestionada.
3. **¿Qué propuesta de la IA rechazaron y qué regla de C4 usaron para hacerlo?**  
   Rechazamos la propuesta de considerar a Docker como contenedor C4. Aplicamos la regla oficial de Simon Brown: *«un contenedor C4 es una aplicación o almacén de datos propio, no una tecnología de virtualización de infraestructura»*.
4. **¿Qué cambió en su modelo al resolver el reto sin conexión y en qué diagramas se nota?**  
   Se agregó el contenedor de datos local IndexedDB dentro del Portal PWA y relaciones de sincronización por lotes. Se refleja en la vista `ContenedoresReto` y en el Diagrama de Despliegue dentro del nodo Tablet de Agencia.
5. **Ticket de salida de Patrones: Un banco nuevo ofrece pagos con su propia API. ¿Qué patrón usaría y qué clase crearía?**  
   Usaríamos el patrón Adaptador (Adapter) creando una nueva clase concreta, por ejemplo `BancoNuevoAdapter`, que implemente la interfaz `PasarelaPago` y traduzca las llamadas hacia el SDK del banco, respetando el principio Abierto/Cerrado (OCP).

---

## 8. Conclusiones y Referencias Bibliográficas

1. **Continuidad entre arquitectura y diseño:** El modelo C4 proporcionó la visión macroscópica del sistema, mientras que los patrones GoF estructuraron las clases internas garantizando bajo acoplamiento y alta cohesión.
2. **Sentido crítico frente a la 'paternite':** El verdadero mérito del diseño no radica en sobrecargar el código con patrones, sino en discernir cuándo la infraestructura relacional nativa es más simple y robusta.
3. **Trazabilidad con Diagramas como Código:** Structurizr DSL y PlantUML aseguran que la documentación viva evolucione al ritmo del código sin desincronizaciones.

### Referencias Bibliográficas (Norma APA 7ma Edición)
* Bass, L., Clements, P., & Kazman, R. (2021). *Software architecture in practice* (4th ed.). Addison-Wesley.
* Brown, S. (2026). *The C4 model for visualising software architecture*. O’Reilly Media / c4model.com.
* Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design patterns: Elements of reusable object-oriented software*. Addison-Wesley.
* ISO/IEC/IEEE. (2022). *ISO/IEC/IEEE 42010:2022 Software, systems and enterprise — Architecture description*. International Organization for Standardization.
* Ousterhout, J. (2018). *A philosophy of software design*. Yaknyam Press.
* Valente, M. T. (2020). *Engenharia de software moderna* (cap. 5: Princípios de projeto; cap. 6: Padrões de projeto). Independente. https://engsoftmoderna.info/
