# Informe Técnico de Justificación: Reto de la "Paternite" en RutaColca

**Caso:** Actividad Grupal AG-09 · Patrones de Diseño  
**Autor:** Mauro Snayder Sullca Mamani (`msullcam@unsa.edu.pe`) — Evaluador de Arquitectura  
**Equipo:** Emanuel Hilacondo Begazo, Leonardo Baca Calsin, German Chipana Jeronimo  
**Docente:** Mg. Antonio Arroyo Paz — EPIS UNSA (2026-B)  

---

## 1. El Dilema de la Sobreaplicación de Patrones ("Paternite")

El concepto de **paternite** (*patternitis*) describe el antipatrón de ingeniería de software en el cual un desarrollador intenta forzar la aplicación de patrones del catálogo GoF a cualquier problema técnico, ignorando que los patrones introducen un costo tangible: **indirección, mayor número de clases, mayor superficie de pruebas y acoplamiento estructural**.

John Ousterhout en *A Philosophy of Software Design* (2018) y Marco Tulio Valente en *Engenharia de Software Moderna* (2020) advierten que antes de adoptar un patrón, el ingeniero debe responder tres preguntas clave:
1. *¿Existen variantes reales de comportamiento que justifiquen polimorfismo?*
2. *¿Basta con una solución simple o tradicional (un `new`, un índice de BD o una configuración)?*
3. *¿La flexibilidad ganada compensa la complejidad de las nuevas clases?*

---

## 2. Análisis Comparativo de los Cinco Escenarios de RutaColca

| Escenario | ¿Hay variantes reales? | ¿Se justifica el costo del patrón? | Veredicto |
| :--- | :---: | :---: | :---: |
| **1. Métodos de pago** | Sí (Tarjeta, Yape, PayPal con diferentes protocolos) | **Sí:** Aislar SDKs financieros externos en Adaptadores y crearlos con Factory evita modificar el servicio nuclear. | **Aplica Patrón** |
| **2. Tarifas dinámicas** | Sí (Temporada alta, grupos, estudiantes, estándar) | **Sí:** Las fórmulas de descuento son reglas de negocio intercambiables en tiempo de ejecución. Strategy encaja perfecto. | **Aplica Patrón** |
| **3. Notificaciones** | Sí (Email, WhatsApp, WebSocket PWA con ciclo de vida asíncrono) | **Sí:** El sujeto no debe conocer a los suscriptores. Observer garantiza extensibilidad abierta. | **Aplica Patrón** |
| **4. AUTOCOLCA** | Sí (API legada gubernamental incompatible con el dominio) | **Sí:** Adapter actúa como Capa Anticorrupción (ACL), aislando el modelo de dominio. | **Aplica Patrón** |
| **5. Consultas de disponibilidad** | **NO** (Es una única operación de lectura repetitiva de cupos) | **NO:** Forzar un Proxy de caché artesanal en memoria introduce sobrecarga de clases y riesgo de concurrencia. | **RECHAZADO (Paternite)** |

---

## 3. Justificación Técnica: Por qué el Escenario 5 NO debe usar un Patrón

### 3.1. La Falsa Solución del Patrón Proxy
Si nos dejáramos llevar por la "paternite", la propuesta canónica de la IA o de un estudiante inexperto sería:
```java
// Antipatrón: Proxy manual innecesario
public class DisponibilidadServiceProxy implements ConsultaDisponibilidad {
    private final ConsultaDisponibilidad realService;
    private final Map<String, DisponibilidadDto> cache = new ConcurrentHashMap<>();

    public DisponibilidadDto consultar(Long tourId, LocalDate fecha) {
        String key = tourId + ":" + fecha;
        return cache.computeIfAbsent(key, k -> realService.consultar(tourId, fecha));
    }
}
```

### 3.2. Problemas que introduce este Proxy manual:
1. **Inconsistencia de Negocio y Riesgo de Overbooking:**  
   Si una agencia en Chivay o un turista en Arequipa reserva el último cupo, el mapa en memoria de otras instancias del proxy seguirá devolviendo que hay cupos libres, permitiendo reservas sobrevendidas.
2. **Incompatibilidad con Arquitectura Cloud Multiusuario:**  
   El ADR-001 y el Diagrama de Despliegue de RutaColca establecen **dos máquinas virtuales de backend balanceadas**. Una caché en memoria local dentro de un Proxy artesanal genera desincronización inmediata entre las dos réplicas.
3. **Mantenimiento Innecesario:**  
   Se crea una interfaz artificial, una clase proxy y lógica de invalidación manual propensa a fugas de memoria (*memory leaks*).

### 3.3. La Solución Simple Primero (Best Practice de Ingeniería)
1. **Índice B-Tree en PostgreSQL 16:**  
   La base de datos relacional resuelve consultas de disponibilidad en menos de 0.8 ms mediante un índice condicional:
   ```sql
   CREATE INDEX idx_salidas_disp ON salidas (tour_id, fecha_salida) WHERE cupos_libres > 0;
   ```
2. **Caché Declarativa HTTP (Gateway / CDN / Nginx):**  
   Configurar cabeceras de respuesta estándar en el controlador REST:
   ```java
   @GetMapping("/tours/{id}/disponibilidad")
   public ResponseEntity<DisponibilidadDto> consultar(...) {
       return ResponseEntity.ok()
           .cacheControl(CacheControl.maxAge(30, TimeUnit.SECONDS).cachePublic())
           .body(service.consultar(id, fecha));
   }
   ```
   El Balanceador de Carga (AWS ALB / Nginx) absorbe los cientos de solicitudes por minuto sin que una sola línea de código Java deba gestionar un patrón de diseño.

---

## 4. Conclusión

El Escenario 5 representa la frontera exacta entre el buen diseño de software y la **paternite**. Un buen ingeniero no es quien implementa la mayor cantidad de patrones GoF, sino quien sabe cuándo **una solución técnica estándar de base de datos o infraestructura web es superior, más segura y más simple de mantener**.
