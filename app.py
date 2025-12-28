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
st.write("Convert PDFs to dark mode and preview pages like a gallery. Click a thumbnail to focus.")

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
    accept_multiple_files=True
)

contrast = st.slider("Text Contrast", 1.5, 3.0, 2.2, 0.1)
brightness = st.slider("Brightness", 0.9, 1.2, 1.0, 0.05)
bg_color = st.slider("Background Darkness (0=Black → 80=Dark Gray)", 0, 80, 0, 1)
dpi = st.slider("PDF DPI (Performance)", 100, 300, 150, 10)

# -----------------------
# Session state for processed PDFs and focused image
# -----------------------
if "pdfs" not in st.session_state:
    st.session_state.pdfs = {}  # name -> {processed_pages, thumbnails}
if "focused_image" not in st.session_state:
    st.session_state.focused_image = None

# -----------------------
# Process uploaded PDFs
# -----------------------
if uploaded_files:
    for uploaded_file in uploaded_files:
        if uploaded_file.name not in st.session_state.pdfs:
            try:
                pages = convert_from_bytes(uploaded_file.read(), dpi=dpi)
                processed_pages = []
                thumbnails = []

                for page in pages:
                    if is_mostly_white(page):
                        out = smart_dark_mode(page, contrast, brightness, bg_color)
                    else:
                        out = smart_dark_mode(page, contrast=1.6, brightness=brightness, bg_color=bg_color)

                    processed_pages.append(out)
                    # Create small thumbnail for gallery
                    thumb = out.copy()
                    thumb.thumbnail((100, 140))
                    thumbnails.append(thumb)

                st.session_state.pdfs[uploaded_file.name] = {
                    "processed_pages": processed_pages,
                    "thumbnails": thumbnails
                }

            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {e}")

# -----------------------
# Display gallery previews
# -----------------------
for pdf_name, pdf_data in st.session_state.pdfs.items():
    st.subheader(f"📄 {pdf_name}")

    thumbnails = pdf_data["thumbnails"]
    processed_pages = pdf_data["processed_pages"]

    # Show thumbnails in columns
    cols = st.columns(len(thumbnails))
    for idx, col in enumerate(cols):
        if col.button(" ", key=f"{pdf_name}_{idx}", help=f"Page {idx+1}"):
            st.session_state.focused_image = processed_pages[idx]
        col.image(thumbnails[idx], use_column_width=True)

# -----------------------
# Show focused image
# -----------------------
if st.session_state.focused_image:
    st.divider()
    st.subheader("Focused Preview")
    st.image(st.session_state.focused_image, use_column_width=True)

# -----------------------
# Prepare ZIP download
# -----------------------
if st.session_state.pdfs:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for pdf_name, pdf_data in st.session_state.pdfs.items():
            pdf_bytes = io.BytesIO()
            pdf_data["processed_pages"][0].save(
                pdf_bytes,
                format="PDF",
                save_all=True,
                append_images=pdf_data["processed_pages"][1:]
            )
            zip_file.writestr(f"dark_{pdf_name}", pdf_bytes.getvalue())

    st.download_button(
        label="⬇️ Download All PDFs as ZIP",
        data=zip_buffer.getvalue(),
        file_name="dark_mode_pdfs.zip",
        mime="application/zip"
    )
