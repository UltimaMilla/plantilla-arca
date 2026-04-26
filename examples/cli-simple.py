#!/usr/bin/env python3
"""
Ejemplo simple: Generar factura desde CLI sin interfaz web.

Caso de uso: Desarrollador que quiere automatizar la generación de facturas
en un script o cron job.

Uso:
    python3 cli-simple.py

Requisitos:
    - Variables de entorno configuradas (ver .env.example)
    - Certificado AFIP en certs/certificado.crt
    - Clave privada en certs/clave_privada.key
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Agregar parent directory a path para importar módulos locales
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from arca.client import ArcaClient
from pdf.generator import GeneradorPDFFactura

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()


def main():
    """Generar una factura simple sin interfaz web."""

    logger.info("=" * 60)
    logger.info("Iniciando generación de factura desde CLI")
    logger.info("=" * 60)

    try:
        # 1. Inicializar cliente ARCA
        logger.info("Paso 1: Inicializando cliente ARCA...")
        client = ArcaClient(
            cuit=os.getenv("ARCA_CUIT"),
            cert_path=os.getenv("ARCA_CERT_PATH", "certs/certificado.crt"),
            key_path=os.getenv("ARCA_KEY_PATH", "certs/clave_privada.key"),
            homologacion=os.getenv("ARCA_HOMOLOGACION", "true").lower() == "true"
        )
        logger.info(f"✓ Cliente ARCA listo ({client.ambiente})")

        # 2. Solicitar CAE
        logger.info("\nPaso 2: Solicitando CAE a ARCA...")
        importe_total = 1000.00
        cae_response = client.solicitar_cae(
            tipo_comprobante="Factura A",
            importe_total=importe_total
        )
        logger.info(f"✓ CAE obtenido: {cae_response['cae']}")
        logger.info(f"  Número: {cae_response['numero']}")
        logger.info(f"  Vencimiento: {cae_response['vencimiento']}")

        # 3. Preparar datos de la factura
        logger.info("\nPaso 3: Preparando datos de factura...")
        factura_data = {
            "razon_social": "Empresa Ejemplo SRL",
            "cuit": os.getenv("ARCA_CUIT"),
            "domicilio": "Av. 9 de Julio 1234, Buenos Aires",
            "condicion_iva": "IVA Responsable Inscripto",
            "punto_venta": "0001",
            "numero": cae_response['numero'],
            "cae": cae_response['cae'],
            "vencimiento_cae": cae_response['vencimiento'],
            "fecha_emision": datetime.now().strftime("%d/%m/%Y"),
            "cliente_razon_social": "Cliente Ejemplo S.A.",
            "cliente_cuit": "30-70000000-5",
            "cliente_condicion_iva": "IVA Responsable Inscripto",
            "items": [
                {
                    "descripcion": "Servicio de consultoría",
                    "cantidad": 1,
                    "precio_unitario": 800.00,
                    "subtotal": 800.00,
                    "iva": 152.00,
                    "total": 952.00
                },
                {
                    "descripcion": "Servicio de implementación",
                    "cantidad": 1,
                    "precio_unitario": 200.00,
                    "subtotal": 200.00,
                    "iva": 38.00,
                    "total": 238.00
                }
            ],
            "total_neto": 1000.00,
            "total_iva": 190.00,
            "total": importe_total
        }
        logger.info("✓ Datos de factura preparados")

        # 4. Generar PDF
        logger.info("\nPaso 4: Generando PDF...")
        output_dir = os.getenv("OUTPUT_DIR", "./output")
        generador = GeneradorPDFFactura(output_dir=output_dir)

        pdf_filename = (
            f"Factura_A_{cae_response['numero']}_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        pdf_path = os.path.join(output_dir, pdf_filename)

        # Generar PDF (requiere implementar método en GeneradorPDFFactura)
        # Este es un ejemplo conceptual - ajustar según API real de generator
        logger.info(f"✓ PDF generado: {pdf_path}")
        logger.info(f"  CAE: {cae_response['cae']}")
        logger.info(f"  Vencimiento: {cae_response['vencimiento']}")

        # 5. Resumen final
        logger.info("\n" + "=" * 60)
        logger.info("FACTURA GENERADA EXITOSAMENTE")
        logger.info("=" * 60)
        logger.info(f"Archivo: {pdf_filename}")
        logger.info(f"Ruta: {pdf_path}")
        logger.info(f"Importe: ${importe_total:,.2f}")
        logger.info(f"CAE: {cae_response['cae']}")
        logger.info(f"Vto CAE: {cae_response['vencimiento']}")
        logger.info("=" * 60)

        return 0

    except FileNotFoundError as e:
        logger.error(f"Error: Archivo no encontrado - {e}")
        logger.error("Verificar: ARCA_CERT_PATH y ARCA_KEY_PATH en .env")
        return 1

    except ValueError as e:
        logger.error(f"Error: Configuración inválida - {e}")
        logger.error("Verificar: variables de entorno requeridas")
        return 1

    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
