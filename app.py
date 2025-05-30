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
def index():
    if request.method == "POST":
        uploaded_files = request.files.getlist("pdf_files")
        if not uploaded_files:
            return "לא נבחר קובץ!", 400

        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            for file in uploaded_files:
                filename = secure_filename(file.filename)
                if not filename:
                    continue
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                try:
                    file.save(file_path)
                except Exception as e:
                    return f"שגיאה בשמירת קובץ: {e}", 500
                extracted_text = extract_item12_text(file_path)
                txt_filename = filename.replace(".pdf", "_item12.txt")
                zf.writestr(txt_filename, extracted_text or "לא נמצא טקסט")
        memory_file.seek(0)
        return send_file(memory_file, download_name="item12_texts.zip", as_attachment=True)
    return '''
    <!doctype html>
    <html>
        <head><title>PDF Item12 Extractor</title></head>
        <body>
            <h1>Extract Item 12 from PDFs</h1>
            <form method="post" enctype="multipart/form-data">
                <input type="file" name="pdf_files" multiple accept="application/pdf">
                <br><br>
                <input type="submit" value="Extract and Download">
            </form>
        </body>
    </html>
    '''

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

