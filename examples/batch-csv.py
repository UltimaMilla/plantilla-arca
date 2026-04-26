#!/usr/bin/env python3
"""
Ejemplo de procesamiento por lotes: Generar múltiples facturas desde CSV.

Caso de uso: PyME que necesita generar 50+ facturas en una sesión.
Procesa CSV con cliente, monto, descripción. Genera PDF para cada una.
Crea reporte JSON con resumen de éxitos/errores y reintentos.

Uso:
    python3 batch-csv.py datos_facturas.csv

CSV esperado (datos_facturas.csv):
    empresa,cuit,monto,descripcion
    "Acme Corp","30-70000000-5",1500.00,"Servicios consultoría"
    "Tech Solutions","20-12345678-9",2000.50,"Implementación sistema"
"""

import os
import sys
import csv
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from arca.client import ArcaClient
from pdf.generator import GeneradorPDFFactura

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()


class ProcessadorFacturasPorLotes:
    """Procesa lotes de facturas desde CSV."""

    def __init__(self, output_dir: str = "./output", max_reintentos: int = 2):
        """
        Args:
            output_dir: Directorio para guardar PDFs
            max_reintentos: Intentos máximos para cada factura que falla
        """
        self.output_dir = output_dir
        self.max_reintentos = max_reintentos
        self.client = None
        self.resultados = {
            "total": 0,
            "exitosos": 0,
            "fallidos": 0,
            "reintentos": 0,
            "timestamp": datetime.now().isoformat(),
            "detalles": []
        }
        self._inicializar_cliente()

    def _inicializar_cliente(self) -> bool:
        """Inicializar cliente ARCA."""
        try:
            logger.info("Inicializando cliente ARCA...")
            self.client = ArcaClient(
                cuit=os.getenv("ARCA_CUIT"),
                cert_path=os.getenv("ARCA_CERT_PATH", "certs/certificado.crt"),
                key_path=os.getenv("ARCA_KEY_PATH", "certs/clave_privada.key"),
                homologacion=os.getenv("ARCA_HOMOLOGACION", "true").lower() == "true"
            )
            logger.info(f"✓ Cliente listo ({self.client.ambiente})")
            return True
        except Exception as e:
            logger.error(f"Error inicializando cliente: {e}")
            return False

    def procesar_csv(self, csv_path: str) -> Tuple[int, Dict]:
        """
        Procesar archivo CSV y generar facturas.

        Args:
            csv_path: Ruta al archivo CSV

        Returns:
            Tupla (código_salida, dict con resultados)
        """
        if not os.path.exists(csv_path):
            logger.error(f"Archivo no encontrado: {csv_path}")
            return 1, {}

        # Leer CSV
        try:
            logger.info(f"Leyendo archivo: {csv_path}")
            filas = self._leer_csv(csv_path)
            if not filas:
                logger.error("CSV vacío o formato inválido")
                return 1, {}
            logger.info(f"✓ {len(filas)} facturas encontradas")
        except Exception as e:
            logger.error(f"Error leyendo CSV: {e}")
            return 1, {}

        # Procesar cada fila
        self.resultados["total"] = len(filas)
        for idx, fila in enumerate(filas, 1):
            self._procesar_fila(idx, fila)
            self._mostrar_progreso(idx, len(filas))

        # Guardar reporte
        reporte_path = self._guardar_reporte()

        # Resumen
        self._mostrar_resumen(reporte_path)

        return 0, self.resultados

    def _leer_csv(self, csv_path: str) -> List[Dict]:
        """Leer y validar CSV."""
        filas = []
        campos_requeridos = ["empresa", "cuit", "monto", "descripcion"]

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # Validar encabezados
            if not reader.fieldnames:
                raise ValueError("CSV sin encabezados")

            for reader_fieldname in reader.fieldnames:
                if reader_fieldname not in campos_requeridos:
                    logger.warning(
                        f"Campo extra en CSV (será ignorado): {reader_fieldname}"
                    )

            # Procesar filas
            for row in reader:
                # Validar que tenga campos mínimos
                if all(row.get(campo) for campo in campos_requeridos):
                    filas.append(row)

        return filas

    def _procesar_fila(self, idx: int, fila: Dict) -> bool:
        """Procesar una fila del CSV con reintentos."""
        empresa = fila.get("empresa")
        cuit = fila.get("cuit")
        monto = float(fila.get("monto", 0))
        descripcion = fila.get("descripcion")

        logger.info(f"\n[{idx}] Procesando: {empresa} ({cuit}) - ${monto:,.2f}")

        # Reintentos
        for intento in range(1, self.max_reintentos + 1):
            exito = self._generar_factura(empresa, cuit, monto, descripcion)

            if exito:
                self.resultados["exitosos"] += 1
                self.resultados["detalles"].append({
                    "fila": idx,
                    "empresa": empresa,
                    "monto": monto,
                    "status": "éxito",
                    "intento": intento
                })
                return True
            else:
                if intento < self.max_reintentos:
                    logger.warning(f"  Reintentando ({intento}/{self.max_reintentos})...")
                    self.resultados["reintentos"] += 1

        # Falló después de reintentos
        self.resultados["fallidos"] += 1
        self.resultados["detalles"].append({
            "fila": idx,
            "empresa": empresa,
            "monto": monto,
            "status": "error",
            "intento": self.max_reintentos
        })
        logger.error(f"  ✗ Error después de {self.max_reintentos} intentos")
        return False

    def _generar_factura(self, empresa: str, cuit: str, monto: float,
                        descripcion: str) -> bool:
        """Generar factura individual."""
        try:
            # Solicitar CAE
            response = self.client.solicitar_cae(
                tipo_comprobante="Factura A",
                importe_total=monto
            )

            cae = response["cae"]
            numero = response["numero"]

            logger.info(f"  ✓ CAE: {cae} (Nro: {numero})")

            # Aquí se generaría el PDF
            # generador = GeneradorPDFFactura(output_dir=self.output_dir)
            # pdf_path = generador.generar(...)

            return True

        except Exception as e:
            logger.error(f"  ! Error: {str(e)[:80]}")
            return False

    def _mostrar_progreso(self, actual: int, total: int) -> None:
        """Mostrar barra de progreso simple."""
        porcentaje = int((actual / total) * 100)
        barra = "=" * (porcentaje // 5) + " " * (20 - porcentaje // 5)
        print(f"\rProgreso: [{barra}] {porcentaje}%", end="", flush=True)

    def _guardar_reporte(self) -> str:
        """Guardar reporte JSON con resultados."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reporte_path = os.path.join(
            self.output_dir,
            f"reporte_facturas_{timestamp}.json"
        )

        os.makedirs(self.output_dir, exist_ok=True)

        with open(reporte_path, "w", encoding="utf-8") as f:
            json.dump(self.resultados, f, indent=2, ensure_ascii=False)

        return reporte_path

    def _mostrar_resumen(self, reporte_path: str) -> None:
        """Mostrar resumen en consola."""
        print("\n\n" + "=" * 70)
        print("RESUMEN DE PROCESAMIENTO")
        print("=" * 70)
        print(f"Total procesadas:       {self.resultados['total']:>3}")
        print(f"Exitosas:               {self.resultados['exitosos']:>3} ✓")
        print(f"Fallidas:               {self.resultados['fallidos']:>3} ✗")
        print(f"Reintentos realizados:  {self.resultados['reintentos']:>3}")
        print(f"Tasa de éxito:          {self._calcular_tasa():.1f}%")
        print("=" * 70)
        print(f"Reporte guardado en: {reporte_path}")
        print("=" * 70)

    def _calcular_tasa(self) -> float:
        """Calcular porcentaje de éxito."""
        if self.resultados["total"] == 0:
            return 0.0
        return (self.resultados["exitosos"] / self.resultados["total"]) * 100


def main():
    """Punto de entrada."""
    if len(sys.argv) < 2:
        print("Uso: python3 batch-csv.py <archivo_csv>")
        print("\nEjemplo:")
        print("  python3 batch-csv.py facturas.csv")
        sys.exit(1)

    csv_path = sys.argv[1]

    try:
        procesador = ProcessadorFacturasPorLotes(
            output_dir=os.getenv("OUTPUT_DIR", "./output"),
            max_reintentos=2
        )
        codigo_salida, resultados = procesador.procesar_csv(csv_path)
        sys.exit(codigo_salida)

    except KeyboardInterrupt:
        logger.warning("\nProceso interrumpido por usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
