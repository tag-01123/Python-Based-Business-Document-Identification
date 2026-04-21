# 📄 Intelligent Document Processing & Signature Verification

A full-stack mobile application and AI backend designed to automate the scanning, extraction, and verification of industrial business documents (Chalans/Invoices). 

Instead of relying on legacy OCR, this system uses a custom Deep Learning pipeline to extract specific data (like Gas Types and Cylinder Serial Numbers) and utilizes a Siamese Neural Network to mathematically verify authorized signatures to prevent forgery.

## ✨ Key Features
* **Mobile Document Scanner:** A custom React Native camera interface for aligning and capturing physical documents.
* **Deep Learning OCR:** Uses EasyOCR to accurately read messy text, handwriting, and numbers on real-world industrial paper, immune to standard Tesseract limitations.
* **Smart Parsing & Fuzzy Matching:** Automatically cross-references scanned text with a known database of companies and gas products, correcting minor OCR typos on the fly.
* **AI Signature Verification:** Isolates the document signature using OpenCV and verifies its authenticity against a database truth-sample using PyTorch.
* **Automated PDF Generation:** Compiles the extracted data and signature status into a clean, dynamically generated PDF abstract that can be downloaded straight to the mobile device.

## 🛠️ Tech Stack
**Frontend (Mobile App)**
* React Native (Expo)
* TypeScript
* FileSystem & Sharing API

**Backend (AI Server)**
* Python (FastAPI)
* PyTorch / ResNet18 (Signature Verification)
* EasyOCR (Text Extraction)
* OpenCV & NumPy (Image Processing)
* ReportLab (PDF Generation)

## 📁 Project Structure
* `/mobile-scanner-app` - The React Native frontend source code.
* `/processing` - The AI brain (EasyOCR and PyTorch Siamese Network logic).
* `/utils` - The ReportLab PDF wireframe generator.
* `/database` - Secure storage for authorized truth-sample signatures.
* `api.py` - The FastAPI server connecting the phone to the AI.

## 🚀 How to Run Locally

### 1. Start the Python AI Backend
Ensure you have Python installed, then set up a virtual environment and install the required dependencies (FastAPI, Uvicorn, Torch, EasyOCR, OpenCV).
```bash
# Create the local storage folders
mkdir uploads outputs

# Run the server
uvicorn api:app --host 0.0.0.0 --port 8000 --reload

### ⚠️ Troubleshooting Network Issues
If the Expo app fails to connect to the Metro Bundler, or if you are getting `fetch failed` errors, you may need to explicitly define your laptop's IPv4 address. 

Find your local IP address (using `ipconfig` on Windows or `ifconfig` on Mac) and run the start command like this:

**Windows:**
`set REACT_NATIVE_PACKAGER_HOSTNAME=<YOUR_LAPTOP_IP> && npx expo start --clear`

**Mac/Linux:**
`REACT_NATIVE_PACKAGER_HOSTNAME=<YOUR_LAPTOP_IP> npx expo start --clear`
