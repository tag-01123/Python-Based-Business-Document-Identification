from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from processing.signature_verifier import verify_signature
import cv2
import os

# Import your custom brain modules!
from processing.signature_detector import process_and_detect_signature
from processing.dl_extractor import extract_document_data_dl
from utils.pdf_generator import generate_pdf

app = FastAPI()

@app.post("/upload/")
async def process_mobile_image(file: UploadFile = File(...)):
    print(f"📥 Receiving file from phone: {file.filename}")
    
    # 🎯 FIX 1: Use the Docker 'uploads' folder!
    save_path = f"uploads/{file.filename}"
    
    # 🎯 FIX 2: AWAIT the file! This forces Python to wait until the photo 
    # is 100% downloaded from the phone before letting OpenCV touch it.
    contents = await file.read()
    with open(save_path, "wb") as f:
        f.write(contents)
        
    print("✅ File 100% saved! Starting Computer Vision pipeline...")
    
    # Read the image using OpenCV
    image = cv2.imread(save_path)
    if image is None:
        return {"message": "Image corrupted during transfer.", "company_info": None}
        
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Run Your Signature Detector
    document, signature_detected, final_image, cropped_signatures = process_and_detect_signature(image_rgb)
    
    if document is None:
        return {"message": "No document detected in the image.", "company_info": None}

    auth_status = "Not Found"
    
    if signature_detected and len(cropped_signatures) > 0:
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

    # Run Your Deep Learning Extractor
    extracted_data, raw_text = extract_document_data_dl(document)
    
    # Update the PDF data with our official Verifier status
    extracted_data["Status"] = auth_status
    
    print("Generating PDF layout...")
    
    # Generate the PDF buffer in memory
    pdf_buffer = generate_pdf(extracted_data)
    
    # 🎯 FIX 3: Save the PDF into your Docker 'outputs' folder!
    pdf_filename = f"Final_Invoice_{file.filename.split('.')[0]}.pdf"
    pdf_save_path = f"outputs/{pdf_filename}"
    
    with open(pdf_save_path, "wb") as f:
        f.write(pdf_buffer.getbuffer())
        
    print(f"🖨️ PDF Saved Successfully as: {pdf_filename}")
    
    # Send the REAL results back to the phone!
    return {
        "message": "Document processed and PDF created!", 
        "filename": file.filename,
        "signature_detected": signature_detected,
        "pdf_generated": pdf_filename,
        "extracted_data": extracted_data
    }

# 🎯 FIX 4: Update the download door to look inside the 'outputs' folder!
@app.get("/download/{filename}")
async def download_pdf(filename: str):
    file_path = f"outputs/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/pdf', filename=filename)
    return {"error": "File not found inside outputs folder!"}
