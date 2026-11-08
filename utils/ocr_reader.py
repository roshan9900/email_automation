import os
import re
import zlib
from pathlib import Path
from typing import Optional

def _extract_pdf_pure_python(data: bytes) -> str:
    """
    Zero-dependency pure Python PDF text stream extractor.
    Extracts and decompresses zlib streams and decodes text and hex strings.
    """
    text_out = []
    # Find all streams in PDF
    streams = re.findall(rb"stream[\r\n]+(.*?)[\r\n]+endstream", data, re.DOTALL)
    for s in streams:
        try:
            decomp = zlib.decompress(s).decode("latin1", errors="ignore")
            # 1. Hex encoded strings <48444643...>
            for h in re.findall(r"<([0-9a-fA-F]{4,})>", decomp):
                try:
                    decoded = bytes.fromhex(h).decode("latin1", errors="ignore")
                    if decoded.strip():
                        text_out.append(decoded.strip())
                except Exception:
                    pass
            # 2. Literal strings (text)
            for lit in re.findall(r"\(([^)]+)\)", decomp):
                if lit.strip() and not lit.startswith("/"):
                    text_out.append(lit.strip())
        except Exception:
            # Non-zlib or raw stream
            try:
                raw_text = s.decode("latin1", errors="ignore")
                for lit in re.findall(r"\(([^)]+)\)", raw_text):
                    text_out.append(lit.strip())
            except Exception:
                pass

    return "\n".join(text_out)

def extract_text_from_attachment(file_path: str) -> str:
    """
    Extracts text from PDF or mock image attachments.
    Uses PyMuPDF / pypdf if available, otherwise uses pure Python zlib decompressor.
    """
    path = Path(file_path)
    if not path.exists():
        # Fallback check relative to email_automation directory
        alt = Path(__file__).resolve().parent.parent / file_path
        if alt.exists():
            path = alt
        else:
            return ""
    
    ext = path.suffix.lower()
    
    if ext == ".pdf":
        # 1. Try PyMuPDF
        try:
            import fitz
            doc = fitz.open(str(path))
            text_parts = [page.get_text() for page in doc]
            doc.close()
            extracted = "\n".join(text_parts).strip()
            if extracted:
                return extracted
        except Exception:
            pass

        # 2. Try pypdf
        try:
            import pypdf
            reader = pypdf.PdfReader(str(path))
            text_parts = [page.extract_text() for page in reader.pages if page.extract_text()]
            extracted = "\n".join(text_parts).strip()
            if extracted:
                return extracted
        except Exception:
            pass

        # 3. Pure Python Standard Library Fallback (Decompresses PDF Streams)
        try:
            with open(path, "rb") as f:
                data = f.read()
            extracted = _extract_pdf_pure_python(data)
            if extracted:
                return extracted
        except Exception:
            pass

        return ""

    elif ext in [".png", ".jpg", ".jpeg", ".tiff"]:
        try:
            import pytesseract
            from PIL import Image
            img = Image.open(path)
            return pytesseract.image_to_string(img).strip()
        except Exception:
            txt_sidecar = path.with_suffix(".txt")
            if txt_sidecar.exists():
                return txt_sidecar.read_text(encoding="utf-8")
            return f"[OCR simulation for {path.name}]: Cheque/Statement image attached."

    elif ext in [".txt", ".csv", ".json"]:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read().strip()
        except Exception:
            return ""

    return ""
