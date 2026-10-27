# Caso Práctico Grupal AG-08 y AG-09: Arquitectura y Diseño de RutaColca

**Universidad Nacional de San Agustín de Arequipa (UNSA)**  
**Facultad de Ingeniería de Producción y Servicios**  
**Escuela Profesional de Ingeniería de Sistemas**  
**Asignatura:** Construcción de Software (1703243) — Semestre 2026-B  
**Docente:** Mg. Antonio Arroyo Paz  

---

## 1. Integrantes del Equipo y Asignación de Roles

Conforme a las directivas de las prácticas AG-08 y AG-09, los roles rotaron para asegurar que todos los miembros participen activamente en el diseño arquitectónico, la redacción de Structurizr DSL, el diseño orientado a objetos GoF y la auditoría con IA:

| Integrante | Correo Institucional | Rol AG-08 (Modelo C4) | Rol AG-09 (Patrones de Diseño) |
| :--- | :--- | :--- | :--- |
| **Emanuel Hilacondo Begazo** | `ehilacondob@unsa.edu.pe` | **Modelador** (Clase) / **Revisor** (Ext.) | **Analista de Diseño** (Identificación de problemas y principios) |
| **Leonardo Juan José Baca Calsin** | `lbacac@unsa.edu.pe` | **Redactor del DSL** (Clase) / **Vocero** (Ext.) | **Líder Técnico** (Implementación Java 21 y gobernanza IA) |
| **Mauro Snayder Sullca Mamani** | `msullcam@unsa.edu.pe` | **Revisor** (Clase) / **Redactor del DSL** (Ext.) | **Evaluador de Arquitectura** (Reto de Paternite y justificación) |
| **German Arturo Chipana Jeronimo** | `gchipanaj@unsa.edu.pe` | **Vocero** (Clase) / **Modelador** (Ext.) | **Diseñador de Modelos** (Diagramas de clases PlantUML) |

---

## 2. Descripción del Caso de Estudio

**RutaColca** es una plataforma tecnológica concebida para un consorcio de agencias de viajes de Arequipa y Chivay, con el propósito de optimizar la venta, reserva y coordinación operativa de tours turísticos en el Cañón del Colca (rutas tradicionales de 2 días, Cruz del Cóndor, trekkings y turismo vivencial).

### 2.1. Arquitectura Base (ADR-001)
* **Web del Turista:** Single Page Application (SPA) desarrollada en React.
* **Portal de Agencias:** Progressive Web Application (PWA) desarrollada en React.
* **Backend de Servicios:** API REST desarrollada en Java 21 con Spring Boot.
* **Persistencia Relacional:** PostgreSQL 16.
* **Integraciones Externas:**
  * Pasarela de pagos externa para transacciones con tarjeta y billeteras digitales (RutaColca no almacena datos sensibles).
  * API del Sistema AUTOCOLCA para validación digital de boletos turísticos.
  * WhatsApp Business API para entrega automatizada de manifiestos de viaje e itinerarios a los guías de turismo.
* **Infraestructura de Producción:** Despliegue en proveedor cloud con Docker, balanceador de carga TLS y base de datos gestionada.

---

## 3. Matriz de Entregables Oficiales AG-08 (Tabla 8)

| Código | Descripción del Entregable | Archivo en el Repositorio | Parte | Responsable Principal |
| :---: | :--- | :--- | :---: | :--- |
| **E1** | Inventario clasificado de elementos C4 | [`docs/architecture/c4/ruta-colca/inventario.md`](docs/architecture/c4/ruta-colca/inventario.md) | A | Emanuel Hilacondo Begazo |
| **E2** | Modelo base en Structurizr DSL | [`docs/architecture/c4/ruta-colca/workspace.dsl`](docs/architecture/c4/ruta-colca/workspace.dsl) | A | Leonardo Baca Calsin |
| **E3** | Revisión cruzada documentada y explicación ejecutiva | [`docs/architecture/c4/ruta-colca/revision-cruzada.md`](docs/architecture/c4/ruta-colca/revision-cruzada.md)<br>[`docs/architecture/c4/ruta-colca/explicacion.md`](docs/architecture/c4/ruta-colca/explicacion.md) | A | Mauro Sullca Mamani<br>German Chipana Jeronimo |
| **E4** | Modelo final con despliegue y vista `ContenedoresReto` | [`workspace.dsl`](workspace.dsl) | B | Mauro Sullca Mamani |
| **E5** | Registro de decisión arquitectónica para trabajo sin conexión | [`docs/architecture/adr/ADR-002-trabajo-sin-conexion.md`](docs/architecture/adr/ADR-002-trabajo-sin-conexion.md) | B | German Chipana Jeronimo |
| **E6** | Exportaciones a C4-PlantUML, Mermaid y PNG | [`docs/architecture/c4/ruta-colca/export/`](docs/architecture/c4/ruta-colca/export/) | B | Mauro Sullca Mamani |
| **E7** | Bitácora de trazabilidad de uso de IA (prompts P1 a P8) | [`docs/architecture/c4/ruta-colca/bitacora-ia.md`](docs/architecture/c4/ruta-colca/bitacora-ia.md) | A y B | Leonardo Baca Calsin |

