# Guía de Instalación - Plantilla ARCA

Esta guía cubre tres escenarios de instalación: Docker (recomendado), sin Docker en tu máquina local, y en un servidor VPS propio.

---

## Instalación Con Docker (Recomendado - 5 minutos)

Docker permite ejecutar Plantilla ARCA en un contenedor aislado sin instalar Python ni dependencias manualmente.

### Requisitos Previos

- **Docker** (versión 20.10+): [Descargar](https://www.docker.com/products/docker-desktop)
- **Docker Compose** (incluido en Docker Desktop)
- **Git** para clonar el repositorio

### Pasos de Instalación

#### 1. Clonar el repositorio

```bash
git clone https://github.com/UltimaMilla/plantilla-arca.git
cd plantilla-arca
```

**Resultado esperado:**
```
Cloning into 'plantilla-arca'...
remote: Enumerating objects...
...
Unpacking objects: 100% (245/245), done.
```

#### 2. Crear archivo de configuración

Copia el archivo de ejemplo y personalízalo con tus credenciales AFIP:

```bash
cp .env.example .env
nano .env    # En Windows: notepad .env
```

**Contenido de `.env` (ejemplo):**

```env
# Credenciales AFIP
ARCA_CUIT=20123456789
ARCA_CERT_PATH=/app/certs/certificado.pem
ARCA_KEY_PATH=/app/certs/clave.pem
ARCA_HOMOLOGACION=true

# Base de datos PostgreSQL
DATABASE_URL=postgresql://arca_user:secure_password@db:5432/arca_facturas

# Email (opcional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_email@gmail.com
SMTP_PASSWORD=tu_contraseña_app
```

#### 3. Copiar certificados AFIP

Coloca tus certificados en el directorio `certs/`:

```bash
# Estructura esperada:
ls -la certs/
# certificado.pem  (certificado digital de AFIP)
# clave.pem        (clave privada)
```

**¿No tienes certificados?** Lee la sección "Generar certificados AFIP" al final de este documento.

#### 4. Levantar los contenedores

```bash
docker-compose up -d
```

**Salida esperada:**
```
Creating arca_app ... done
Creating arca_db  ... done
Network fumbling-field_umbot-network created
```

#### 5. Verificar que los servicios estén corriendo

```bash
docker-compose ps
```

**Salida esperada:**
```
NAME      STATUS        PORTS
arca_app  Up 2 seconds  127.0.0.1:8501->8501/tcp
arca_db   Up 3 seconds  5432/tcp
```

#### 6. Acceder a la interfaz web

Abre tu navegador en: **http://localhost:8501**

Deberías ver la interfaz de Plantilla ARCA lista para emitir facturas.

### Detener los servicios

```bash
docker-compose down
```

Para detener SIN eliminar datos:

```bash
docker-compose stop
```

---

## Instalación Sin Docker (Entorno Virtual Local)

Para desarrolladores que prefieren Python en su máquina sin contenedores.

### Requisitos Previos

- **Python 3.10+**: [Descargar](https://www.python.org/downloads/)
- **PostgreSQL 13+** (opcional, puedes usar SQLite para desarrollo)
- **Git**
- **OpenSSL** (incluido en macOS/Linux; Windows lo incluye en Python)

### Pasos de Instalación

#### 1. Clonar el repositorio

```bash
git clone https://github.com/UltimaMilla/plantilla-arca.git
cd plantilla-arca
```

#### 2. Crear un entorno virtual

```bash
# En Linux/macOS:
python3 -m venv venv
source venv/bin/activate

# En Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1

# En Windows (CMD):
python -m venv venv
venv\Scripts\activate.bat
```

**Indicador:** Tu prompt debería mostrar `(venv) $` si está activado.

#### 3. Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Verificar instalación:**
```bash
python -m pip show arca_arg
# Debería mostrar: Version: 0.1.2
```

#### 4. Crear archivo `.env`

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:

```env
ARCA_CUIT=20123456789
ARCA_CERT_PATH=./certs/certificado.pem
ARCA_KEY_PATH=./certs/clave.pem
ARCA_HOMOLOGACION=true
DATABASE_URL=sqlite:///./arca_facturas.db
```

#### 5. Copiar certificados AFIP

```bash
mkdir -p certs
# Coloca certificado.pem y clave.pem en ./certs/
```

#### 6. Inicializar la base de datos

```bash
# Si usas PostgreSQL, crea la DB manualmente
createdb arca_facturas

# Si usas SQLite, se crea automáticamente
python -c "from src.models import Base, engine; Base.metadata.create_all(bind=engine)"
```

#### 7. Ejecutar la aplicación

```bash
# Interfaz Streamlit (web):
streamlit run src/web/streamlit_app.py

# O API FastAPI:
uvicorn src.web.fastapi_app:app --reload --port 8000
```

**Acceso:**
- Streamlit: http://localhost:8501
- FastAPI: http://localhost:8000
- API docs: http://localhost:8000/docs

#### 8. Desactivar entorno virtual

```bash
deactivate
```

---

## Instalación en VPS Propio (Producción)

Para desplegar Plantilla ARCA en un servidor Linux propio con Nginx, systemd y certificados SSL.

### Requisitos Previos

- Servidor Linux (Ubuntu 20.04+ recomendado)
- Acceso SSH con permisos sudo
- Dominio propio (ej: arca.tudominio.com)
- PostgreSQL 13+ instalado en el servidor

### Pasos de Instalación

#### 1. Conectar por SSH y actualizar sistema

```bash
ssh usuario@192.168.1.100
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3.10 python3.10-venv python3.10-dev build-essential
```

#### 2. Clonar repositorio

```bash
cd /opt
sudo git clone https://github.com/UltimaMilla/plantilla-arca.git
sudo chown -R usuario:usuario /opt/plantilla-arca
cd /opt/plantilla-arca
```

#### 3. Crear entorno virtual

```bash
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configurar variables de entorno

```bash
cp .env.example .env
nano .env
```

Configuración para producción:

```env
ARCA_CUIT=20123456789
ARCA_CERT_PATH=/opt/plantilla-arca/certs/certificado.pem
ARCA_KEY_PATH=/opt/plantilla-arca/certs/clave.pem
ARCA_HOMOLOGACION=false

DATABASE_URL=postgresql://arca_user:contraseña_segura@localhost:5432/arca_facturas

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=notificaciones@tudominio.com
SMTP_PASSWORD=contraseña_app_gmail
```

#### 5. Copiar certificados AFIP

```bash
mkdir -p certs
sudo chown -R usuario:usuario certs
# Coloca certificado.pem y clave.pem
chmod 600 certs/*
```

#### 6. Crear base de datos PostgreSQL

```bash
sudo -u postgres createdb arca_facturas
sudo -u postgres psql -c "CREATE USER arca_user WITH PASSWORD 'contraseña_segura';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE arca_facturas TO arca_user;"
```

#### 7. Inicializar esquema de DB

```bash
cd /opt/plantilla-arca
python -c "from src.models import Base, engine; Base.metadata.create_all(bind=engine)"
```

#### 8. Crear servicio systemd

```bash
sudo nano /etc/systemd/system/arca-api.service
```

Contenido:

```ini
[Unit]
Description=Plantilla ARCA API
After=network.target postgresql.service
StartLimitInterval=200
StartLimitBurst=5

[Service]
Type=simple
User=usuario
WorkingDirectory=/opt/plantilla-arca
Environment="PATH=/opt/plantilla-arca/venv/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=/opt/plantilla-arca/venv/bin/uvicorn src.web.fastapi_app:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Registrar y habilitar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable arca-api
sudo systemctl start arca-api
sudo systemctl status arca-api
```

**Salida esperada:**
```
● arca-api.service - Plantilla ARCA API
     Loaded: loaded (/etc/systemd/system/arca-api.service; enabled)
     Active: active (running)
```

#### 9. Configurar Nginx como proxy inverso

```bash
sudo nano /etc/nginx/sites-available/arca
```

Contenido:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name arca.tudominio.com;
    
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name arca.tudominio.com;
    
    ssl_certificate /etc/letsencrypt/live/arca.tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/arca.tudominio.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    client_max_body_size 50M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
    }
}
```

Habilitar sitio:

```bash
sudo ln -s /etc/nginx/sites-available/arca /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 10. Generar certificado SSL con Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot certonly --nginx -d arca.tudominio.com
```

Automático: Certbot renueva automáticamente cada 90 días.

#### 11. Verificar que todo está funcionando

```bash
# Ver logs de la API:
sudo journalctl -u arca-api -f

# Probar en otra terminal:
curl -H "Authorization: Bearer tu_token" https://arca.tudominio.com/api/health
```

---

## Generar Certificados AFIP

### Opción 1: Con OpenSSL (Línea de comandos)

Crea una clave privada y solicita certificado en el portal AFIP:

```bash
# Generar clave privada (2048 bits):
openssl genrsa -out clave.pem 2048

# Generar solicitud de certificado (CSR):
openssl req -new -key clave.pem -out solicitud.csr \
    -subj "/C=AR/ST=Buenos Aires/L=CABA/O=Tu Empresa/CN=123456789"
```

Luego, sube `solicitud.csr` al portal AFIP y descarga el certificado como `certificado.pem`.

### Opción 2: Con el portal CUIT de AFIP

1. Accede a https://www.afip.gob.ar/
2. Ingresa a "CUIT" → "Mis datos"
3. Solicita un certificado de homologación para pruebas
4. Sigue el asistente para generar tu CSR
5. Descarga el certificado firmado

---

## Troubleshooting por Plataforma

### Windows

**Problema:** "python: command not found"
- Solución: Añade Python al PATH (marca la casilla durante instalación)
- O usa: `python -m pip install...` en lugar de `pip install...`

**Problema:** "SSL: CERTIFICATE_VERIFY_FAILED"
- Solución: Instala certificados SSL
  ```powershell
  /Applications/Python\ 3.10/Install\ Certificates.command
  ```

**Problema:** Archivo `.env` no se lee
- Solución: Crea el archivo con Notepad++ (no Notepad), asegurate que no tenga extensión `.txt`

### macOS

**Problema:** "ModuleNotFoundError: No module named 'arca_arg'"
- Solución: Asegúrate que el venv está activado
  ```bash
  which python  # Debe mostrar: /ruta/al/venv/bin/python
  ```

**Problema:** Permisos rechazados en directorio `certs/`
- Solución:
  ```bash
  sudo chown -R $USER:staff ./certs
  chmod 600 certs/*
  ```

### Linux

**Problema:** "ModuleNotFoundError: No module named 'psycopg2'"
- Solución: Instala dependencias del sistema
  ```bash
  sudo apt install -y libpq-dev python3.10-dev
  pip install --force-reinstall psycopg2-binary
  ```

**Problema:** Puerto 8501 ya está en uso
- Solución: Ejecuta en otro puerto
  ```bash
  streamlit run src/web/streamlit_app.py --server.port 8502
  ```

**Problema:** Certificados AFIP con permiso rechazado
- Solución: Ajusta permisos
  ```bash
  chmod 600 certs/certificado.pem certs/clave.pem
  chmod 700 certs/
  ```

---

## Verificación de Instalación

Confirma que todo está funcionando correctamente:

```bash
# 1. Verificar Python
python --version
# Esperado: Python 3.10.x o superior

# 2. Verificar dependencias
pip list | grep arca_arg
# Esperado: arca_arg version 0.1.2

# 3. Verificar conexión a DB
python -c "from src.models import engine; print('✓ Base de datos conectada')"

# 4. Verificar certificados AFIP
ls -la certs/
# Esperado: certificado.pem y clave.pem existen
```

---

## Próximos Pasos

- **API**: Lee [API.md](./API.md) para integración programática
- **Desarrollo**: Lee [DESARROLLO.md](./DESARROLLO.md) para contribuir
- **Regulación**: Lee [RG-5824-EXPLICADO.md](./RG-5824-EXPLICADO.md) para entender la normativa
