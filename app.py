def extract_item12_text(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    matches = list(re.finditer(
        r'^\s*ITEM\s*12[\.\s\S]*?(?=^\s*ITEM\s*13)',
        full_text,
        re.IGNORECASE | re.DOTALL | re.MULTILINE
    ))

    if matches:
        match = matches[-1]  # נבחר את ההתאמה האחרונה - כלומר את הפרק האמיתי, לא טבלת תוכן
        text = match.group(0)
        text = re.sub(r'(Page|עמוד)\s*\d+', '', text, flags=re.IGNORECASE)
        return ' '.join(text.split())

    return "No ITEM 12 section found."
def extract_item12_text(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    matches = list(re.finditer(
        r'^\s*ITEM\s*12[\.\s\S]*?(?=^\s*ITEM\s*13)',
        full_text,
        re.IGNORECASE | re.DOTALL | re.MULTILINE
    ))

    if matches:
        match = matches[-1]  # נבחר את ההתאמה האחרונה - כלומר את הפרק האמיתי, לא טבלת תוכן
        text = match.group(0)
        text = re.sub(r'(Page|עמוד)\s*\d+', '', text, flags=re.IGNORECASE)
        return ' '.join(text.split())

    return "No ITEM 12 section found."
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

    matches = list(re.finditer(
        r'^\s*ITEM\s*12[\.\s\S]*?(?=^\s*ITEM\s*13)',
        full_text,
        re.IGNORECASE | re.DOTALL | re.MULTILINE
    ))

    if matches:
        match = matches[-1]  # נבחר את ההתאמה האחרונה - כלומר את הפרק האמיתי, לא טבלת תוכן
        text = match.group(0)
        text = re.sub(r'(Page|עמוד)\s*\d+', '', text, flags=re.IGNORECASE)
        return ' '.join(text.split())

    return "No ITEM 12 section found."

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded_files = request.files.getlist("pdf_files")
        memory_file = BytesIO()

        with zipfile.ZipFile(memory_file, 'w') as zf:
            for file in uploaded_files:
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)

                extracted_text = extract_item12_text(file_path)

                print(f"=== קובץ: {filename} ===")
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

    matches = list(re.finditer(
        r'^\s*ITEM\s*12[\.\s\S]*?(?=^\s*ITEM\s*13)',
        full_text,
        re.IGNORECASE | re.DOTALL | re.MULTILINE
    ))

    if matches:
        match = matches[-1]  # נבחר את ההתאמה האחרונה - כלומר את הפרק האמיתי, לא טבלת תוכן
        text = match.group(0)
        text = re.sub(r'(Page|עמוד)\s*\d+', '', text, flags=re.IGNORECASE)
        return ' '.join(text.split())

    return "No ITEM 12 section found."

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded_files = request.files.getlist("pdf_files")
        memory_file = BytesIO()

        with zipfile.ZipFile(memory_file, 'w') as zf:
            for file in uploaded_files:
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)

                extracted_text = extract_item12_text(file_path)

                print(f"=== קובץ: {filename} ===")
                if extracted_text:
                    print(f"אורך הטקסט שהופק: {len(extracted_text)} תווים")
                    txt_filename = filename.replace(".pdf", "_item12.txt")
                    zf.writestr(txt_filename, extracted_text)
                else:
                    print("לא הופק טקסט בכלל")

        memory_file.seek(0)
        return send_file(memory_file, download_name="item12_texts.zip", as_attachment=True)

    return """
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
    """

if __name__ == "__main__":
    app.run(debug=True)

