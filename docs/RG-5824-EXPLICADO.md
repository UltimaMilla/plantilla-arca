# RG 5824 Explicado - Guía Completa

La Resolución General 5824 es la normativa argentina que obliga facturación electrónica inmediata. Esta guía explica en lenguaje simple qué significa, quién está obligado y cómo Plantilla ARCA lo resuelve.

---

## ¿Quién Está Obligado?

La RG 5824 AFIP obliga a emitir **facturas electrónicas a través de ARCA** a:

### Profesionales Independientes

- **Abogados**: Consultoría legal, asesoría
- **Contadores Públicos**: Auditoría, asesoramiento contable
- **Escribanos**: Instrumentación de actos jurídicos
- **Ingenieros**: Consultoría, proyectos, inspección
- **Arquitectos**: Diseño, supervisión de obras
- **Médicos**: Consulta, procedimientos (no aplica si es paciente con cobertura)
- **Dentistas**: Tratamientos dentales
- **Psicólogos**: Sesiones de psicoterapia
- **Otros profesionales**: Maestros, nutricionistas, kinesiólogos, etc.

### Empresas y PyMEs

- **Pequeñas empresas (PyMEs)**: Hasta ciertos montos de facturación
- **Sociedades anónimas**: Todas sin excepción
- **Sociedades de hecho**: Con regulación especial

### No obligados

- Monotributistas (usan otros sistemas)
- Exentos de IVA (instituciones sin fines de lucro)
- Ciertos regímenes especiales (consultar AFIP)

**Verificar tu situación**: https://www.afip.gob.ar/cuit/

---

## Conceptos Técnicos Explicados

### ¿Qué es ARCA?

**ARCA = Sistema de Autorización de Comprobantes Electrónicos**

En argot AFIP, es el sistema web que autoriza que tus facturas sean legales. Antes emitías facturas en papel. Ahora:

```
Tú generas factura digitalmente → ARCA la autoriza → Es válida legalmente
```

**Características:**
- Operado por AFIP (Administración Federal de Ingresos Públicos)
- Responde en segundos
- Requiere conexión a internet
- Usa protocolo SOAP + certificados digitales

### ¿Qué es CAE?

**CAE = Código de Autorización Electrónica**

Es un número único que AFIP te da que significa: "Esta factura es válida". Sin CAE, la factura no tiene valor legal.

**Ejemplo real:**
```
Factura N° 1-5
Sin CAE = Papel sin valor legal
Con CAE = Documento válido fiscalmente
```

**Características del CAE:**
- 14 dígitos
- Válido durante 30 días (entonces vence)
- Único por factura
- Registra automáticamente en los servidores AFIP

**Ejemplo:**
```
CAE: 12345678901234
Vencimiento: 2024-07-20 (30 días después de emisión)
```

### ¿Qué es WSAA?

**WSAA = Web Service de Autorización de Afiliados**

Traducciendo: Es el servicio que AFIP usa para verificar que TÚ eres quien dices ser.

**Flujo:**
```
1. Conectas a WSAA con tu certificado digital
2. WSAA verifica: "¿Eres realmente Juan Pérez CUIT 20-12345678-9?"
3. WSAA te da un TOKEN (credencial temporal)
4. Usas ese TOKEN para pedir CAE a ARCA
```

Sin WSAA, cualquiera podría emitir facturas a tu nombre.

### ¿Qué es SOAP?

**SOAP = Protocolo de Servicios Web**

Es solo la forma en que se comunican las computadoras. Como si fuera el idioma entre tú y AFIP.

No necesitas conocer SOAP: **Plantilla ARCA lo maneja automáticamente.**

---

## Flujo Completo de Emisión de Facturas

### Paso a Paso (Manual vs Plantilla ARCA)

#### SIN Plantilla ARCA (tedioso)

```
1. Descargas SDK de AFIP (complicado)
2. Instalas Java o .NET
3. Generas certificado digital (costoso)
4. Conectas a WSAA manualmente
5. Obtienes TOKEN
6. Conectas a ARCA con TOKEN
7. Solicitas CAE
8. Genera PDF manualmente
9. Arma QR con datos de ARCA
10. Envía al cliente
```

**Tiempo:** 2-3 horas para configurar  
**Conocimiento requerido:** Desarrollo backend

#### CON Plantilla ARCA (simple)

```
1. Configuras .env con tu CUIT y certificado
2. Ejecutas: docker-compose up
3. Entras a http://localhost:8501
4. Completas formulario (datos factura)
5. Haces clic en "Generar Factura"
6. ¡CAE + PDF en 5 segundos!
7. Descargas o envías por email
```

**Tiempo:** 5 minutos setup, 10 segundos por factura  
**Conocimiento requerido:** Ninguno

---

## Detalles de Puntos de Venta y Números de Comprobante

### Punto de Venta (PV)

Es un identificador que AFIP asigna a cada sucursal o lugar donde generas comprobantes.

