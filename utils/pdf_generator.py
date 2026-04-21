import io
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_pdf(data):
    """Draws the final wireframe layout matching the custom design."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    margin = 50
    # ⚠️ Pushed the box down to make room for the large new header
    box_top = height - 220  
    box_bottom = 100
    box_left = margin
    box_right = width - margin
    center_x = width / 2
    
    # --- HEADER SECTION ---
    
    # 1. Company Name (Large & Bold)
    c.setFont("Helvetica-Bold", 22)
    company = data.get("Company Name", "MAHALAXMI GASES")
    c.drawCentredString(center_x, height - 60, company.upper())
    
    # 2. Address (Two lines)
    c.setFont("Helvetica", 12)
    address1 = data.get("Address1", "123, Gas Lane, Industrial Area,")
    address2 = data.get("Address2", "Vadodara, Gujarat, India - 390001")
    c.drawCentredString(center_x, height - 85, address1)
    c.drawCentredString(center_x, height - 100, address2)
    
    # 3. Titles
    c.setFont("Helvetica", 14)
    c.drawCentredString(center_x, height - 130, "Verified Cylinder Abstract")
    c.setFont("Helvetica", 9)
    c.drawCentredString(center_x, height - 145, "Verified Cylinder Abstract")
    
    # 4. Targeted Company
    c.setFont("Helvetica-Bold", 14)
    target = data.get("Target Company", "Unknown Target Company")
    c.drawCentredString(center_x, height - 180, f"Targeted Company: {target}")
    
    # --- THE WIREFRAME DRAWING ---
    c.rect(box_left, box_bottom, box_right - box_left, box_top - box_bottom)
    c.line(center_x, box_bottom, center_x, box_top) 
    
    # Horizontal lines for headers and totals
    header_y = box_top - 40
    c.line(box_left, header_y, box_right, header_y) 
    totals_y = box_bottom + 150
    c.line(box_left, totals_y, box_right, totals_y) 
    
    # --- TABLE HEADERS ---
    c.setFont("Helvetica-Bold", 12)
    c.drawString(box_left + 10, box_top - 25, "Detected Gas Types:")
    c.drawCentredString(center_x + (box_right - center_x)/2, box_top - 25, "Scanned Cylinders (SN)")
    
    # --- DYNAMIC DATA LOOPS ---
    c.setFont("Helvetica", 11)
    
    # 1. Loop through Gas Types (Left Column)
    y_pos_left = header_y - 30
    for gas in data.get("Gas Types", []):
        c.drawString(box_left + 10, y_pos_left, f"• {gas}")
        y_pos_left -= 25
        
    # 2. Loop through Cylinders (Right Column)
    y_pos_right = header_y - 30
    for cyl in data.get("Cylinders", []):
        c.drawCentredString(center_x + (box_right - center_x)/2, y_pos_right, cyl)
        y_pos_right -= 25
        
    # --- TOTALS / STATUS AREA ---
    c.setFont("Helvetica-Bold", 11)
    total_cylinders = len(data.get("Cylinders", []))
    status = data.get("Status", "Pending Verification")
    
    c.drawString(center_x + 20, totals_y - 30, f"Total Cylinders: {total_cylinders}")
    c.drawString(center_x + 20, totals_y - 60, f"Status: {status}")
    
    # --- THE SIGNATURE BOX ---
    sig_box_width = 120
    sig_box_height = 50
    sig_x = box_right - sig_box_width - 10
    sig_y = box_bottom + 10
    
    c.setLineWidth(2)
    c.rect(sig_x, sig_y, sig_box_width, sig_box_height)
    
    sig_image_path = "database/mahalaxmi_auth.jpeg" 
    if os.path.exists(sig_image_path):
        c.drawImage(sig_image_path, sig_x + 5, sig_y + 5, width=sig_box_width - 10, height=sig_box_height - 10, preserveAspectRatio=True, mask='auto')
    else:
        c.setFont("Helvetica", 10)
        c.drawString(sig_x + 30, sig_y + 30, "Authorized")
        c.drawString(sig_x + 35, sig_y + 15, "Signature")
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer