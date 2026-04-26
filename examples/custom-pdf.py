#!/usr/bin/env python3
"""
Ejemplo de personalización de template PDF.

Caso de uso: Empresa con requisitos de branding específico.
Personaliza header, tabla de detalles, footer con logo y colores.

Subclasea GeneradorPDFFactura para:
  - Cambiar colores (azul en lugar de rojo)
  - Ajustar layout de tabla de items
  - Agregar footer con información de empresa
  - Posicionar logo personalizado

Uso:
    generador = GeneradorPDFFacturaPersonalizado(
        output_dir="./output",
        logo_url="https://empresa.com/logo.png"
    )
    pdf_path = generador.generar_factura(datos_factura)
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white, black, lightgrey
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.graphics.barcode import qr as qr_module
from reportlab.graphics.shapes import Drawing

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pdf.generator import GeneradorPDFFactura

logger = logging.getLogger(__name__)


class GeneradorPDFFacturaPersonalizado(GeneradorPDFFactura):
    """
    Generador de PDF personalizado con branding corporativo.

    Personaliza:
    - Colores: azul corporativo (#0066CC) en lugar de rojo
    - Header: Logo + info empresa en azul
    - Tabla de items: columnas anchas, fuente más grande
    - Footer: Datos bancarios, website, teléfono
    - Márgenes: reducidos para más contenido
    """

    # Colores personalizados
    COLOR_PRIMARIO = HexColor("#0066CC")      # Azul corporativo
    COLOR_SECUNDARIO = HexColor("#003399")    # Azul oscuro
    COLOR_ACENTO = HexColor("#99CCFF")        # Azul claro
    COLOR_TEXTO = HexColor("#1A1A1A")         # Gris oscuro
    COLOR_GRIS = HexColor("#CCCCCC")

    def __init__(self, output_dir: str = "./output", logo_url: str = None):
        """
        Args:
            output_dir: Directorio para guardar PDFs
            logo_url: URL del logo personalizado (PNG/JPG)
        """
        super().__init__(output_dir=output_dir)
        self.logo_url = logo_url
        self.estilos = getSampleStyleSheet()
        self._crear_estilos_personalizados()

    def _crear_estilos_personalizados(self) -> None:
        """Crear estilos personalizados de ReportLab."""
        # Estilo para título
        self.estilos.add(ParagraphStyle(
            name="titulo_personalizado",
            fontSize=14,
            textColor=self.COLOR_PRIMARIO,
            fontName="Helvetica-Bold",
            alignment=TA_CENTER,
            spaceAfter=10
        ))

        # Estilo para subtítulo
        self.estilos.add(ParagraphStyle(
            name="subtitulo_personalizado",
            fontSize=10,
            textColor=self.COLOR_SECUNDARIO,
            fontName="Helvetica",
            alignment=TA_CENTER
        ))

        # Estilo para encabezados de tabla
        self.estilos.add(ParagraphStyle(
            name="header_tabla",
            fontSize=11,
            textColor=white,
            fontName="Helvetica-Bold",
            alignment=TA_LEFT,
            leftIndent=5
        ))

        # Estilo para contenido de tabla
        self.estilos.add(ParagraphStyle(
            name="contenido_tabla",
            fontSize=10,
            textColor=self.COLOR_TEXTO,
            fontName="Helvetica",
            alignment=TA_LEFT,
            leftIndent=5
        ))

    def _header_table_personalizado(self) -> Table:
        """
        Header personalizado con:
        - Logo a la izquierda
        - Título + subtítulo a la derecha
        - Fondo azul corporativo
        """
        # Logo (simplificado - en producción sería una imagen real)
        logo_html = (
            '<font size="20" color="#0066CC"><b>●</b></font> '
            '<font size="16" color="#1A1A1A"><b>EMPRESA</b></font><br/>'
            '<font size="8" color="#666666">Soluciones Profesionales</font>'
        )
        logo_elem = Paragraph(logo_html, self.estilos["Normal"])

        # Título derecha
        titulo_html = (
            '<font size="13" color="#0066CC"><b>FACTURA ELECTRÓNICA</b></font><br/>'
            '<font size="8" color="#0066CC">RG 5824 / ARCA</font>'
        )
        titulo_elem = Paragraph(titulo_html, self.estilos["titulo_personalizado"])

        # Tabla header
        header_table = Table(
            [[logo_elem, titulo_elem]],
            colWidths=[280, 280],
            rowHeights=[60]
        )

        header_table.setStyle(TableStyle([
            # Fondo azul
            ("BACKGROUND", (0, 0), (-1, 0), self.COLOR_ACENTO),
            # Bordes
            ("LINEBELOW", (0, 0), (-1, 0), 2, self.COLOR_PRIMARIO),
            # Padding
            ("LEFTPADDING", (0, 0), (0, 0), 15),
            ("RIGHTPADDING", (1, 0), (1, 0), 15),
            ("TOPPADDING", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            # Alineación
            ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
            ("ALIGN", (0, 0), (0, 0), "LEFT"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ]))

        return header_table

    def _tabla_items_personalizada(self, items: list) -> Table:
        """
        Tabla de items con:
        - Header azul con texto blanco
        - Alternancia de colores de fila
        - Columnas: Descripción (ancha), Cantidad, P.U., Subtotal
        """
        datos = [
            [
                Paragraph("<b>DESCRIPCIÓN</b>", self.estilos["header_tabla"]),
                Paragraph("<b>CANTIDAD</b>", self.estilos["header_tabla"]),
                Paragraph("<b>P. UNITARIO</b>", self.estilos["header_tabla"]),
                Paragraph("<b>SUBTOTAL</b>", self.estilos["header_tabla"]),
            ]
        ]

        # Agregar items
        for idx, item in enumerate(items):
            descripcion = item.get("descripcion", "—")
            cantidad = item.get("cantidad", 1)
            precio_unitario = item.get("precio_unitario", 0)
            subtotal = item.get("subtotal", 0)

            datos.append([
                Paragraph(descripcion, self.estilos["contenido_tabla"]),
                Paragraph(f"{cantidad:,.0f}", self.estilos["contenido_tabla"]),
                Paragraph(f"${precio_unitario:,.2f}", self.estilos["contenido_tabla"]),
                Paragraph(f"${subtotal:,.2f}", self.estilos["contenido_tabla"]),
            ])

        # Crear tabla
        tabla_items = Table(
            datos,
            colWidths=[280, 80, 100, 100],
            repeatRows=1  # Repetir header en saltos de página
        )

        # Estilos
        estilo = TableStyle([
            # Header
            ("BACKGROUND", (0, 0), (-1, 0), self.COLOR_PRIMARIO),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 11),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("TOPPADDING", (0, 0), (-1, 0), 8),
            # Línea debajo de header
            ("LINEBELOW", (0, 0), (-1, 0), 1, self.COLOR_PRIMARIO),
            # Filas de contenido
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 10),
            ("VALIGN", (0, 1), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 1), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
            # Alternancia de colores (zebra striping)
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, self.COLOR_ACENTO]),
            # Bordes
            ("GRID", (0, 0), (-1, -1), 0.5, self.COLOR_GRIS),
            # Alineación de números a la derecha
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ("ALIGN", (0, 1), (0, -1), "LEFT"),
        ])

        tabla_items.setStyle(estilo)
        return tabla_items

    def _footer_personalizado(self, datos: dict) -> Table:
        """
        Footer personalizado con:
        - Información de empresa (teléfono, website, dirección)
        - Datos bancarios
        - Nota fiscal
        """
        info_empresa = (
            f"Tel: {datos.get('telefono', '(011) XXXX-XXXX')} | "
            f"Web: {datos.get('website', 'www.empresa.com.ar')} | "
            f"Email: {datos.get('email', 'info@empresa.com.ar')}"
        )

        datos_bancarios = (
            f"CBU: {datos.get('cbu', '—')} | "
            f"Banco: {datos.get('banco', '—')} | "
            f"Titular: {datos.get('titular_cuenta', '—')}"
        )

        condiciones = "Condiciones: " + datos.get(
            "condiciones_pago",
            "Contado. Consultar otras formas de pago."
        )

        footer_table = Table(
            [
                [Paragraph(
                    f'<font size="8" color="#666666">{info_empresa}</font>',
                    self.estilos["Normal"]
                )],
                [Paragraph(
                    f'<font size="8" color="#666666">{datos_bancarios}</font>',
                    self.estilos["Normal"]
                )],
                [Paragraph(
                    f'<font size="8" color="#0066CC"><i>{condiciones}</i></font>',
                    self.estilos["Normal"]
                )],
            ],
            colWidths=[560]
        )

        footer_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LINEABOVE", (0, 0), (-1, 0), 1, self.COLOR_PRIMARIO),
        ]))

        return footer_table

    def generar_factura(self, datos: dict) -> str:
        """
        Generar PDF personalizado.

        Args:
            datos: Dict con todos los datos de la factura

        Returns:
            Ruta al PDF generado
        """
        filename = (
            f"Factura_{datos['numero']}_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        pdf_path = os.path.join(self.output_dir, filename)

        # Crear documento
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            topMargin=0.5 * cm,
            bottomMargin=1 * cm,
            leftMargin=1 * cm,
            rightMargin=1 * cm
        )

        # Elementos
        elementos = []

        # Header
        elementos.append(self._header_table_personalizado())
        elementos.append(Spacer(1, 0.3 * cm))

        # Datos emisor y receptor
        emisor_receptor = self._tabla_datos_emisor_receptor(datos)
        elementos.append(emisor_receptor)
        elementos.append(Spacer(1, 0.3 * cm))

        # Tabla de items
        items_tabla = self._tabla_items_personalizada(datos.get("items", []))
        elementos.append(items_tabla)
        elementos.append(Spacer(1, 0.3 * cm))

        # Totales
        totales_tabla = self._tabla_totales(datos)
        elementos.append(totales_tabla)
        elementos.append(Spacer(1, 0.3 * cm))

        # Footer
        footer = self._footer_personalizado(datos)
        elementos.append(footer)

        # Generar PDF
        try:
            doc.build(elementos)
            logger.info(f"PDF generado: {pdf_path}")
            return pdf_path
        except Exception as e:
            logger.error(f"Error generando PDF: {e}")
            raise

    def _tabla_datos_emisor_receptor(self, datos: dict) -> Table:
        """Tabla con datos de emisor y receptor."""
        emisor_html = (
            f"<b>EMISOR</b><br/>"
            f"{datos.get('razon_social', '—')}<br/>"
            f"CUIT: {datos.get('cuit', '—')}<br/>"
            f"Dirección: {datos.get('domicilio', '—')}<br/>"
            f"Condición IVA: {datos.get('condicion_iva', '—')}"
        )

        receptor_html = (
            f"<b>RECEPTOR</b><br/>"
            f"{datos.get('cliente_razon_social', '—')}<br/>"
            f"CUIT: {datos.get('cliente_cuit', '—')}<br/>"
            f"Dirección: {datos.get('cliente_domicilio', '—')}<br/>"
            f"Condición IVA: {datos.get('cliente_condicion_iva', '—')}"
        )

        comprobante_html = (
            f"<b>COMPROBANTE</b><br/>"
            f"Nro: {datos.get('numero', '—')}<br/>"
            f"CAE: {datos.get('cae', '—')}<br/>"
            f"Vto CAE: {datos.get('vencimiento_cae', '—')}<br/>"
            f"Fecha: {datos.get('fecha_emision', '—')}"
        )

        tabla = Table(
            [
                [
                    Paragraph(emisor_html, self.estilos["Normal"]),
                    Paragraph(receptor_html, self.estilos["Normal"]),
                    Paragraph(comprobante_html, self.estilos["Normal"]),
                ]
            ],
            colWidths=[180, 180, 180]
        )

        tabla.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LINEABOVE", (0, 0), (-1, 0), 1, self.COLOR_GRIS),
            ("LINEBELOW", (0, 0), (-1, -1), 1, self.COLOR_GRIS),
            ("GRID", (0, 0), (-1, -1), 0.5, self.COLOR_GRIS),
        ]))

        return tabla

    def _tabla_totales(self, datos: dict) -> Table:
        """Tabla de totales alineada a la derecha."""
        total_neto = datos.get("total_neto", 0)
        total_iva = datos.get("total_iva", 0)
        total = datos.get("total", 0)

        tabla = Table(
            [
                ["NETO:", f"${total_neto:,.2f}"],
                ["IVA (21%):", f"${total_iva:,.2f}"],
                ["TOTAL:", f"${total:,.2f}"],
            ],
            colWidths=[450, 110]
        )

        tabla.setStyle(TableStyle([
            ("ALIGN", (0, 0), (0, -1), "RIGHT"),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (0, -2), "Helvetica"),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (0, -2), 10),
            ("FONTSIZE", (0, -1), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LINEABOVE", (0, -1), (-1, -1), 2, self.COLOR_PRIMARIO),
            ("TEXTCOLOR", (0, -1), (-1, -1), self.COLOR_PRIMARIO),
        ]))

        return tabla


# ============================================================================
# Ejemplo de uso
# ============================================================================

if __name__ == "__main__":
    # Datos de ejemplo
    datos_ejemplo = {
        "numero": "0001-00000123",
        "cae": "12345678901234",
        "vencimiento_cae": "30042026",
        "fecha_emision": "26/04/2026",
        "razon_social": "Empresa S.A.",
        "cuit": "30-12345678-9",
        "domicilio": "Av. Principal 1234, Buenos Aires",
        "condicion_iva": "IVA Responsable Inscripto",
        "cliente_razon_social": "Cliente SRL",
        "cliente_cuit": "20-87654321-6",
        "cliente_domicilio": "Calle Secundaria 5678",
        "cliente_condicion_iva": "IVA Responsable",
        "items": [
            {
                "descripcion": "Servicio de consultoría empresarial",
                "cantidad": 10,
                "precio_unitario": 150.00,
                "subtotal": 1500.00
            },
            {
                "descripcion": "Implementación de sistema",
                "cantidad": 1,
                "precio_unitario": 2500.00,
                "subtotal": 2500.00
            }
        ],
        "total_neto": 4000.00,
        "total_iva": 840.00,
        "total": 4840.00,
        "telefono": "(011) 4123-4567",
        "website": "www.empresa.com.ar",
        "email": "ventas@empresa.com.ar",
        "cbu": "1234567890123456789012",
        "banco": "Banco Nación",
        "titular_cuenta": "Empresa S.A.",
        "condiciones_pago": "30 días. Transferencia bancaria.",
    }

    # Generar PDF
    generador = GeneradorPDFFacturaPersonalizado(output_dir="./output")
    pdf_path = generador.generar_factura(datos_ejemplo)
    print(f"PDF creado: {pdf_path}")
