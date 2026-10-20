# ADR-002: Estrategia de Persistencia Local y Sincronización sin Conexión para Agencias en Chivay

* **Estado:** Aceptado  
* **Fecha:** Octubre 2026  
* **Autores:** German Arturo Chipana Jeronimo (Modelador - Parte B), Mauro Snayder Sullca Mamani, Emanuel Hilacondo Begazo, Leonardo Juan José Baca Calsin  
* **Historia de Usuario:** HU-05 (Registro de reservas presenciales sin internet)  
* **Supersede / Relacionado con:** ADR-001 (Portal de agencias en React como PWA, Spring Boot en backend)  

---

## 1. Contexto y Problemática

El Valle del Colca presenta condiciones geográficas y de infraestructura de telecomunicaciones que provocan caídas frecuentes del servicio de internet y energía eléctrica en localidades clave como Chivay y Cabanaconde. A pesar de esto, las agencias de turismo locales reciben un flujo constante de visitantes que solicitan reservas presenciales de último minuto directamente en ventanilla (counter).

La historia de usuario **HU-05** exige:  
> *«Como operador de una agencia en Chivay, quiero registrar reservas presenciales aunque no haya internet y sincronizarlas cuando vuelva la conexión».*

El principal reto técnico y de negocio radica en resolver la **concurrencia y el riesgo de sobreventa (overbooking)**: si una agencia en Chivay vende cupos mientras opera desconectada, y simultáneamente turistas en Arequipa compran los mismos cupos a través de la Web SPA central, podría superarse la capacidad máxima del transporte o guía al momento de la reconciliación.

Asimismo, debemos respetar la restricción del **ADR-001** y el plazo del proyecto: entrega del MVP en 1 mes con un equipo de 4 desarrolladores, evitando arquitecturas distribuidas de alta complejidad como CRDTs pesados o motores de sincronización propietarios.

---

## 2. Decisión Arquitectónica

Se aprueba la implementación de una arquitectura **Offline-First ligera basada en PWA** compuesta por los siguientes pilares:

### 2.1. Almacenamiento Local en Cliente (IndexedDB)
* Se incorpora un contenedor de datos local dentro del Portal de Agencias (PWA) ejecutado sobre **IndexedDB** en el navegador del dispositivo (tablet o PC de ventanilla).
* El portal mantendrá una réplica local de solo lectura del catálogo de tours y disponibilidad de fechas descargada en la última sesión con conexión.
* Las nuevas reservas presenciales capturadas sin internet se guardarán en una tabla local de salida (*Local Outbox Queue*) con estado `PENDIENTE_SINCRONIZACION` y un identificador único universal (UUID v4) generado en el cliente para garantizar **idempotencia**.

### 2.2. Política de Asignación de Cupos y Mitigación de Overbooking
Para erradicar la sobreventa sin bloquear la venta física, se establece un modelo de **Partición de Cupos de Contingencia (Quota Partitioning)**:
1. **Cupo Asignado en Ventanilla (Garantizado):**  
   Cada mañana o al sincronizar con internet, la API central reserva y delega una cuota fija de cupos offline (por ejemplo, 3 cupos por salida diaria) a la terminal autorizada de Chivay. La agencia puede vender y confirmar de inmediato estos cupos con total certeza matemática de no conflicto.
2. **Venta Excedente en Contingencia (Reserva Provisional):**  
   Si la demanda en ventanilla agota el cupo asignado durante el corte de red, el sistema permite registrar la venta bajo el estado `RESERVA_PROVISIONAL_OFFLINE`. El comprobante impreso o emitido advierte explícitamente al pasajero que la asignación definitiva del asiento quedará confirmada al reanudarse la conectividad.
3. **Regla de Reconciliación First-Come, First-Served con Compensación:**  
   Al reconectarse, las reservas se procesan en la API central en estricto orden cronológico (utilizando la marca de tiempo local firmada criptográficamente por la PWA). En el caso excepcional de sobrecupo absoluto en el transporte, la API dispara un evento de compensación: asignación prioritaria en la siguiente salida disponible o notificación urgente al operador para reubicación asistida.

### 2.3. Mecanismo de Sincronización
* La PWA utiliza **Service Workers** con la API de `Background Sync` y escuchas al evento `window.addEventListener('online')`.
* Al detectar enlace a internet, el cliente envía por lotes las transacciones pendientes mediante peticiones seguras `POST /api/v1/reservas/sincronizar` acompañadas del UUID de cada reserva para evitar duplicados ante fallos intermitentes de red.

---

## 3. Consecuencias

### 3.1. Consecuencias Positivas
* **Resiliencia Operativa:** Las agencias de Chivay continúan atendiendo público y registrando ingresos incluso durante caídas prolongadas de telecomunicaciones en el valle.
* **Cero Sobreventa en Cupos Asignados:** La partición de cuotas garantiza integridad transaccional sin requerir comunicación en tiempo real con el servidor central.
* **Alineación con el Stack Tecnológico:** Aprovecha las capacidades nativas de React PWA y estándares web modernos, sin requerir el desarrollo de aplicaciones móviles nativas ni añadir sobrecarga de dependencias complejas.
* **Idempotencia y Trazabilidad:** El uso de UUIDs evita la duplicidad de registros si la red se corta a mitad de una sincronización.

### 3.2. Consecuencias Negativas y Mitigaciones
* **Manejo de estados en frontend:** Mayor complejidad en la interfaz de usuario de la PWA para mostrar indicadores visuales del estado de conexión (Online / Modo Offline) y advertencias de sincronización pendiente.
* **Dependencia del navegador:** Los operadores deben utilizar navegadores compatibles con soporte moderno de PWA e IndexedDB (e.g., Google Chrome, Microsoft Edge, Safari Mobile). Se establece como requisito operativo de hardware y software en las agencias.
* **Riesgo residual de validación de boletos:** Al no haber internet, no es posible validar en tiempo real el boleto turístico con el sistema externo de AUTOCOLCA. Las reservas offline almacenan el código de boleto para su validación asíncrona diferida durante la reconciliación central.