**Ejemplo:**
- Punto de Venta 1 = Oficina central en CABA
- Punto de Venta 2 = Sucursal en Rosario
- Punto de Venta 3 = Sucursal en Córdoba

Cada PV tiene su propia secuencia de números.

**Formato:**
- **4 dígitos**, ceros a izquierda: `0001`, `0002`, etc.
- O simplemente: `1`, `2`, `3`, etc. (Plantilla ARCA lo formatea)

**Rango permitido:** 1 a 9999

### Número de Comprobante

Es el número secuencial de cada factura dentro de un Punto de Venta.

**Ejemplo:**
```
Punto de Venta: 1, Número: 1  → Factura "1-1"
Punto de Venta: 1, Número: 2  → Factura "1-2"
Punto de Venta: 1, Número: 50 → Factura "1-50"
Punto de Venta: 2, Número: 1  → Factura "2-1" (nueva secuencia en otro PV)
```

**Requisitos:**
- Números consecutivos (no puedes saltar números)
- Sin duplicados en el mismo PV
- AFIP lo valida automáticamente (rechaza duplicados)
- Rango: 1 a 99.999.999

**¿Qué pasa si saltas números?**
```
Emites: 1-1, 1-2, 1-4 (saltas 1-3)
ARCA rechaza: "Número 1-4 es inválido, esperaba 1-3"
```

Plantilla ARCA gestiona esto automáticamente desde la base de datos.

---

## Validaciones que ARCA Realiza

Cuando solicitas un CAE, ARCA valida automáticamente:

### Validación de Emisor

| Validación | Qué chequea | Resultado |
|------------|------------|-----------|
| CUIT válido | Tu CUIT existe en AFIP | Si falla: rechaza |
| Certificado válido | Certificado no expirado | Si falla: rechaza |
| Inscripción actualizada | Estás inscripto en RG 5824 | Si falla: rechaza |
| Deudas | No tienes deudas fiscales graves | Si falla: rechaza |

### Validación de Comprobante

| Validación | Qué chequea | Resultado |
|------------|------------|-----------|
| Tipo válido | Es "Factura A", "B" o "C" | Si falla: rechaza |
| Número secuencial | Número es el siguiente esperado | Si falla: rechaza |
| Punto de Venta válido | PV está registrado en AFIP | Si falla: rechaza |
| Importe válido | Monto es lógico (> 0, formato correcto) | Si falla: rechaza |
| Fecha válida | Fecha no es futura, no muy antigua | Si falla: rechaza |
| Condición IVA correcta | Receptos válido para tu condición | Si falla: rechaza |

### Validación de Receptor

| Validación | Qué chequea | Resultado |
|-----------|------------|-----------|
| CUIT/DNI válido | Receptor existe o es válido | Si falla: rechaza o aviso |
| Condición IVA válida | Es "Responsable Inscripto", etc. | Si falla: rechaza |

**Ejemplo de rechazo real:**

```
Solicitas CAE para:
Factura A, PV 1, Número 15, Importe $5000

Pero tu última fue: PV 1, Número 13

ARCA responde:
❌ Error: Número secuencial inválido
   Esperaba: 14
   Recibió: 15
```

---

## Tipos de Comprobantes

La RG 5824 permite emitir tres tipos de facturas:

### Factura A (Factura Completa)

- **Para quién:** Clientes "Responsables Inscriptos" en IVA
- **Qué incluye:** Número de comprobante, IVA discriminado, datos completos
- **Ejemplo:**
  ```
  Factura A N° 1-123
  Cliente: CUIT 20-12345678-9, "ABC S.A."
  Importe neto: $1000
  IVA 21%: $210
  Total: $1210
  ```

### Factura B (Factura para No Responsables)

- **Para quién:** Clientes "Monotributistas" o "Consumidor Final"
- **Qué incluye:** Número de comprobante, IVA incluido, menos datos
- **Ejemplo:**
  ```
  Factura B N° 1-50
  Cliente: "Juan García"
  Monto total: $1210 (IVA incluido, no discriminado)
  ```

### Factura C (Recibo)

- **Para quién:** Clientes sin CUIT, consumidor anónimo
- **Qué incluye:** Número, datos mínimos, sin IVA discriminado
- **Ejemplo:**
  ```
  Factura C N° 1-100
  Cliente: No especificado
  Monto: $100
  ```

**Validación automática:**
```
Tu cliente es Monotributista
Intentas emitir Factura A
ARCA rechaza: "Debes usar Factura B para Monotributistas"
```

---

## Cambios Clave que RG 5824 Obliga

| Antes | Ahora (RG 5824) |
|-------|----------------|
| Emitías facturas en papel o PDF | Debes registrar en ARCA antes de usar |
| AFIP auditaba después (semanas/meses) | AFIP valida en tiempo real (segundos) |
| Podías cambiar números fácilmente | Números estrictamente secuenciales |
| Guardaba facturas en tu archivo | AFIP guarda registro permanente |
| Facturación opcional para algunos | Obligatoria para profesionales |
| Costo cero | Costo cero (pero requiere certificado digital ~$100-300/año) |

