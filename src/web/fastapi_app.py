import logging
import os
import re
import tempfile
import smtplib
from datetime import datetime, timedelta
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

# Import the PDF generator
from src.pdf.generator import GeneradorPDFFactura

load_dotenv()

logger = logging.getLogger(__name__)

app = FastAPI(title="Plantilla ARCA API", version="1.0.0")

# ============================================================================
# Pydantic Models
# ============================================================================


class GeneratePDFRequest(BaseModel):
    """Request model for PDF generation"""
    cuit: str
    razon_social: str
    domicilio: str
    condicion_iva: str
    tipo_comprobante: str
    fecha_emision: str
    descripcion: str
    importe_total: float
    logo_url: str = None

    @field_validator("cuit")
    @classmethod
    def validate_cuit(cls, v):
        """CUIT should be numeric, 11 digits"""
        if not v or not re.match(r'^\d{11}$', v.replace("-", "")):
            raise ValueError("CUIT debe ser válido (11 dígitos)")
        return v

    @field_validator("importe_total")
    @classmethod
    def validate_importe(cls, v):
        """Importe must be positive"""
        if v <= 0:
            raise ValueError("El importe debe ser mayor a 0")
        return v


class GeneratePDFResponse(BaseModel):
    """Response model for PDF generation"""
    ok: bool
    pdf_url: str = None
    cae: str = None
    vencimiento_cae: str = None
    error: str = None


class SendEmailRequest(BaseModel):
    """Request model for email sending"""
    email_destino: str
    pdf_path: str
    empresa: str


class SendEmailResponse(BaseModel):
    """Response model for email sending"""
    ok: bool
    mensaje: str = None
    error: str = None


class GetCAERequest(BaseModel):
    """Request model for CAE retrieval"""
    cuit: str
    importe: float
    tipo_comprobante: str
    ambiente: str = "homologacion"

    @field_validator("cuit")
    @classmethod
    def validate_cuit(cls, v):
        """CUIT should be numeric"""
        if not v or not re.match(r'^\d{11}$', v.replace("-", "")):
            raise ValueError("CUIT debe ser válido")
        return v


class GetCAEResponse(BaseModel):
    """Response model for CAE retrieval"""
    ok: bool
    cae: str = None
    vencimiento: str = None
    numero_comprobante: str = None
    error: str = None


# ============================================================================
# Health Check Endpoint
# ============================================================================


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


# ============================================================================
# PDF Generation Endpoint
# ============================================================================


@app.post("/api/arca/generate-pdf", response_model=GeneratePDFResponse)
async def generate_pdf(request: GeneratePDFRequest) -> GeneratePDFResponse:
    """
    Generate PDF invoice from ARCA data.

    Returns:
        GeneratePDFResponse with pdf_url, CAE, and vencimiento_cae
    """
    try:
        # Create output directory for PDFs
        output_dir = "/tmp/plantilla-arca-pdf"
        os.makedirs(output_dir, exist_ok=True)

        # Prepare data for PDF generator
        pdf_data = {
            "cuit": request.cuit,
            "razon_social": request.razon_social,
            "domicilio": request.domicilio,
            "condicion_iva": request.condicion_iva,
            "tipo_comprobante": request.tipo_comprobante,
            "fecha_emision": request.fecha_emision,
            "descripcion": request.descripcion,
            "importe_total": request.importe_total,
            "numero_comprobante": "0001-00000001",  # Placeholder
            "punto_venta": "0001",
            "cae": "71234567890123",  # MVP: simulated CAE
            "vencimiento_cae": "25/06/2026",  # MVP: simulated vencimiento
        }

        # Add logo if provided
        if request.logo_url:
            pdf_data["logo_url"] = request.logo_url

        # Generate PDF
        generator = GeneradorPDFFactura(output_dir=output_dir)
        pdf_path = generator.generar(pdf_data)

        # Get relative URL for PDF (assuming it's accessible from /pdf endpoint)
        pdf_filename = os.path.basename(pdf_path)
        pdf_url = f"/pdf/{pdf_filename}"

        logger.info(f"PDF generated successfully: {pdf_path}")

        return GeneratePDFResponse(
            ok=True,
            pdf_url=pdf_url,
            cae="71234567890123",
            vencimiento_cae="25/06/2026",
        )

    except ValueError as e:
        logger.warning(f"Validation error in generate_pdf: {str(e)}")
        return GeneratePDFResponse(
            ok=False,
            error=str(e),
        )
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        return GeneratePDFResponse(
            ok=False,
            error=f"Error generando PDF: {str(e)}",
        )


# ============================================================================
# Email Sending Endpoint
# ============================================================================


