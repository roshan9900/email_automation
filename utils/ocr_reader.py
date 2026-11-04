import os
from pathlib import Path
from typing import Optional

def extract_text_from_attachment(file_path: str) -> str:
    """
    Extracts text from PDF or mock image attachments.
    Uses PyMuPDF (fitz) if available.
    """
    path = Path(file_path)
    if not path.exists():
        return ""
    
    ext = path.suffix.lower()
    
    if ext == ".pdf":
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(str(path))
            text_parts = []
            for page in doc:
                text_parts.append(page.get_text())
            doc.close()
            return "\n".join(text_parts).strip()
        except ImportError:
            # Fallback reading as plain text or bytes
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
            except Exception:
                return ""
        except Exception as e:
            return f"Error extracting PDF: {e}"
    
    elif ext in [".png", ".jpg", ".jpeg", ".tiff"]:
        # Simulated OCR extractor for image formats if tesseract not installed
        try:
            import pytesseract
            from PIL import Image
            img = Image.open(path)
            return pytesseract.image_to_string(img).strip()
        except Exception:
            # Check if there is an accompanying .txt mock or return standard simulated OCR text
            txt_sidecar = path.with_suffix(".txt")
            if txt_sidecar.exists():
                return txt_sidecar.read_text(encoding="utf-8")
            return f"[OCR simulation for {path.name}]: Cheque/Statement image attached."
            
    elif ext in [".txt", ".csv", ".json"]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            return ""

    return ""

