"""
Plantilla ARCA - Generador de Facturas Electrónicas RG 5824
Ultima Milla - Soluciones técnicas para pymes argentinas
"""

import streamlit as st
import sys
import os
import tempfile
from datetime import datetime, date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

st.set_page_config(
    page_title="Plantilla ARCA - Generador de Facturas | Ultima Milla",
    page_icon="🧾",
    layout="wide",
)

# ── Branding Constants ──────────────────────────────────────────────
PRIMARY = "#DC2626"
SECONDARY = "#1A56C0"
DARK = "#111827"
LIGHT_BG = "#F9FAFB"

LOGO_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 620 100" width="200" height="32">
  <path d="M56 446H200V200Q200 151 225 128Q248 107 285 107Q323 107 346 128Q370 151 370 200V446H514V186Q514 140 504.5 106.5Q495 73 464 43Q405 -15 285 -15Q164 -15 105 43Q56 91 56 177Z" fill="#000000" transform="translate(0.00,62.00) scale(0.072000,-0.072000)"/>
  <path d="M60 729H204V0H60Z" fill="#000000" transform="translate(40.97,62.00) scale(0.072000,-0.072000)"/>
  <path d="M293 330H204V0H60V330H10V446H60V590H204V446H293Z" fill="#000000" transform="translate(59.91,62.00) scale(0.072000,-0.072000)"/>
  <path d="M66 446H210V0H66ZM78.5 576.5Q54 601 54.0 636.0Q54 671 78.5 695.5Q103 720 138.0 720.0Q173 720 197.5 695.5Q222 671 222.0 636.0Q222 601 197.5 576.5Q173 552 138.0 552.0Q103 552 78.5 576.5Z" fill="#000000" transform="translate(81.38,62.00) scale(0.072000,-0.072000)"/>
  <path d="M56 0V446H200V394Q242 457 325 457Q376 457 409 437Q444 417 463 375Q484 410 520 432Q561 457 615 457Q696 457 740 415Q786 371 786 282V0H642V226Q642 289 623.0 313.0Q604 337 571 337Q535 337 515 310Q493 282 493 222V0H349V232Q349 296 326 319Q308 337 278 337Q247 337 228 319Q200 292 200 228V0Z" fill="#000000" transform="translate(101.18,62.00) scale(0.072000,-0.072000)"/>
  <path d="M398 396V446H542V0H398V54Q353 -15 266 -15Q163 -15 99 53Q34 122 34 220Q34 331 103 400Q164 461 258 461Q350 461 398 396ZM294 337Q247 337 215 305Q182 272 182.0 224.0Q182 176 212 144Q245 109 297 109Q341 109 372 140Q407 173 407.0 224.0Q407 275 374 306Q342 337 294 337Z" fill="#000000" transform="translate(161.81,62.00) scale(0.072000,-0.072000)"/>
  <path d="M56 0V446H200V394Q242 457 325 457Q376 457 409 437Q444 417 463 375Q484 410 520 432Q561 457 615 457Q696 457 740 415Q786 371 786 282V0H642V226Q642 289 623.0 313.0Q604 337 571 337Q535 337 515 310Q493 282 493 222V0H349V232Q349 296 326 319Q308 337 278 337Q247 337 228 319Q200 292 200 228V0Z" fill="#000000" transform="translate(204.80,62.00) scale(0.072000,-0.072000)"/>
  <path d="M66 446H210V0H66ZM78.5 576.5Q54 601 54.0 636.0Q54 671 78.5 695.5Q103 720 138.0 720.0Q173 720 197.5 695.5Q222 671 222.0 636.0Q222 601 197.5 576.5Q173 552 138.0 552.0Q103 552 78.5 576.5Z" fill="#000000" transform="translate(265.43,62.00) scale(0.072000,-0.072000)"/>
  <path d="M60 729H204V0H60Z" fill="#000000" transform="translate(285.23,62.00) scale(0.072000,-0.072000)"/>
  <path d="M60 729H204V0H60Z" fill="#000000" transform="translate(304.18,62.00) scale(0.072000,-0.072000)"/>
  <path d="M398 396V446H542V0H398V54Q353 -15 266 -15Q163 -15 99 53Q34 122 34 220Q34 331 103 400Q164 461 258 461Q350 461 398 396ZM294 337Q247 337 215 305Q182 272 182.0 224.0Q182 176 212 144Q245 109 297 109Q341 109 372 140Q407 173 407.0 224.0Q407 275 374 306Q342 337 294 337Z" fill="#000000" transform="translate(323.12,62.00) scale(0.072000,-0.072000)"/>
  <path d="M74.5 10.5Q48 37 48.0 75.0Q48 113 74.5 139.5Q101 166 139.0 166.0Q177 166 203.5 139.5Q230 113 230.0 75.0Q230 37 203.5 10.5Q177 -16 139.0 -16.0Q101 -16 74.5 10.5Z" fill="#DC2626" transform="translate(366.11,62.00) scale(0.072000,-0.072000)"/>
  <path d="M391 436V305Q350 339 297 339Q247 339 215 307Q182 274 182 223Q182 175 212 143Q245 107 299 107Q350 107 391 142V12Q342 -15 277 -15Q173 -15 104 52Q34 120 34 222Q34 328 108 398Q175 461 278 461Q338 461 391 436Z" fill="#000000" transform="translate(386.06,62.00) scale(0.072000,-0.072000)"/>
  <path d="M491 57Q419 -15 296.0 -15.0Q173 -15 101 57Q34 124 34.0 223.0Q34 322 101 389Q173 461 296.0 461.0Q419 461 491 389Q558 322 558.0 223.0Q558 124 491 57ZM215 307Q182 274 182.0 223.0Q182 172 215 139Q247 107 297 107Q345 107 377 139Q410 172 410.0 223.0Q410 274 377 307Q345 339 296.0 339.0Q247 339 215 307Z" fill="#000000" transform="translate(417.02,62.00) scale(0.072000,-0.072000)"/>
  <path d="M56 0V446H200V394Q242 457 325 457Q376 457 409 437Q444 417 463 375Q484 410 520 432Q561 457 615 457Q696 457 740 415Q786 371 786 282V0H642V226Q642 289 623.0 313.0Q604 337 571 337Q535 337 515 310Q493 282 493 222V0H349V232Q349 296 326 319Q308 337 278 337Q247 337 228 319Q200 292 200 228V0Z" fill="#000000" transform="translate(459.58,62.00) scale(0.072000,-0.072000)"/>
  <path d="M74.5 10.5Q48 37 48.0 75.0Q48 113 74.5 139.5Q101 166 139.0 166.0Q177 166 203.5 139.5Q230 113 230.0 75.0Q230 37 203.5 10.5Q177 -16 139.0 -16.0Q101 -16 74.5 10.5Z" fill="#DC2626" transform="translate(520.21,62.00) scale(0.072000,-0.072000)"/>
  <path d="M398 396V446H542V0H398V54Q353 -15 266 -15Q163 -15 99 53Q34 122 34 220Q34 331 103 400Q164 461 258 461Q350 461 398 396ZM294 337Q247 337 215 305Q182 272 182.0 224.0Q182 176 212 144Q245 109 297 109Q341 109 372 140Q407 173 407.0 224.0Q407 275 374 306Q342 337 294 337Z" fill="#000000" transform="translate(540.16,62.00) scale(0.072000,-0.072000)"/>
  <path d="M56 0V446H200V376Q221 417 256 438Q286 457 333 457Q358 457 380 450L372 315Q342 331 307 331Q263 331 235 301Q200 264 200 181V0Z" fill="#000000" transform="translate(583.15,62.00) scale(0.072000,-0.072000)"/>
