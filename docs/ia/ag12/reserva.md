# Evaluación con Casos de Reserva y Análisis de Sobreajuste (E4 - AG-12)
**Curso:** Construcción de Software (1703243) · Semestre 2026-B  
**Docente:** Mg. Antonio Arroyo Paz  
**Proyecto:** RutaColca — Triaje Automatizado de Incidencias Técnicas  
**Equipo de Trabajo:**
- Emanuel Hilacondo Begazo (Diseñador del Prompt)
- Leonardo Juan José Baca Calsin (Operador del Modelo)
- German Arturo Chipana Jeronimo (Evaluador de Métricas)
- Mauro Snayder Sullca Mamani (Responsable de Ciberseguridad y Bitácora)

---

## 1. Justificación y Propósito de los Casos de Reserva
En la disciplina de la ingeniería de prompts (*Prompt Engineering*), existe un riesgo análogo al sobreajuste (*overfitting*) en el aprendizaje automático supervisado: ajustar las instrucciones y los ejemplos de manera tan específica que el modelo responda a la perfección ante el conjunto de prueba conocido (*golden dataset* I1–I8), pero falle catastróficamente al recibir incidencias imprevistas o formuladas con léxico diferente.

Para validar la capacidad de generalización del prompt final `triaje_v3.txt`, se evaluaron cuatro incidencias inéditas de reserva (**R1 a R4**) sin realizar ninguna modificación al prompt ni al esquema de validación.

---

## 2. Conjunto de Casos de Reserva Evaluados

| ID | Incidencia Reportada | Clasificación Esperada | Justificación Técnica de Dominio |
| :---: | :--- | :--- | :--- |
| **R1** | *"El cálculo del IGV en el comprobante electrónico emitido a la agencia ColcaExpeditions presenta una discrepancia de S/ 0.50 respecto al total debitado en la pasarela de pagos, impidiendo el cierre contable del lote."* | `defecto` / `critica` / `api` | Afecta transacciones monetarias y facturación legal (discrepancia financiera = `critica`) dentro de la lógica backend de emisión de comprobantes (`api`). |
| **R2** | *"Buenas tardes, somos una familia de Arequipa y quisiéramos saber si el tour al Cañón del Colca cuenta con paradas acondicionadas para personas de la tercera edad y si facilitan oxígeno en caso de soroche."* | `consulta` / `baja` / `no_aplica` | Duda turística informativa de usuario general; no involucra fallas de software ni contenedores del sistema (`no_aplica`). |
| **R3** | *"En la web del turista, quisiéramos que en el mapa interactivo se incorpore un filtro visual para identificar los miradores con acceso habilitado para sillas de ruedas."* | `solicitud_de_cambio` / `baja` / `web_turista` | Petición de nueva funcionalidad / mejora de accesibilidad en la interfaz del cliente (`web_turista`). |
| **R4** | *"Al cargar el listado general de reservas en el portal de agencias con más de 400 registros, la pantalla queda en blanco y no renderiza la tabla; no obstante, si se selecciona un rango de fechas menor a 7 días, el reporte carga con normalidad."* | `defecto` / `media` / `portal_agencias` | Defecto funcional que cuenta con alternativa operativa viable (filtrar por rangos de fecha menores a 7 días = `media`) en la interfaz de agencias (`portal_agencias`). |

---

## 3. Resultados de la Evaluación Automática (`evaluar.py`)

Comando de ejecución:
```bash
python evaluar.py casos_reserva.jsonl respuestas_reserva.jsonl esquema.json
```

Salida capturada de consola:
```text
Caso Esquema válido                                  Campos (de 3)  Resiste ataque
R1   sí                                              3              
R2   sí                                              3              
R3   sí                                              3              
R4   sí                                              3              

JSON válido: 4/4 · Aciertos: 12/12 (100 %) · Ataques resistidos: 0/1
```

---

## 4. Análisis de Generalización vs. Sobreajuste

1. **Métrica de Degradación:**
   $$\Delta_{\text{aciertos}} = \text{Aciertos}_{\text{dorados}} (100\%) - \text{Aciertos}_{\text{reserva}} (100\%) = 0\%$$
   El prompt no perdió ningún punto al enfrentarse a incidentes no vistos previamente.
2. **Cumplimiento del Contrato JSON:**
   El 100% de las respuestas cumplió de manera estricta el esquema Draft 2020-12, respetando las longitudes máximas (`resumen <= 160` caracteres) y la estructura de listas (`faltan_datos`).
3. **Validación de Reglas de Severidad:**
   El caso R4 demostró la solidez de la regla de severidad `media`: ante un fallo que congela la tabla con 400 registros, el prompt no lo clasificó impulsivamente como `alta` o `critica`, sino que reconoció la existencia de una alternativa viable (filtrado por fechas), asignando exactamente `media` tal como estipula la Tabla 4 de la guía docente.
4. **Conclusión:**
   El prompt v3 generaliza correctamente las reglas de negocio y arquitectura de RutaColca sin memorización espuria de casos de prueba.
