Mistral OCR App
===============

Mistral OCR App is a Streamlit application for extracting text from PDFs or images using the Mistral OCR API. It provides download options in TXT, Markdown, JSON, and PDF formats.

---

Features
--------
- Extract text from PDFs and images (jpg, jpeg, png)
- Input via local upload or URL
- Preview uploaded files
- Download extracted results in multiple formats
- Modern UI styling

---

Installation
------------
1. Clone the repository:
   git clone https://github.com/shehab0911/Mistral_OCR.git
2. Navigate to the project folder:
   cd Mistral_OCR
3. (Optional) Create and activate a virtual environment
4. Install dependencies:
   pip install -r requirements.txt

---

Usage
-----
1. Run the app:
   streamlit run app.py
2. Enter your Mistral API Key in the sidebar
3. Select file type (PDF/Image) and source type (URL/Upload)
4. Upload files or provide URLs
5. Click "Process Files"
6. Preview and download extracted results

---

Dependencies
------------
- Streamlit
- Mistralai
- ReportLab

---

License
-------
Open-source project, free to use and modify.
