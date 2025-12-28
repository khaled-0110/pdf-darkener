import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image, ImageOps, ImageEnhance
import numpy as np
import io
import zipfile

# -----------------------
# Page configuration
# -----------------------
st.set_page_config(
    page_title="PDF Dark Mode Converter",
    page_icon="🌙",
    layout="wide"
)

st.title("🌙 PDF Dark Mode Converter")
st.write(
    "Convert PDFs to dark mode for better eye comfort. "
    "Supports batch uploads, collapsible previews, and adjustable settings."
)

# -----------------------
# Utility functions
# -----------------------
def is_mostly_white(img, threshold=200):
    """Detect if the page background is mostly white"""
    gray = np.array(img.convert("L"))
    white_ratio = np.mean(gray > threshold)
    return white_ratio > 0.6


def smart_dark_mode(img, contrast=2.2, brightness=1.0, bg_color=0):
    """Convert a PDF page to dark mode with optional dark gray background"""
    gray = img.convert("L")
    gray = ImageEnhance.Contrast(gray).enhance(contrast)
    gray = ImageEnhance.Brightness(gray).enhance(brightness)
    inverted = ImageOps.invert(gray)

    # Merge with background color
    final = Image.new("L", inverted.size, color=bg_color)
    final.paste(inverted, mask=inverted)

    return final


# -----------------------
# UI Controls
# -----------------------
uploaded_files = st.file_uploader(
    "Upload one or more PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

contrast = st.slider("Text Contrast", 1.5, 3.0, 2.2, 0.1)
brightness = st.slider("Brightness", 0.9, 1.2, 1.0, 0.05)
bg_color = st.slider("Background Darkness (0=Black → 80=Dark Gray)", 0, 80, 0, 1)
dpi = st.slider("PDF DPI (Performance)", 100, 300, 150, 10)

# -----------------------
# Processing
# -----------------------
if uploaded_files:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for uploaded_file in uploaded_files:
            st.divider()

            # Collapsible section for each PDF
            with st.expander(f"📄 {uploaded_file.name}", expanded=False):
                with st.spinner("Processing PDF..."):
                    try:
                        # Convert PDF pages to images
                        pages = convert_from_bytes(uploaded_file.read(), dpi=dpi)
                        processed_pages = []

                        # Process each page
                        for i, page in enumerate(pages):
                            if is_mostly_white(page):
                                out = smart_dark_mode(page, contrast, brightness, bg_color)
                            else:
                                out = smart_dark_mode(page, contrast=1.6, brightness=brightness, bg_color=bg_color)

                            processed_pages.append(out)
                            st.image(out, caption=f"Page {i+1}", use_column_width=True)

                        # Save processed pages to PDF in memory
                        pdf_bytes = io.BytesIO()
                        processed_pages[0].save(
                            pdf_bytes,
                            format="PDF",
                            save_all=True,
                            append_images=processed_pages[1:]
                        )

                        # Add PDF to ZIP file
                        zip_file.writestr(f"dark_{uploaded_file.name}", pdf_bytes.getvalue())

                        st.success("✅ Conversion complete for this PDF!")

                    except Exception as e:
                        st.error(f"❌ Error processing {uploaded_file.name}: {e}")

    st.success("✅ All PDFs processed!")
    st.download_button(
        label="⬇️ Download All PDFs as ZIP",
        data=zip_buffer.getvalue(),
        file_name="dark_mode_pdfs.zip",
        mime="application/zip"
    )
