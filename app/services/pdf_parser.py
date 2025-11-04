import fitz

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        text = []
        for page in doc:
            text.append(page.get_text("text"))
    return "\n".join(text)