---

## 4. Diagramas de Arquitectura (Niveles C4)

### 4.1. Nivel 1 · Diagrama de Contexto
Delimita las fronteras del sistema, identificando los cuatro actores humanos y los tres sistemas externos.

![Diagrama de Contexto](docs/architecture/c4/ruta-colca/export/structurizr-Contexto.png)

---

### 4.2. Nivel 2 · Diagrama de Contenedores (Operación Estándar)
Zoom interno a RutaColca según las especificaciones técnicas del ADR-001.

![Diagrama de Contenedores](docs/architecture/c4/ruta-colca/export/structurizr-Contenedores.png)

---

### 4.3. Nivel 2 · Diagrama de Contenedores con Soporte Offline (Reto Chivay - HU-05)
Incorporación del almacén de datos del lado del cliente (`IndexedDB`) dentro del Portal PWA para garantizar ventas en ventanilla sin red.

![Diagrama de Contenedores con Reto Offline](docs/architecture/c4/ruta-colca/export/structurizr-ContenedoresReto.png)

---

### 4.4. Diagrama Dinámico · Reservar y Pagar un Tour (HU-02 y HU-03)
Flujo temporal ordenado que prioriza la validación del boleto con AUTOCOLCA antes de procesar el cargo financiero.

![Diagrama Dinámico](docs/architecture/c4/ruta-colca/export/structurizr-Dinamico.png)

---

### 4.5. Diagrama de Despliegue en Producción
Topología física/virtual con balanceador de carga TLS, 2 réplicas de la API en VMs con Docker y base de datos relacional gestionada.

![Diagrama de Despliegue en Producción](docs/architecture/c4/ruta-colca/export/structurizr-DespliegueProduccion.png)

---

## 5. Instrucciones de Compilación y Validación de Arquitectura (C4)

El modelo fue verificado con **Structurizr CLI** (versión 2025.11.09) y **Java 22**:

```bash
# Validar la sintaxis del modelo
structurizr.bat validate -w docs/architecture/c4/ruta-colca/workspace.dsl

# Exportar a C4-PlantUML
structurizr.bat export -w docs/architecture/c4/ruta-colca/workspace.dsl -f plantuml/c4plantuml -o docs/architecture/c4/ruta-colca/export

# Exportar a Mermaid
structurizr.bat export -w docs/architecture/c4/ruta-colca/workspace.dsl -f mermaid -o docs/architecture/c4/ruta-colca/export

# Generar imágenes PNG a partir de PlantUML
java -jar plantuml.jar -tpng docs/architecture/c4/ruta-colca/export/*.puml
```

---

## 6. Actividad Grupal AG-09: Patrones de Diseño en RutaColca (Tema 09)

En la Semana 09, la plataforma **RutaColca** entra al nivel de diseño detallado de componentes y código orientado a objetos. Se analizaron cinco escenarios de crecimiento del sistema aplicando el catálogo GoF y principios SOLID:

### 6.1. Matriz de Identificación de Patrones (Paso 1)

