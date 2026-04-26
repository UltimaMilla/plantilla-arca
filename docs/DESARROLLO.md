# Guía de Desarrollo - Plantilla ARCA

Contribuye al proyecto. Esta guía cubre setup local, estructura del código, testing y workflow de PRs.

---

## Setup para Desarrollo

### Paso 1: Clonar repositorio

```bash
git clone https://github.com/UltimaMilla/plantilla-arca.git
cd plantilla-arca
```

### Paso 2: Crear rama de feature

```bash
git checkout -b feature/tu-feature-name
# O para bugfix:
git checkout -b bugfix/descripcion-del-bug
```

**Convención de nombres:**
- Features: `feature/nueva-validacion-cuit`
- Bugfixes: `bugfix/error-pdf-logo-faltante`
- Docs: `docs/mejorar-readme`

### Paso 3: Configurar entorno virtual

```bash
# En Linux/macOS:
python3 -m venv venv
source venv/bin/activate

# En Windows:
python -m venv venv
venv\Scripts\activate.bat
```

### Paso 4: Instalar dependencias + herramientas de desarrollo

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Si existe, o instala manualmente:
pip install pytest pytest-cov black flake8 mypy
```

### Paso 5: Copiar configuración local

```bash
cp .env.example .env.local
```

Edita con valores de prueba:

```env
ARCA_CUIT=20123456789
ARCA_CERT_PATH=./certs/certificado.pem
ARCA_KEY_PATH=./certs/clave.pem
ARCA_HOMOLOGACION=true
DATABASE_URL=sqlite:///./test.db
```

---

## Estructura del Código

```
plantilla-arca/
├── src/
│   ├── arca/
│   │   ├── __init__.py
│   │   └── client.py          # Cliente ARCA, obtención de CAE
│   ├── pdf/
│   │   ├── __init__.py
│   │   └── generator.py       # Generador de PDFs con QR
│   ├── web/
│   │   ├── __init__.py
│   │   ├── streamlit_app.py   # Interfaz web (Streamlit)
│   │   └── fastapi_app.py     # API REST (FastAPI)
│   ├── comprobante/
│   │   └── __init__.py        # Modelos de comprobante
│   ├── config.py              # Variables de entorno
│   └── models.py              # Modelos SQLAlchemy (DB)
├── tests/
│   ├── __init__.py
│   ├── test_arca_client.py    # Tests para ARCA client
│   ├── test_pdf_generator.py  # Tests para PDF generator
│   └── test_api_endpoints.py  # Tests para API endpoints
├── docs/
│   ├── INSTALACION.md         # Instalación
│   ├── API.md                 # Referencia API
│   ├── DESARROLLO.md          # Esta guía
│   └── RG-5824-EXPLICADO.md   # Explicación normativa
├── certs/                     # Certificados AFIP (gitignored)
├── output/                    # PDFs generados (gitignored)
├── requirements.txt           # Dependencias Python
├── README.md                  # Descripción general
├── Dockerfile                 # Para Docker
├── docker-compose.yml         # Orquestación Docker
└── pytest.ini                 # Configuración pytest
```

**Propósito de cada módulo:**

| Módulo | Función |
|--------|---------|
| `src.arca.client` | Conecta a ARCA Web Services, obtiene CAEs |
| `src.pdf.generator` | Crea PDFs profesionales con QR y validación |
| `src.web.streamlit_app` | UI simple para usuarios sin conocimiento técnico |
| `src.web.fastapi_app` | API REST para integración programática |
| `src.models` | Modelos de base de datos (SQLAlchemy) |
| `src.config` | Carga y valida variables de entorno |

---

## Cómo Hacer un PR (Pull Request)

### 1. Hacer cambios y commits

```bash
# Edita archivos
nano src/arca/client.py

# Stage cambios
git add src/arca/client.py

# Commit con mensaje descriptivo
git commit -m "feat: agregar validacion mejorada de CUIT"
```

**Mensajes de commit (Conventional Commits):**

```
feat: nueva característica
fix: corrección de bug
docs: cambios en documentación
refactor: cambio sin agregar funcionalidad
test: agregar o mejorar tests
chore: cambios en dependencias, build, etc.
```

**Ejemplos:**
- `feat: validar CUIT con dígito verificador`
- `fix: error al cargar logo desde data:image URL`
- `docs: mejorar ejemplos en API.md`

### 2. Preparar rama para PR

```bash
# Actualizar rama con cambios remotos
git fetch origin
git rebase origin/main

# Corregir conflictos si los hay (raro para features nuevas)
git status
# Edita archivos con conflictos, luego:
git add .
git rebase --continue
```

### 3. Empujar rama

```bash
git push origin feature/tu-feature-name
```

### 4. Crear PR en GitHub

- Ve a: https://github.com/UltimaMilla/plantilla-arca/pulls
- Haz clic en "New Pull Request"
- Selecciona `base: main` y `compare: feature/tu-feature-name`
- Completa el título y descripción
- Verifica que los tests pasan

**Template de descripción PR:**

```markdown
## Descripción
Breve descripción de qué hace este PR.

## Cambios
- Cambio 1
- Cambio 2
- Cambio 3

## Testing
Cómo probaste estos cambios:
- [ ] Tests unitarios pasan
- [ ] Probado localmente con `npm run dev`
- [ ] Sin warnings de linter

## Checklist
- [ ] Código sigue convención de estilos
- [ ] Documentación actualizada si aplica
- [ ] Tests nuevos/actualizados
```

---

## Cómo Correr Tests Localmente

### Ejecutar todos los tests

```bash
pytest
```

**Salida esperada:**
```
======================== test session starts =========================
collected 12 items

