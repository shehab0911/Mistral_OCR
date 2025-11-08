import streamlit as st 
import os
import base64
import json
import time
from mistralai import Mistral
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Page setup
st.set_page_config(layout="wide", page_title="Mistral OCR App", page_icon="🧠")

# ---------- Custom CSS ----------
st.markdown("""
<style>
body, .stApp {
    background: radial-gradient(circle at 10% 20%, #141E30, #243B55);
    color: #EAEAEA;
    font-family: "Inter", sans-serif;
}
h1,h2,h3,h4{color:#FFF;font-weight:700;}
h1{text-shadow:0 0 20px rgba(0,162,255,.5);}
div[data-testid="stTextInput"] input, div[data-testid="stRadio"] > div {
    background: rgba(255,255,255,.08);
    border: 1px solid rgba(0,198,255,.3);
    border-radius: 10px;
    color: #FFF;
    padding: .4rem .8rem;
}
label{color:#FFD700;font-weight:600;}
.stButton>button{
    background: linear-gradient(90deg,#00C6FF,#0072FF);
    color:#fff;
    border:none;
    padding:.7em 1.4em;
    border-radius:12px;
    font-weight:600;
    transition:all .3s ease-in-out;
    box-shadow:0 4px 15px rgba(0,162,255,.4);
}
.stButton>button:hover{
    background: linear-gradient(90deg,#0072FF,#00C6FF);
    transform:scale(1.05);
    box-shadow:0 6px 20px rgba(0,162,255,.6);
}
div[data-testid="stFileUploader"]{
    border:2px dashed #00C6FF;
    background: rgba(255,255,255,.05);
    padding:1rem;
    border-radius:15px;
    transition:.3s;
}
div[data-testid="stFileUploader"]:hover{
    background: rgba(255,255,255,.08);
}
.result-card{
    background: rgba(0,0,0,0.3);
    border-radius:16px;
    padding:15px;
    margin-top:15px;
    color:#fff;
    font-family: "Courier New", monospace;
    line-height:1.5;
    overflow-x:auto;
}
.result-card pre{
    white-space: pre-wrap;
    word-break: break-word;
    max-height: 300px;
    overflow-y: auto;
}
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:
    st.title("🧠 Mistral OCR Settings")
    api_key = st.text_input("🔑 API Key", type="password", placeholder="sk-xxxxxxxxxxxxxxxx")
    
    if api_key.strip():
        file_type = st.radio("📄 File Type", ["PDF","Image"])
        source_type = st.radio("🌐 Source Type", ["URL","Local Upload"])
        st.markdown("---")
        st.info("Instructions:\n1. Upload files or enter URLs\n2. Click Process\n3. Download extracted results")

if not api_key.strip():
    st.warning("🔑 Please enter your API key in the left sidebar to continue.")
    st.stop()

# ---------- Main area ----------
st.title("🧠 Mistral OCR App")
st.markdown("<h4 style='color:#A9A9A9;'>Extract text from PDFs or images using Mistral OCR API</h4>", unsafe_allow_html=True)

uploaded_files = []
input_url = ""
if 'file_type' in locals() and 'source_type' in locals():
    if source_type=="URL":
        input_url = st.text_area("Enter URLs (multiple lines supported)", height=100)
    else:
        uploaded_files = st.file_uploader("Upload Files", type=["pdf","jpg","jpeg","png"], accept_multiple_files=True)

# ---------- Process Button ----------
if st.button("🚀 Process Files", use_container_width=True):
    sources = input_url.split("\n") if source_type=="URL" else uploaded_files
    if not sources:
        st.error("⚠️ Please upload files or enter URLs.")
        st.stop()

    client = Mistral(api_key=api_key)
    st.session_state["ocr_result"] = []
    st.session_state["preview_src"] = []
    st.session_state["image_bytes"] = []

    progress = st.progress(0)
    for idx, source in enumerate(sources):
        percent = int((idx+1)/len(sources)*100)
        progress.progress(percent)

        if file_type=="PDF":
            if source_type=="URL":
                document={"type":"document_url","document_url":source.strip()}
                preview_src = source.strip()
            else:
                file_bytes = source.read()
                encoded_pdf = base64.b64encode(file_bytes).decode("utf-8")
                document={"type":"document_url","document_url":f"data:application/pdf;base64,{encoded_pdf}"}
                preview_src=f"data:application/pdf;base64,{encoded_pdf}"
        else:
            if source_type=="URL":
                document={"type":"image_url","image_url":source.strip()}
                preview_src = source.strip()
            else:
                file_bytes = source.read()
                mime_type = source.type
                encoded_image = base64.b64encode(file_bytes).decode("utf-8")
                document={"type":"image_url","image_url":f"data:{mime_type};base64,{encoded_image}"}
                preview_src=f"data:{mime_type};base64,{encoded_image}"
                st.session_state["image_bytes"].append(file_bytes)

        with st.spinner(f"Processing {source if source_type=='URL' else source.name}..."):
            try:
                ocr_response = client.ocr.process(model="mistral-ocr-latest", document=document, include_image_base64=True)
                time.sleep(1)
                pages = getattr(ocr_response,"pages",[])
                result_text="\n\n".join(page.markdown for page in pages) or "No text found."
            except Exception as e:
                result_text=f"❌ Error extracting result: {e}"

            st.session_state["ocr_result"].append(result_text)
            st.session_state["preview_src"].append(preview_src)

    st.success("✅ Processing complete!")

# ---------- Results Display ----------
if st.session_state.get("ocr_result"):
    for idx, result in enumerate(st.session_state["ocr_result"]):
        st.markdown(f"<div class='result-card'>", unsafe_allow_html=True)
        
        # Preview
        if file_type=="PDF":
            st.markdown(f'<iframe src="{st.session_state["preview_src"][idx]}" width="100%" height="400" frameborder="0"></iframe>', unsafe_allow_html=True)
        else:
            if source_type=="Local Upload" and st.session_state["image_bytes"]:
                st.image(st.session_state["image_bytes"][idx], caption=f"Image {idx+1}")
            else:
                st.image(st.session_state["preview_src"][idx])
        
        # ---------- Download Options ----------
        st.write("### 💾 Download Options")
        download_choice = st.selectbox(
            f"Select format for Result {idx+1}",
            ("TXT","Markdown","JSON","PDF"),
            key=f"download_{idx}"
        )

        if download_choice=="TXT":
            st.download_button(f"⬇️ Download TXT {idx+1}", result, file_name=f"OCR_Result_{idx+1}.txt")
        elif download_choice=="Markdown":
            st.download_button(f"⬇️ Download MD {idx+1}", result, file_name=f"OCR_Result_{idx+1}.md")
        elif download_choice=="JSON":
            json_data = json.dumps({"ocr_result": result}, ensure_ascii=False, indent=2)
            st.download_button(f"⬇️ Download JSON {idx+1}", json_data, file_name=f"OCR_Result_{idx+1}.json")
        elif download_choice=="PDF":
            pdf_buffer = BytesIO()
            pdf = canvas.Canvas(pdf_buffer, pagesize=A4)
            textobject = pdf.beginText(40, 800)
            textobject.setFont("Helvetica", 10)
            for line in result.split("\n"):
                textobject.textLine(line)
            pdf.drawText(textobject)
            pdf.save()
            pdf_buffer.seek(0)
            st.download_button(f"⬇️ Download PDF {idx+1}", pdf_buffer, file_name=f"OCR_Result_{idx+1}.pdf", mime="application/pdf")

        # Extracted Text
        st.text_area(f"Result {idx+1}", value=result, height=300)
        st.markdown("</div>", unsafe_allow_html=True)
