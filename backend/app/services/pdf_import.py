from typing import Dict
from pdfminer.high_level import extract_text
import re
try:
    from PIL import Image  # type: ignore
    import pytesseract  # type: ignore
    _OCR_AVAILABLE = True
except Exception:
    _OCR_AVAILABLE = False
import io

def _text_from_pdf(file_path: str) -> str:
    try:
        return extract_text(file_path) or ""
    except Exception:
        return ""

def _ocr_first_page(file_bytes: bytes) -> str:
    if not _OCR_AVAILABLE:
        return ""
    try:
        img = Image.open(io.BytesIO(file_bytes))
        return pytesseract.image_to_string(img)
    except Exception:
        return ""

def parse_pdf_to_policy_fields(file_path: str, raw_bytes: bytes | None = None) -> Dict:
    text = _text_from_pdf(file_path)
    if not text and raw_bytes:
        text = _ocr_first_page(raw_bytes)

    def find(pattern, default=""):
        m = re.search(pattern, text, flags=re.IGNORECASE)
        return m.group(1).strip() if m else default

    data = {
        "owner_name": find(r"Owner\s*Name[:\-]\s*(.+)"),
        "insurer": find(r"Insurer[:\-]\s*(.+)"),
        "product_type": find(r"Product\s*Type[:\-]\s*(.+)"),
        "policy_number": find(r"Policy\s*(?:Number|No\.?)[:\-]\s*(\S+)"),
        "start_date": find(r"Start\s*Date[:\-]\s*([0-9\-/]{8,10})"),
        "end_date": find(r"End\s*Date[:\-]\s*([0-9\-/]{8,10})"),
        "premium_monthly": find(r"(?:Monthly\s*)?Premium[:\-]\s*([0-9.,]+)"),
        "deductible": find(r"Deductible[:\-]\s*([0-9.,]+)"),
        "coverage_limit": find(r"Coverage\s*Limit[:\-]\s*([0-9.,]+)"),
        "notes": "Imported from PDF"
    }
    for k in ["premium_monthly","deductible","coverage_limit"]:
        v = (data.get(k) or "").replace(",", "").strip()
        try:
            data[k] = float(v) if v else 0.0
        except:
            data[k] = 0.0
    return data