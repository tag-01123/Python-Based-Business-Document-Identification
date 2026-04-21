from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from processing.signature_verifier import verify_signature
import shutil
import cv2
import os

# Import your custom brain modules!
from processing.signature_detector import process_and_detect_signature
#from processing.text_extractor import extract_document_data
from processing.dl_extractor import extract_document_data_dl
from utils.pdf_generator import generate_pdf
app = FastAPI()

@app.post("/upload/")
async def process_mobile_image(file: UploadFile = File(...)):
    print(f"📥 Receiving file from phone: {file.filename}")
    
    # 1. Save the incoming image from the phone
    save_path = f"received_{file.filename}"
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    print("✅ File saved! Starting Computer Vision pipeline...")
    
    # 2. Read the image using OpenCV
    # OpenCV loads images in BGR format, but your scripts use COLOR_RGB2GRAY, 
    # so we convert it to RGB first to match your logic!
    image = cv2.imread(save_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

   # 3. Run Your Signature Detector (Now returns the cropped ink!)
    document, signature_detected, final_image, cropped_signatures = process_and_detect_signature(image_rgb)
    
    if document is None:
        return {"message": "No document detected in the image.", "company_info": None}

    auth_status = "Not Found"
    
    if signature_detected and len(cropped_signatures) > 0:
        # Grab the first signature the detector found
        scanned_ink = cropped_signatures[0] 
        
        # Pass it to the Verifier along with our database file!
        is_match, auth_status = verify_signature(scanned_ink, "database/mahalaxmi_auth.jpeg")
        
        # 🚨 THE HARD STOP 🚨
        if not is_match:
            print(f"🚨 ALARM: {auth_status} - Halting execution!")
            return {
                "message": "Security Alert: Signature Forgery Detected. Processing Aborted.",
                "status": auth_status,
                "pdf_generated": None,
                "extracted_data": None
            }
    # You could even write logic here to refuse generating the PDF!
    # --------------------------------------

# 4. Run Your Deep Learning Extractor
    extracted_data, raw_text = extract_document_data_dl(document)
    
    # Update the PDF data with our official Verifier status!
    extracted_data["Status"] = auth_status
    
    # ---------------------------------------------------------
    # ---> NEW PDF GENERATOR CODE STARTS HERE <---
    print("Generating PDF layout...")
    
    # Generate the PDF buffer in memory using your ReportLab code
    pdf_buffer = generate_pdf(extracted_data)
    
    # Save the memory buffer to a real PDF file on your laptop
    pdf_filename = f"Final_Invoice_{file.filename.split('.')[0]}.pdf"
    with open(pdf_filename, "wb") as f:
        f.write(pdf_buffer.getbuffer())
        
    print(f"🖨️ PDF Saved Successfully as: {pdf_filename}")
    # ---------------------------------------------------------
    # 5. Send the REAL results back to the phone!
    return {
        "message": "Document processed and PDF created!", 
        "filename": file.filename,
        "signature_detected": signature_detected,
        "pdf_generated": pdf_filename,
        "extracted_data": extracted_data
    }
# Add this AT THE VERY BOTTOM of api.py
@app.get("/download/{filename}")
async def download_pdf(filename: str):
    import os
    if os.path.exists(filename):
        return FileResponse(filename, media_type='application/pdf', filename=filename)
    return {"error": "File not found"}