| Escenario | Problema de Diseño | ¿Aplica Patrón? | Patrón Seleccionado | Principio de Diseño Clave |
| :---: | :--- | :---: | :---: | :--- |
| **1. Pagos** | Creación dispersa de clientes bancarios (Tarjeta, Yape, PayPal) con `new` acoplados a `ReservaService`. | **SÍ** | **Factory Method + Adapter** | **Programar para interfaces / Abierto-Cerrado (OCP)** |
| **2. Tarifas** | Fórmulas de cálculo de precio cambiantes embebidas en condicionales `if/else` dentro de `Reserva`. | **SÍ** | **Strategy** | **Encapsular lo que varía / Composición sobre herencia** |
| **3. Notificaciones** | `ReservaService` fuertemente acoplado a múltiples canales (correo, WhatsApp, WebSocket PWA). | **SÍ** | **Observer** | **Bajo acoplamiento / Abierto-Cerrado (OCP)** |
| **4. AUTOCOLCA** | Interfaz del servicio legado de AUTOCOLCA incompatible con las firmas del dominio interno. | **SÍ** | **Adapter** | **Programar para interfaces / Inversión de Dependencias (DIP)** |
| **5. Disponibilidad** | Consultas masivas repetitivas sobre disponibilidad de cupos por salida. | **NO (Paternite)** | *Ninguno (Índice BD + HTTP Cache)* | **Simple primero / No forzar patrones donde la tecnología base resuelve** |

*Documentación detallada en:* [`docs/patterns/ruta-colca/escenarios.md`](docs/patterns/ruta-colca/escenarios.md)

---

### 6.2. Resolución del Reto: Justificación de la "Paternite" en el Escenario 5

> *«El mayor riesgo de los patrones de diseño es su sobreaplicación: no fuerce un problema a encajar en un patrón cuando una solución tradicional funciona mejor».*  
> — John Ousterhout (2018), *A Philosophy of Software Design*.

* **Por qué se rechazó el patrón Proxy:** Implementar un `DisponibilidadProxy` manual con caché en memoria en Java introduce problemas de concurrencia multihilo, desincronización entre las dos máquinas virtuales del clúster cloud y alto riesgo de *overbooking* (sobreventa) por lecturas sucias de cupos en memoria.
* **Solución de ingeniería aplicada:** Un índice B-Tree relacional en PostgreSQL 16 (`CREATE INDEX idx_salidas_disp ON salidas (tour_id, fecha_salida) WHERE cupos_libres > 0;`) y cabeceras de respuesta HTTP estándar `Cache-Control: public, max-age=30` en el balanceador resuelven cientos de lecturas por minuto en sub-milisegundos sin añadir una sola clase innecesaria.

*Informe completo del reto en:* [`docs/patterns/ruta-colca/reto-paternite.md`](docs/patterns/ruta-colca/reto-paternite.md)

---

### 6.3. Diagramas de Clases de los Patrones (PlantUML)

#### Escenario 1 · Procesamiento Multipasarela (Factory Method + Adapter)
![Patrón Pagos](docs/patterns/ruta-colca/diagramas/patron-pagos-factory-adapter.png)

#### Escenario 2 · Tarifas y Precios Dinámicos (Strategy)
![Patrón Tarifas](docs/patterns/ruta-colca/diagramas/patron-tarifas-strategy.png)

#### Escenario 3 · Notificaciones Concurrentes Desacopladas (Observer)
![Patrón Notificaciones](docs/patterns/ruta-colca/diagramas/patron-notificaciones-observer.png)

#### Escenario 4 · Integración con API Legada de AUTOCOLCA (Adapter)
![Patrón AUTOCOLCA](docs/patterns/ruta-colca/diagramas/patron-autocolca-adapter.png)

---

### 6.4. Trazabilidad y Gobernanza de IA en Patrones (AG-09)
Se auditó cada respuesta de IA según la plantilla de la Slide 31, identificando los sesgos de sobreaplicación:
* Se rechazó la propuesta de la IA de aplicar *Abstract Factory* en Pagos (sobrediseño innecesario).
* Se rechazó la propuesta de la IA de aplicar *Chain of Responsibility* en Tarifas (las tarifas son excluyentes, no un pipeline de filtros).
* Se rechazó la propuesta de la IA de aplicar *Proxy de Caché* en el Escenario 5, detectando el antipatrón de *paternite*.

*Registro de prompts en:* [`docs/patterns/ruta-colca/bitacora-ia-patrones.md`](docs/patterns/ruta-colca/bitacora-ia-patrones.md)

---

### 6.5. Demostración en Código Java 21
El código fuente de los cuatro patrones se implementó de forma modular en [`docs/patterns/ruta-colca/src/`](docs/patterns/ruta-colca/src/) y se compila sin dependencias externas:

```bash
# Compilar todas las clases
javac -d bin docs/patterns/ruta-colca/src/com/rutacolca/patterns/**/*.java docs/patterns/ruta-colca/src/com/rutacolca/patterns/*.java

# Ejecutar la demostración en consola
java -cp bin com.rutacolca.patterns.DemoRutaColcaPatrones
```