tests/test_arca_client.py ......                              [ 50%]
tests/test_pdf_generator.py ....                              [ 67%]
tests/test_api_endpoints.py ..                                [ 83%]

======================== 12 passed in 1.23s ============================
```

### Ejecutar tests de un archivo

```bash
pytest tests/test_arca_client.py -v
```

### Ejecutar con cobertura

```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html  # Abre reporte en navegador
```

Objetivo de cobertura: **80%+**

### Ejecutar en watch mode (re-ejecuta al cambiar archivos)

```bash
pytest-watch
# O manualmente:
while inotifywait -e modify src/**/*.py; do pytest; done
```

### Escribir un test nuevo

```python
# tests/test_mi_feature.py
import pytest
from src.arca.client import ArcaClient

def test_validacion_cuit_valido():
    """Verifica que un CUIT válido se acepta"""
    cuit = "20123456789"
    # Implementar test
    assert True

def test_validacion_cuit_invalido():
    """Verifica que un CUIT inválido lanza excepción"""
    with pytest.raises(ValueError):
        ArcaClient(cuit="invalid", cert_path="x", key_path="y")
```

---

## Git Workflow

### Rama principal

```
main (producción)
├── feature/nueva-validacion (tu rama)
│   └── commit: "feat: validar CUIT"
│       └── commit: "test: agregar test para CUIT"
└── feature/otro-fix
```

### Pasos completos

```bash
# 1. Crear rama de feature
git checkout -b feature/validacion-cuit

# 2. Hacer cambios
vim src/arca/client.py
pytest  # Verifica que tests pasen

# 3. Commit
git add src/arca/client.py
git commit -m "feat: agregar validacion de dígito verificador CUIT"

# 4. Empujar
git push origin feature/validacion-cuit

# 5. Crear PR en GitHub y esperar review

# 6. Después de merge, limpiar
git checkout main
git pull origin main
git branch -d feature/validacion-cuit
git push origin --delete feature/validacion-cuit
```

---

## Code Style & Linting

### Formateo automático con Black

```bash
# Formatea todos los archivos Python
black src/ tests/

# Ver cambios sin aplicar
black --diff src/
```

Configuración: `.black.toml` (si existe) o estándar de Black (88 caracteres línea)

### Linting con Flake8

```bash
flake8 src/ tests/
```

Ignora estos errores (configurados en `.flake8`):
- E501: Línea muy larga (Black lo maneja)
- W503: Operador antes de salto de línea

### Type hints con mypy (opcional)

```bash
mypy src/
```

---

## Estructura de Tests

Ubicación: `tests/test_*.py`

**Naming convention:**
- Archivo: `test_modulo.py`
- Función: `test_descripcion_de_lo_que_se_prueba`
- Clase: `TestClaseAProbar`

**Ejemplo completo:**

```python
# tests/test_arca_client.py
import pytest
from unittest.mock import Mock, patch
from src.arca.client import ArcaClient

class TestArcaClient:
    """Suite de tests para ArcaClient"""
    
    @pytest.fixture
    def cliente(self):
        """Fixture: cliente ARCA para tests"""
        return ArcaClient(
            cuit="20123456789",
            cert_path="./certs/test_cert.pem",
            key_path="./certs/test_key.pem",
            homologacion=True
        )
    
    def test_cliente_inicializa(self, cliente):
        """Verifica que cliente se inicializa correctamente"""
        assert cliente.cuit == "20123456789"
        assert cliente.homologacion == True
    
    @patch('src.arca.client.ArcaClient.solicitar_cae')
    def test_solicitar_cae_retorna_dict(self, mock_cae, cliente):
        """Verifica que solicitar_cae retorna dict con CAE"""
        mock_cae.return_value = {
            "cae": "12345678901234",
            "vencimiento": "2024-07-20"
        }
        resultado = cliente.solicitar_cae()
        assert isinstance(resultado, dict)
        assert "cae" in resultado
```

---

## Debugging

### Ver logs

```bash
# Logs de Streamlit
streamlit run src/web/streamlit_app.py --logger.level=debug

# Logs de FastAPI
uvicorn src.web.fastapi_app:app --log-level debug

# Logs de pytest
pytest -v -s  # -s muestra prints
```

### Debugger interactivo

```python
# En tu código, agrega:
import pdb; pdb.set_trace()

# Comando en terminal:
pytest tests/test_file.py -v -s --pdb
```

### Ver variables de entorno

```bash
python -c "from src.config import *; print(ARCA_CUIT, ARCA_HOMOLOGACION)"
```

---

## Checklist antes de hacer PR

- [ ] Tests nuevos/actualizados y pasando (`pytest`)
- [ ] Código formateado (`black src/ tests/`)
- [ ] Sin warnings de linter (`flake8 src/ tests/`)
- [ ] Documentación actualizada si aplica
- [ ] Mensaje de commit descriptivo
- [ ] Rama actualizada con main (`git rebase origin/main`)
- [ ] Sin conflictos git
- [ ] Sin cambios de `.env` o credenciales

---

## Recursos

- **Python 3.10+**: https://www.python.org/
- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://sqlalchemy.org/
- **Pytest**: https://pytest.org/
- **AFIP API**: https://www.afip.gob.ar/

---

## Soporte

- Preguntas: Abre issue con etiqueta `question`
- Bugs: Abre issue con etiqueta `bug`
- Features: Abre issue con etiqueta `enhancement`
- Discussiones: https://github.com/UltimaMilla/plantilla-arca/discussions
