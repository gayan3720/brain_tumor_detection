import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads/'

def save_scan_file(file, user_id):
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    filename = secure_filename(f"user{user_id}_" + file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    return filepath

def generate_pdf_report(user):
    # Implement PDF generation logic using reportlab or other lib
    # Placeholder returning dummy path for now
    pdf_path = f"reports/{user.username}_report.pdf"
    return pdf_path
