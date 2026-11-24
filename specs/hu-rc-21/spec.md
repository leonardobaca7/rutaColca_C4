# HU-RC-21 · Calcular el reembolso por cancelación

Como **agente de soporte** de RutaColca quiero **calcular el reembolso de una reserva cancelada**
para **proponer un monto correcto y saber si debe derivarlo a un supervisor**.

## Reglas de Negocio
- Cancelación por **clima** u **operador**: se devuelve el 100 %.
- Cancelación del **cliente**:
  - 72 h o más antes del tour ($\ge 72$ h) $\rightarrow$ 100 %.
  - De 24 h a menos de 72 h ($24 \le \text{horas} < 72$) $\rightarrow$ 50 %.
  - Menos de 24 h ($< 24$ h) $\rightarrow$ 0 %.
- El monto se calcula en Soles (PEN) con dos decimales, redondeando la mitad exacta hacia arriba (`ROUND_HALF_UP`, por ejemplo S/ 60.125 $\rightarrow$ S/ 60.13).
- Si el monto reembolsado supera el límite de autonomía del agente (`politica.LIMITE_AGENTE`, S/ 300.00), se deriva obligatoriamente a un supervisor (`requiere_supervisor = True`). Si es menor o igual a S/ 300.00, no se deriva.
- Entradas inválidas se rechazan inmediatamente lanzando una excepción `ValueError`:
  - Monto pagado $\le 0$ o $> 10\,000$ PEN.
  - Horas de anticipación negativas ($< 0$).
  - Motivo de cancelación distinto de `"clima"`, `"operador"` o `"cliente"`.

---

## Criterios de Aceptación (Escenarios Gherkin)

```gherkin
# Escenario 1 (Original): Borde de 72 horas exactas
Escenario: cancelación del cliente con 72 horas exactas
  Dado un pago de S/ 120.00
  Cuando el cliente cancela 72 horas antes
  Entonces el reembolso es S/ 120.00 (100 %) y no se deriva

# Escenario 2 (Original): Caso intermedio con redondeo mitad hacia arriba
Escenario: cancelación del cliente con 30 horas
  Dado un pago de S/ 120.25
  Cuando el cliente cancela 30 horas antes
  Entonces el reembolso es S/ 60.13 (50 %) y no se deriva

# Escenario 3 (Original): Cancelación por causas de fuerza mayor con monto superior al límite
Escenario: cancelación por clima de un tour caro
  Dado un pago de S/ 520.00
  Cuando el operador cancela por clima
  Entonces el reembolso es S/ 520.00 (100 %) y se deriva a un supervisor

# Escenario 4 (Nuevo - Paso 1): Borde exacto de 24 horas de anticipación
Escenario: cancelación del cliente con 24 horas exactas
  Dado un pago de S/ 240.00
  Cuando el cliente cancela 24 horas antes
  Entonces el porcentaje es 50 %, el reembolso es S/ 120.00 y no se deriva a un supervisor

# Escenario 5 (Nuevo - Paso 1): Borde exacto del límite del agente (S/ 300.00)
Escenario: cancelación con reembolso exactamente en el límite del agente
  Dado un pago de S/ 300.00
  Cuando el cliente cancela 80 horas antes
  Entonces el reembolso es S/ 300.00 (100 %) y no se deriva a un supervisor

# Escenario 6 (Nuevo - Paso 1): Rechazo estricto de entradas inválidas
Escenario: cancelación con parámetros inválidos o fuera de rango
  Dado un pago de S/ -50.00 o S/ 15000.00 o motivo "lluvia"
  Cuando se solicita el cálculo de reembolso
  Entonces el sistema rechaza la operación lanzando ValueError
```
