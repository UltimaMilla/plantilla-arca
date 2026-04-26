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

    def solicitar_cae(
        self,
        tipo_comprobante: str = "Factura A",
        importe_total: float = 0.0,
    ) -> dict:
        """
        Solicita un CAE a ARCA para un comprobante.

        Args:
            tipo_comprobante: "Factura A", "Factura B" o "Factura C"
            importe_total: Importe total del comprobante en ARS

        Returns:
            Dict con cae, vencimiento, numero, vto
        """
        logger.info(
            "Solicitando CAE: tipo=%s importe=%.2f ambiente=%s",
            tipo_comprobante, importe_total, self.ambiente,
        )

        tipo_map = {
            "Factura A": 1,
            "Factura B": 6,
            "Factura C": 11,
        }
        cod_tipo = tipo_map.get(tipo_comprobante, 1)

        try:
            auth = self.cliente.obtener_token()
            logger.info("Token WSAA obtenido correctamente")

            response = self.cliente.solicitar_cae(
                auth=auth,
                tipo_comprobante=cod_tipo,
                importe_total=importe_total,
                moneda="PES",
                cotizacion=1.0,
                concepto="Servicios",
            )

            cae = response.get("CAE", "")
            vencimiento = response.get("CAEVencimiento", "")
            numero = response.get("ComprobanteNumero", "")

            logger.info("CAE obtenido: %s vto: %s nro: %s", cae, vencimiento, numero)

            return {
                "cae": cae,
                "vencimiento": vencimiento,
                "numero": numero,
            }

        except Exception as e:
            logger.error("Error obteniendo CAE: %s", str(e))
            raise
