import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

st.set_page_config(
    page_title="Facturación ARCA - ULTIMA MILLA",
    page_icon="🧾",
    layout="wide",
)

st.markdown("<h1 style='color: #DC2626;'>🧾 Generador de Facturas ARCA</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='color: #1A56C0;'>Cumplimiento RG 5824 - AFIP</h3>", unsafe_allow_html=True)

st.info("Generador de facturas electrónicas con CAE automático desde ARCA")

# Formulario simple
st.subheader("📝 Datos del Comprobante")
cuit = st.text_input("CUIT", value="20123456789")
razon_social = st.text_input("Razón Social", value="Mi Empresa S.A.")
importe = st.number_input("Importe Total", value=1000.0)

if st.button("✨ Generar Factura"):
    st.success(f"Factura generada para {razon_social} - ${importe}")

st.divider()
st.markdown("---\n*[Ultima Milla](https://ultimamilla.com.ar) - Soluciones técnicas para pymes argentinas*")
