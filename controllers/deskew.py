from PIL import Image
import numpy as np
import cv2
import fitz
import io
import streamlit as st

# Function to deskew PDF pages
def deskewPdfPages(file_content):
    pdf_document = fitz.open(stream=file_content, filetype='pdf')
    deskewed_images = []

    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        pix = page.get_pixmap()
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        deskewed_image = fileDeskewing(img)
        deskewed_images.append(deskewed_image)

    new_pdf = fitz.open()
    for img in deskewed_images:
        img_pil = Image.fromarray(img)
        img_byte_arr = io.BytesIO()
        img_pil.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        pdf_page = new_pdf.new_page(width=img_pil.width, height=img_pil.height)
        pdf_page.insert_image(pdf_page.rect, stream=img_byte_arr.getvalue())

    pdf_bytes = new_pdf.write()
    new_pdf.close()
    return pdf_bytes

# Function to perform deskewing on an image
def fileDeskewing(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(gray, (3, 3), 0)
    binary_image = cv2.adaptiveThreshold(blurred_image, 255,
                                         cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY_INV, 9, 2)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    morphed = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)
    edges = cv2.Canny(morphed, 100, 200)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=30, minLineLength=30, maxLineGap=5)
    angles = []

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
            angles.append(angle)

    if angles:
        median_angle = np.median(angles)
        angles = [angle for angle in angles if abs(angle - median_angle) < 10]
        average_angle = np.mean(angles)
    else:
        average_angle = 0

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)

    if average_angle < -45:
        average_angle += 90
    elif average_angle > 45:
        average_angle -= 90

    M = cv2.getRotationMatrix2D(center, average_angle, 1.0)
    result_img = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return result_img

def showDeskewResult(file_content):
    deskewPdf = deskewPdfPages(file_content)
    deskewed_pdf = fitz.open(stream=deskewPdf, filetype='pdf')
    for page_number in range(len(deskewed_pdf)):
        page_pix = deskewed_pdf[page_number].get_pixmap()
        img = Image.frombytes("RGB", (page_pix.width, page_pix.height), page_pix.samples)
        st.image(img, caption=f"Deskewed Page {page_number + 1}", use_column_width=True)