import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image, ImageOps, ImageEnhance
import numpy as np
import cv2
import io
import os

# -----------------------
# Page config
# -----------------------
st.set_page_config(
    page_title="PDF Dark Mode Converter",
    page_icon="🌙",
    layout="centered"
)

st.title("🌙 PDF Dark Mode Converter")
st.write("Convert PDFs to dark mode for better eye comfort. Supports batch upload.")

# -----------------------
# Utils
# -----------------------
def is_mostly_white(img, threshold=200):
    """
    Detect if page background is mostly white
    """
    gray = np.array(img.convert("L"))
    white_ratio = np.mean(gray > threshold)
    return white_ratio > 0.6


def smart_dark_mode(img, contrast=2.2, brightness=1.0):
    """
    Convert page to dark mode
    """
    gray = img.convert("L")

    contrast_enhancer = ImageEnhance.Contrast(gray)
    gray = contrast_enhancer.enhance(contrast)

    brightness_enhancer = ImageEnhance.Brightness(gray)
    gray = brightness_enhancer.enhance(brightness)

    inverted = ImageOps.invert(gray)
    return inverted


# -----------------------
# UI
# -----------------------
uploaded_files = st.file_uploader(
    "Upload one or more PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

contrast = st.slider("Text Contrast", 1.5, 3.0, 2.2, 0.1)
brightness = st.slider("Brightness", 0.9, 1.2, 1.0, 0.05)

# -----------------------
# Processing
# -----------------------
if uploaded_files:
    for uploaded_file in uploaded_files:
        st.divider()
        st.subheader(f"📄 {uploaded_file.name}")

        with st.spinner("Processing PDF..."):
            try:
                pages = convert_from_bytes(uploaded_file.read())

                processed_pages = []

                for page in pages:
                    # Auto-detect background
                    if is_mostly_white(page):
                        out = smart_dark_mode(page, contrast, brightness)
                    else:
                        # If already dark-ish, apply lighter processing
                        out = smart_dark_mode(page, contrast=1.6, brightness=brightness)

                    processed_pages.append(out)

                pdf_bytes = io.BytesIO()
                processed_pages[0].save(
                    pdf_bytes,
                    format="PDF",
                    save_all=True,
                    append_images=processed_pages[1:]
                )

                st.success("✅ Done")

                st.download_button(
                    label="⬇️ Download Dark Mode PDF",
                    data=pdf_bytes.getvalue(),
                    file_name=f"dark_{uploaded_file.name}",
                    mime="application/pdf"
                )

            except Exception as e:
                st.error(f"❌ Error processing PDF: {e}")
