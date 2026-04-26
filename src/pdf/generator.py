import logging
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing

logger = logging.getLogger(__name__)

PRIMARY = HexColor("#DC2626")
SECONDARY = HexColor("#1A56C0")
DARK = HexColor("#111827")
LIGHT_GRAY = HexColor("#F3F4F6")
MEDIUM_GRAY = HexColor("#9CA3AF")


class GeneradorPDFFactura:
    def __init__(self, output_dir: str = "./output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _header_table(self):
        logo_svg = (
            '<img src="https://ultimamilla.com.ar/images/logo-dark.svg" '
            'width="180" height="29" valign="middle"/>'
        )

        title_html = """
        <para align="right">
            <font size="14" color="#1A56C0"><b>FACTURA ELECTRÓNICA</b></font><br/>
            <font size="8" color="#6B7280">RG 5824 - ARCA</font>
        </para>
        """

        logo = Paragraph(logo_svg, ParagraphStyle("logo", fontSize=1, leading=1))
        title = Paragraph(title_html, ParagraphStyle("title_right", alignment=TA_RIGHT))

        header_data = [[logo, title]]
        header_table = Table(header_data, colWidths=[280, 280])
        header_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (0, 0), 0),
            ("RIGHTPADDING", (1, 1), (1, 1), 0),
        ]))
        return header_table

    def _emisor_block(self, data: dict):
        style = ParagraphStyle("emisor", fontSize=8, leading=12, spaceAfter=2)
        lines = [
            f'<font color="#DC2626"><b>{data.get("razon_social", "—")}</b></font>',
            f'CUIT: {data.get("cuit", "—")}',
            f'Domicilio: {data.get("domicilio", "—")}',
            f'IVA: {data.get("condicion_iva", "—")}',
            f'Punto de Venta: {data.get("punto_venta", "0001")}',
        ]
        return Paragraph("<br/>".join(lines), style)

    def _comprobante_info(self, data: dict):
        style = ParagraphStyle("info", fontSize=8, leading=12, alignment=TA_RIGHT)
        lines = [
            f'<b>Tipo:</b> {data.get("tipo_comprobante", "—")}',
            f'<b>N°:</b> {data.get("numero_comprobante", "—")}',
            f'<b>CAE:</b> {data.get("cae", "—")}',
            f'<b>Vto. CAE:</b> {data.get("vencimiento_cae", "—")}',
            f'<b>Fecha Emisión:</b> {data.get("fecha_emision", "—")}',
        ]
        return Paragraph("<br/>".join(lines), style)

    def _detail_table(self, items: list, total: float):
        cell_style = ParagraphStyle("cell", fontSize=8, leading=11)
        header_style = ParagraphStyle("hdr", fontSize=8, leading=11, textColor=white)

        headers = [
            Paragraph("<b>Concepto</b>", header_style),
            Paragraph("<b>Cant.</b>", header_style),
            Paragraph("<b>P. Unit.</b>", header_style),
            Paragraph("<b>Subtotal</b>", header_style),
        ]

        rows = [headers]
        for item in items:
            rows.append([
                Paragraph(item.get("descripcion", "—"), cell_style),
                Paragraph(str(item.get("cantidad", 1)), cell_style),
                Paragraph("$ {:,.2f}".format(item.get("precio_unitario", 0)), cell_style),
                Paragraph("$ {:,.2f}".format(item.get("subtotal", 0)), cell_style),
            ])

        total_style = ParagraphStyle("b", parent=cell_style, fontSize=10, textColor=PRIMARY)
        rows.append([
            Paragraph("", cell_style),
            Paragraph("", cell_style),
            Paragraph("<b>TOTAL</b>", total_style),
            Paragraph("<b>$ {:,.2f}</b>".format(total), total_style),
        ])

        col_widths = [240, 60, 100, 100]
        table = Table(rows, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), SECONDARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-2, -2), 0.5, HexColor("#E5E7EB")),
            ("BACKGROUND", (0, -1), (-1, -1), HexColor("#FEF2F2")),
            ("LINEABOVE", (0, -1), (-1, -1), 1, PRIMARY),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        return table

    def _build_qr(self, data: dict):
        qr_text = (
            "Factura {} | CUIT: {} | PV: {} | N°: {} | "
            "CAE: {} | Total: ${:,.2f}".format(
                data.get("tipo_comprobante", ""),
                data.get("cuit", ""),
                data.get("punto_venta", ""),
                data.get("numero_comprobante", ""),
                data.get("cae", ""),
                data.get("importe_total", 0),
            )
        )
        try:
            qr_code = qr.QrCodeWidget(qr_text, barHeight=60, barWidth=60)
            d = Drawing(65, 65)
            d.add(qr_code)
            return d
        except Exception:
            return None

    def generar(self, data: dict) -> str:
        filename = "factura_{}_{}.pdf".format(
            data.get("numero_comprobante", "NN"),
            datetime.now().strftime("%Y%m%d_%H%M%S"),
        )
        filepath = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
        )

        story = []

        # Header with logo
        story.append(self._header_table())
        story.append(Spacer(1, 15))

        # Separator line
        sep_table = Table([[""]], colWidths=[500])
        sep_table.setStyle(TableStyle([
            ("LINEBELOW", (0, 0), (-1, -1), 1, PRIMARY),
        ]))
        story.append(sep_table)
        story.append(Spacer(1, 15))

        # Emisor + Comprobante info side by side
        info_data = [[self._emisor_block(data), self._comprobante_info(data)]]
        info_table = Table(info_data, colWidths=[280, 220])
        info_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 15))

        # Detail header
        story.append(Paragraph(
            '<font size="11" color="#111827"><b>Detalle del Comprobante</b></font>',
            ParagraphStyle("detalle", spaceAfter=6),
        ))

        # Detail table
        items = data.get(
            "items",
            [
                {
                    "descripcion": data.get("descripcion", ""),
                    "cantidad": 1,
                    "precio_unitario": data.get("importe_total", 0),
                    "subtotal": data.get("importe_total", 0),
                }
            ],
        )
        story.append(self._detail_table(items, data.get("importe_total", 0)))
        story.append(Spacer(1, 15))

        # QR + footer
        qr_code = self._build_qr(data)
        if qr_code:
            qr_data = [
                [
                    qr_code,
                    Paragraph(
                        "Este comprobante cumple con RG 5824 ARCA.<br/>"
                        "Generado por Ultima Milla - www.ultimamilla.com.ar",
                        ParagraphStyle("qr_footer", fontSize=7, leading=9, textColor=MEDIUM_GRAY),
                    ),
                ]
            ]
            qr_table = Table(qr_data, colWidths=[70, 430])
            qr_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LINEABOVE", (0, 0), (-1, -1), 0.5, MEDIUM_GRAY),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
            ]))
            story.append(qr_table)

        doc.build(story)
        logger.info("PDF generado: %s", filepath)
        return filepath
