# Referencia de API - Plantilla ARCA

Documentación completa de módulos, funciones y ejemplos de uso para integración programática.

---

## Módulos Principales

Plantilla ARCA expone tres módulos principales para integración:

| Módulo | Propósito | Interfaz |
|--------|-----------|----------|
| `src.arca.client` | Conexión a ARCA, obtención de CAE | Python directo |
| `src.pdf.generator` | Generación de PDFs con QR | Python directo |
| `src.web.fastapi_app` | API REST HTTP/JSON | HTTP REST |

---

## Módulo: arca.client

Maneja la comunicación con ARCA Web Services de AFIP para obtener códigos de autorización.

### Clase: ArcaClient

Inicializa la conexión a ARCA con certificados digitales.

**Constructor:**

```python
from src.arca.client import ArcaClient

cliente = ArcaClient(
    cuit="20123456789",              # Tu CUIT (11 dígitos)
    cert_path="./certs/certificado.pem",  # Ruta al certificado
    key_path="./certs/clave.pem",         # Ruta a la clave privada
    homologacion=True                # True para pruebas, False para producción
)
```

**Parámetros:**

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `cuit` | str | Sí | CUIT de tu empresa (11 dígitos sin guiones) |
| `cert_path` | str | Sí | Ruta absoluta al certificado digital AFIP |
| `key_path` | str | Sí | Ruta absoluta a la clave privada |
| `homologacion` | bool | No | Ambiente de pruebas (default: True) |

**Excepciones:**

- `ValueError`: Si CUIT, certificado o clave están vacíos
- `FileNotFoundError`: Si los archivos de certificado no existen
- `RuntimeError`: Si hay error inicializando el cliente ARCA

### Método: solicitar_cae()

Solicita un Código de Autorización Electrónica (CAE) a ARCA.

**Firma:**

```python
def solicitar_cae(
    tipo_comprobante: str = "Factura A",
    importe_total: float = 0.0
) -> dict:
```

**Parámetros:**

| Parámetro | Tipo | Descripción | Ejemplos |
|-----------|------|-------------|----------|
| `tipo_comprobante` | str | Tipo de comprobante a emitir | "Factura A", "Factura B", "Factura C" |
| `importe_total` | float | Monto total en ARS | 1500.00, 10000.50 |

**Retorna:** dict con estructura

```json
{
  "cae": "12345678901234",
  "vencimiento": "2024-07-20",
  "numero": 5,
  "vto": "2024-07-20",
  "estado": "A"
}
```

**Excepciones:**

- `RuntimeError`: Si falla conexión a ARCA
- `ValueError`: Si el CAE es rechazado por validaciones

**Ejemplo de uso:**

```python
try:
    resultado = cliente.solicitar_cae(
        tipo_comprobante="Factura A",
        importe_total=5000.00
    )
    print(f"✓ CAE obtenido: {resultado['cae']}")
    print(f"  Vencimiento: {resultado['vencimiento']}")
except RuntimeError as e:
    print(f"✗ Error: {e}")
```

---

## Módulo: pdf.generator

Genera PDFs profesionales con QR, logo empresarial y validación ARCA.

### Clase: GeneradorPDFFactura

Constructor y métodos para generar facturas en PDF.

**Constructor:**

```python
from src.pdf.generator import GeneradorPDFFactura

generador = GeneradorPDFFactura(output_dir="./output")
```

**Parámetro:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `output_dir` | str | Directorio donde guardar PDFs (se crea si no existe) |

### Método: generar_factura()

Genera una factura en PDF.

**Firma:**

```python
def generar_factura(
    datos: dict,
    cae: str,
    numero: int,
    punto_venta: int = 1
) -> str:
```

**Parámetro `datos` (dict):**

```python
datos = {
    "cuit": "20123456789",
    "razon_social": "Mi Empresa S.A.",
    "domicilio": "Av. Corrientes 1234, CABA",
    "condicion_iva": "Responsable Inscripto",
    "fecha_emision": "2024-04-26",
    "descripcion": "Servicios profesionales",
    "importe_total": 5000.00,
    "logo_url": "data:image/png;base64,..." # o "http://ejemplo.com/logo.png"
}
```

**Parámetros adicionales:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `cae` | str | Código de Autorización obtenido de ARCA |
| `numero` | int | Número secuencial de comprobante |
| `punto_venta` | int | Punto de venta (default: 1) |

**Retorna:** str (ruta al archivo PDF generado)

**Excepciones:**

- `IOError`: Si no puede escribir el archivo
- `ValueError`: Si los datos están incompletos

**Ejemplo:**

```python
resultado = generador.generar_factura(
    datos={
        "cuit": "20123456789",
        "razon_social": "Tu Empresa",
        "domicilio": "Calle 123",
        "condicion_iva": "Responsable Inscripto",
        "fecha_emision": "2024-04-26",
        "descripcion": "Asesoría profesional",
        "importe_total": 3500.00,
        "logo_url": None  # Sin logo
    },
    cae="12345678901234",
    numero=5
)

print(f"✓ PDF guardado: {resultado}")
# Salida: ./output/factura_20123456789_1_5.pdf
```

---

## API REST (FastAPI)

Endpoints HTTP para integración remota con otras aplicaciones.

### Requisito: Iniciar servidor

```bash
uvicorn src.web.fastapi_app:app --reload --port 8000
```

Documentación interactiva: http://localhost:8000/docs

### Endpoint: POST /api/generar-factura

Genera una factura en PDF y obtiene CAE automáticamente.

**Ruta:** `POST /api/generar-factura`

**Request (JSON):**

