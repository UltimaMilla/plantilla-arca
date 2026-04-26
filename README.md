# 🧾 Plantilla ARCA - Facturación Electrónica Open Source

**Generador automático de facturas electrónicas según RG 5824 AFIP - Sin costo, sin vendor lock-in, código libre**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## Tabla de Contenidos

- [¿Qué es?](#qué-es)
- [¿Qué es RG 5824?](#qué-es-rg-5824)
- [Quick Start (3 opciones)](#quick-start)
- [Instalación Completa](#instalación-completa)
- [Stack Técnico](#stack-técnico)
- [Casos de Uso](#casos-de-uso)
- [Interfaz Web](#interfaz-web)
- [Integración Programática](#integración-programática)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Documentación](#documentación)
- [Roadmap](#roadmap)
- [Licencia y Recursos](#licencia-y-recursos)

---

## ¿Qué es?

**Plantilla ARCA** es una solución open source que automatiza **100% de la facturación electrónica** bajo la Resolución General 5824 de AFIP. 

Con una sola herramienta, obtén:

✅ **Conexión automática a ARCA Web Services** - Sin certificados manuales  
✅ **CAE instantáneo** - Solicitud automática de código de autorización  
✅ **PDF profesional con QR** - Facturas listas para imprimir o enviar  
✅ **Base de datos integrada** - PostgreSQL para historial completo  
✅ **Interfaz web intuitiva** - Streamlit para usuarios sin conocimiento técnico  
✅ **API REST** - Para integración con tus sistemas  
✅ **100% Open Source** - MIT License, modifica lo que necesites  

**Resultado real:** De "¿cómo conecto a ARCA?" a "tengo mi factura en PDF con QR válido" en menos de 2 minutos.

---

## ¿Qué es RG 5824?

La **Resolución General 5824 (AFIP)** es una normativa de Argentina que obliga facturación electrónica inmediata a través de **ARCA Web Services** (sistema de AFIP) para:

- Directores de empresa
- Abogados
- Contadores  
- Escribanos
- Profesionales independientes (médicos, ingenieros, arquitectos, etc.)
- Pequeñas empresas (PyMEs) bajo determinados montos

**¿Qué obliga RG 5824?**
- Emitir facturas electrónicas a través de ARCA (no más e-Factura G)
- Obtener CAE (Código de Autorización Electrónica) antes de usar el comprobante
- Registrar transacciones en tiempo real
- Mantener trazabilidad completa

**¿Por qué es importante?**
- AFIP audita automáticamente todas las transacciones
- Previene evasión fiscal y blanqueo de dinero
- Garantiza que tus facturas sean legalmente válidas
- Sin cumplimiento = multas desde $1000

**Plantilla ARCA** elimina la complejidad técnica de RG 5824 en una interfaz simple.

---

## Quick Start

Elige la opción que mejor se adapte a tu situación:

### Opción 1: Docker (Recomendado - 2 minutos)

**Requisitos:** Docker y Docker Compose instalados

```bash
# 1. Clonar el repositorio
git clone https://github.com/UltimaMilla/plantilla-arca.git
cd plantilla-arca

# 2. Copiar configuración de ejemplo
cp .env.example .env

# 3. Editar .env con tus datos AFIP (CUIT, certificado, etc.)
nano .env

# 4. Levantar los servicios
docker-compose up -d

# 5. Acceder a la interfaz web
# Abre: http://localhost:8501
# La base de datos PostgreSQL se inicia automáticamente en puerto 5432
```

**Ventajas:**
- Todo aislado en contenedores - no contamina tu PC
- PostgreSQL y app se inician solos
- Un comando para detener: `docker-compose down`
- Perfecto para producción

**Desventajas:**
- Necesitas Docker instalado
- Ligeramente más lento en M1/M2 Mac

---

### Opción 2: Instalación Local (Sin Docker - 5 minutos)

**Requisitos:**
- Python 3.10 o superior
- PostgreSQL 13+ (instalado y ejecutándose)
- pip (gestor de paquetes Python)

```bash
# 1. Clonar el repositorio
git clone https://github.com/UltimaMilla/plantilla-arca.git
cd plantilla-arca

# 2. Crear entorno virtual Python (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
nano .env  # Editar con tus credenciales AFIP

# 5. Inicializar base de datos (primera ejecución)
python src/models.py

# 6. Iniciar la aplicación web
streamlit run src/web/streamlit_app.py

# La app estará en: http://localhost:8501
```

**Ventajas:**
- Más rápido si ya tienes Python
- Acceso directo a código para debugging
- Menor uso de memoria

**Desventajas:**
- Necesitas gestionar PostgreSQL manualmente
- Más pasos de configuración
- Problemas con dependencias entre sistemas operativos

---

### Opción 3: VPS Propio o Servidor Remoto (10 minutos)

**Para alojar en un servidor Linux en la nube (DigitalOcean, Linode, AWS, Google Cloud, etc.)**

```bash
# 1. SSH a tu servidor
ssh usuario@tu_servidor_ip

# 2. Instalar Docker (si no está instalado)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 3. Clonar el repositorio
git clone https://github.com/UltimaMilla/plantilla-arca.git
cd plantilla-arca

# 4. Configurar variables de entorno
cp .env.example .env
nano .env  # Editar con datos AFIP + datos servidor

# 5. Crear archivo docker-compose.prod.yml (producción)
# Ver sección "Deployment" en documentación

# 6. Levantar en background
docker-compose -f docker-compose.yml up -d

# 7. Verificar que esté corriendo
docker-compose ps

# 8. Ver logs
docker-compose logs -f

# 9. Acceder desde tu navegador
# http://tu_servidor_ip:8501
```

**Para usar dominio personalizado con HTTPS:**

```bash
# Instalar Nginx (reverse proxy)
sudo apt-get install nginx

# Configurar SSL con Let's Encrypt (gratis)
sudo apt-get install certbot python3-certbot-nginx

# Renovación automática
sudo certbot --nginx -d tu_dominio.com
```

**Ventajas:**
- Accesible desde cualquier lugar
- Datos en la nube, no en tu PC
- Escalable para múltiples usuarios
- Backups automáticos

**Desventajas:**
- Requiere suscripción a hosting
- Necesita conocimientos básicos de Linux

---

## Instalación Completa

### Paso 1: Obtener Certificado AFIP (Gratis, 3-5 días)

La RG 5824 requiere certificado X.509 para firmar digitalmente. AFIP lo provee gratis.

**Pasos:**

1. Ir a https://www.afip.gob.ar
2. Ingresar con Clave Fiscal
3. Menú → Web Services → Solicitar Certificado
4. Cargar CUIT de tu empresa
5. Descargar:
   - `certificado.crt` (certificado)
   - `clave_privada.key` (llave privada)

**Guardar en:**
```
plantilla-arca/
├── certs/
│   ├── certificado.crt
│   └── clave_privada.key
```

### Paso 2: Configurar Variables de Entorno

```bash
cp .env.example .env
```

Editar `.env` con tus datos:

```bash
# AFIP y ARCA
ARCA_CUIT=20123456789              # Tu CUIT sin guiones
ARCA_CERT_PATH=certs/certificado.crt
ARCA_KEY_PATH=certs/clave_privada.key
ARCA_HOMOLOGACION=false            # true para pruebas, false para producción

# PostgreSQL
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/plantilla_arca
DB_HOST=localhost
DB_PORT=5432
DB_USER=plantilla_arca
DB_PASSWORD=tu_contraseña_segura
DB_NAME=plantilla_arca

# Aplicación
APP_ENV=production                 # development o production
APP_DEBUG=false
SECRET_KEY=tu_clave_secreta_aqui

# Email (opcional, para enviar facturas)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_email@gmail.com
SMTP_PASSWORD=tu_contraseña_app
```

### Paso 3: Iniciando la Aplicación

**Opción Docker:**
```bash
docker-compose up -d
```

**Opción Local:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run src/web/streamlit_app.py
```

### Paso 4: Verificar Conexión a ARCA

```bash
# Ejecutar test de conexión
python scripts/test_arca_homologacion.py

# Deberías ver:
# ✓ Certificado cargado
# ✓ Conexión a ARCA exitosa
# ✓ Solicitud de CAE aprobada
```

### Paso 5: Primera Factura

1. Abrir http://localhost:8501
2. Cargar datos del comprobante
3. Seleccionar "Tipo Factura" (A o B)
4. Presionar "Generar Factura"
5. Descargar PDF con QR válido

---

## Stack Técnico

| Componente | Herramienta | Versión | Función |
|-----------|-----------|---------|---------|
| **Lenguaje** | Python | 3.10+ | Lógica principal |
| **Cliente ARCA** | arca_arg | 0.1.2 | Conexión a Web Services AFIP |
| **Base de Datos** | PostgreSQL | 13+ | Persistencia de facturas |
| **Web** | Streamlit | 1.28+ | Interfaz gráfica sin JavaScript |
| **API** | FastAPI | 0.104+ | REST API para integración |
| **PDF** | ReportLab | 4.0+ | Generación de documentos |
| **QR** | PyQRCode | 1.2+ | Códigos QR en facturas |
| **Contenedores** | Docker | 20+ | Aislamiento de servicios |
| **ORM** | SQLAlchemy | 2.0+ | Mapeo objeto-relacional |
| **Validación** | Pydantic | 2.5+ | Tipos de datos seguros |

---

## Casos de Uso

### Caso 1: Contador Independiente (50 clientes)

**Situación:**
Martín es contador en Buenos Aires con 50 clientes pequeños que necesitan facturas mensuales. Cada cliente requiere factura por servicios de asesoría.

**Antes (Manual):**
- Llenar formularios en el sitio de AFIP
- Esperar respuesta de ARCA
- Generar PDF manualmente
- Enviar por email
- **Tiempo:** 15 minutos por factura × 50 = 12.5 horas/mes

**Con Plantilla ARCA:**
```python
# Script Python que automatiza todo (2 minutos de setup, después automático)
from src.arca.client import ArcaClient
from src.pdf.generator import GeneradorPDFFactura

cliente = ArcaClient()
for cliente_data in clientes_base_datos:
    cae, vto = cliente.solicitar_cae(
        tipo_comprobante=6,  # Factura tipo A
        punto_venta=1,
        numero=cliente_data['numero_factura_siguiente'],
        importe_neto=cliente_data['honorarios'],
        importe_iva=cliente_data['honorarios'] * 0.21
    )
    
    pdf = GeneradorPDFFactura()
    pdf.generar(cae=cae, cliente_data=cliente_data)
    # Enviar por email automáticamente
```

**Resultado:**
- Tiempo: 2 minutos (automático)
- Costo: $0 (open source)
- Precisión: 100% (sin errores manuales)
- **ROI:** 12.5 horas/mes = 50 horas/año = $2000+ ahorrados

---

### Caso 2: Director de PyME (Obligatorio por RG 5824)

**Situación:**
Andrea es directora de empresa con obligación de RG 5824. Necesita emitir facturas de venta, pero no sabe cómo conectar a ARCA.

**Sin Plantilla ARCA:**
- Contratar desarrollador: $3000-5000
- Esperar implementación: 2-4 semanas
- Mantenimiento continuo: $500/mes

**Con Plantilla ARCA:**
- Descargar código gratis
- Configurar en 5 minutos
- Interfaz web lista para usar
- Sin gastos de mantenimiento

**Interfaz Web:**
```
┌─────────────────────────────┐
│ PLANTILLA ARCA              │
├─────────────────────────────┤
│                             │
│ NUEVO COMPROBANTE           │
│                             │
│ Tipo de Factura:  [A / B ]  │
│ Cliente CUIT:     [_______] │
│ Cliente Nombre:   [_______] │
│ Monto Neto:       [$______] │
│ IVA (21%):        [$______] │
│ TOTAL:            [$______] │
│                             │
│ [ GENERAR FACTURA ]         │
│                             │
└─────────────────────────────┘
```

**Resultado:**
- Sin conocimiento técnico requerido
- Facturas válidas en minutos
- Costo total: $0
- **ROI:** Vs. contratar desarrollador = ahorro de $3000+

---

### Caso 3: Estudio Jurídico (Obligatorio RG 5824)

**Situación:**
Estudio con 8 abogados. Cada uno emite facturas por servicios legales. Necesitan trazabilidad y auditoría.

**Requisitos:**
- Múltiples usuarios
- Historial completo de facturas
- Reportes por abogado
- Cumplimiento AFIP
- Backups automáticos

**Solución:**
```bash
# VPS en DigitalOcean ($5/mes)
docker-compose up

# Cada abogado accede a:
# http://estudio.midominio.com
```

**Base de datos captura:**
- Fecha/hora exacta de emisión
- CAE y número de comprobante
- Cliente, monto, IVA
- Abogado que emitió
- Timestamp de auditoría

**Reportes integrados:**
```sql
-- Reporte mensual por abogado
SELECT 
  abogado,
  COUNT(*) as facturas,
  SUM(importe_total) as ingresos,
  SUM(importe_iva) as iva_cobrado
FROM facturas
WHERE MONTH(fecha) = MONTH(NOW())
GROUP BY abogado;
```

**Resultado:**
- Cumplimiento RG 5824 ✓
- Trazabilidad completa ✓
- Costo: $5/mes (hosting) + $0 (software)
- **ROI vs. software propietario:** Ahorro de $200/mes

---

### Caso 4: Profesional Independiente (Médico, Ingeniero)

**Situación:**
Profesional que emite facturas ocasionalmente por servicios. No necesita gestión compleja.

**Ventajas:**
- Interfaz super simple (3 campos)
- Genera PDF en segundos
- Válido para AFIP
- Gratis

**Integración con otras herramientas:**
```python
# Desde Excel, Google Sheets, o cualquier sistema
import requests

respuesta = requests.post(
    'http://localhost:8000/api/facturas',
    json={
        'cliente_cuit': '20123456789',
        'cliente_nombre': 'Juan García',
        'importe_neto': 1000,
        'importe_iva': 210,
        'importe_total': 1210
    }
)

print(respuesta.json()['pdf_url'])  # Descargar PDF
```

---

## Interfaz Web

La interfaz Streamlit no requiere ningún conocimiento técnico:

```
╔════════════════════════════════════════════════════════════╗
║                     PLANTILLA ARCA                         ║
║            Generador de Facturas Electrónicas             ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  TIPO DE COMPROBANTE                                       ║
║  ○ Factura A (IVA Responsable)                            ║
║  ○ Factura B (Monotributista)                             ║
║  ○ Nota de Crédito                                        ║
║                                                            ║
║  DATOS DEL CLIENTE                                         ║
║  CUIT: ┌────────────────────────────┐                      ║
║        │ 20123456789                 │                      ║
║        └────────────────────────────┘                      ║
║  Nombre: ┌────────────────────────────┐                    ║
║          │ García, Juan S.A.           │                    ║
║          └────────────────────────────┘                    ║
║                                                            ║
║  MONTO                                                     ║
║  Neto: ┌────────────────────────────┐                      ║
║        │ 1000.00                     │                      ║
║        └────────────────────────────┘                      ║
║  IVA: ┌────────────────────────────┐                       ║
║       │ 210.00 (Calculado: 21%)    │                       ║
║       └────────────────────────────┘                       ║
║  TOTAL: $1210.00                                           ║
║                                                            ║
║              [ GENERAR FACTURA ] [ LIMPIAR ]               ║
║                                                            ║
║  ✓ Factura emitida (CAE: 1234567890123)                   ║
║  ✓ PDF descargable                                        ║
║  ✓ Guardado en base de datos                              ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

**Características:**
- Validación en tiempo real
- Cálculo automático de IVA
- Historial de facturas
- Búsqueda y filtros
- Exportación a Excel/CSV
- Reemisión de facturas

---

## Integración Programática

Para desarrolladores que quieren integrar con sus sistemas:

### API REST (FastAPI)

```python
import requests

# Solicitar CAE y generar factura
respuesta = requests.post(
    'http://localhost:8000/api/v1/facturas',
    headers={'Authorization': 'Bearer tu_token_api'},
    json={
        'tipo_comprobante': 6,  # Factura A
        'punto_venta': 1,
        'numero': 1,
        'fecha_emision': '2026-04-26',
        'cliente_cuit': '20123456789',
        'cliente_nombre': 'García, Juan',
        'importe_neto': 1000.00,
        'importe_iva': 210.00,
        'importe_total': 1210.00,
        'conceptos': [
            {'descripcion': 'Servicio de consultoría', 'cantidad': 1, 'precio': 1000}
        ]
    }
)

# Respuesta
resultado = respuesta.json()
print(f"CAE: {resultado['cae']}")
print(f"PDF: {resultado['pdf_url']}")
print(f"QR: {resultado['qr_codigo']}")
```

### Librería Python

```python
from src.arca.client import ArcaClient
from src.pdf.generator import GeneradorPDFFactura

# Conectar a ARCA
arca = ArcaClient()

# Solicitar CAE
cae, vto_cae = arca.solicitar_cae(
    tipo_comprobante=6,
    punto_venta=1,
    numero=1,
    fecha_emision='20260426',
    importe_neto=1000.0,
    importe_iva=210.0,
    importe_total=1210.0
)

# Generar PDF
pdf_gen = GeneradorPDFFactura()
pdf_path = pdf_gen.generar(
    cae=cae,
    vto_cae=vto_cae,
    cliente_cuit='20123456789',
    cliente_nombre='García, Juan'
)

print(f"Factura guardada en: {pdf_path}")
```

### Desde CLI (Command Line)

```bash
python src/main.py \
  --cuit 20123456789 \
  --comprobante 6 \
  --punto-venta 1 \
  --numero 1 \
  --importe-neto 1000.00 \
  --importe-iva 210.00 \
  --cliente-nombre "García, Juan" \
  --output /tmp/factura.pdf

# Resultado: /tmp/factura.pdf listo para usar
```

---

## Testing

Plantilla ARCA incluye suite de tests completa:

### Tests Unitarios

```bash
# Ejecutar todos los tests
pytest tests/

# Tests específicos
pytest tests/test_api_endpoints.py -v
pytest tests/test_pdf_generator.py -v

# Con cobertura
pytest --cov=src tests/
```

### Test contra ARCA Homologación

Antes de usar en producción, prueba contra servidores de AFIP en ambiente de prueba:

```bash
python scripts/test_arca_homologacion.py

# Output esperado:
# ✓ Certificado cargado correctamente
# ✓ Conexión a ARCA exitosa
# ✓ Solicitud de CAE rechazada (esperado - es homologación)
# ✓ Validación de XML correcto
# ✓ Estructura PDF válida
```

### Ejemplos de Tests

```python
# tests/test_pdf_generator.py
from src.pdf.generator import GeneradorPDFFactura

def test_generar_pdf_valido():
    generador = GeneradorPDFFactura()
    pdf_path = generador.generar(
        cae='1234567890123',
        vto_cae='20260430',
        cliente_cuit='20123456789'
    )
    assert pdf_path.exists()
    assert pdf_path.suffix == '.pdf'

def test_generar_qr():
    generador = GeneradorPDFFactura()
    qr = generador.generar_qr(
        cae='1234567890123',
        cuit='20123456789'
    )
    assert qr is not None
```

---

## Troubleshooting

### Error 1: "Certificado no válido"

**Síntoma:**
```
Error: Certificate verification failed
```

**Causa:** Certificado AFIP expirado o ruta incorrecta

**Solución:**
```bash
# 1. Verificar ruta en .env
cat .env | grep ARCA_CERT_PATH

# 2. Verificar que archivos existan
ls -la certs/

# 3. Renovar certificado en AFIP (gratis, cada 1-2 años)
# https://www.afip.gob.ar

# 4. Reintentar
python scripts/test_arca_homologacion.py
```

---

### Error 2: "No puedo conectar a PostgreSQL"

**Síntoma:**
```
psycopg2.OperationalError: could not translate host name "postgres" to address
```

**Causa:** PostgreSQL no está ejecutándose o credenciales incorrectas

**Solución para Docker:**
```bash
# Verificar que postgres esté corriendo
docker-compose ps

# Si no está corriendo:
docker-compose up -d postgres

# Ver logs
docker-compose logs postgres
```

**Solución local:**
```bash
# Verificar PostgreSQL está ejecutándose
sudo systemctl status postgresql

# Si no está corriendo (macOS con Homebrew):
brew services start postgresql

# Verificar credenciales en .env
cat .env | grep DATABASE_URL

# Conectarse manualmente
psql -U plantilla_arca -d plantilla_arca -h localhost
```

---

### Error 3: "ARCA rechaza mi solicitud de CAE"

**Síntoma:**
```
ARCA Error 301: Rechazado por autoridad
```

**Causa:** Número de comprobante duplicado, punto de venta incorrecto, o datos inválidos

**Solución:**
```bash
# 1. Consultar número de comprobante siguiente en ARCA
python scripts/consultar_ultimo_numero.py

# 2. Actualizar en aplicación con número correcto

# 3. Verificar punto de venta
cat .env | grep PUNTO_VENTA

# 4. Validar montos (no pueden ser 0)

# 5. Probar en HOMOLOGACIÓN primero
# Editar .env:
ARCA_HOMOLOGACION=true
# Después de pruebas exitosas:
ARCA_HOMOLOGACION=false
```

---

### Error 4: "El PDF se ve mal o sin QR"

**Síntoma:**
```
PDF generado pero sin QR o datos incompletos
```

**Causa:** Fuentes faltantes o WeasyPrint no funciona correctamente

**Solución:**
```bash
# 1. Instalar fuentes (Linux)
sudo apt-get install fonts-dejavu fonts-liberation xfonts-encodings

# 2. Reinstalar dependencias
pip install --upgrade reportlab weasyprint

# 3. Probar nuevamente
python tests/test_pdf_generator.py

# 4. En macOS, puede requerir:
brew install libffi librsvg
```

---

## FAQ

### P: ¿Por qué open source y no software propietario?

**R:** Porque AFIP es un servicio público de Argentina. La facturación electrónica no debería ser un negocio privado:

- Softonic, Zucchetti, Siecom cobran $50-200/mes
- Nosotros: $0, código abierto, sin vendor lock-in
- Si AFIP cambia RG 5824, la comunidad actualiza el código juntos
- Transparencia: ves exactamente qué se envía a AFIP

**Además:** Desarrollo comunitario = mejor seguridad (más ojos revisando código)

---

### P: ¿Es seguro enviar datos a AFIP?

**R:** Sí, más seguro que software cerrado:

1. **Conexión:** SSL/TLS (https), certificado X.509
2. **Autenticación:** Certificado firmado por AFIP
3. **Código abierto:** Puedes auditar exactamente qué se envía
4. **Sin intermediarios:** Los datos van directo a AFIP, no a servidores terceros

```python
# Ver exactamente qué se envía:
import src.arca.client
# grep "requests.post" - no hay datos ocultos
```

---

### P: ¿Cómo integro con mi sistema actual?

**R:** Tres opciones:

**Opción 1: API REST** (recomendada para sistemas externos)
```bash
# Tu app hace POST a http://plantilla-arca.tudominio.com/api/v1/facturas
curl -X POST http://localhost:8000/api/v1/facturas \
  -H "Content-Type: application/json" \
  -d '{...}'
```

**Opción 2: Base de datos compartida** (si usas Python)
```python
from sqlalchemy import create_engine
engine = create_engine('postgresql://...')
# Lees/escribes directamente la tabla facturas
```

**Opción 3: Webhooks** (si quieres notificaciones)
```python
# Plantilla ARCA puede llamar a tu API cuando se emite factura
# POST https://tu-sistema.com/webhook/factura-emitida
```

---

### P: ¿Qué pasa si AFIP está caído?

**R:** Plantilla ARCA maneja esto automáticamente:

```python
# Reintenta hasta 3 veces con backoff exponencial
# Si AFIP sigue caído, guarda en base de datos como "pendiente"
# Cuando AFIP se recupera, reintenta automáticamente
```

Nunca pierdes una factura, incluso si AFIP tiene problemas de servicio.

---

### P: ¿Funciona con Monotributo / Factura B?

**R:** Sí, completamente:

```python
# Factura A (IVA Responsable)
tipo_comprobante = 6

# Factura B (Monotributista)
tipo_comprobante = 11

# Nota de Crédito A
tipo_comprobante = 3

# Nota de Crédito B
tipo_comprobante = 8
```

La interfaz web te deja elegir automáticamente.

---

### P: ¿Funciona en macOS, Windows, Linux?

**R:** Sí a todo:

- **macOS:** Intel y M1/M2 (con Docker Colima)
- **Windows:** Con Docker Desktop (o WSL2)
- **Linux:** Ubuntu, Debian, CentOS (cualquier distribución)

Recomendamos Docker para máxima compatibilidad.

---

### P: ¿Cómo hago backup de mis facturas?

**R:** Automático en 2 pasos:

```bash
# Opción 1: Backup automático (recomendado)
# Cron job que ejecuta diariamente:
0 2 * * * /backup-script.sh

# Opción 2: Manual
docker-compose exec postgres pg_dump plantilla_arca > backup_$(date +%Y%m%d).sql

# Opción 3: A la nube (AWS S3, Google Drive)
# Ver documentación/backups.md
```

---

## Documentación

Para profundizar en temas específicos:

- **[INSTALACIÓN_AVANZADA.md](docs/INSTALACION_AVANZADA.md)** - Configuración en VPS, Docker, múltiples ambientes
- **[ARQUITECTURA.md](docs/ARQUITECTURA.md)** - Diseño interno, flujo de datos, decisiones técnicas
- **[INTEGRACION_API.md](docs/INTEGRACION_API.md)** - Documentación completa de REST API
- **[SEGURIDAD.md](docs/SEGURIDAD.md)** - Mejores prácticas, encriptación, cumplimiento normativo
- **[RG_5824_EXPLICADA.md](docs/RG_5824_EXPLICADA.md)** - Normativa en lenguaje simple
- **[CONTRIBUCIONES.md](docs/CONTRIBUCIONES.md)** - Cómo colaborar al proyecto

---

## Ejemplos

Código completo para casos comunes:

- **[Generar factura simple](samples/ejemplo_1_factura_simple.py)** - Caso más básico
- **[Batch de facturas](samples/ejemplo_2_batch_facturas.py)** - Procesar 100+ facturas
- **[Integración con Django](samples/ejemplo_3_django_integration.py)** - Desde app Django existente
- **[Integración con Flask](samples/ejemplo_4_flask_integration.py)** - Desde app Flask existente
- **[Integración con Google Sheets](samples/ejemplo_5_google_sheets.py)** - Leer clientes de Sheet, generar facturas
- **[Integración con Zapier](samples/ejemplo_6_zapier_webhook.py)** - Automación sin código

---

## Roadmap

Funcionalidades planeadas:

**Q2 2026 (Próximo):**
- ✓ Descuentos y aumentos por línea
- ✓ Nota de crédito (devoluciones)
- ✓ Exportación a SAP/Tango
- ✓ Dashboard con reportes

**Q3 2026:**
- Integración con sistemas contables (SAP, Tango)
- Facturación recurrente (suscripciones)
- Envío automático por email
- Almacenamiento en la nube (AWS S3)

**Q4 2026:**
- Factura de Exportación (FEX)
- RG 5586 (Factura de Crédito Fiscal)
- Integración con sistemas ERP
- App móvil (iOS/Android)

**Contribuciones bienvenidas:** Ver [CONTRIBUCIONES.md](docs/CONTRIBUCIONES.md)

---

## Licencia y Recursos

### Licencia

**MIT License** - Úsalo, modifícalo, distribúyelo sin restricciones

```
Copyright (c) 2026 Ultima Milla S.A.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

Ver [LICENSE](LICENSE) completa.

---

### Recursos Oficiales

- **AFIP Web Services:** https://www.afip.gob.ar/ws/
- **RG 5824 Completa:** https://www.afip.gob.ar/genericos/basesnormativas/AFIP_Resolucion_General_5824.pdf
- **RG 5586:** https://www.afip.gob.ar/genericos/basesnormativas/AFIP_Resolucion_General_5586.pdf
- **Estructura XML ARCA:** https://www.afip.gob.ar/ws/documentos/

### Biblioteca arca_arg

Usamos la excelente librería `arca_arg` de [@tinybike](https://github.com/tinybike):

- **Repo:** https://github.com/tinybike/arca_arg
- **Docs:** https://github.com/tinybike/arca_arg#readme
- **Issues:** https://github.com/tinybike/arca_arg/issues

---

### Comunidad

- **GitHub Issues:** [Reportar bugs](https://github.com/UltimaMilla/plantilla-arca/issues)
- **Discussions:** [Hacer preguntas](https://github.com/UltimaMilla/plantilla-arca/discussions)
- **Blog:** [Tutoriales y noticias](https://ultimamilla.com.ar/blog)
- **Email:** contacto@ultimamilla.com.ar

---

## Soporte

**¿Necesitas ayuda?**

1. **Revisa el FAQ** - Probablemente tu pregunta ya está respondida
2. **Busca en Issues** - Tu problema posiblemente ya fue resuelto
3. **Lee la documentación** - Detalles técnicos en `docs/`
4. **Abre una Issue** - Describe claramente el problema con logs
5. **Email:** contacto@ultimamilla.com.ar

---

## Créditos

Hecho por **[Ultima Milla S.A.](https://ultimamilla.com.ar)** - Transformamos PyMEs en empresas digitales.

Gracias a la comunidad Argentina por usar y mejorar Plantilla ARCA.

---

**Última actualización:** Abril 2026  
**Versión:** 1.0.0
