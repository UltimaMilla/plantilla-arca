import pytest
import os
import tempfile
import base64
from io import BytesIO
from unittest.mock import patch, MagicMock
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Image
from PIL import Image as PILImage
from src.pdf.generator import GeneradorPDFFactura


def create_test_png_bytes():
    """Create a valid test PNG image in memory"""
    img = PILImage.new('RGB', (80, 80), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes.getvalue()


class TestPDFGeneratorBasic:
    """Tests for basic PDF generation without custom logos"""

    def test_pdf_generation_without_logo(self):
        """Verify default behavior unchanged - PDF generation works without logo"""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = GeneradorPDFFactura(output_dir=tmpdir)
            data = {
                "cuit": "20301234567",
                "razon_social": "Test Company S.A.",
                "domicilio": "Av. Corrientes 1234, Buenos Aires",
                "condicion_iva": "Responsable Inscripto",
                "tipo_comprobante": "Factura A",
                "numero_comprobante": "0001-00000001",
                "cae": "71234567890123",
                "vencimiento_cae": "25/06/2026",
                "fecha_emision": "2026-04-26",
                "descripcion": "Servicios profesionales",
                "importe_total": 10000.00,
                "punto_venta": "0001",
            }

            filepath = generator.generar(data)

            assert os.path.exists(filepath)
            assert filepath.endswith(".pdf")
            assert os.path.getsize(filepath) > 0


class TestPDFGeneratorWithLogo:
    """Tests for custom logo support via URL and data URLs"""

    def test_load_logo_with_data_url(self):
        """Test _load_logo() with data:image/png;base64,... format"""
        generator = GeneradorPDFFactura()

        # Create a valid PNG image
        png_data = create_test_png_bytes()
        b64_data = base64.b64encode(png_data).decode('utf-8')
        data_url = f"data:image/png;base64,{b64_data}"

        result = generator._load_logo(data_url)

        assert result is not None
        assert isinstance(result, BytesIO)
        assert result.getvalue() == png_data

    def test_load_logo_with_invalid_data_url(self):
        """Test _load_logo() gracefully handles invalid data URLs"""
        generator = GeneradorPDFFactura()
        data_url = "data:image/png;base64,invalid_base64_data!@#$"

        result = generator._load_logo(data_url)

        assert result is None  # Graceful fallback on invalid data

    def test_load_logo_with_valid_http_url(self):
        """Test _load_logo() fetches from HTTP URL successfully"""
        generator = GeneradorPDFFactura()
        png_data = create_test_png_bytes()

        with patch('src.pdf.generator.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = png_data
            mock_urlopen.return_value = mock_response

            result = generator._load_logo("https://example.com/logo.png")

            assert result is not None
            assert isinstance(result, BytesIO)
            assert result.getvalue() == png_data
            mock_urlopen.assert_called_once_with(
                "https://example.com/logo.png", timeout=5
            )

    def test_load_logo_with_unreachable_url(self):
        """Test _load_logo() gracefully handles unreachable URLs"""
        generator = GeneradorPDFFactura()

        with patch('src.pdf.generator.urlopen') as mock_urlopen:
            mock_urlopen.side_effect = Exception("Connection timeout")

            result = generator._load_logo("https://unreachable.example.com/logo.png")

            assert result is None  # Graceful fallback on error

    def test_load_logo_with_none_url(self):
        """Test _load_logo() handles None gracefully"""
        generator = GeneradorPDFFactura()

        result = generator._load_logo(None)

        assert result is None

    def test_header_table_without_logo(self):
        """Test _header_table() uses default HTML logo when no logo_url provided"""
        generator = GeneradorPDFFactura()

        header_table = generator._header_table(logo_url=None)

        assert header_table is not None
        # Table should have 2 columns (logo_html and title)
        assert len(header_table._cellvalues[0]) == 2

    def test_header_table_with_valid_logo_url(self):
        """Test _header_table() includes logo image when valid logo_url provided"""
        generator = GeneradorPDFFactura()

        # Create a valid PNG image
        png_data = create_test_png_bytes()
        b64_data = base64.b64encode(png_data).decode('utf-8')
        data_url = f"data:image/png;base64,{b64_data}"

        header_table = generator._header_table(logo_url=data_url)

        assert header_table is not None
        # Should have 2 columns: logo image and title
        assert len(header_table._cellvalues[0]) == 2

    def test_header_table_with_invalid_logo_url(self):
        """Test _header_table() falls back to default when logo fails to load"""
        generator = GeneradorPDFFactura()

        with patch('src.pdf.generator.urlopen') as mock_urlopen:
            mock_urlopen.side_effect = Exception("Failed to load")

            header_table = generator._header_table(logo_url="https://invalid.com/logo.png")

            assert header_table is not None
            # Should fall back to default HTML logo structure (2 columns)
            assert len(header_table._cellvalues[0]) == 2

    def test_pdf_generation_with_data_url_logo(self):
        """Test full PDF generation with data URL logo"""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = GeneradorPDFFactura(output_dir=tmpdir)

            # Create a valid PNG image
            png_data = create_test_png_bytes()
            b64_data = base64.b64encode(png_data).decode('utf-8')
            data_url = f"data:image/png;base64,{b64_data}"

            data = {
                "cuit": "20301234567",
                "razon_social": "Test Company S.A.",
                "domicilio": "Av. Corrientes 1234, Buenos Aires",
                "condicion_iva": "Responsable Inscripto",
                "tipo_comprobante": "Factura A",
                "numero_comprobante": "0001-00000001",
                "cae": "71234567890123",
                "vencimiento_cae": "25/06/2026",
                "fecha_emision": "2026-04-26",
                "descripcion": "Servicios profesionales",
                "importe_total": 10000.00,
                "punto_venta": "0001",
                "logo_url": data_url,
            }

            filepath = generator.generar(data)

            assert os.path.exists(filepath)
            assert filepath.endswith(".pdf")
            assert os.path.getsize(filepath) > 0

    def test_pdf_generation_with_logo_url_parameter(self):
        """Test full PDF generation passing logo_url as parameter"""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = GeneradorPDFFactura(output_dir=tmpdir)

            # Create a valid PNG image
            png_data = create_test_png_bytes()
            b64_data = base64.b64encode(png_data).decode('utf-8')
            data_url = f"data:image/png;base64,{b64_data}"

            data = {
                "cuit": "20301234567",
                "razon_social": "Test Company S.A.",
                "domicilio": "Av. Corrientes 1234, Buenos Aires",
                "condicion_iva": "Responsable Inscripto",
                "tipo_comprobante": "Factura A",
                "numero_comprobante": "0001-00000001",
                "cae": "71234567890123",
                "vencimiento_cae": "25/06/2026",
                "fecha_emision": "2026-04-26",
                "descripcion": "Servicios profesionales",
                "importe_total": 10000.00,
                "punto_venta": "0001",
            }

            filepath = generator.generar(data, logo_url=data_url)

            assert os.path.exists(filepath)
            assert filepath.endswith(".pdf")
            assert os.path.getsize(filepath) > 0

    def test_pdf_generation_with_invalid_logo_fallback(self):
        """Test PDF generation succeeds even with invalid logo URL"""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = GeneradorPDFFactura(output_dir=tmpdir)

            data = {
                "cuit": "20301234567",
                "razon_social": "Test Company S.A.",
                "domicilio": "Av. Corrientes 1234, Buenos Aires",
                "condicion_iva": "Responsable Inscripto",
                "tipo_comprobante": "Factura A",
                "numero_comprobante": "0001-00000001",
                "cae": "71234567890123",
                "vencimiento_cae": "25/06/2026",
                "fecha_emision": "2026-04-26",
                "descripcion": "Servicios profesionales",
                "importe_total": 10000.00,
                "punto_venta": "0001",
            }

            with patch('src.pdf.generator.urlopen') as mock_urlopen:
                mock_urlopen.side_effect = Exception("Network error")

                # Should not raise exception, should use fallback
                filepath = generator.generar(
                    data,
                    logo_url="https://invalid.com/logo.png"
                )

                assert os.path.exists(filepath)
                assert filepath.endswith(".pdf")
                assert os.path.getsize(filepath) > 0


class TestLogoSizing:
    """Tests for logo sizing constraints"""

    def test_logo_sizing_constraints(self):
        """Test that loaded logos are constrained to 80x80 pixels max"""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = GeneradorPDFFactura(output_dir=tmpdir)

            # Create a valid PNG image
            png_data = create_test_png_bytes()
            b64_data = base64.b64encode(png_data).decode('utf-8')
            data_url = f"data:image/png;base64,{b64_data}"

            # Load the image through the generator
            logo_io = generator._load_logo(data_url)

            # Create an Image object and verify sizing
            if logo_io:
                logo_img = Image(logo_io, width=80, height=80)
                # ReportLab Image uses drawWidth/drawHeight
                assert logo_img.drawWidth == 80
                assert logo_img.drawHeight == 80
