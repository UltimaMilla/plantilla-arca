"""
Plantilla ARCA - Generador de Facturas Electrónicas RG 5824
Ultima Milla - Soluciones técnicas para pymes argentinas
"""

import streamlit as st
import sys
import os
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

st.set_page_config(
    page_title="Plantilla ARCA - Facturas RG 5824 | Ultima Milla",
    page_icon="🧾",
    layout="wide",
)

# ── Constants ───────────────────────────────────────────────────────
PRIMARY = "#DC2626"
SECONDARY = "#1A56C0"
DARK = "#111827"
BLOG_URL = "https://ultimamilla.com.ar/blog/arca-5824-2026-el-director-que-nunca-facturo-tiene-fecha"
GITHUB_URL = "https://github.com/UltimaMilla/plantilla-arca"

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
    .um-hero .hl-blue {{ color: #60A5FA; font-weight: 600; }}
    .um-btn {{
        display: inline-block; padding: 0.4rem 1rem; background: {PRIMARY};
        color: white !important; text-decoration: none; border-radius: 5px;
        font-size: 0.8rem; font-weight: 600; margin-right: 0.5rem;
    }}
    .um-btn-gh {{
        display: inline-block; padding: 0.4rem 1rem; background: #333;
        color: white !important; text-decoration: none; border-radius: 5px;
        font-size: 0.8rem; font-weight: 600;
    }}
    .um-section {{
        background: #F9FAFB; border: 1px solid #E5E7EB; border-left: 4px solid {PRIMARY};
        padding: 1.2rem 1.5rem; border-radius: 6px; margin: 1rem 0;
    }}
    .um-section h3 {{ color: {DARK}; margin: 0 0 0.5rem 0; font-size: 1rem; }}
    .um-section p {{ color: #4B5563; font-size: 0.9rem; line-height: 1.5; margin: 0; }}
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
    '<div class="um-topbar">'
    '<div class="um-logo"><span>●</span> ULTIMA MILLA</div>'
    '<div class="um-topbar-right">'
    '<span class="um-badge">Open Source</span><br>'
    'RG 5824 · ARCA · Factura Electrónica</div>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Hero ────────────────────────────────────────────────────────────
st.markdown(
    '<div class="um-hero">'
    '<h1>🧾 Generador de Facturas ARCA</h1>'
    '<p>La <strong>RG 5824</strong> de ARCA (ex AFIP) exige que <strong>directores, síndicos, abogados, '
    'contadores y profesionales independientes</strong> emitan <span class="hl">facturación electrónica</span> '
    'por todas sus operaciones. Desde 2026, quienes antes no facturaban o lo hacían en papel están '
    '<span class="hl">obligados a presentar comprobantes electrónicos ante ARCA</span>.</p>'
    '<p>Esta herramienta <strong>open source</strong> resuelve ese problema: completá los datos del '
    'portador y obtené al instante una factura en PDF lista para presentar. Sin depender de proveedores '
    'ni pagar licencias — todo corre sobre tu propia infraestructura.</p>'
    '<p style="font-size:0.8rem;color:#9CA3AF;">"'
    '✅ CAE automático vía Web Services ARCA · ✅ QR · ✅ Persistencia en DB</p>'
    '<a class="um-btn" href="%s" target="_blank">📖 Nota técnica RG 5824 →</a>'
    '<a class="um-btn-gh" href="%s" target="_blank">🐙 Código fuente en GitHub</a>'
    '</div>' % (BLOG_URL, GITHUB_URL),
    unsafe_allow_html=True,
)

# ── Explanation sections ────────────────────────────────────────────
st.markdown(
    '<div class="um-section">'
    '<h3>📌 ¿Qué cambió con RG 5824?</h3>'
    '<p>Hasta 2025, directores, síndicos y ciertos profesionales podían emitir comprobantes '
    'en papel o directamente no facturar. La <strong>RG 5824</strong> cerró esa puerta: '
    '<strong>todas las operaciones</strong> (honorarios, consultorías, servicios profesionales) '
    'deben emitirse como <strong>factura electrónica con CAE</strong> ante ARCA. '
    'No hacerlo es incumplimiento formal con multas actualizadas.</p>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="um-section">'
    '<h3>🧾 ¿Qué hace este formulario?</h3>'
    '<p>Completá los datos del <strong>portador</strong> (emisor de la factura) y del '
    '<strong>comprobante</strong> (tipo, monto, concepto). Al hacer clic en "Generar Factura", '
    'el sistema arma un PDF profesional con todos los datos requeridos por ARCA: '
    'CUIT, condición fiscal, detalle, CAE, código QR y vencimiento. '
    'El PDF se descarga al instante y queda listo para presentar.</p>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="um-section">'
    '<h3>🐙 ¿Por qué open source?</h3>'
    '<p>Porque facturar no debería ser un negocio. Este código es <strong>100% libre</strong>, '
    'se audita, se mejora y se adapta. Descargalo, ejecutalo en tu propio servidor, '
    'modificalo. Sin SaaS, sin límites de emisión, sin costos ocultos. '
    '<a href="%s" target="_blank" style="color:%s;">Descargar desde GitHub →</a></p>'
    '</div>' % (GITHUB_URL, PRIMARY),
    unsafe_allow_html=True,
)

# ── Form ────────────────────────────────────────────────────────────
st.markdown(f"<h3 style='color:{DARK};margin-top:1.5rem;'>📝 Datos del Portador</h3>", unsafe_allow_html=True)

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
    desc = st.text_area("Descripción del Servicio", value="Servicios de consultoría tecnológica", height=70)
    importe = st.number_input("Importe Total ($)", min_value=0.0, value=150000.0, step=1000.0)

st.markdown("<br>", unsafe_allow_html=True)
gen_btn = st.button("✨ Generar Factura", type="primary", use_container_width=True)

# ── Generate ────────────────────────────────────────────────────────
if gen_btn:
    with st.spinner("Generando factura electrónica…"):
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
    '<div class="um-footer">'
    '<a href="https://ultimamilla.com.ar">Ultima Milla</a> · '
    'Soluciones técnicas para pymes argentinas · '
    '<a href="%s">GitHub</a> · '
    '<a href="%s">Blog</a><br>'
    '<span style="font-size:0.7rem;">MIT License · Streamlit · ReportLab · arca_arg · PostgreSQL</span>'
    '</div>' % (GITHUB_URL, BLOG_URL),
    unsafe_allow_html=True,
)
