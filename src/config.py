import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://arca_user:arca_password_dev@localhost:5432/arca_facturas"
)

ARCA_CUIT = os.getenv("ARCA_CUIT")
ARCA_HOMOLOGACION = os.getenv("ARCA_HOMOLOGACION", "true").lower() == "true"
ARCA_CERT_PATH = os.getenv("ARCA_CERT_PATH", "certs/certificado.crt")
ARCA_KEY_PATH = os.getenv("ARCA_KEY_PATH", "certs/clave_privada.key")
ARCA_PUNTO_VENTA = int(os.getenv("ARCA_PUNTO_VENTA", "1"))

ARCA_URLS = {
    "homologacion": {
        "wsaa": "https://wsaahomo.afip.gov.ar/ws/services/LoginCMS",
        "wsmtxca": "https://wswhomo.afip.gov.ar/ws/services/wsmtxca",
    },
    "produccion": {
        "wsaa": "https://wsaa.afip.gov.ar/ws/services/LoginCMS",
        "wsmtxca": "https://ws.afip.gov.ar/ws/services/wsmtxca",
    },
}

ARCA_ENVIRONMENT = "homologacion" if ARCA_HOMOLOGACION else "produccion"

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")
CERTS_DIR = os.getenv("CERTS_DIR", "./certs")

engine = create_engine(DATABASE_URL, echo=False)

TIPO_COMPROBANTE = {
    1: "Factura A",
    6: "Factura B",
    11: "Factura C",
}

IDENTIDAD_UMSA = {
    "nombre_empresa": "Ultima Milla",
    "url": "https://ultimamilla.com.ar",
    "color_primario": "#DC2626",
    "color_secundario": "#1A56C0",
}
