import pytest
import os
import tempfile
import json
from pathlib import Path
from fastapi.testclient import TestClient
from src.web.fastapi_app import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_check_returns_ok(self):
        """Health endpoint should return status ok"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestGeneratePDFEndpoint:
    def test_generate_pdf_with_valid_data(self):
        """Should generate PDF with valid request data"""
        payload = {
            "cuit": "20301234567",
            "razon_social": "Test Company S.A.",
            "domicilio": "Av. Corrientes 1234, Buenos Aires",
            "condicion_iva": "Responsable Inscripto",
            "tipo_comprobante": "Factura A",
            "fecha_emision": "2026-04-26",
            "descripcion": "Servicios profesionales",
            "importe_total": 10000.00,
        }
        response = client.post("/api/arca/generate-pdf", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "pdf_url" in data
        assert "cae" in data
        assert "vencimiento_cae" in data
        assert data["cae"] == "71234567890123"
        assert data["vencimiento_cae"] == "25/06/2026"

    def test_generate_pdf_with_logo_url(self):
        """Should accept optional logo_url parameter"""
        payload = {
            "cuit": "20301234567",
            "razon_social": "Test Company S.A.",
            "domicilio": "Av. Corrientes 1234, Buenos Aires",
            "condicion_iva": "Responsable Inscripto",
            "tipo_comprobante": "Factura A",
            "fecha_emision": "2026-04-26",
            "descripcion": "Servicios profesionales",
            "importe_total": 10000.00,
            "logo_url": "https://example.com/logo.png",
        }
        response = client.post("/api/arca/generate-pdf", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "pdf_url" in data

    def test_generate_pdf_missing_required_field(self):
        """Should return error when required field is missing"""
        payload = {
            "cuit": "20301234567",
            "razon_social": "Test Company S.A.",
            # Missing domicilio and other required fields
        }
        response = client.post("/api/arca/generate-pdf", json=payload)

        # Pydantic validation error or our custom error
        assert response.status_code in [400, 422]

    def test_generate_pdf_invalid_cuit(self):
        """Should handle invalid CUIT format gracefully"""
        payload = {
            "cuit": "invalid",
            "razon_social": "Test Company S.A.",
            "domicilio": "Av. Corrientes 1234, Buenos Aires",
            "condicion_iva": "Responsable Inscripto",
            "tipo_comprobante": "Factura A",
            "fecha_emision": "2026-04-26",
            "descripcion": "Servicios profesionales",
            "importe_total": 10000.00,
        }
        response = client.post("/api/arca/generate-pdf", json=payload)

        # Should handle gracefully
        assert response.status_code in [200, 400, 422]
        if response.status_code == 200:
            data = response.json()
            # Either ok=True (if we accept any CUIT) or ok=False with error
            assert "ok" in data


class TestSendEmailEndpoint:
    def test_send_email_with_valid_data(self):
        """Should send email with valid request"""
        # Create a temporary PDF file for testing
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"Mock PDF content")
            tmp_path = tmp.name

        try:
            payload = {
                "email_destino": "cliente@example.com",
                "pdf_path": tmp_path,
                "empresa": "Test Company",
            }
            response = client.post("/api/arca/send-email", json=payload)

            assert response.status_code == 200
            data = response.json()
            # Could be ok=True if SMTP configured, or graceful error
            assert "ok" in data
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_send_email_invalid_email(self):
        """Should reject invalid email format"""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"Mock PDF content")
            tmp_path = tmp.name

        try:
            payload = {
                "email_destino": "not-an-email",
                "pdf_path": tmp_path,
                "empresa": "Test Company",
            }
            response = client.post("/api/arca/send-email", json=payload)

            assert response.status_code == 200
            data = response.json()
            assert data["ok"] is False
            assert "error" in data
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_send_email_nonexistent_pdf(self):
        """Should handle nonexistent PDF file"""
        payload = {
            "email_destino": "cliente@example.com",
            "pdf_path": "/tmp/nonexistent_file_12345.pdf",
            "empresa": "Test Company",
        }
        response = client.post("/api/arca/send-email", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is False
        assert "error" in data


class TestGetCAEEndpoint:
    def test_get_cae_with_valid_data(self):
        """Should return CAE for valid request"""
        payload = {
            "cuit": "20301234567",
            "importe": 10000.00,
            "tipo_comprobante": "Factura A",
            "ambiente": "homologacion",
        }
        response = client.post("/api/arca/get-cae", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "cae" in data
        assert "vencimiento" in data
        assert "numero_comprobante" in data
        # MVP: simulated CAE
        assert data["cae"] == "71234567890123"

    def test_get_cae_with_produccion_ambiente(self):
        """Should accept produccion ambiente"""
        payload = {
            "cuit": "20301234567",
            "importe": 5000.00,
            "tipo_comprobante": "Factura B",
            "ambiente": "produccion",
        }
        response = client.post("/api/arca/get-cae", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "ok" in data


class TestDownloadPDFEndpoint:
    def test_download_pdf_valid_filename(self):
        """Should download PDF with valid filename"""
        # Create a test PDF in /tmp
        test_filename = "test_factura_001.pdf"
        test_path = os.path.join("/tmp", test_filename)

        with open(test_path, "wb") as f:
            f.write(b"Mock PDF content")

        try:
            response = client.get(f"/pdf/{test_filename}")
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/pdf"
            assert response.content == b"Mock PDF content"
        finally:
            if os.path.exists(test_path):
                os.unlink(test_path)

    def test_download_pdf_directory_traversal_attempt(self):
        """Should prevent directory traversal attacks"""
        response = client.get("/pdf/../../etc/passwd")

        # Should either 404 or reject with 400
        assert response.status_code in [400, 404]

    def test_download_pdf_nonexistent_file(self):
        """Should return 404 for nonexistent file"""
        response = client.get("/pdf/nonexistent_file_12345.pdf")

        assert response.status_code == 404


class TestErrorHandling:
    def test_generate_pdf_returns_error_response(self):
        """Error responses should have ok=False and error field"""
        payload = {
            "cuit": "",  # Empty CUIT might cause issues
            "razon_social": "Test",
            "domicilio": "Test",
            "condicion_iva": "Test",
            "tipo_comprobante": "Test",
            "fecha_emision": "2026-04-26",
            "descripcion": "Test",
            "importe_total": 100,
        }
        response = client.post("/api/arca/generate-pdf", json=payload)

        # Should have structured response
        if response.status_code == 200:
            data = response.json()
            if not data.get("ok"):
                assert "error" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
