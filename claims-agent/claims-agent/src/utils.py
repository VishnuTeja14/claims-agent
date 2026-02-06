import os
from pypdf import PdfReader

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python utils.py <pdf_file>")
        sys.exit(1)
    print(extract_text_from_pdf(sys.argv[1]))