@app.post("/api/arca/send-email", response_model=SendEmailResponse)
async def send_email(request: SendEmailRequest) -> SendEmailResponse:
    """
    Send PDF via email.

    Returns:
        SendEmailResponse with success/error status
    """
    try:
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, request.email_destino):
            return SendEmailResponse(
                ok=False,
                error="Email inválido (debe contener @ y dominio válido)",
            )

        # Validate PDF file exists
        if not os.path.exists(request.pdf_path):
            return SendEmailResponse(
                ok=False,
                error=f"Archivo PDF no encontrado: {request.pdf_path}",
            )

        # Get SMTP configuration from environment
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))

        # If SMTP not configured, return graceful error
        if not all([smtp_server, smtp_user, smtp_password]):
            logger.warning("SMTP no configurado, email no será enviado")
            return SendEmailResponse(
                ok=True,
                mensaje="Email no configurado (SMTP no disponible). PDF generado correctamente.",
            )

        # Create email message
        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = request.email_destino
        msg["Subject"] = f"Factura - {request.empresa}"

        # Email body
        body = f"""
        Estimado cliente,

        Adjunto encontrará la factura electrónica de {request.empresa}.

        Saludos,
        Ultima Milla
        """
        msg.attach(MIMEText(body, "plain"))

        # Attach PDF
        try:
            with open(request.pdf_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {os.path.basename(request.pdf_path)}",
                )
                msg.attach(part)
        except Exception as e:
            logger.error(f"Error attaching PDF: {str(e)}")
            return SendEmailResponse(
                ok=False,
                error=f"Error adjuntando PDF: {str(e)}",
            )

        # Send email
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()

            logger.info(f"Email enviado a {request.email_destino}")
            return SendEmailResponse(
                ok=True,
                mensaje=f"Email enviado exitosamente a {request.email_destino}",
            )

        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {str(e)}")
            return SendEmailResponse(
                ok=False,
                error=f"Error SMTP: {str(e)}",
            )

    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return SendEmailResponse(
            ok=False,
            error=f"Error enviando email: {str(e)}",
        )


# ============================================================================
# CAE Retrieval Endpoint
# ============================================================================


@app.post("/api/arca/get-cae", response_model=GetCAEResponse)
async def get_cae(request: GetCAERequest) -> GetCAEResponse:
    """
    Get CAE for invoice.

    Returns:
        GetCAEResponse with CAE, vencimiento, and numero_comprobante
    """
    try:
        # MVP: Return simulated CAE
        # In production, this would call ARCA AFIP web services

        cae = "71234567890123"
        vencimiento = (datetime.now() + timedelta(days=30)).strftime("%d/%m/%Y")
        numero_comprobante = "0001-00000001"

        logger.info(f"CAE obtenido para CUIT {request.cuit}")

        return GetCAEResponse(
            ok=True,
            cae=cae,
            vencimiento=vencimiento,
            numero_comprobante=numero_comprobante,
        )

    except Exception as e:
        logger.error(f"Error getting CAE: {str(e)}")
        return GetCAEResponse(
            ok=False,
            error=f"Error obteniendo CAE: {str(e)}",
        )


# ============================================================================
# PDF Download Endpoint
# ============================================================================


@app.get("/pdf/{filename}")
async def download_pdf(filename: str):
    """
    Download generated PDF.

    Security: Only allows alphanumeric, dash, and underscore in filename.
    Prevents directory traversal attacks.
    """
    try:
        # Validate filename to prevent directory traversal
        if not re.match(r'^[\w\-\.]+\.pdf$', filename):
            raise HTTPException(
                status_code=400,
                detail="Nombre de archivo inválido",
            )

        # Try multiple locations: first /tmp, then /tmp/plantilla-arca-pdf
        candidate_dirs = ["/tmp", "/tmp/plantilla-arca-pdf"]
        file_path = None

        for pdf_dir in candidate_dirs:
            candidate_path = os.path.join(pdf_dir, filename)
            # Ensure the file is within the pdf_dir (prevent ../ attacks)
            if os.path.abspath(candidate_path).startswith(os.path.abspath(pdf_dir)):
                if os.path.exists(candidate_path):
                    file_path = candidate_path
                    break

        if not file_path:
            raise HTTPException(
                status_code=404,
                detail="Archivo no encontrado",
            )

        logger.info(f"Descargando PDF: {filename}")

        return FileResponse(
            path=file_path,
            media_type="application/pdf",
            filename=filename,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading PDF: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error descargando PDF",
        )


# ============================================================================
# Exception handlers
# ============================================================================


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors"""
    logger.error(f"Validation error: {str(exc)}")
    return {
        "ok": False,
        "error": str(exc),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
