# Caso Práctico Grupal AG-08: Modelo C4 de RutaColca

**Universidad Nacional de San Agustín de Arequipa (UNSA)**  
**Facultad de Ingeniería de Producción y Servicios**  
**Escuela Profesional de Ingeniería de Sistemas**  
**Asignatura:** Construcción de Software (1703243) — Semestre 2026-B  
**Docente:** Mg. Antonio Arroyo Paz  

---

## 1. Integrantes del Equipo y Asignación de Roles

Conforme a la directiva de la práctica, los roles rotaron entre la Parte A (modelado en clase) y la Parte B (extensión y reto offline) para asegurar que todos los miembros participen activamente en el diseño y en la redacción de código en Structurizr DSL:

| Integrante | Correo Institucional | Rol en Parte A (Clase) | Rol en Parte B (Extensión) | Entregable Principal a Cargo |
| :--- | :--- | :--- | :--- | :--- |
| **Emanuel Hilacondo Begazo** | `ehilacondob@unsa.edu.pe` | **Modelador** | **Revisor** | Inventario C4 (`inventario.md`) y auditoría final de rúbrica |
| **Leonardo Juan José Baca Calsin** | `lbacac@unsa.edu.pe` | **Redactor del DSL** | **Vocero** | Modelo C4 base (`workspace.dsl`), validación CLI y bitácora |
| **Mauro Snayder Sullca Mamani** | `msullcam@unsa.edu.pe` | **Revisor** | **Redactor del DSL** | Matriz de revisión cruzada, entorno de despliegue y exportaciones |
| **German Arturo Chipana Jeronimo** | `gchipanaj@unsa.edu.pe` | **Vocero** | **Modelador** | Explicación no técnica a gerencia y diseño de persistencia offline (`ADR-002`) |

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

## 3. Matriz de Entregables Oficiales (Tabla 8)

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

## 5. Instrucciones de Compilación y Validación

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
