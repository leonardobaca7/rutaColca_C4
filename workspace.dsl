workspace "RutaColca" "Modelo C4 de la plataforma de tours RutaColca - EPIS UNSA" {

    !identifiers hierarchical

    model {
        // ==========================================
        // PASO 2 · Personas (Un rol humano por elemento)
        // ==========================================
        turista = person "Turista" "Visitante interesado en buscar, reservar y pagar tours hacia el Valle del Colca."
        operador = person "Operador de Agencia" "Personal de agencia de turismo en Arequipa o Chivay que publica tours, administra cupos y atiende ventanilla."
        administrador = person "Administrador" "Auditor interno de la plataforma que aprueba agencias aliadas y supervisa métricas de venta."
        guia = person "Guía de Turismo" "Profesional de campo que recibe itinerarios y listas de pasajeros para liderar los recorridos turísticos."

        // ==========================================
        // PASO 2 y 3 · Sistema en estudio y Contenedores (ADR-001, ADR-002 y ADR-003)
        // ==========================================
        ruta = softwareSystem "RutaColca" "Plataforma digital para la publicación, validación de boletos turísticos, reserva y pago de tours al Valle del Colca." {
            webTurista = container "Web del Turista" "Permite a los turistas explorar catálogo de tours, seleccionar fechas y pagar reservas en línea." "React (SPA)"
            portalAgencias = container "Portal de Agencias" "Permite a las agencias publicar tours, administrar cupos y registrar ventas presenciales (online y offline)." "React (PWA)"
            apiBackend = container "API Backend" "Provee la lógica de negocio para tours, validación de boletos turísticos, orquestación de pagos resilientes con Outbox y notificaciones." "Java 21, Spring Boot"
            baseDatos = container "Base de Datos Principal" "Almacena información de agencias, guías, tours, cupos, boletos validados, transacciones y cola de pagos outbox." "PostgreSQL 16" "Database"
            almacenLocal = container "Almacén Local de Reservas" "Almacena temporalmente en el navegador de la tablet las ventas presenciales durante cortes de conectividad en Chivay." "IndexedDB" "Database"
        }

        // ==========================================
        // PASO 2 · Sistemas Externos (Etiqueta "Externo")
        // ==========================================
        pasarelaPagos = softwareSystem "Pasarela de Pagos" "Servicio externo para procesamiento seguro de pagos con tarjetas bancarias y billeteras móviles." "Externo"
        autocolca = softwareSystem "Sistema de AUTOCOLCA" "Sistema externo institucional para verificación de validez y vigencia de boletos turísticos." "Externo"
        whatsApp = softwareSystem "WhatsApp Business" "Plataforma externa de mensajería empresarial para entrega automatizada de itinerarios." "Externo"

        // ==========================================
        // Relaciones de Contexto (Nivel 1)
        // ==========================================
        turista -> ruta "Busca tours, reserva cupos y realiza el pago de servicios en" "HTTPS"
        operador -> ruta "Publica itinerarios, gestiona cupos y registra ventas presenciales en" "HTTPS"
        administrador -> ruta "Aprueba agencias registradas y consulta reportes de ventas en" "HTTPS"
        ruta -> pasarelaPagos "Solicita autorización de cargos y cobro de reservas a" "HTTPS"
        ruta -> autocolca "Valida número y vigencia de boleto turístico en" "HTTPS"
        ruta -> whatsApp "Envía itinerarios y listas de pasajeros a través de" "HTTPS"
        whatsApp -> guia "Entrega notificaciones con itinerarios y lista del grupo a" "WhatsApp Protocol"
        whatsApp -> turista "Entrega confirmaciones de reserva y vouchers confirmados a" "WhatsApp Protocol"

        // ==========================================
        // Relaciones de Contenedores (Nivel 2)
        // ==========================================
        turista -> ruta.webTurista "Explora catálogo, solicita reserva y efectúa pagos en" "HTTPS"
        operador -> ruta.portalAgencias "Publica salidas, administra cupos y gestiona reservas en" "HTTPS"
        administrador -> ruta.portalAgencias "Audita agencias y supervisa indicadores comerciales en" "HTTPS"

        ruta.webTurista -> ruta.apiBackend "Solicita catálogo, envía reservas y procesa pagos en" "JSON/HTTPS"
        ruta.portalAgencias -> ruta.apiBackend "Gestiona tours, consulta disponibilidad y sincroniza reservas con" "JSON/HTTPS"
        ruta.portalAgencias -> ruta.almacenLocal "Guarda y recupera reservas presenciales en cola de salida en" "IndexedDB API"
        ruta.almacenLocal -> ruta.portalAgencias "Provee datos de reservas pendientes para sincronización hacia" "IndexedDB API"

        ruta.apiBackend -> ruta.baseDatos "Lee y escribe información transaccional persistente y cola outbox en" "JDBC"
        ruta.apiBackend -> pasarelaPagos "Solicita cobro de transacciones financieras a" "JSON/HTTPS"
        ruta.apiBackend -> autocolca "Consulta estado y validez de boleto turístico en" "JSON/HTTPS"
        ruta.apiBackend -> whatsApp "Dispara envío de itinerarios y listas de grupo mediante" "JSON/HTTPS"

        // ==========================================
        // PASO 7 · Despliegue en Producción
        // ==========================================
        prod = deploymentEnvironment "Produccion" {
            turistaDevice = deploymentNode "Dispositivo del Turista" "Smartphone o computadora personal del visitante" "Android / iOS / Windows / macOS" {
                navegador = deploymentNode "Navegador Web del Cliente" "Navegador web moderno estándar" "Chrome / Safari / Firefox" {
                    containerInstance ruta.webTurista
                }
            }

            agenciaDevice = deploymentNode "Terminal de Agencia (Chivay / Arequipa)" "Tablet o PC en counter de venta de la agencia" "Android Tablet / Windows PC" {
                pwaRuntime = deploymentNode "Runtime PWA de Agencia" "Navegador compatible con Service Workers y almacenamiento offline" "Chromium Runtime / PWA" {
                    containerInstance ruta.portalAgencias
                    containerInstance ruta.almacenLocal
                }
            }

            cloud = deploymentNode "Proveedor Cloud" "Infraestructura de nube de alta disponibilidad" "AWS / GCP / Cloud Datacenter (Región Sudamérica)" {
                balanceador = infrastructureNode "Balanceador de Carga" "Termina conexiones TLS/HTTPS y distribuye las peticiones entre los nodos de backend" "AWS ALB / Nginx"

                cluster = deploymentNode "Grupo de Cómputo API" "Instancias virtuales para absorción de demanda y picos en temporada alta" "Cluster Linux" {
                    vm1 = deploymentNode "VM Ubuntu 24.04 (Instancia 1)" "Máquina virtual de producción" "Ubuntu Server / Docker" {
                        api1 = containerInstance ruta.apiBackend
                    }
                    vm2 = deploymentNode "VM Ubuntu 24.04 (Instancia 2)" "Máquina virtual de producción para alta disponibilidad" "Ubuntu Server / Docker" {
                        api2 = containerInstance ruta.apiBackend
                    }
                }

                dbNode = deploymentNode "Servicio Gestionado de Base de Datos" "Instancia relacional administrada de alta confiabilidad" "AWS RDS PostgreSQL / Cloud SQL" {
                    dbInstance = containerInstance ruta.baseDatos
                }
            }
        }

        prod.cloud.balanceador -> prod.cloud.cluster.vm1.api1 "Distribuye peticiones balanceadas a" "HTTP/8080"
        prod.cloud.balanceador -> prod.cloud.cluster.vm2.api2 "Distribuye peticiones balanceadas a" "HTTP/8080"
    }

    views {
        // Vista 1: Diagrama de Contexto
        systemContext ruta "Contexto" "Diagrama de contexto del sistema RutaColca" {
            include *
            autolayout lr
        }

        // Vista 2: Diagrama de Contenedores (Línea base estándar sin reto offline)
        container ruta "Contenedores" "Diagrama de contenedores de la plataforma RutaColca (Operación estándar)" {
            include *
            exclude ruta.almacenLocal
            autolayout tb
        }

        // Vista 3: Diagrama de Contenedores con Reto Offline (HU-05)
        container ruta "ContenedoresReto" "Diagrama de contenedores con soporte offline para agencias en Chivay (HU-05)" {
            include *
            autolayout tb
        }

        // Vista 4: Diagrama Dinámico (HU-02 y HU-03)
        dynamic ruta "Dinamico" "Flujo dinámico: Reservar y pagar un tour (HU-02 y HU-03)" {
            turista -> ruta.webTurista "1. Selecciona tour, ingresa datos de pasajeros y código de boleto turístico"
            ruta.webTurista -> ruta.apiBackend "2. Envía solicitud de reserva con boleto y datos de pago (JSON/HTTPS)"
            ruta.apiBackend -> autocolca "3. Valida vigencia y autenticidad del boleto turístico (JSON/HTTPS)"
            ruta.apiBackend -> pasarelaPagos "4. Solicita cargo y confirmación del pago del tour (JSON/HTTPS)"
            ruta.apiBackend -> ruta.baseDatos "5. Registra la reserva confirmada con estado PAGADO (JDBC)"
            ruta.apiBackend -> whatsApp "6. Solicita envío de itinerario y lista del grupo (JSON/HTTPS)"
            whatsApp -> guia "7. Entrega mensaje con itinerario y lista de pasajeros (WhatsApp Protocol)"
            ruta.apiBackend -> ruta.webTurista "8. Retorna confirmación de reserva exitosa con voucher digital (JSON/HTTPS)"
            autolayout lr
        }

        // Vista 5: Diagrama de Despliegue en Producción
        deployment ruta "Produccion" "DespliegueProduccion" "Diagrama de despliegue en entorno de producción con alta disponibilidad" {
            include *
            autolayout tb
        }

        // Vista 6: Diagrama Dinámico - Resiliencia de Pagos en Temporada Alta (Escenario E2 / ADR-003)
        dynamic ruta "DinamicoPagosResiliente" "Flujo dinámico resiliente: Caída de pasarela de pagos por 15 min y reconciliación diferida (Escenario E2 / ADR-003)" {
            turista -> ruta.webTurista "1. Envía solicitud de reserva con boleto y datos de pago"
            ruta.webTurista -> ruta.apiBackend "2. Despacha intento de reserva y cobro (JSON/HTTPS)"
            ruta.apiBackend -> pasarelaPagos "3. Intenta cobro síncrono; pasarela no responde (Timeout 3s / HTTP 504)"
            ruta.apiBackend -> ruta.baseDatos "4. Registra atómicamente la reserva y la orden en la tabla pagos_outbox (Estado: PENDIENTE_PAGO)"
            ruta.apiBackend -> ruta.webTurista "5. Retorna confirmación de reserva diferida con ticket de seguimiento temporal (JSON/HTTPS)"
            ruta.webTurista -> turista "6. Informa que su reserva está asegurada y su pago en proceso de verificación"
            ruta.apiBackend -> ruta.baseDatos "7. Worker Outbox sondea pagos diferidos con SELECT ... FOR UPDATE SKIP LOCKED"
            ruta.apiBackend -> pasarelaPagos "8. Pasarela se restablece; Worker reintenta y confirma cobro exitoso con Idempotency-Key"
            ruta.apiBackend -> ruta.baseDatos "9. Actualiza reserva a CONFIRMADA_PAGADA y marca outbox como PROCESADO"
            ruta.apiBackend -> whatsApp "10. Solicita envío de voucher confirmado e itinerario oficial"
            whatsApp -> turista "11. Notifica voucher de pago confirmado y código QR del boleto turístico al WhatsApp del turista"
            autolayout lr
        }

        // Estilos visuales institucionales
        styles {
            element "Person" {
                shape Person
                background #0B3D62
                color #ffffff
            }
            element "Software System" {
                background #1B5E8B
                color #ffffff
            }
            element "Container" {
                background #0E7D73
                color #ffffff
            }
            element "Database" {
                shape Cylinder
                background #0E7D73
                color #ffffff
            }
            element "Externo" {
                background #8C8C8C
                color #ffffff
            }
            element "Infrastructure Node" {
                shape RoundedBox
                background #546E7A
                color #ffffff
            }
        }
    }
}
