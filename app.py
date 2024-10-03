import fitz
import streamlit as st
from PIL import Image
import controllers.deskew as deskew

# Main layout
st.set_page_config(page_title="Image Deskewing", layout="wide")

# Define the direct path to the PDF
pdf_path = "/home/neelima/Downloads/pdf3.pdf"  # Replace with your PDF path
# pdf_path = "/home/neelima/Downloads/skewedImg1.png"  # Replace with your PDF path

# Read the PDF file
with open(pdf_path, "rb") as f:
    file_content = f.read()

# Checkbox options
st.sidebar.title("Edit Options")
deskew_checkbox = st.sidebar.checkbox("Deskew")
boundingBox_checkbox = st.sidebar.checkbox("Bounding")

# Display section for images and PDFs
st.title("Edit the File")
if deskew_checkbox:
    deskew.showDeskewResult(file_content)
else:
    # Shows the original file before edit
    original_pdf = fitz.open(stream=file_content, filetype='pdf')
    for page_number in range(len(original_pdf)):
        original_page_pix = original_pdf[page_number].get_pixmap()
        original_img = Image.frombytes("RGB", (original_page_pix.width, original_page_pix.height), original_page_pix.samples)
        st.image(original_img, caption=f"Original Page {page_number + 1}", use_column_width=True)