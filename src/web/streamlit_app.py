"""
Plantilla ARCA - Generador de Facturas Electrónicas RG 5824
Ultima Milla - Soluciones técnicas para pymes argentinas
"""

import streamlit as st
import sys
import os
from datetime import datetime, date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

st.set_page_config(
    page_title="Plantilla ARCA - Facturas RG 5824 | Ultima Milla",
    page_icon="🧾",
    layout="wide",
)

PRIMARY = "#DC2626"
SECONDARY = "#1A56C0"
DARK = "#111827"
BLOG_URL = "https://ultimamilla.com.ar/blog/arca-5824-2026-el-director-que-nunca-facturo-tiene-fecha"


st.markdown(f"""
<style>
    .um-topbar {{
        display: flex; justify-content: space-between; align-items: center;
        padding: 0.75rem 0; border-bottom: 3px solid {PRIMARY}; margin-bottom: 1.5rem;
    }}
    .um-logo {{ font-size: 1.6rem; font-weight: 800; color: {DARK}; letter-spacing: -0.03em; }}
    .um-logo span {{ color: {PRIMARY}; }}
    .um-topbar-right {{ font-size: 0.8rem; color: #6B7280; text-align: right; }}
    .um-badge {{
        display: inline-block; background: #FEF2F2; color: {PRIMARY};
        padding: 0.15rem 0.6rem; border-radius: 999px;
        font-size: 0.7rem; font-weight: 700;
    }}
    .um-hero {{
        background: linear-gradient(135deg, {DARK} 0%, #1F2937 100%);
        color: white; padding: 2rem 2rem; border-radius: 10px; margin: 0 0 1.5rem 0;
    }}
    .um-hero h1 {{ color: white; font-size: 1.6rem; margin: 0 0 0.4rem 0; }}
    .um-hero p {{ color: #D1D5DB; font-size: 0.9rem; line-height: 1.5; margin: 0 0 0.5rem 0; }}
    .um-hero .hl {{ color: {PRIMARY}; font-weight: 700; }}
    .um-btn {{
        display: inline-block; padding: 0.4rem 1rem; background: {PRIMARY};
        color: white !important; text-decoration: none; border-radius: 5px;
        font-size: 0.8rem; font-weight: 600;
    }}
    .um-footer {{
        text-align: center; padding: 1.5rem 0 0.5rem 0;
        border-top: 1px solid #E5E7EB; margin-top: 2.5rem;
        font-size: 0.8rem; color: #6B7280;
    }}
    .um-footer a {{ color: {SECONDARY}; }}
</style>
""", unsafe_allow_html=True)

# ── Top Bar ─────────────────────────────────────────────────────────
st.markdown(
    f'<div class="um-topbar">'
    f'<div class="um-logo"><span>●</span> ULTIMA MILLA</div>'
    f'<div class="um-topbar-right">'
    f'<span class="um-badge">Open Source</span><br/>'
    f'RG 5824 · ARCA · Factura Electrónica</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Hero ────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="um-hero">'
    f'<h1>🧾 Generador de Facturas ARCA</h1>'
    f'<p>La <strong>RG 5824</strong> de ARCA (ex AFIP) exige facturación electrónica '
    f'para directores, síndicos, abogados, contadores y profesionales. Esta herramienta '
    f'<strong>open source</strong> te permite emitir comprobantes con '
    f'<span class="hl">CAE automático</span> sin depender de proveedores '
    f'privados ni pagar licencias mensuales.</p>'
    f'<p>Completá los datos del portador y generá tu factura en PDF lista para '
    f'entregar a ARCA. Todo corre sobre tus propios servicios — sin límites de '
    f'emisión, sin costos ocultos.</p>'
    f'<a class="um-btn" href="{BLOG_URL}" target="_blank">📖 Nota técnica RG 5824 →</a>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Form ────────────────────────────────────────────────────────────
st.markdown(f"<h3 style='color: {DARK};'>📝 Datos del Portador</h3>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    tipo = st.selectbox(
        "Tipo de Comprobante",
        ["Factura A (Resp. Inscripto)", "Factura B (Monotributista)", "Factura C (Exento)"],
    )
    cuit = st.text_input("CUIT del Emisor", value="30-12345678-9")
    razon = st.text_input("Razón Social", value="Ultima Milla S.A.")
    domicilio = st.text_input("Domicilio Comercial", value="Av. Corrientes 1234, CABA")

with col2:
    iva = st.selectbox("Condición frente al IVA", [
        "Responsable Inscripto", "Monotributista", "Exento",
        "Consumidor Final", "Sujeto No Categorizado",
    ])
    fecha = st.date_input("Fecha de Emisión", date.today())
    desc = st.text_area(
        "Descripción del Servicio",
        value="Servicios de consultoría tecnológica",
        height=70,
    )
    importe = st.number_input("Importe Total ($)", min_value=0.0, value=150000.0, step=1000.0)

st.markdown("<br>", unsafe_allow_html=True)

# ── Generate ────────────────────────────────────────────────────────
gen_btn = st.button("✨ Generar Factura", type="primary", use_container_width=True)

if gen_btn:
    with st.spinner("Generando factura…"):
        tipo_map = {
            "Factura A (Resp. Inscripto)": "Factura A",
            "Factura B (Monotributista)": "Factura B",
            "Factura C (Exento)": "Factura C",
        }
        data = {
            "tipo_comprobante": tipo_map.get(tipo, tipo),
            "cuit": cuit,
            "razon_social": razon,
            "domicilio": domicilio,
            "condicion_iva": iva,
            "punto_venta": "0001",
            "numero_comprobante": "00001-00000001",
            "cae": "71234567890123",
            "vencimiento_cae": "15/05/2026",
            "fecha_emision": fecha.strftime("%d/%m/%Y"),
            "descripcion": desc,
            "importe_total": importe,
            "items": [{"descripcion": desc, "cantidad": 1, "precio_unitario": importe, "subtotal": importe}],
        }

        try:
            from src.pdf.generator import GeneradorPDFFactura
            generador = GeneradorPDFFactura(output_dir="/tmp/plantilla-arca-pdf")
            pdf_path = generador.generar(data)
            st.session_state.pdf_path = pdf_path
            st.success("✅ Factura generada exitosamente")
        except Exception as e:
            st.error(f"Error al generar la factura: {e}")
            st.exception(e)

# ── Download ────────────────────────────────────────────────────────
if "pdf_path" in st.session_state and st.session_state.pdf_path:
    pdf_path = st.session_state.pdf_path
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 Descargar PDF",
                data=f,
                file_name=os.path.basename(pdf_path),
                mime="application/pdf",
                use_container_width=True,
            )

# ── Footer ──────────────────────────────────────────────────────────
st.markdown(
    f'<div class="um-footer">'
    f'<a href="https://ultimamilla.com.ar">Ultima Milla</a> · '
    f'Soluciones técnicas para pymes argentinas · '
    f'<a href="https://github.com/UltimaMilla/plantilla-arca">GitHub</a> · '
    f'<a href="{BLOG_URL}">Blog</a><br>'
    f'<span style="font-size:0.7rem;">MIT License · Streamlit · ReportLab · arca_arg</span>'
    f'</div>',
    unsafe_allow_html=True,
)
