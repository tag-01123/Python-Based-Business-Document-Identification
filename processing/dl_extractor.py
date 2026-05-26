import easyocr
import numpy as np
import cv2
import re
import difflib

print("🧠 Booting up Deep Learning OCR Model...")
reader = easyocr.Reader(['en'], gpu=False) 

# --- 📋 YOUR OFFICIAL DATABASES ---
# Added Rolex Fabricators to the known list so it can recognize the buyer too!
KNOWN_COMPANIES = ['ab enterprise', 'arpan enterprise', 'xy company', 'yz sons', 'mahalaxmi gases', 'rolex fabricators']

# Upgraded to match the exact gases found on the Mahalaxmi invoice
KNOWN_GASES = ['co2', 'o2', 'argon', 'n2', 'oxygen', 'argon+co2']
# ----------------------------------

def extract_document_data_dl(image_rgb):
    print("🔍 AI is scanning the document for text...")
    
    height, width, _ = image_rgb.shape
    if width > 1200:  
        scale = 1200 / width
        image_rgb = cv2.resize(image_rgb, (int(width * scale), int(height * scale)))

    # 🐛 THE SLASH FIX: Tell EasyOCR specifically not to ignore slashes, commas, and decimals!
    results = reader.readtext(image_rgb, detail=0, allowlist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz/.-+,: ') 
    raw_text = "\n".join(results)
    
    # 🪣 UPDATED DATA BUCKET (Matches what your React Native app expects!)
    extracted_data = {
        "Company Name": "Unknown",
        "Date": "Unknown",
        "Total": "Unknown",
        "Gas Types": [], 
        "Cylinders": []  
    }

    # --- 🕵️‍♂️ THE SMART MATCHER ---
    for i, text_line in enumerate(results):
        clean_text = text_line.lower().strip()

        # 1. Look for Companies (Using Fuzzy Match)
        company_matches = difflib.get_close_matches(clean_text, KNOWN_COMPANIES, n=1, cutoff=0.8)
        if company_matches:
            extracted_data["Company Name"] = company_matches[0].title()

        # 2. Look for Gas Products
        for gas in KNOWN_GASES:
            if gas in clean_text or clean_text.replace("0", "o") == gas:
                if gas.upper() not in extracted_data["Gas Types"]:
                    extracted_data["Gas Types"].append(gas.upper())

        # 3. Look for Dates (Fixing the Slash Bug!)
        # This regex magically finds any text formatted like DD/MM/YY or DD/MM/YYYY
        date_match = re.search(r'\b\d{2}/\d{2}/\d{2,4}\b', text_line)
        if date_match:
            extracted_data["Date"] = date_match.group(0)

        # 4. Look for the Grand Total Money Amount
        # Finds numbers with commas and decimals (e.g., 13,604.00 or 11,529.00)
        if "total" in clean_text:
            amounts = re.findall(r'\d{1,3}(?:,\d{3})*(?:\.\d{2})', clean_text)
            if amounts:
                extracted_data["Total"] = amounts[-1] # Grabs the last number on the line
            else:
                # Sometimes OCR splits the word "Total" and the number onto two different lines.
                # This safely checks the next line down just in case!
                if i + 1 < len(results):
                    next_line = results[i+1]
                    amounts_next = re.findall(r'\d{1,3}(?:,\d{3})*(?:\.\d{2})', next_line)
                    if amounts_next:
                        extracted_data["Total"] = amounts_next[-1]

    return extracted_data, raw_text
