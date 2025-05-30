from flask import Flask, request, send_file
import os
import pdfplumber
import re
from werkzeug.utils import secure_filename
from io import BytesIO
import zipfile

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_item12_text(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    match = re.search(
        r'^\s*ITEM\s*12[\.\s\S]*?(?=^\s*ITEM\s*13)',
        full_text,
        re.IGNORECASE | re.DOTALL | re.MULTILINE
    )
    if match:
        text = match.group(0)
        text = re.sub(r'(Page|עמוד)\s*\d+', '', text, flags=re.IGNORECASE)
        return ' '.join(text.split())
    return None

@app.route("/", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded_file = request.files.get("pdf_files")
        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            uploaded_file.save(file_path)
            extracted_text = extract_item12_text(file_path)
            if extracted_text:
                # מציג טקסט ישירות בדף החדש
                return f"""
                <h2>תוצאה עבור: {filename}</h2>
                <pre style="white-space: pre-wrap; direction: ltr;">{extracted_text}</pre>
                <a href="/">חזור לדף הראשי</a>
                """
            else:
                return f"""
                <h2>לא נמצא טקסט בפרק 12</h2>
                <a href="/">נסה שוב</a>
                """
        else:
            return """
            <h2>לא נבחר קובץ</h2>
            <a href="/">נסה שוב</a>
            """

    return """
    <!doctype html>
    <html>
        <head><title>PDF Item12 Extractor</title></head>
        <body>
            <h1>Extract Item 12 from PDFs</h1>
            <form method="post" enctype="multipart/form-data">
                <input type="file" name="pdf_files" accept="application/pdf">
                <br><br>
                <input type="submit" value="Extract and Show">
            </form>
        </body>
    </html>
    """
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

