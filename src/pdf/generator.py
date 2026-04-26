import logging
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
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
        logo_html = (
            '<font size="16" color="#DC2626"><b>●</b></font>'
            '&nbsp;<font size="14" color="#111827"><b>ULTIMA MILLA</b></font>'
            '<br/><font size="7" color="#6B7280">Soluciones técnicas para pymes argentinas</font>'
        )
        title_html = (
            '<font size="13" color="#1A56C0"><b>FACTURA ELECTRÓNICA</b></font><br/>'
            '<font size="8" color="#6B7280">RG 5824 - ARCA</font>'
        )
        logo = Paragraph(logo_html, ParagraphStyle("logo", fontSize=1, leading=1))
        title = Paragraph(title_html, ParagraphStyle("title_right", alignment=TA_RIGHT))
        header_table = Table([[logo, title]], colWidths=[280, 280])
        header_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (0, 0), 0),
            ("RIGHTPADDING", (1, 1), (1, 1), 0),
        ]))
        return header_table

    def _emisor_block(self, data: dict):
        lines = [
            '<font color="#DC2626"><b>%s</b></font>' % data.get("razon_social", "—"),
            'CUIT: %s' % data.get("cuit", "—"),
            'Domicilio: %s' % data.get("domicilio", "—"),
            'IVA: %s' % data.get("condicion_iva", "—"),
            'Punto de Venta: %s' % data.get("punto_venta", "0001"),
        ]
        return Paragraph(
            "<br/>".join(lines),
            ParagraphStyle("emisor", fontSize=8, leading=12, spaceAfter=2),
        )

    def _comprobante_info(self, data: dict):
        lines = [
            '<b>Tipo:</b> %s' % data.get("tipo_comprobante", "—"),
            '<b>N°:</b> %s' % data.get("numero_comprobante", "—"),
            '<b>CAE:</b> %s' % data.get("cae", "—"),
            '<b>Vto. CAE:</b> %s' % data.get("vencimiento_cae", "—"),
            '<b>Fecha Emisión:</b> %s' % data.get("fecha_emision", "—"),
        ]
        return Paragraph(
            "<br/>".join(lines),
            ParagraphStyle("info", fontSize=8, leading=12, alignment=TA_RIGHT),
        )

    def _detail_table(self, items: list, total: float):
        cell = ParagraphStyle("cell", fontSize=8, leading=11)
        hdr = ParagraphStyle("hdr", fontSize=8, leading=11, textColor=white)
        headers = [
            Paragraph("<b>Concepto</b>", hdr),
            Paragraph("<b>Cant.</b>", hdr),
            Paragraph("<b>P. Unit.</b>", hdr),
            Paragraph("<b>Subtotal</b>", hdr),
        ]
        rows = [headers]
        for item in items:
            rows.append([
                Paragraph(item.get("descripcion", "—"), cell),
                Paragraph(str(item.get("cantidad", 1)), cell),
                Paragraph("$ {:,.2f}".format(item.get("precio_unitario", 0)), cell),
                Paragraph("$ {:,.2f}".format(item.get("subtotal", 0)), cell),
            ])
        tot = ParagraphStyle("tot", parent=cell, fontSize=10, textColor=PRIMARY)
        rows.append([
            Paragraph("", cell),
            Paragraph("", cell),
            Paragraph("<b>TOTAL</b>", tot),
            Paragraph("<b>$ {:,.2f}</b>".format(total), tot),
        ])
        col_widths = [240, 60, 100, 100]
        table = Table(rows, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), SECONDARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-2, -2), 0.5, HexColor("#E5E7EB")),
            ("BACKGROUND", (0, -1), (-1, -1), HexColor("#FEF2F2")),
            ("LINEABOVE", (0, -1), (-1, -1), 1, PRIMARY),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        return table

    def _build_qr(self, data: dict):
        qr_text = (
            "Factura %s | CUIT: %s | PV: %s | N°: %s | "
            "CAE: %s | Total: $%s" % (
                data.get("tipo_comprobante", ""),
                data.get("cuit", ""),
                data.get("punto_venta", ""),
                data.get("numero_comprobante", ""),
                data.get("cae", ""),
                "{:,.2f}".format(data.get("importe_total", 0)),
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
        filename = "factura_%s_%s.pdf" % (
            data.get("numero_comprobante", "NN").replace("/", "-"),
            datetime.now().strftime("%Y%m%d_%H%M%S"),
        )
        filepath = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(
            filepath, pagesize=A4,
            topMargin=1.5*cm, bottomMargin=1.5*cm,
            leftMargin=2*cm, rightMargin=2*cm,
        )

        story = [self._header_table(), Spacer(1, 15)]

        sep = Table([[""]], colWidths=[500])
        sep.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 1, PRIMARY)]))
        story.append(sep)
        story.append(Spacer(1, 15))

        info_data = [[self._emisor_block(data), self._comprobante_info(data)]]
        info_table = Table(info_data, colWidths=[280, 220])
        info_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
        story.append(info_table)
        story.append(Spacer(1, 15))

        story.append(Paragraph(
            '<font size="11" color="#111827"><b>Detalle del Comprobante</b></font>',
            ParagraphStyle("detalle", spaceAfter=6),
        ))

        items = data.get("items") or [{
            "descripcion": data.get("descripcion", ""),
            "cantidad": 1,
            "precio_unitario": data.get("importe_total", 0),
            "subtotal": data.get("importe_total", 0),
        }]
        story.append(self._detail_table(items, data.get("importe_total", 0)))
        story.append(Spacer(1, 15))

        qr_code = self._build_qr(data)
        if qr_code:
            qr_rows = [[
                qr_code,
                Paragraph(
                    "Este comprobante cumple con RG 5824 ARCA.<br/>"
                    "Generado por Ultima Milla - www.ultimamilla.com.ar",
                    ParagraphStyle("f", fontSize=7, leading=9, textColor=MEDIUM_GRAY),
                ),
            ]]
            qr_table = Table(qr_rows, colWidths=[70, 430])
            qr_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LINEABOVE", (0, 0), (-1, -1), 0.5, MEDIUM_GRAY),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
            ]))
            story.append(qr_table)

        doc.build(story)
        logger.info("PDF generado: %s", filepath)
        return filepath
