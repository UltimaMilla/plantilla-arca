# 🧾 Plantilla ARCA - Facturación Electrónica Open Source

**Generador automático de facturas electrónicas según RG 5824 AFIP**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

## ¿Qué es?

La RG 5824 obliga a facturación electrónica para directores, abogados, contadores y profesionales. Esta herramienta automatiza TODO:

- ✅ Conexión a ARCA Web Services
- ✅ Solicitud automática de CAE
- ✅ Generación de PDF con QR
- ✅ Persistencia en PostgreSQL
- ✅ Interfaz web (Streamlit)

**Resultado:** De "¿cómo conecto a ARCA?" a "tengo mi factura en PDF" en 2 minutos.

---

## Quick Start

### Con Docker (Recomendado)

```bash
# Clonar
git clone https://github.com/UltimaMilla/plantilla-arca.git
cd plantilla-arca

# Copiar env
cp .env.example .env

# Levantar
docker-compose up

# Acceder a http://localhost:8501
```

### Sin Docker

```bash
# Requisitos
python 3.10+
postgresql
pip install -r requirements.txt

# Config
cp .env.example .env
# Editar .env con tus datos

# Ejecutar
streamlit run src/web/streamlit_app.py
```

---

## Estructura

```
plantilla-arca/
├── src/
│   ├── config.py           # Configuración
│   ├── models.py           # Modelos SQLAlchemy
│   ├── arca/
│   │   └── client.py       # Cliente ARCA (corazón)
│   ├── pdf/
│   │   └── generator.py    # Generador PDF + QR
│   └── web/
│       └── streamlit_app.py # Interfaz web
├── tests/                  # Tests
├── docs/                   # Documentación
├── docker-compose.yml      # Stack completo
├── Dockerfile              # Imagen Docker
├── requirements.txt        # Dependencias
└── certs/                  # Certificados AFIP
```

---

## Stack Técnico

| Componente | Herramienta |
|-----------|-----------|
| **Lenguaje** | Python 3.10+ |
| **Cliente ARCA** | arca_arg |
| **BD** | PostgreSQL |
| **PDF** | ReportLab + PyQRCode |
| **Web** | Streamlit |
| **Contenedores** | Docker Compose |

---

## Requisitos Previos

### Certificado AFIP (Gratis pero tarda 3-5 días)

1. Ve a https://www.afip.gob.ar → Web Services
2. Solicita certificado con tu CUIT
3. Descargá: `certificado.crt` y `clave_privada.key`
4. Copia a: `certs/`

### Variables de Entorno

```bash
cp .env.example .env
# Editar:
ARCA_CUIT=tu_cuit_sin_guiones
ARCA_CERT_PATH=certs/tu_certificado.crt
ARCA_KEY_PATH=certs/tu_clave.key
```

---

## Uso

### Interfaz Web (Recomendado)

```bash
streamlit run src/web/streamlit_app.py
# http://localhost:8501
```

Cargá los datos del comprobante y presioná "Generar Factura".

### CLI (Para automatización)

```bash
python src/main.py --cuit 20123456789 --datos datos.json --output factura.pdf
```

### Código Python (Para integración)

```python
from src.arca.client import ArcaClient
from src.pdf.generator import GeneradorPDFFactura

cliente = ArcaClient()
cae, vto = cliente.solicitar_cae(
    tipo_comprobante=6,
    punto_venta=1,
    numero=1,
    fecha_emision="20260426",
    importe_neto=100.0,
    importe_iva=21.0,
    importe_total=121.0,
)

generador = GeneradorPDFFactura()
pdf_path = generador.generar(cae=cae, vencimiento_cae=vto)
```

---

## Testing

```bash
# Tests unitarios
pytest tests/

# Coverage
pytest --cov=src tests/

# Test contra ARCA homologación
python scripts/test_arca_homologacion.py
```

---

## 🚀 Deployment

### En VPS Propio

```bash
git clone https://github.com/UltimaMilla/plantilla-arca.git
cd plantilla-arca
cp .env.example .env
# Editar .env
docker-compose up -d
```

### En Render.com

1. Push a GitHub ✓
2. https://render.com → New Web Service
3. Conectar repo
4. Build: `pip install -r requirements.txt`
5. Start: `streamlit run src/web/streamlit_app.py`
6. Deploy

---

## 📝 Licencia

MIT - Úsalo, modificalo, distribuilo sin restricciones.

---

## 🔗 Enlaces Útiles

- [Blog sobre RG 5824](https://ultimamilla.com.ar/blog/arca-5824-2026-el-director-que-nunca-facturo-tiene-fecha/)
- [AFIP Web Services](https://www.afip.gob.ar/ws/)
- [arca_arg Documentación](https://github.com/tinybike/arca_arg)
- [RG 5824 Completa](https://www.afip.gob.ar/genericos/basesnormativas/AFIP_Resolucion_General_5824.pdf)

---

**Hecho por [Ultima Milla](https://ultimamilla.com.ar)**
