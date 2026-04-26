# Ejemplos de Plantilla ARCA

4 ejemplos prácticos de integración de ARCA en diferentes escenarios.

## 1. CLI Simple (`cli-simple.py`)

**Propósito:** Generar una factura desde línea de comandos sin interfaz web.

**Caso de uso:** Desarrollador que quiere automatizar la generación de facturas en un script o cron job.

**Características:**
- Carga variables de entorno (CUIT, certificado, clave)
- Solicita CAE a ARCA
- Genera PDF
- Manejo elegante de errores
- Muestra CAE, número y vencimiento

**Líneas:** ~50

**Ejecución:**
```bash
# Configurar variables de entorno
export ARCA_CUIT="30-12345678-9"
export ARCA_CERT_PATH="certs/certificado.crt"
export ARCA_KEY_PATH="certs/clave_privada.key"
export ARCA_HOMOLOGACION="true"

# Ejecutar
python3 cli-simple.py
```

**Salida esperada:**
```
INFO - Paso 1: Inicializando cliente ARCA...
INFO - ✓ Cliente ARCA listo (Homologación)
INFO - Paso 2: Solicitando CAE a ARCA...
INFO - ✓ CAE obtenido: 12345678901234
INFO - FACTURA GENERADA EXITOSAMENTE
INFO - CAE: 12345678901234
INFO - Vto CAE: 30042026
```

---

## 2. Integración Django (`integracion-django.py`)

**Propósito:** Integrar ARCA en un modelo Django con auto-generación de CAE.

**Caso de uso:** Aplicación Django que gestiona facturas de clientes.

**Características:**
- Modelo `Comprobante` con campos de cliente, monto, fecha
- Método `generar_cae()` que solicita CAE a ARCA
- Signal handler para auto-generar CAE al crear comprobante
- Validación de estado (borrador → aprobado → error)
- Método `puede_emitirse()` para verificar CAE válido
- Manejo de errores y logging

**Líneas:** ~80

**Uso en Django Shell:**
```python
from invoices.models import Comprobante
from datetime import date

# Crear comprobante (dispara signal → auto-genera CAE)
comprobante = Comprobante.objects.create(
    cliente="Acme Corp",
    monto=2500.00,
    fecha=date.today(),
    tipo_comprobante=1  # Factura A
)

print(f"CAE: {comprobante.cae}")
print(f"Status: {comprobante.status}")

# Filtrar por status
aprobados = Comprobante.objects.filter(status="aprobado")

# Verificar si puede emitirse
if comprobante.puede_emitirse():
    print("Listo para emitir")
```

**Configuración en Django:**
```python
# settings.py
ARCA_CUIT = "30-12345678-9"
ARCA_CERT_PATH = os.path.join(BASE_DIR, "certs/certificado.crt")
ARCA_KEY_PATH = os.path.join(BASE_DIR, "certs/clave_privada.key")
ARCA_HOMOLOGACION = True
```

**Opciones de status:**
- `borrador` - Recién creado, sin CAE
- `pendiente_cae` - En proceso de solicitud
- `aprobado` - CAE obtenido exitosamente
- `error` - Falló la solicitud a ARCA

---

## 3. Procesamiento por Lotes (`batch-csv.py`)

**Propósito:** Procesar múltiples facturas desde archivo CSV.

**Caso de uso:** PyME que necesita generar 50+ facturas en una sesión.

**Características:**
- Lee CSV con: empresa, CUIT, monto, descripción
- Procesa cada fila y solicita CAE
- Reintentos automáticos (por defecto 2)
- Indicador de progreso en consola
- Reporte JSON con resultados (éxito/error)
- Resumen final con tasa de éxito

**Líneas:** ~100

**CSV esperado** (`facturas.csv`):
```csv
empresa,cuit,monto,descripcion
"Acme Corp","30-70000000-5",1500.00,"Servicios consultoría"
"Tech Solutions","20-12345678-9",2000.50,"Implementación"
"Premium Services","23-98765432-1",500.00,"Soporte técnico"
```

**Ejecución:**
```bash
python3 batch-csv.py facturas.csv
```

**Salida esperada:**
```
Leyendo archivo: facturas.csv
✓ 3 facturas encontradas
[====================] 100%

RESUMEN DE PROCESAMIENTO
Total procesadas:         3
Exitosas:                 3 ✓
Fallidas:                 0 ✗
Reintentos realizados:    0
Tasa de éxito:          100.0%
Reporte guardado en: output/reporte_facturas_20260426_153000.json
```

