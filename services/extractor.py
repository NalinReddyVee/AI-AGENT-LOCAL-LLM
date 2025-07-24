from fastapi import UploadFile, HTTPException
from pypdf import PdfReader
import docx
import json

def extract_text(file: UploadFile) -> str:
    if file.filename.endswith(".pdf"):
        reader = PdfReader(file.file)
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    
    elif file.filename.endswith(".docx"):
        doc = docx.Document(file.file)
        return "\n".join(para.text for para in doc.paragraphs)
    
    elif file.filename.endswith(".json"):
        try:
            data = json.load(file.file)
            return json.dumps(data, indent=2)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")