```json
{
  "cuit": "20123456789",
  "razon_social": "Mi Empresa S.A.",
  "domicilio": "Av. Corrientes 1234, CABA",
  "condicion_iva": "Responsable Inscripto",
  "tipo_comprobante": "Factura A",
  "fecha_emision": "2024-04-26",
  "descripcion": "Servicios profesionales",
  "importe_total": 5000.00,
  "logo_url": "http://ejemplo.com/logo.png"
}
```

**Response (200 OK):**

```json
{
  "ok": true,
  "pdf_url": "http://localhost:8000/output/factura_20123456789_1_5.pdf",
  "cae": "12345678901234",
  "vencimiento_cae": "2024-07-20",
  "error": null
}
```

**Response (400 Bad Request):**

```json
{
  "ok": false,
  "error": "CUIT debe ser válido (11 dígitos)",
  "pdf_url": null,
  "cae": null
}
```

**Códigos de error:**

| Código | Descripción | Solución |
|--------|-------------|----------|
| 400 | Validación fallida (CUIT, importe) | Verifica formato de datos |
| 500 | Error en ARCA o base de datos | Revisa logs: `tail -f logs/api.log` |
| 503 | Servicio ARCA no disponible | Reintenta en 5 minutos |

**Ejemplo cURL:**

```bash
curl -X POST http://localhost:8000/api/generar-factura \
  -H "Content-Type: application/json" \
  -d '{
    "cuit": "20123456789",
    "razon_social": "Mi Empresa",
    "domicilio": "Calle 123",
    "condicion_iva": "Responsable Inscripto",
    "tipo_comprobante": "Factura A",
    "fecha_emision": "2024-04-26",
    "descripcion": "Servicios",
    "importe_total": 5000.00
  }'
```

**Ejemplo Python/requests:**

```python
import requests

payload = {
    "cuit": "20123456789",
    "razon_social": "Mi Empresa",
    "domicilio": "Calle 123",
    "condicion_iva": "Responsable Inscripto",
    "tipo_comprobante": "Factura A",
    "fecha_emision": "2024-04-26",
    "descripcion": "Servicios profesionales",
    "importe_total": 5000.00
}

response = requests.post(
    "http://localhost:8000/api/generar-factura",
    json=payload
)

if response.status_code == 200:
    resultado = response.json()
    print(f"✓ CAE: {resultado['cae']}")
    print(f"  PDF: {resultado['pdf_url']}")
else:
    print(f"✗ Error: {response.json()['error']}")
```

### Endpoint: POST /api/enviar-email

Envía factura PDF por correo.

**Ruta:** `POST /api/enviar-email`

**Request:**

```json
{
  "email_destino": "cliente@ejemplo.com",
  "pdf_path": "./output/factura_20123456789_1_5.pdf",
  "empresa": "Mi Empresa S.A."
}
```

**Response (200 OK):**

```json
{
  "ok": true,
  "mensaje": "Email enviado a cliente@ejemplo.com"
}
```

**Excepciones posibles:**

| Excepción | Causa | Solución |
|-----------|-------|----------|
| `FileNotFoundError` | PDF no existe | Generar factura primero |
| `SMTPAuthenticationError` | Credenciales SMTP inválidas | Verifica `.env` con credenciales email |
| `SMTPException` | Servidor SMTP rechaza email | Verifica límite diario de envíos |

---

## Ciclo Completo: Ejemplo Integrado

Genera factura, obtén CAE, crea PDF y envía por email:

```python
from src.arca.client import ArcaClient
from src.pdf.generator import GeneradorPDFFactura

# 1. Conectar a ARCA
cliente = ArcaClient(
    cuit="20123456789",
    cert_path="./certs/certificado.pem",
    key_path="./certs/clave.pem",
    homologacion=True
)

# 2. Solicitar CAE
cae_response = cliente.solicitar_cae(
    tipo_comprobante="Factura A",
    importe_total=5000.00
)

# 3. Generar PDF
generador = GeneradorPDFFactura()
pdf_path = generador.generar_factura(
    datos={
        "cuit": "20123456789",
        "razon_social": "Mi Empresa",
        "domicilio": "Calle 123",
        "condicion_iva": "Responsable Inscripto",
        "fecha_emision": "2024-04-26",
        "descripcion": "Servicios",
        "importe_total": 5000.00
    },
    cae=cae_response["cae"],
    numero=5
)

# 4. Resultado
print(f"✓ Factura generada con éxito")
print(f"  CAE: {cae_response['cae']}")
print(f"  Vencimiento: {cae_response['vencimiento']}")
print(f"  PDF: {pdf_path}")
```

---

## Validaciones de Entrada

Todas las funciones validan automáticamente:

**CUIT:**
- Debe ser exactamente 11 dígitos
- No puede estar vacío
- Formatos aceptados: `20123456789` o `20-12345678-9`

**Importe:**
- Debe ser > 0
- Máximo 2 decimales
- Ejemplos válidos: `1000.00`, `99.99`, `5000`

**Tipo de comprobante:**
- Solo: `"Factura A"`, `"Factura B"`, `"Factura C"`
- Case-sensitive

**Fecha:**
- Formato: `YYYY-MM-DD` (ISO 8601)
- No puede ser futura
- No puede ser anterior a 30 días

---

## Notas Importantes

- **Homologación vs Producción:** En homologación (testing), usa `homologacion=True`. CAEs de homologación no son válidos en producción
- **Certificados:** Cada cambio de certificado AFIP requiere reiniciar el servicio
- **Limite de CAEs:** ARCA tiene límites de solicitudes por minuto; implementa retry con backoff exponencial
- **Base de datos:** Todos los CAEs y facturas se registran automáticamente en PostgreSQL

---

## Soporte y Recursos

- Especificación AFIP: https://www.afip.gob.ar/
- Portal CUIT: https://www.afip.gob.ar/
- Issues: https://github.com/UltimaMilla/plantilla-arca/issues
