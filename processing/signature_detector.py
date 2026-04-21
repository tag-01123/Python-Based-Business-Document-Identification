import cv2
import numpy as np

def process_and_detect_signature(image):
    """Searches the bottom half of the raw image for signatures."""
    final_display_image = image.copy()
    cropped_signatures = []

    # 🧠 FIX: Stop trying to crop the edges! Just use the entire raw photo.
    document = image.copy() 

    # Search the bottom 50% of the photo for the ink
    doc_h, doc_w, _ = document.shape
    y_offset = int(doc_h * 0.5)
    search_region = document[y_offset:doc_h, :]

    # Find the ink!
    gray2 = cv2.cvtColor(search_region, cv2.COLOR_RGB2GRAY)
    thresh = cv2.adaptiveThreshold(gray2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
    dilated = cv2.dilate(thresh, kernel, iterations=1)
    contours2, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected = False
    for c in contours2:
        area = cv2.contourArea(c)
        # Using the sensitive thresholds we set earlier
        if area > 50:   
            x2, y2, w2, h2 = cv2.boundingRect(c)
            if w2 > 15 and h2 > 15:
                global_x = x2
                global_y = y_offset + y2
                cv2.rectangle(final_display_image, (global_x, global_y), (global_x + w2, global_y + h2), (0, 255, 0), 3)
                detected = True
                
                # Crop the signature and save it!
                sig_crop = search_region[y2:y2+h2, x2:x2+w2]
                cropped_signatures.append(sig_crop)

    return document, detected, final_display_image, cropped_signatures