import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image, ImageOps, ImageEnhance
import numpy as np
import io
import zipfile

st.set_page_config(
    page_title="PDF Dark Mode Converter",
    page_icon="🌙",
    layout="wide"
)

st.title("🌙 PDF Dark Mode Converter")
st.write("Convert PDFs to dark mode with collapsible previews and batch download.")

# -----------------------
# Utilities
# -----------------------
def is_mostly_white(img, threshold=200):
    gray = np.array(img.convert("L"))
    return np.mean(gray > threshold) > 0.6

def smart_dark_mode(img, contrast=2.2, brightness=1.0, bg_color=0):
    gray = img.convert("L")
    gray = ImageEnhance.Contrast(gray).enhance(contrast)
    gray = ImageEnhance.Brightness(gray).enhance(brightness)
    inverted = ImageOps.invert(gray)
    final = Image.new("L", inverted.size, color=bg_color)
    final.paste(inverted, mask=inverted)
    return final

# -----------------------
# UI Controls
# -----------------------
uploaded_files = st.file_uploader(
    "Upload one or more PDFs",
    type=["pdf"],
    accept_multiple_files=True,
    key="pdf_uploader"
)

contrast = st.slider("Text Contrast", 1.5, 3.0, 2.2, 0.1)
brightness = st.slider("Brightness", 0.9, 1.2, 1.0, 0.05)
bg_color = st.slider("Background Darkness (0=Black → 80=Dark Gray)", 0, 80, 0, 1)
dpi = st.slider("PDF DPI (Performance)", 100, 300, 150, 10)

# -----------------------
# Initialize session state
# -----------------------
if "pdfs" not in st.session_state:
    st.session_state.pdfs = {}

# Store uploaded files in session state
if uploaded_files:
    for uploaded_file in uploaded_files:
        if uploaded_file.name not in st.session_state.pdfs:
            st.session_state.pdfs[uploaded_file.name] = {"file": uploaded_file, "processed": None}

# -----------------------
# Display expanders for each uploaded PDF
# -----------------------
zip_buffer = io.BytesIO()
with zipfile.ZipFile(zip_buffer, "w") as zip_file:
    for name, pdf_data in st.session_state.pdfs.items():
        with st.expander(f"📄 {name}", expanded=False):
            file = pdf_data["file"]
            if pdf_data["processed"] is None:
                # Convert PDF pages to images
                try:
                    pages = convert_from_bytes(file.read(), dpi=dpi)
                    processed_pages = []
                    st.write("Preview of pages:")

                    for i, page in enumerate(pages):
                        if is_mostly_white(page):
                            out = smart_dark_mode(page, contrast, brightness, bg_color)
                        else:
                            out = smart_dark_mode(page, contrast=1.6, brightness=brightness, bg_color=bg_color)
                        processed_pages.append(out)
                        st.image(out, caption=f"Page {i+1}", use_column_width=True)

                    # Save processed PDF in memory
                    pdf_bytes = io.BytesIO()
                    processed_pages[0].save(
                        pdf_bytes,
                        format="PDF",
                        save_all=True,
                        append_images=processed_pages[1:]
                    )

                    # Store in session state
                    st.session_state.pdfs[name]["processed"] = pdf_bytes.getvalue()
                    st.success("✅ Conversion complete for this PDF!")

                except Exception as e:
                    st.error(f"❌ Error processing {name}: {e}")

            else:
                # Already processed, just show button
                st.success("✅ Already processed")
                st.download_button(
                    label="⬇️ Download PDF",
                    data=st.session_state.pdfs[name]["processed"],
                    file_name=f"dark_{name}",
                    mime="application/pdf"
                )

            # Add to ZIP
            if st.session_state.pdfs[name]["processed"]:
                zip_file.writestr(f"dark_{name}", st.session_state.pdfs[name]["processed"])

# -----------------------
# Download all PDFs as ZIP
# -----------------------
if st.session_state.pdfs:
    st.download_button(
        label="⬇️ Download All PDFs as ZIP",
        data=zip_buffer.getvalue(),
        file_name="dark_mode_pdfs.zip",
        mime="application/zip"
    )