</svg>
"""

BLOG_URL = "https://ultimamilla.com.ar/blog/arca-5824-2026-el-director-que-nunca-facturo-tiene-fecha"


# ── Custom CSS ───────────────────────────────────────────────────────
st.markdown(
    """
<style>
    .um-header { display: flex; align-items: center; gap: 16px; padding: 1rem 0; }
    .um-hero { background: linear-gradient(135deg, #111827 0%, #1F2937 100%);
                color: white; padding: 2.5rem 2rem; border-radius: 12px; margin: 1rem 0 2rem 0; }
    .um-hero h1 { color: white; font-size: 1.8rem; margin: 0 0 0.5rem 0; }
    .um-hero p { color: #D1D5DB; font-size: 1rem; line-height: 1.6; margin: 0; }
    .um-hero .um-highlight { color: #DC2626; font-weight: 700; }
    .um-blog-link { display: inline-block; margin-top: 1rem; padding: 0.5rem 1.2rem;
                     background: #DC2626; color: white; text-decoration: none;
                     border-radius: 6px; font-size: 0.9rem; font-weight: 600; }
    .um-blog-link:hover { background: #B91C1C; }
    .um-footer { text-align: center; padding: 2rem 0 1rem 0;
                 border-top: 1px solid #E5E7EB; margin-top: 3rem;
                 font-size: 0.85rem; color: #6B7280; }
    .um-badge { display: inline-block; background: #FEF2F2; color: #DC2626;
                padding: 0.25rem 0.75rem; border-radius: 999px;
                font-size: 0.75rem; font-weight: 600; }
</style>
""",
    unsafe_allow_html=True,
)

# ── Header ──────────────────────────────────────────────────────────
col_logo, col_tag = st.columns([1, 3])
with col_logo:
    st.markdown(LOGO_SVG, unsafe_allow_html=True)
with col_tag:
    st.markdown(
        '<div style="text-align: right;">'
        '<span class="um-badge">Open Source</span>'
        '<br/><span style="color: #6B7280; font-size: 0.85rem;">'
        "RG 5824 &bull; ARCA &bull; Factura Electrónica</span></div>",
        unsafe_allow_html=True,
    )

# ── Hero / Explanation ──────────────────────────────────────────────
st.markdown(
    """
<div class="um-hero">
    <h1>🧾 Generador de Facturas ARCA</h1>
    <p>
        La <strong>RG 5824</strong> de ARCA (ex AFIP) exige facturación electrónica para
        directores, síndicos, abogados, contadores y profesionales. Esta herramienta
        <strong>open source</strong> te permite emitir comprobantes electrónicos con
        <span class="um-highlight">CAE automático</span> sin depender de proveedores
        privados ni pagar licencias mensuales.
    </p>
    <p style="margin-top: 1rem;">
        Completá los datos del portador y generá tu factura en PDF lista para
        entregar a ARCA. Todo corre sobre tus propios servicios — sin límites de
        emisión, sin costos ocultos.
    </p>
    <a class="um-blog-link" href="%s" target="_blank">
        📖 Leer la nota técnica sobre RG 5824 →
    </a>
</div>
"""
    % BLOG_URL,
    unsafe_allow_html=True,
)

# ── Form ────────────────────────────────────────────────────────────
st.markdown(
    "<h3 style='color: %s; margin-bottom: 1.5rem;'>📝 Datos del Portador</h3>" % DARK,
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:
    tipo_factura = st.selectbox(
        "Tipo de Comprobante",
        options=["Factura A (Responsable Inscripto)", "Factura B (Monotributista)", "Factura C (Exento)"),
        index=0,
    )
    cuit = st.text_input("CUIT del Emisor", value="30-12345678-9", placeholder="XX-XXXXXXXX-X")
    razon_social = st.text_input("Razón Social", value="Ultima Milla S.A.", placeholder="Nombre de la empresa")
    domicilio = st.text_input("Domicilio Comercial", value="Av. Corrientes 1234, CABA", placeholder="Calle y número")

with col2:
    condicion_iva = st.selectbox(
        "Condición frente al IVA",
        options=[
            "Responsable Inscripto",
            "Monotributista",
            "Exento",
            "Consumidor Final",
            "Sujeto No Categorizado",
        ],
        index=0,
    )
    fecha_emision = st.date_input("Fecha de Emisión", value=date.today())
    descripcion = st.text_area(
        "Concepto / Descripción del Servicio",
        value="Servicios de consultoría tecnológica - Desarrollo de software a medida",
        placeholder="Detalle del servicio prestado",
        height=80,
    )
    importe = st.number_input("Importe Total ($)", min_value=0.0, value=150000.0, step=1000.0)

# ── Generate Button ─────────────────────────────────────────────────
st.markdown("<br/>", unsafe_allow_html=True)
gen_col1, gen_col2, _ = st.columns([1, 1, 3])

with gen_col1:
    generar = st.button("✨ Generar Factura", type="primary", use_container_width=True)

with gen_col2:
    if "pdf_path" in st.session_state and st.session_state.pdf_path:
        with open(st.session_state.pdf_path, "rb") as f:
            st.download_button(
                label="📥 Descargar PDF",
                data=f,
                file_name=os.path.basename(st.session_state.pdf_path),
                mime="application/pdf",
                use_container_width=True,
            )

# ── PDF Generation ──────────────────────────────────────────────────
if generar:
    with st.spinner("Generando factura electrónica..."):

        tipo_map = {
            "Factura A (Responsable Inscripto)": "Factura A",
            "Factura B (Monotributista)": "Factura B",
            "Factura C (Exento)": "Factura C",
        }

        data = {
            "tipo_comprobante": tipo_map.get(tipo_factura, tipo_factura),
            "cuit": cuit,
            "razon_social": razon_social,
            "domicilio": domicilio,
            "condicion_iva": condicion_iva,
            "punto_venta": "0001",
            "numero_comprobante": "00001-00000001",
            "cae": "71234567890123",
            "vencimiento_cae": datetime.now().strftime("%d/%m/%Y"),
            "fecha_emision": fecha_emision.strftime("%d/%m/%Y"),
            "descripcion": descripcion,
            "importe_total": importe,
            "items": [
                {
                    "descripcion": descripcion,
                    "cantidad": 1,
                    "precio_unitario": importe,
                    "subtotal": importe,
                }
            ],
        }

        try:
            from src.pdf.generator import GeneradorPDFFactura

            generador = GeneradorPDFFactura(output_dir="/tmp/plantilla-arca-pdf")
            pdf_path = generador.generar(data)

            st.session_state.pdf_path = pdf_path

            st.success("✅ Factura generada exitosamente")
            st.balloons()

            st.info(
                "💡 **CAE Simulado**: En producción, este número se obtiene automáticamente "
                "conectando a los Web Services de ARCA. "
                "[Ver documentación oficial](https://www.arca.gob.ar)",
            )

            # Show download button immediately
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Descargar PDF",
                    data=f,
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf",
                    use_container_width=True,
                )

        except Exception as e:
            st.error("Error al generar la factura: %s" % str(e))
            st.exception(e)

# ── Footer ──────────────────────────────────────────────────────────
st.markdown(
    """
<div class="um-footer">
    <a href="https://ultimamilla.com.ar" target="_blank">Ultima Milla</a> &bull;
    Soluciones técnicas para pymes argentinas &bull;
    <a href="https://github.com/UltimaMilla/plantilla-arca" target="_blank">GitHub</a> &bull;
    <a href="%s" target="_blank">Blog</a><br/>
    <span style="font-size: 0.75rem;">
        MIT License &bull; Built with Streamlit &bull; ReportLab &bull; arca_arg
    </span>
</div>
"""
    % BLOG_URL,
    unsafe_allow_html=True,
)
