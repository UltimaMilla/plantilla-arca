import logging
from datetime import datetime, timedelta
from typing import Tuple

try:
    from arca_arg import ArcaClient as _ArcaClientBase
except ImportError:
    raise ImportError("arca_arg no está instalado: pip install arca_arg")

from config import ARCA_CUIT, ARCA_CERT_PATH, ARCA_KEY_PATH, ARCA_HOMOLOGACION

logger = logging.getLogger(__name__)

class ArcaClient:
    def __init__(
        self,
        cuit: str = ARCA_CUIT,
        cert_path: str = ARCA_CERT_PATH,
        key_path: str = ARCA_KEY_PATH,
        homologacion: bool = ARCA_HOMOLOGACION,
    ):
        if not all([cuit, cert_path, key_path]):
            raise ValueError("CUIT, certificado y clave privada son obligatorios")

        self.cuit = cuit
        self.homologacion = homologacion
        self.ambiente = "Homologación" if homologacion else "Producción"

        try:
            self.cliente = _ArcaClientBase(
                cuit=cuit,
                cert_path=cert_path,
                key_path=key_path,
                production=not homologacion,
            )
            logger.info(f"✓ Cliente ARCA inicializado ({self.ambiente})")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Certificado o clave no encontrados: {e}")
        except Exception as e:
            raise RuntimeError(f"Error inicializando cliente ARCA: {e}")