---

## Certificado Digital AFIP

### ¿Qué es?

Una "credencial electrónica" que AFIP usa para verificar tu identidad. Es como tu DNI, pero digital.

### Características

- **Formato:** Archivo `.pem` (certificado + clave privada)
- **Validez:** 1-2 años
- **Costo:** $0-300 ARS según proveedor
- **Obligatorio:** Sí, para usar ARCA
- **Reutilizable:** Entre múltiples aplicaciones

### Dónde conseguir

1. **Portal CUIT de AFIP**: https://www.afip.gob.ar
2. **Entidades certificantes autorizadas**:
   - Sindicato de Profesionales de Informática
   - Banco de Galicia
   - Otros proveedores

### Proceso

```
1. Solicitas en AFIP
2. Completas datos personales
3. Descargas o recibes por email
4. Importas en tu aplicación (Plantilla ARCA)
5. Listo para emitir facturas
```

---

## Comparación: Plantilla ARCA vs Alternativas

| Característica | Plantilla ARCA | e-Factura G | Software pago |
|---|---|---|---|
| Costo | Gratis | Depende | $100-500/mes |
| Código abierto | Sí | No | No |
| Customizable | Sí | No | Limitado |
| Control sobre datos | Total | AFIP controla | Proveedor |
| Facilidad de instalar | Muy fácil | Fácil | Muy fácil |
| Funciona sin internet | No | No | No |
| Soporte | Comunidad | AFIP | Empresa |

---

## Validación Práctica: Ejemplo Real

Imaginemos que emites una factura con Plantilla ARCA:

### Tu entrada

```json
{
  "cuit": "20123456789",
  "razon_social": "Mi Estudio Jurídico",
  "cliente_cuit": "20987654321",
  "cliente_nombre": "ABC S.A.",
  "tipo_comprobante": "Factura A",
  "punto_venta": 1,
  "numero": 50,
  "fecha": "2024-04-26",
  "importe_neto": 1000,
  "importe_iva": 210,
  "importe_total": 1210
}
```

### ARCA valida

```
✓ CUIT emisor válido
✓ Certificado no expirado
✓ Inscripto en RG 5824
✓ Tipo Factura A permitido para tu condición
✓ Número secuencial válido (era 49, ahora 50)
✓ Punto de Venta 1 existe
✓ Importe > 0
✓ Fecha válida (no futura, no muy antigua)
✓ CUIT cliente válido
✓ Cliente es Responsable Inscripto (✓ para Factura A)
✓ IVA discriminación correcta
```

### Respuesta AFIP

```json
{
  "cae": "12345678901234",
  "vencimiento": "2024-05-26",
  "numero": 50,
  "estado": "A"
}
```

✓ **Factura válida, lista para imprimir y enviar**

---

## Fallos Comunes y Soluciones

| Problema | Causa | Solución |
|----------|-------|----------|
| "Certificado expirado" | Tu certificado AFIP vence el día siguiente | Renovar certificado en AFIP |
| "CUIT no inscripto en RG 5824" | No completaste inscripción en AFIP | Inscribirse en https://www.afip.gob.ar |
| "Número secuencial inválido" | Saltaste números o emitiste duplicado | Verificar base de datos Plantilla ARCA |
| "Tipo comprobante inválido" | Cliente es Monotributista, usaste Factura A | Cambiar a Factura B |
| "Timeout de conexión" | Servidor ARCA caído o conexión lenta | Reintentar en 30 segundos |

---

## Recursos Oficiales AFIP

- **Portal CUIT**: https://www.afip.gob.ar/cuit/
- **Resolución 5824**: https://www.afip.gob.ar/genericos/normativas/
- **Consultas**: https://www.afip.gob.ar/contacto
- **Estado de servicios**: https://www.afip.gob.ar/servicios/

---

## Cumplimiento Legal

Usar Plantilla ARCA significa:

✓ Cumples RG 5824 AFIP  
✓ Facturas válidas legalmente  
✓ Registro automático en AFIP  
✓ Protección frente a auditoría  
✓ Sin multas por incumplimiento  

**Multa por incumplimiento**: $1000-100.000+ según gravedad

---

## Resumen Ejecutivo

| Concepto | Significado |
|----------|-------------|
| **RG 5824** | Ley que obliga facturación electrónica en Argentina |
| **ARCA** | Sistema de AFIP que autoriza facturas electrónicamente |
| **CAE** | Código que autoriza tu factura, válido 30 días |
| **WSAA** | Servicio que verifica tu identidad ante AFIP |
| **Certificado Digital** | Credencial electrónica que prueba quién eres |
| **Punto de Venta** | Sucursal/lugar donde generas comprobantes |
| **Número secuencial** | Identificador único de factura por punto de venta |
| **Plantilla ARCA** | Software que automatiza todo esto |

---

**¿Más preguntas?** Lee [API.md](./API.md) para ejemplos técnicos o [INSTALACION.md](./INSTALACION.md) para comenzar.
