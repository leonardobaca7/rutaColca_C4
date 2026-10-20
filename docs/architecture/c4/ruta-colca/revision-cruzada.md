# Informe de Revisión Cruzada de Arquitectura C4

**Asignatura:** Construcción de Software (1703243) — Semestre 2026-B  
**Docente:** Mg. Antonio Arroyo Paz  
**Equipo Evaluador:** Mauro Snayder Sullca Mamani (Revisor - Parte A), Emanuel Hilacondo Begazo, Leonardo Baca Calsin, German Chipana Jeronimo  
**Grupo Auditado:** Grupo Par N.º 2  
**Norma de Referencia:** Lista oficial de verificación de Simon Brown (*c4model.com/diagrams/checklist*)  

---

## 1. Matriz de Hallazgos y Auditoría Arquitectónica

Se realizó una revisión exhaustiva del modelo `workspace.dsl` presentado por el grupo par, aplicando los criterios de los Anexos A y B del documento AG-08:

| N.º | Elemento o Relación Afectada | Hallazgo Detectado | Gravedad | ¿Se acepta el hallazgo? | Justificación y Corrección Aplicada |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **1** | Relación `Web Turista -> API Backend` | Se utilizó la etiqueta genérica *"usa"* sin indicar la acción funcional ni el protocolo de transporte. | **Media** | **Sí** | Viola la directiva de relaciones C4. Se corrigió a: *"Consulta disponibilidad de salidas y envía solicitud de reserva en"* con protocolo `JSON/HTTPS`. |
| **2** | Diagrama de Contenedores | Se incluyó una caja nombrada *"Docker Engine"* dentro del límite del sistema `RutaColca`. | **Alta** | **Sí** | Error conceptual grave según la rúbrica. Un contenedor C4 es una aplicación ejecutable o un almacén de datos, no una tecnología de virtualización. Se eliminó del diagrama de contenedores y se trasladó como runtime al Diagrama de Despliegue. |
| **3** | Diagrama de Contexto | No se incluyó al *Guía de Turismo* bajo el argumento de que *"no tiene usuario en el sistema"*. | **Media** | **Sí** | El guía es un actor humano indispensable en la entrega de valor turístico del negocio. Recibe el itinerario por WhatsApp Business, por lo que debe figurar como `Person` conectado al canal de mensajería. |
| **4** | Diagrama Dinámico | El paso de cobro se ejecutaba antes de verificar el boleto turístico con AUTOCOLCA. | **Alta** | **Sí** | Inconsistencia de negocio. Cobrar antes de validar expone a la plataforma a costos bancarios de contracargo y reembolsos si el boleto es inválido. Se reordenó el flujo para validar con AUTOCOLCA previamente al débito en la pasarela. |
| **5** | Vista de Contenedores | El contenedor de base de datos no indicaba la versión del motor relacional. | **Baja** | **Sí** | Según el ADR-001 debe especificarse la tecnología exacta. Se añadió la etiqueta tecnológica explícita `PostgreSQL 16`. |

---

## 2. Checklist de Verificación Aplicado (Anexo A)

- [x] **General:** Cada vista cuenta con título descriptivo, alcance delimitado y leyenda que define formas y códigos cromáticos.
- [x] **Elementos:** Cada persona, sistema y contenedor tiene nombre concreto, responsabilidad resumida y tecnologías explícitas en corchetes.
- [x] **Siglas:** Acrónimos técnicos como *SPA*, *PWA*, *REST*, *JDBC* y *TLS* están claramente contextualizados o explicados.
- [x] **Relaciones:** Todas las flechas son unidireccionales, describen la intención con una frase verbal activa y declaran el protocolo (`JSON/HTTPS`, `JDBC`, `HTTPS`).
- [x] **Notación:** Distinción cromática clara entre personas (azul oscuro), sistemas internos (azul intermedio), contenedores lógicos (verde azulado) y sistemas externos (gris neutro), legibles en monocromo.
- [x] **Audiencia:** El diagrama de contexto es comprensible para directivos de agencias sin requerir explicación técnica asistida.
