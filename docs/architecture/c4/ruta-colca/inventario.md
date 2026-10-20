# Inventario de Elementos C4 — Plataforma RutaColca

**Asignatura:** Construcción de Software (1703243) — Semestre 2026-B  
**Docente:** Mg. Antonio Arroyo Paz  
**Caso Práctico:** AG-08 · Modelo C4 de RutaColca  
**Equipo de Trabajo:**
* Emanuel Hilacondo Begazo (Modelador - Parte A)
* Leonardo Juan José Baca Calsin (Redactor del DSL - Parte A)
* Mauro Snayder Sullca Mamani (Revisor - Parte A)
* German Arturo Chipana Jeronimo (Vocero - Parte A)  

---

## 1. Clasificación de Elementos según el Modelo C4

A continuación se detalla el inventario exhaustivo de personas, sistemas (propios y externos) y contenedores identificados en el caso RutaColca, conforme a las abstracciones formales definidas por Simon Brown en el modelo C4.

| Elemento del caso | Tipo C4 | Justificación arquitectónica |
| :--- | :--- | :--- |
| **Turista** | Persona | Usuario final externo que navega el catálogo, reserva salidas y procesa el pago de sus tours en línea. |
| **Operador de agencia** | Persona | Usuario de negocio (en Arequipa o Chivay) que publica tours, gestiona cupos y registra reservas presenciales. |
| **Guía de turismo** | Persona | Actor humano operativo que recibe itinerarios y listas de pasajeros mediante mensajería externa sin ingresar al portal web. |
| **Administrador** | Persona | Usuario interno con privilegios elevados encargado de validar agencias aliadas y supervisar métricas de venta. |
| **RutaColca** | Sistema de software (Propio) | Núcleo de software en estudio que centraliza la publicación, validación de boletos, pagos y despacho de información de tours. |
| **Pasarela de pagos** | Sistema de software (Externo) | Plataforma financiera externa (e.g., Niubiz, Stripe, MercadoPago, Izipay) que procesa transacciones bancarias y billeteras móviles de manera segura. |
| **WhatsApp Business** | Sistema de software (Externo) | Plataforma de mensajería corporativa de Meta que entrega notificaciones operativas automatizadas a los teléfonos de los guías. |
| **Sistema de AUTOCOLCA** | Sistema de software (Externo) | Servicio gubernamental externo consultado vía API HTTPS para verificar la autenticidad y estado de los boletos turísticos obligatorios. |
| **Web del turista** | Contenedor (Aplicación) | Single Page Application (SPA) construida en React para clientes finales en navegadores web de escritorio y móviles. |
| **Portal de agencias** | Contenedor (Aplicación) | Progressive Web App (PWA) construida en React para operadores turísticos, con capacidades de operación sin conexión en Chivay. |
| **API Backend** | Contenedor (Aplicación) | Servicio web central en Java 21 con Spring Boot que implementa la lógica de negocio, validaciones y orquestación externa. |
| **Base de datos principal** | Contenedor (Almacén de datos) | Base de datos relacional PostgreSQL 16 que almacena de forma consistente usuarios, tours, cupos, boletos y transacciones. |
| **Almacén local en navegador** *(Reto Chivay)* | Contenedor (Almacén de datos) | Almacenamiento local estructurado del lado del cliente (IndexedDB) para persistir temporalmente ventas presenciales sin internet. |

---

## 2. Decisiones de Modelado y Criterios de Exclusión

### 2.1. ¿Por qué el Guía de Turismo se modela como Persona en el Contexto?
El guía de turismo no posee credenciales directas para iniciar sesión en la Web SPA ni en el Portal PWA de RutaColca. Sin embargo, en el modelo C4, una **Persona** representa cualquier rol humano que interactúa con el ecosistema del sistema de software o recibe valor/información directa de él. Dado que el sistema genera el itinerario y lo entrega al guía a través de WhatsApp Business, el guía es el destinatario final del flujo operacional. Excluirlo dejaría incompleto el alcance del servicio turístico en el diagrama de contexto.

### 2.2. Exclusión de Docker, Kubernetes o Servidores en este nivel
Conforme a la regla fundamental del modelo C4:
> *«Un contenedor C4 representa una unidad de software ejecutable de manera independiente o un almacén de datos (ej. una SPA, una API REST, una base de datos o un bucket S3); no debe confundirse con un contenedor de infraestructura como Docker o Podman».*

Las máquinas virtuales, los contenedores Docker y los balanceadores de carga corresponden a **Nodos de Despliegue** e **Infrastructure Nodes**, por lo que se modelan estrictamente en el Diagrama de Despliegue (Paso 7), manteniéndose fuera de los diagramas de Contexto y Contenedores lógicos.
