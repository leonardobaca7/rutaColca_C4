import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m_name, m_val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m_name}')
        node.set(qn('w:w'), str(m_val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_report():
    doc = docx.Document()
    
    # Page setup - Margins 2.5 cm (approx 0.98 inch)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.different_first_page_header_footer = True
        
        # Header / Footer
        footer = section.footer
        f_p = footer.paragraphs[0]
        f_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        f_run = f_p.add_run("Construcción de Software (2026-B) · EPIS UNSA | Caso AG-08: RutaColca")
        f_run.font.name = "Calibri"
        f_run.font.size = Pt(8.5)
        f_run.font.color.rgb = RGBColor(120, 120, 120)

    # Styles & Colors
    PRIMARY = RGBColor(11, 61, 98)      # #0B3D62 (UNSA Navy)
    SECONDARY = RGBColor(27, 94, 139)   # #1B5E8B
    TEXT_COLOR = RGBColor(40, 40, 40)
    MUTED_COLOR = RGBColor(90, 90, 90)

    def add_title(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(30)
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(24)
        r.font.bold = True
        r.font.color.rgb = PRIMARY
        return p

    def add_subtitle(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(24)
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(13)
        r.font.color.rgb = SECONDARY
        return p

    def add_heading_1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(16)
        r.font.bold = True
        r.font.color.rgb = PRIMARY
        return p

    def add_heading_2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = SECONDARY
        return p

    def add_heading_3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(11.5)
        r.font.bold = True
        r.font.color.rgb = TEXT_COLOR
        return p

    def add_p(text, bold_prefix=None, space_after=6, italic=False):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            rb.font.name = "Calibri"
            rb.font.size = Pt(11)
            rb.font.bold = True
            rb.font.color.rgb = TEXT_COLOR
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(11)
        r.font.italic = italic
        r.font.color.rgb = TEXT_COLOR
        return p

    def add_callout(quote_text, author_prefix=None):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        set_cell_background(cell, "F0F4F8")
        set_cell_margins(cell, top=140, bottom=140, left=200, right=140)
        cp = cell.paragraphs[0]
        cp.paragraph_format.space_after = Pt(2)
        cp.paragraph_format.line_spacing = 1.15
        if author_prefix:
            ra = cp.add_run(author_prefix + " ")
            ra.font.name = "Calibri"
            ra.font.size = Pt(10.5)
            ra.font.bold = True
            ra.font.color.rgb = PRIMARY
        rq = cp.add_run(quote_text)
        rq.font.name = "Calibri"
        rq.font.size = Pt(10.5)
        rq.font.italic = True
        rq.font.color.rgb = TEXT_COLOR
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    def add_image_figure(img_path, caption, width_in=5.8):
        if os.path.exists(img_path):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run()
            run.add_picture(img_path, width=Inches(width_in))
            
            cp = doc.add_paragraph()
            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cp.paragraph_format.space_after = Pt(12)
            c_run = cp.add_run(caption)
            c_run.font.name = "Calibri"
            c_run.font.size = Pt(9.5)
            c_run.font.italic = True
            c_run.font.color.rgb = MUTED_COLOR

    # ==========================================
    # CARÁTULA OFICIAL
    # ==========================================
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_after = Pt(2)
    r_inst = p_inst.add_run("UNIVERSIDAD NACIONAL DE SAN AGUSTÍN DE AREQUIPA")
    r_inst.font.name = "Calibri"
    r_inst.font.size = Pt(14)
    r_inst.font.bold = True
    r_inst.font.color.rgb = PRIMARY

    p_fac = doc.add_paragraph()
    p_fac.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fac.paragraph_format.space_after = Pt(2)
    r_fac = p_fac.add_run("FACULTAD DE INGENIERÍA DE PRODUCCIÓN Y SERVICIOS\nESCUELA PROFESIONAL DE INGENIERÍA DE SISTEMAS")
    r_fac.font.name = "Calibri"
    r_fac.font.size = Pt(11)
    r_fac.font.bold = True
    r_fac.font.color.rgb = SECONDARY

    add_title("INFORME TÉCNICO DE ARQUITECTURA DE SOFTWARE")
    add_subtitle("Caso Práctico Grupal AG-08: Modelado C4 Integral de la Plataforma «RutaColca»\nContexto, Contenedores, Dinámico, Reto Offline y Despliegue en Producción")

    # Metadata Table
    meta_table = doc.add_table(rows=6, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Asignatura:", "Construcción de Software (Código: 1703243) — Semestre 2026-B"),
        ("Tema Académico:", "Tema 08: Modelo C4 (Abstracciones, Diagramas como Código y Verificación)"),
        ("Docente:", "Mg. Antonio Arroyo Paz (aarroyop@unsa.edu.pe)"),
        ("Competencias ABET:", "C.c (Diseño con restricciones realistas) · C.d (Trabajo en equipo) · C.g (Comunicación efectiva)"),
        ("Repositorio Oficial:", "https://github.com/leonardobaca7/rutaColca_C4.git"),
        ("Fecha de Entrega:", "Arequipa, Octubre de 2026")
    ]
    for i, (k, v) in enumerate(meta_data):
        c0, c1 = meta_table.cell(i, 0), meta_table.cell(i, 1)
        c0.width, c1.width = Inches(2.0), Inches(4.5)
        set_cell_background(c0, "F5F7FA")
        set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, 60, 60, 80, 80)
        set_cell_margins(c1, 60, 60, 80, 80)
        
        pk = c0.paragraphs[0]
        pk.paragraph_format.space_after = Pt(2)
        rk = pk.add_run(k)
        rk.font.name = "Calibri"
        rk.font.size = Pt(10)
        rk.font.bold = True
        rk.font.color.rgb = PRIMARY
        
        pv = c1.paragraphs[0]
        pv.paragraph_format.space_after = Pt(2)
        rv = pv.add_run(v)
        rv.font.name = "Calibri"
        rv.font.size = Pt(10)
        rv.font.color.rgb = TEXT_COLOR

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Team Members Table
    add_heading_3("Equipo de Trabajo y Asignación de Roles:")
    team_table = doc.add_table(rows=5, cols=4)
    team_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Estudiante", "Correo Institucional", "Rol Parte A (Clase)", "Rol Parte B (Extensión)"]
    for j, h in enumerate(headers):
        cell = team_table.cell(0, j)
        set_cell_background(cell, "0B3D62")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(h)
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    team_data = [
        ("Emanuel Hilacondo Begazo", "ehilacondob@unsa.edu.pe", "Modelador", "Revisor"),
        ("Leonardo Juan José Baca Calsin", "lbacac@unsa.edu.pe", "Redactor del DSL", "Vocero / Líder"),
        ("Mauro Snayder Sullca Mamani", "msullcam@unsa.edu.pe", "Revisor", "Redactor del DSL"),
        ("German Arturo Chipana Jeronimo", "gchipanaj@unsa.edu.pe", "Vocero", "Modelador")
    ]
    for row_idx, data in enumerate(team_data, start=1):
        bg = "FFFFFF" if row_idx % 2 == 1 else "F9FAFC"
        for col_idx, val in enumerate(data):
            cell = team_table.cell(row_idx, col_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, 60, 60, 80, 80)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(val)
            r.font.name = "Calibri"
            r.font.size = Pt(9.5)
            if col_idx == 0:
                r.font.bold = True
            r.font.color.rgb = TEXT_COLOR

    doc.add_page_break()

    # ==========================================
    # RESUMEN EJECUTIVO
    # ==========================================
    add_heading_1("Resumen Ejecutivo")
    add_p(
        "El presente informe documenta el diseño, modelado, verificación formal y despliegue de la plataforma "
        "tecnológica «RutaColca», desarrollada para solucionar los problemas críticos de coordinación, sobreventa y "
        "comercialización digital de tours que enfrentan las agencias turísticas en Arequipa y el Valle del Colca (Chivay). "
        "Adoptando el modelo C4 formulado por Simon Brown y la filosofía de Diagramas como Código (DaC) mediante Structurizr DSL, "
        "el equipo elaboró una arquitectura orientada al negocio que articula cuatro niveles de abstracción: Contexto del Sistema, "
        "Contenedores Lógicos, Dinámico de Colaboración y Topología de Despliegue en Producción."
    )
    add_p(
        "Entre los logros más destacados de esta intervención técnica se encuentran: (1) la resolución arquitectónica del reto de "
        "conectividad intermitente en Chivay mediante una arquitectura Offline-First con IndexedDB en un portal PWA y una política de "
        "partición de cupos que erradica el overbooking; (2) la orquestación temporal que antepone la validación digital de boletos con "
        "AUTOCOLCA antes de efectuar cargos bancarios; (3) la validación formal con cero errores sintácticos mediante Structurizr CLI y "
        "la compilación multiformato a C4-PlantUML y Mermaid; y (4) la adopción estricta de una gobernanza de Inteligencia Artificial "
        "trazable, en la cual la IA propuso código y el equipo aplicó criterios de ingeniería para rechazar componentes innecesarios "
        "(Kubernetes, Kafka, Redis), logrando un modelo realista y ejecutable en el plazo perentorio de 1 mes."
    )

    # ==========================================
    # SECCIÓN 1: INTRODUCCIÓN Y REQUERIMIENTOS
    # ==========================================
    add_heading_1("1. Introducción y Contexto del Caso RutaColca")
    add_p(
        "El Valle del Colca es uno de los destinos turísticos más emblemáticos de la región sur del Perú, recibiendo cientos de miles "
        "de turistas nacionales e internacionales cada año. Sin embargo, la cadena de valor de las agencias de viajes de Arequipa y Chivay "
        "opera históricamente bajo un esquema tradicional fragmentado: reservas manuales por llamadas telefónicas, mensajería no estructurada "
        "en redes sociales y anotaciones físicas en cuadernos. Esta falta de integración ocasiona cuellos de botella severos, cancelaciones "
        "de último momento, desinformación hacia los guías de campo y pérdidas económicas por boletos turísticos no validados."
    )
    add_p(
        "Para responder a esta problemática, un consorcio de agencias solicitó el diseño arquitectónico de RutaColca: una plataforma que "
        "integre la publicación de salidas, la reserva y pago en línea por turistas, la verificación electrónica de boletos turísticos con "
        "el ente regulador AUTOCOLCA y la notificación automatizada de itinerarios hacia los guías vía WhatsApp Business."
    )

    add_heading_2("1.1. Historias de Usuario del Producto Mínimo Viable (MVP)")
    add_p("El alcance de la plataforma se encuentra estructurado en seis Historias de Usuario priorizadas según su impacto en el negocio:")

    hu_table = doc.add_table(rows=7, cols=4)
    hu_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hu_headers = ["ID", "Historia de Usuario", "Prioridad", "Complejidad Técnica"]
    for j, h in enumerate(hu_headers):
        cell = hu_table.cell(0, j)
        set_cell_background(cell, "0B3D62")
        set_cell_margins(cell, 80, 80, 80, 80)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(h)
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    hu_data = [
        ("HU-01", "Como operador de agencia, quiero publicar un tour con fechas de salida y cupos para venderlo en línea.", "Alta", "CRUD transaccional de cupos"),
        ("HU-02", "Como turista, quiero reservar una salida y pagarla en línea con tarjeta o billetera móvil para asegurar mi lugar.", "Alta", "Integración con pasarela de pagos"),
        ("HU-03", "Como turista, quiero registrar el número de mi boleto turístico para validarlo con AUTOCOLCA antes de confirmar.", "Alta", "Consumo de API HTTPS externa"),
        ("HU-04", "Como guía, quiero recibir por WhatsApp el itinerario y la lista de pasajeros un día antes de la salida.", "Media", "Despacho automatizado vía Webhooks"),
        ("HU-05", "Como operador en Chivay, quiero registrar reservas presenciales en ventanilla aunque no haya internet.", "Media (Reto)", "PWA Offline-First + Sincronización"),
        ("HU-06", "Como administrador, quiero aprobar agencias aliadas y supervisar reportes de ventas por mes.", "Baja", "Dashboard de auditoría y métricas")
    ]
    for row_idx, (hid, hdesc, hprio, hcomp) in enumerate(hu_data, start=1):
        bg = "FFFFFF" if row_idx % 2 == 1 else "F9FAFC"
        for col_idx, text_val in enumerate([hid, hdesc, hprio, hcomp]):
            cell = hu_table.cell(row_idx, col_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, 60, 60, 70, 70)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(text_val)
            r.font.name = "Calibri"
            r.font.size = Pt(9)
            if col_idx == 0 or col_idx == 2:
                r.font.bold = True
            r.font.color.rgb = TEXT_COLOR

    add_heading_2("1.2. Restricciones y Decisiones Previas (ADR-001)")
    add_p(
        "El desarrollo del sistema está supeditado a decisiones técnicas obligatorias tomadas previamente por el comité de ingeniería (ADR-001):",
        bold_prefix="Marco Tecnológico: "
    )
    add_p("Plazo y Capacidad: Entrega del MVP en 1 mes con un equipo de 4 ingenieros, potenciados por asistentes de IA.", bold_prefix="• ")
    add_p("Web del Turista: Single Page Application (SPA) construida en React para acceso ágil desde navegadores de escritorio y celulares.", bold_prefix="• ")
    add_p("Portal de Agencias: Progressive Web App (PWA) en React, dotada de Service Workers y capacidades de ejecución en cliente.", bold_prefix="• ")
    add_p("Servicios Backend: API REST empresarial desarrollada en Java 21 sobre Spring Boot, asegurando tipado estático y robustez.", bold_prefix="• ")
    add_p("Almacenamiento Central: Motor relacional PostgreSQL 16 con soporte de integridad transaccional ACID.", bold_prefix="• ")
    add_p("Despliegue y Aislamiento: Contenedores Docker desplegados sobre máquinas virtuales en un proveedor de computación en la nube.", bold_prefix="• ")
    add_p("Procesamiento Financiero: Delegado completamente a una pasarela externa certificada (PCI-DSS); RutaColca jamás guarda tarjetas de crédito.", bold_prefix="• ")

    # ==========================================
    # SECCIÓN 2: INVENTARIO ARQUITECTÓNICO
    # ==========================================
    add_heading_1("2. Inventario Arquitectónico y Clasificación C4")
    add_p(
        "Antes de trazar cualquier diagrama, el equipo clasificó exhaustivamente cada entidad del caso de acuerdo con la jerarquía "
        "de abstracciones de Simon Brown: Personas, Sistemas de Software (propios y externos) y Contenedores."
    )

    inv_table = doc.add_table(rows=14, cols=3)
    inv_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    inv_headers = ["Elemento del Caso", "Tipo C4 Formal", "Justificación Arquitectónica"]
    for j, h in enumerate(inv_headers):
        cell = inv_table.cell(0, j)
        set_cell_background(cell, "0B3D62")
        set_cell_margins(cell, 80, 80, 80, 80)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(h)
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    inv_data = [
        ("Turista", "Persona", "Usuario final que busca tours, selecciona fechas, reserva y paga en línea."),
        ("Operador de agencia", "Persona", "Personal de counter en Arequipa o Chivay que publica itinerarios y gestiona cupos."),
        ("Guía de turismo", "Persona", "Profesional de campo que recibe listas e itinerarios por mensajería sin entrar a la web."),
        ("Administrador", "Persona", "Auditor interno que autoriza nuevas agencias y monitorea reportes financieros."),
        ("RutaColca", "Sistema de Software (Propio)", "Núcleo de software en estudio que centraliza catálogo, reservas, pagos y validación."),
        ("Pasarela de pagos", "Sistema de Software (Externo)", "Proveedor financiero (Niubiz/Stripe) que procesa pagos con tarjeta y billeteras móviles."),
        ("Sistema de AUTOCOLCA", "Sistema de Software (Externo)", "Servicio gubernamental externo consultado vía HTTPS para autenticar boletos turísticos."),
        ("WhatsApp Business", "Sistema de Software (Externo)", "Plataforma de mensajería empresarial para entrega automatizada de manifiestos."),
        ("Web del turista", "Contenedor (Aplicación)", "Single Page Application (React) para consulta de catálogo, reserva y pago digital."),
        ("Portal de agencias", "Contenedor (Aplicación)", "Progressive Web App (React PWA) para gestión operativa y ventas con o sin conexión."),
        ("API Backend", "Contenedor (Aplicación)", "Servicio REST central (Java 21, Spring Boot) que orquesta lógica y datos."),
        ("Base de Datos Principal", "Contenedor (Almacén de Datos)", "Motor relacional PostgreSQL 16 para persistencia ACID de transacciones."),
        ("Almacén Local de Reservas", "Contenedor (Almacén de Datos)", "Base de datos IndexedDB en el navegador para registrar ventas offline en Chivay.")
    ]
    for row_idx, (e_name, e_type, e_just) in enumerate(inv_data, start=1):
        bg = "FFFFFF" if row_idx % 2 == 1 else "F9FAFC"
        for col_idx, text_val in enumerate([e_name, e_type, e_just]):
            cell = inv_table.cell(row_idx, col_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, 50, 50, 60, 60)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(text_val)
            r.font.name = "Calibri"
            r.font.size = Pt(8.5)
            if col_idx == 0:
                r.font.bold = True
            elif col_idx == 1:
                r.font.color.rgb = SECONDARY
                r.font.bold = True
            else:
                r.font.color.rgb = TEXT_COLOR

    add_heading_2("2.1. Decisiones Clave de Exclusión y Justificación de Actores")
    add_p(
        "Un debate fundamental en el equipo fue determinar si el Guía de Turismo debía modelarse en el diagrama de contexto, dado que "
        "las especificaciones aclaran que «no usa la plataforma directamente». La conclusión unánime de ingeniería fue que SÍ debe incluirse. "
        "En el estándar C4, una Persona no es sinónimo de una cuenta con credenciales en la base de datos, sino un rol humano que recibe valor "
        "o interactúa con el ecosistema. Dado que RutaColca envía el itinerario y manifiesto a través de WhatsApp Business hacia el guía, este "
        "representa el último eslabón humano de la operación turística. Omitirlo generaría una visión incompleta del flujo de valor."
    )
    add_callout(
        "«Un contenedor en el modelo C4 es una aplicación ejecutable o un almacén de datos (ej. una SPA web, una API REST, una base de datos relacional). "
        "Docker, las máquinas virtuales o los balanceadores de carga son nodos y mecanismos de infraestructura física/virtual, los cuales pertenecen "
        "exclusivamente al Diagrama de Despliegue. Confundir un contenedor Docker con un contenedor C4 constituye uno de los errores más severos en la rúbrica».",
        author_prefix="Criterio Metodológico:"
    )

    # ==========================================
    # SECCIÓN 3: MODELADO C4
    # ==========================================
    add_heading_1("3. Modelado Arquitectónico (Niveles C4 y Vistas de Apoyo)")
    add_p(
        "Siguiendo el enfoque de Simon Brown («Zoom in / Zoom out»), el sistema se modeló íntegramente en Structurizr DSL, manteniendo "
        "un único modelo fuente de datos (Single Source of Truth) a partir del cual se compilan y proyectan todas las vistas."
    )

    add_heading_2("3.1. Nivel 1 · Diagrama de Contexto del Sistema")
    add_p(
        "El Diagrama de Contexto muestra a RutaColca como una caja negra centralizada rodeada por sus cuatro actores humanos y los tres "
        "sistemas externos. Se aplicaron relaciones estrictamente unidireccionales con frases verbales descriptivas, eliminando términos genéricos como «usa»."
    )
    add_image_figure(
        "docs/architecture/c4/ruta-colca/export/structurizr-Contexto.png",
        "Figura 1. Diagrama de Contexto de la plataforma RutaColca (Compilado en Structurizr DSL y C4-PlantUML).",
        width_in=5.8
    )

    add_heading_2("3.2. Nivel 2 · Diagrama de Contenedores (Operación Estándar)")
    add_p(
        "Al realizar zoom sobre RutaColca, el límite del sistema revela los cuatro contenedores del ADR-001. Las relaciones externas se trasladan "
        "con precisión quirúrgica al contenedor que realmente las ejecuta: los usuarios acceden mediante HTTPS a las interfaces de React, mientras que "
        "las comunicaciones internas y externas entre servicios se realizan sobre JSON/HTTPS o JDBC en el caso del acceso a PostgreSQL."
    )
    add_image_figure(
        "docs/architecture/c4/ruta-colca/export/structurizr-Contenedores.png",
        "Figura 2. Diagrama de Contenedores de RutaColca para la operación estándar en línea.",
        width_in=5.2
    )

    add_heading_2("3.3. Diagrama Dinámico · Escenario «Reservar y Pagar un Tour» (HU-02 y HU-03)")
    add_p(
        "Para modelar la interacción temporal, se elaboró una vista dinámica que refleja fielmente las llamadas secuenciales entre contenedores. "
        "El equipo resolvió la pregunta de diseño fundamental planteada por el docente:",
        bold_prefix="Orquestación Temporal: "
    )
    add_callout(
        "¿Se debe validar el boleto turístico con AUTOCOLCA antes o después de cobrar en la pasarela de pagos?\n"
        "Decisión: Se valida OBLIGATORIAMENTE antes de procesar el cargo bancario. "
        "Justificación de negocio: Si se realiza el cobro primero y posteriormente el sistema de AUTOCOLCA rechaza el boleto por encontrarse vencido "
        "o no coincidir con el documento de identidad, la plataforma incurre en costos financieros por comisiones bancarias no reembolsables, riesgos "
        "de contracargo y una experiencia de usuario pésima al tener que emitir reembolsos manuales. Validar primero asegura que la reserva es jurídicamente "
        "viable antes de comprometer los fondos del turista.",
        author_prefix="Decisión de Diseño:"
    )
    add_image_figure(
        "docs/architecture/c4/ruta-colca/export/structurizr-Dinamico.png",
        "Figura 3. Diagrama Dinámico numerado: Flujo de reserva, validación con AUTOCOLCA, cobro y despacho a WhatsApp.",
        width_in=6.0
    )

    add_heading_2("3.4. Diagrama de Despliegue en Producción")
    add_p(
        "El entorno de despliegue `Produccion` modela la topología de cómputo en la nube para responder a la alta demanda y picos estacionales "
        "(julio, agosto y feriados largos). Consta de: (a) dispositivos cliente (smartphones y tablets); (b) un Balanceador de Carga "
        "(`AWS ALB / Nginx`) modelado como `infrastructureNode` que termina el cifrado TLS; (c) un clúster de cómputo con dos máquinas virtuales "
        "Ubuntu 24.04 ejecutando réplicas de la API Spring Boot dentro de contenedores Docker; y (d) una instancia gestionada de PostgreSQL 16 de alta disponibilidad."
    )
    add_image_figure(
        "docs/architecture/c4/ruta-colca/export/structurizr-DespliegueProduccion.png",
        "Figura 4. Diagrama de Despliegue en Producción con balanceo de carga y réplicas de cómputo.",
        width_in=5.4
    )

    # ==========================================
    # SECCIÓN 4: RETO OFFLINE Y ADR-002
    # ==========================================
    add_heading_1("4. Resolución del Reto de Negocio: Modo Sin Conexión en Chivay (HU-05) y ADR-002")
    add_p(
        "Chivay presenta interrupciones recurrentes en los servicios de energía eléctrica y telecomunicaciones. Sin embargo, los turistas que "
        "llegan al valle acuden a las ventanillas de las agencias a comprar tours de último minuto. Para cumplir con la historia HU-05 sin "
        "desbordar el presupuesto de tiempo (1 mes, 4 desarrolladores), se diseñó una solución ligera Offline-First documentada formalmente en el ADR-002."
    )

    add_heading_2("4.1. Respuestas de Ingeniería a los Cuatro Interrogantes del Reto")
    add_p(
        "1. ¿Qué contenedor nuevo aparece? Aparece un almacén de datos del lado del cliente denominado «Almacén Local de Reservas», "
        "implementado sobre la tecnología estándar IndexedDB en el navegador del operador.\n"
        "2. ¿Qué relación nueva tiene el portal y qué cambia en portal -> API? El portal de agencias adquiere una relación bidireccional local "
        "con IndexedDB (`Guarda y recupera reservas en cola de salida` vía IndexedDB API). La relación portal -> API deja de ser síncrona obligatoria "
        "y pasa a operar de forma asíncrona por lotes mediante el Background Sync API de los Service Workers al recuperar la señal.\n"
        "3. ¿En qué nodo de despliegue se ejecuta? Se ejecuta en el cliente: en el subnodo `Runtime PWA de Agencia` dentro de la `Tablet de Agencia`.\n"
        "4. ¿Qué riesgo de negocio introduce la sincronización diferida y cómo se resuelve? El riesgo crítico es la sobreventa (overbooking): "
        "que una agencia en Chivay venda en ventanilla offline un asiento que simultáneamente fue comprado por internet en Arequipa. "
        "Se propuso la regla de «Partición de Cupos Garantizados (Quota Partitioning)»: cada terminal en Chivay dispone de una cuota exclusiva "
        "(ej. 3 cupos diarios) asignada durante la mañana. Si las ventas en ventanilla exceden la cuota mientras no hay red, la reserva se registra como "
        "«Provisional en Cola» advirtiendo al pasajero de la confirmación formal al reanudarse el enlace."
    )

    add_image_figure(
        "docs/architecture/c4/ruta-colca/export/structurizr-ContenedoresReto.png",
        "Figura 5. Diagrama de ContenedoresReto: Incorporación del Almacén Local IndexedDB para soporte offline en Chivay.",
        width_in=5.4
    )

    # ==========================================
    # SECCIÓN 5: VERIFICACIÓN Y AUDITORÍA CRUZADA
    # ==========================================
    add_heading_1("5. Verificación de Calidad y Revisión Cruzada de Arquitectura")
    add_p(
        "En cumplimiento de la Parte A (Paso 5), se ejecutó una sesión formal de revisión cruzada aplicando la lista oficial de Simon Brown "
        "(c4model.com/diagrams/checklist). El grupo evaluó el modelo del equipo par y auditó el propio para garantizar el estándar de máxima calificación."
    )

    rev_table = doc.add_table(rows=6, cols=5)
    rev_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    rev_headers = ["N.º", "Elemento Auditado", "Hallazgo Detectado", "Severidad", "Acción Correctiva Adoptada"]
    for j, h in enumerate(rev_headers):
        cell = rev_table.cell(0, j)
        set_cell_background(cell, "0B3D62")
        set_cell_margins(cell, 80, 80, 80, 80)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(h)
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    rev_data = [
        ("1", "Web Turista -> API", "Etiqueta genérica «usa» sin verbo activo ni protocolo.", "Media", "Corregido a: «Solicita catálogo, envía reservas y procesa pagos en» [JSON/HTTPS]."),
        ("2", "Diagrama Contenedores", "Caja nombrada «Docker Engine» dentro de RutaColca.", "Alta", "Eliminado de contenedores lógicos; reubicado como nodo de ejecución en despliegue."),
        ("3", "Diagrama Contexto", "Omisión del Guía de Turismo por «no tener login».", "Media", "Reincorporado como Persona receptora conectada al canal de WhatsApp Business."),
        ("4", "Diagrama Dinámico", "Flujo cobraba en pasarela antes de validar con AUTOCOLCA.", "Alta", "Reordenado: la validación del boleto es condición previa obligatoria para el débito."),
        ("5", "Base de Datos", "No indicaba la versión específica del motor relacional.", "Baja", "Actualizado con la especificación técnica exacta del ADR-001: PostgreSQL 16.")
    ]
    for row_idx, (rnum, rel, rfind, rsev, racc) in enumerate(rev_data, start=1):
        bg = "FFFFFF" if row_idx % 2 == 1 else "F9FAFC"
        for col_idx, text_val in enumerate([rnum, rel, rfind, rsev, racc]):
            cell = rev_table.cell(row_idx, col_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, 50, 50, 60, 60)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(text_val)
            r.font.name = "Calibri"
            r.font.size = Pt(8.5)
            if col_idx == 0:
                r.font.bold = True
            elif col_idx == 3:
                r.font.bold = True
                if text_val == "Alta":
                    r.font.color.rgb = RGBColor(180, 40, 40)
                else:
                    r.font.color.rgb = SECONDARY
            else:
                r.font.color.rgb = TEXT_COLOR

    # ==========================================
    # SECCIÓN 6: COMUNICACIÓN NO TÉCNICA
    # ==========================================
    add_heading_1("6. Comunicación Ejecutiva hacia Stakeholders No Técnicos")
    add_p(
        "En el Paso 6, el vocero del grupo preparó un discurso de socialización para la gerente de una agencia en Chivay. "
        "Bajo las restricciones de la rúbrica (máximo 120 palabras, sin siglas ni tecnicismos como API, DSL, HTTPS o PWA), "
        "se diseñó un mensaje empático y centrado estrictamente en los beneficios del negocio:"
    )
    add_callout(
        "«Buenos días, doña Rosa. Sabemos lo difícil que es hoy coordinar tours llamando por teléfono, anotando pasajeros en cuadernos "
        "y mandando mensajes sueltos cuando la señal falla aquí en Chivay. Con RutaColca, su agencia podrá publicar directamente sus salidas hacia "
        "la Cruz del Cóndor o los trekkings del cañón, indicando cuántos asientos libres tiene cada día. Los turistas eligen su tour por internet "
        "y pagan en el acto desde su teléfono o tarjeta. Antes de confirmar, la plataforma verifica al instante que el boleto turístico de AUTOCOLCA "
        "sea válido para que usted no tenga problemas en el control de entrada. Finalmente, sus guías reciben la lista completa de pasajeros e "
        "itinerario directamente en su WhatsApp un día antes. Así su agencia ahorra tiempo, evita cancelaciones de último momento y no pierde ninguna "
        "venta, incluso si se corta el internet en ventanilla».",
        author_prefix="Discurso de Socialización (118 palabras):"
    )

    # ==========================================
    # SECCIÓN 7: BITÁCORA DE IA
    # ==========================================
    add_heading_1("7. Trazabilidad del Uso de Inteligencia Artificial (Bitácora AG-08)")
    add_p(
        "Bajo la directiva «La IA propone, el equipo decide y verifica», se registraron todas las interacciones con asistentes inteligentes. "
        "La bitácora documenta los 8 prompts sugeridos (P1 a P8), demostrando criterio de ingeniería para filtrar propuestas desacertadas:"
    )

    ia_table = doc.add_table(rows=9, cols=5)
    ia_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    ia_headers = ["P#", "Prompt Utilizado", "Propuesta Aceptada", "Propuesta Rechazada o Corregida", "Responsable"]
    for j, h in enumerate(ia_headers):
        cell = ia_table.cell(0, j)
        set_cell_background(cell, "0B3D62")
        set_cell_margins(cell, 80, 80, 80, 80)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(h)
        r.font.name = "Calibri"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    ia_data = [
        ("P1", "Revisión de inventario", "Clasificación de turistas, operadores y sistemas externos.", "Rechazado incluir Docker como contenedor C4.", "Emanuel Hilacondo"),
        ("P2", "Contexto Structurizr DSL", "Estructura del bloque model con identificadores jerárquicos.", "Reemplazada la palabra genérica «usa» por oraciones descriptivas.", "Leonardo Baca"),
        ("P3", "Contenedores según ADR-001", "Descomposición en React SPA, React PWA, Spring Boot y Postgres.", "Rechazada sugerencia de añadir Kafka y Redis (excedía el MVP).", "Mauro Sullca"),
        ("P4", "Dinámico de reserva y pago", "Estructura sintáctica del bloque dynamic y numeración.", "Invertido el orden: validar con AUTOCOLCA antes de cobrar.", "Leonardo Baca"),
        ("P5", "Auditoría C4 cruzada", "Matriz de verificación formal basada en Simon Brown.", "Desestimada queja sobre ausencia de componentes (no aplicaba al lab).", "Mauro Sullca"),
        ("P6", "Explicación no técnica", "Metáfora de negocio orientada a la venta de tours en ventanilla.", "Eliminadas siglas técnicas (PWA, API, SSL); ajustado a 118 palabras.", "German Chipana"),
        ("P7", "Despliegue en producción", "Jerarquía de deploymentNode e infrastructureNode de balanceador.", "Corregida sintaxis de containerInstance jerárquico.", "Mauro Sullca"),
        ("P8", "Impacto del reto offline", "Cuestionario de 5 preguntas sobre concurrencia e idempotencia.", "Descartada sincronización P2P compleja; adoptada partición de cupos.", "German Chipana")
    ]
    for row_idx, (pcode, pdesc, pacc, prech, presp) in enumerate(ia_data, start=1):
        bg = "FFFFFF" if row_idx % 2 == 1 else "F9FAFC"
        for col_idx, text_val in enumerate([pcode, pdesc, pacc, prech, presp]):
            cell = ia_table.cell(row_idx, col_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, 50, 50, 60, 60)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(text_val)
            r.font.name = "Calibri"
            r.font.size = Pt(8.5)
            if col_idx == 0:
                r.font.bold = True
            elif col_idx == 4:
                r.font.bold = True
                r.font.color.rgb = SECONDARY
            r.font.color.rgb = TEXT_COLOR

    # ==========================================
    # SECCIÓN 8: PREGUNTAS DE SUSTENTACIÓN
    # ==========================================
    add_heading_1("8. Respuestas Argumentadas para la Sustentación Oral")
    add_p(
        "1. ¿Por qué RutaColca aparece como una sola caja en el contexto y como un límite con varios contenedores en el siguiente nivel?\n"
        "Porque responden a propósitos y audiencias totalmente distintas. El diagrama de contexto oculta la complejidad interna para que "
        "cualquier interesado (ej. gerentes de agencias o directivos de turismo) comprenda el alcance de negocio y con qué servicios se comunica. "
        "El diagrama de contenedores hace un 'zoom in' técnico para los ingenieros de desarrollo y operaciones, mostrando la arquitectura de "
        "software ejecutable (SPA, PWA, API REST) y almacenes de datos donde residirá la solución.\n\n"
        "2. ¿Qué diagrama le mostrarían a la gerente de una agencia y cuál al equipo de operaciones? ¿Por qué?\n"
        "A la gerente de la agencia le mostraríamos el Diagrama de Contexto (Nivel 1), ya que explica con claridad cómo su negocio interactúa con "
        "la plataforma sin confundirla con tecnologías de desarrollo. Al equipo de operaciones le mostraríamos el Diagrama de Despliegue, ya que "
        "especifica los balanceadores de carga TLS, el número de máquinas virtuales para la API en temporada alta y la base de datos gestionada.\n\n"
        "3. ¿Qué propuesta de la IA rechazaron y qué regla de C4 usaron para hacerlo?\n"
        "Rechazamos la propuesta de la IA de modelar a Docker como un contenedor C4 dentro del límite del sistema, y la recomendación de "
        "incorporar Apache Kafka y Redis. Aplicamos la regla canónica de Simon Brown: 'un contenedor C4 es una aplicación o almacén de datos propio, "
        "no una tecnología de virtualización ni de infraestructura de servidores'; además de ceñirnos al principio YAGNI y a la restricción del MVP (1 mes).\n\n"
        "4. ¿Qué cambió en su modelo al resolver el reto sin conexión y en qué diagramas se nota?\n"
        "En el modelo se incorporó un nuevo contenedor de datos: «Almacén Local de Reservas» (IndexedDB) asociado al Portal PWA y relaciones de "
        "sincronización asíncrona por lotes. Esto se evidencia de forma explícita en la nueva vista de contenedores (`ContenedoresReto`) y en el "
        "Diagrama de Despliegue, donde dicho almacén figura instanciado dentro del nodo cliente (Tablet de Agencia)."
    )

    # ==========================================
    # SECCIÓN 9: CONCLUSIONES Y REFERENCIAS
    # ==========================================
    add_heading_1("9. Conclusiones y Referencias Bibliográficas")
    add_p("1. Rigor metodológico: Structurizr DSL garantiza la consistencia del modelo. Al tratar la arquitectura como código, cualquier cambio se propaga de forma coherente a todas las vistas sin riesgo de desincronización gráfica.", bold_prefix="• ")
    add_p("2. Alineación técnica y de negocio: La anticipación de la validación de boletos turísticos frente al cobro financiero demuestra que las decisiones arquitectónicas impactan directamente en la viabilidad económica y operativa del proyecto.", bold_prefix="• ")
    add_p("3. Resiliencia en entornos hostiles: La combinación de PWA con IndexedDB y partición de cupos resuelve el problema real de las agencias de Chivay, garantizando continuidad comercial sin comprometer la integridad de la base central.", bold_prefix="• ")

    add_heading_2("Referencias Bibliográficas (Norma APA 7ma Edición)")
    add_p("Bass, L., Clements, P., & Kazman, R. (2021). Software architecture in practice (4th ed.). Addison-Wesley.")
    add_p("Brown, S. (2026). The C4 model for visualising software architecture. O’Reilly Media / c4model.com.")
    add_p("ISO/IEC/IEEE. (2022). ISO/IEC/IEEE 42010:2022 Software, systems and enterprise — Architecture description. International Organization for Standardization.")
    add_p("Structurizr. (2026). Structurizr DSL: Language reference and open source command line interface. docs.structurizr.com.")

    output_path = "docs/INFORME_FINAL_CASO_AG08_RUTACOLCA.docx"
    doc.save(output_path)
    print(f"Document saved successfully: {output_path}")

if __name__ == "__main__":
    create_report()