**Reporte JSON** (`reporte_facturas_20260426_153000.json`):
```json
{
  "total": 3,
  "exitosos": 3,
  "fallidos": 0,
  "reintentos": 0,
  "timestamp": "2026-04-26T15:30:00",
  "detalles": [
    {
      "fila": 1,
      "empresa": "Acme Corp",
      "monto": 1500.0,
      "status": "éxito",
      "intento": 1
    }
  ]
}
```

---

## 4. PDF Personalizado (`custom-pdf.py`)

**Propósito:** Personalizar template de PDF con branding corporativo.

**Caso de uso:** Empresa con requisitos visuales específicos (colores, logo, layout).

**Características:**
- Subclasea `GeneradorPDFFactura`
- Cambia colores (azul corporativo en lugar de rojo)
- Header personalizado con logo
- Tabla de items con zebra striping (filas alternadas)
- Footer con datos de empresa y banco
- Margins reducidos para más contenido

**Líneas:** ~120

**Personalizaciones:**
- `COLOR_PRIMARIO = #0066CC` (azul corporativo)
- `COLOR_SECUNDARIO = #003399` (azul oscuro)
- `COLOR_ACENTO = #99CCFF` (azul claro)
- Header con logo a la izquierda
- Tabla items con 4 columnas (Descripción, Cantidad, P.U., Subtotal)
- Footer con teléfono, website, email, datos bancarios

**Uso:**
```python
generador = GeneradorPDFFacturaPersonalizado(
    output_dir="./output",
    logo_url="https://empresa.com/logo.png"
)

datos_factura = {
    "numero": "0001-00000123",
    "cae": "12345678901234",
    "razon_social": "Empresa S.A.",
    "cliente_razon_social": "Cliente SRL",
    "items": [
        {
            "descripcion": "Servicio A",
            "cantidad": 10,
            "precio_unitario": 150.00,
            "subtotal": 1500.00
        }
    ],
    "total_neto": 1500.00,
    "total_iva": 315.00,
    "total": 1815.00
}

pdf_path = generador.generar_factura(datos_factura)
print(f"PDF: {pdf_path}")
```

**Métodos personalizables:**
- `_header_table_personalizado()` - Header con fondo azul
- `_tabla_items_personalizada()` - Tabla con alternancia de colores
- `_footer_personalizado()` - Footer con info de empresa

---

## Requisitos Comunes

Todos los ejemplos requieren:

1. **Dependencias Python:**
   ```bash
   pip install arca-arg python-dotenv reportlab sqlalchemy psycopg2-binary
   ```

2. **Certificados AFIP:**
   - `certs/certificado.crt` (certificado X.509)
   - `certs/clave_privada.key` (clave privada)

3. **Variables de entorno** (`.env`):
   ```bash
   ARCA_CUIT=30-12345678-9
   ARCA_CERT_PATH=certs/certificado.crt
   ARCA_KEY_PATH=certs/clave_privada.key
   ARCA_HOMOLOGACION=true
   OUTPUT_DIR=./output
   ```

4. **Estructura de directorios:**
   ```
   plantilla-arca/
   ├── src/
   │   ├── arca/
   │   │   └── client.py
   │   ├── pdf/
   │   │   └── generator.py
   │   └── config.py
   ├── certs/
   │   ├── certificado.crt
   │   └── clave_privada.key
   ├── examples/
   │   ├── cli-simple.py
   │   ├── integracion-django.py
   │   ├── batch-csv.py
   │   ├── custom-pdf.py
   │   └── README.md
   └── .env
   ```

---

## Cuándo Usar Cada Ejemplo

| Caso | Ejemplo | Razón |
|------|---------|-------|
| Script automatizado, cron job | `cli-simple.py` | Interfaz simple, sin dependencias de web framework |
| App Django existente | `integracion-django.py` | Usa ORM, signals, settings de Django |
| Procesar muchas facturas | `batch-csv.py` | Manejo de lotes, reintentos, reportes |
| Branding corporativo | `custom-pdf.py` | Personalización visual, colores, logo |

---

## Troubleshooting

**Problema:** `ModuleNotFoundError: No module named 'arca_arg'`
- Solución: `pip install arca-arg`

**Problema:** `FileNotFoundError: Certificado o clave no encontrados`
- Solución: Verificar rutas en `ARCA_CERT_PATH` y `ARCA_KEY_PATH`

**Problema:** `Error: CUIT no configurado`
- Solución: Agregar `ARCA_CUIT` a `.env` o variables de entorno

**Problema:** Falla conexión a ARCA en homologación
- Solución: Verificar que `ARCA_HOMOLOGACION=true` en `.env`

---

## Referencias

- Documentación ARCA: https://www.afip.gob.ar/
- arca-arg: https://github.com/paxcematica/arca-arg
- ReportLab: https://www.reportlab.com/
- Django: https://docs.djangoproject.com/
