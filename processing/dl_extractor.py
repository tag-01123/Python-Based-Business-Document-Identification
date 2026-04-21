import easyocr
import numpy as np
import cv2
import re
import difflib # ⚠️ NEW: Python's built-in Fuzzy Matcher for OCR typos!

print("🧠 Booting up Deep Learning OCR Model (This takes a few seconds)...")
reader = easyocr.Reader(['en'], gpu=False) 

# --- 📋 YOUR OFFICIAL DATABASES ---
KNOWN_COMPANIES = ['ab enterprise', 'arpan enterprise', 'xy company', 'yz sons', 'mahalaxmi gases']
KNOWN_GASES = ['co2', 'o2', 'argon', 'n2']
# ----------------------------------# ----------------------------------

def extract_document_data_dl(image_rgb):
    print("🔍 AI is scanning the document for handwriting and text...")
    
    height, width, _ = image_rgb.shape
    if width > 1200:  
        scale = 1200 / width
        image_rgb = cv2.resize(image_rgb, (int(width * scale), int(height * scale)))

    results = reader.readtext(image_rgb, detail=0) 
    raw_text = "\n".join(results)
    
    # Set up our empty data bucket 
    extracted_data = {
        "Company Name": "Unknown",
        "Gas Types": [], # New bucket for your specific gas products
        "Cylinders": []  # Keeping your 4-digit serial numbers!
    }

    # --- 🕵️‍♂️ THE SMART MATCHER ---
    
    for text_line in results:
        # Convert everything to lowercase so "O2" and "o2" match perfectly
        clean_text = text_line.lower().strip()

        # 1. Look for Companies (Using Fuzzy Matching for OCR typos!)
        # This checks if the text matches a known company with 80% accuracy
        company_matches = difflib.get_close_matches(clean_text, KNOWN_COMPANIES, n=1, cutoff=0.8)
        if company_matches:
            # If it found a match, save the beautifully formatted official name
            extracted_data["Company Name"] = company_matches[0].title()

        # 2. Look for Gas Products
        # Since gas names are short, we do a direct check
        for gas in KNOWN_GASES:
            # OCR trick: Sometimes it reads 'O2' as '02' (zero-two)
            if gas in clean_text or clean_text.replace("0", "o") == gas:
                if gas.upper() not in extracted_data["Gas Types"]:
                    extracted_data["Gas Types"].append(gas.upper())

        # 3. Look for 4-Digit Cylinder Serial Numbers (Your old logic)
        no_spaces = clean_text.replace(" ", "")
        if no_spaces.isdigit() and len(no_spaces) == 4:
            extracted_data["Cylinders"].append(no_spaces)

    return extracted_data, raw_text