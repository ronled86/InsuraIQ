from typing import Dict, List, Tuple
from pdfminer.high_level import extract_text
import re
import json
from .nlp import policy_analyzer
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

def _detect_language(text: str) -> str:
    """Detect the primary language of the document"""
    # Check for Hebrew characters
    hebrew_chars = len(re.findall(r'[\u0590-\u05FF]', text))
    # Check for English characters  
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    
    if hebrew_chars > english_chars * 2:
        return "he"  # Hebrew
    elif english_chars > 0:
        return "en"  # English
    else:
        return "unknown"

def _extract_hebrew_insurance_fields(text: str) -> Dict:
    """Extract fields specifically from Hebrew insurance documents using dynamic patterns"""
    data = {}
    
    # Company name patterns (Hebrew) - More comprehensive
    company_patterns = [
        r'(אדנל.*?(?:קבוצת|חברת|בע"מ))',  # Landa Group (Hebrew RTL)
        r'(לנדא.*?(?:קבוצה|חברה|בע"מ))',  # Landa Group (alternative)
        r'(Applied.*?Materials.*?Israel)',
        r'(מנורה.*?מבטחים)',
        r'(הפניקס.*?חברה.*?לביטוח)',
        r'(כלל.*?ביטוח)',
        r'(הראל.*?ביטוח)',
        r'(מגדל.*?ביטוח)',
        r'(איילון.*?ביטוח)',
        r'([^\n]*סבל.*?אדנל[^\n]*)',  # "סבל אדנל" (Leseb Landa)
        r'([^\n]*בע"מ[^\n]*)',  # Any company with Ltd designation
        r'([^\n]*עמ"ב[^\n]*)',  # Reverse Hebrew Ltd
    ]
    
    # Extract company/insurer
    for pattern in company_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Clean and use the first meaningful match
            company = matches[0].strip()
            if len(company) > 3:  # Avoid very short matches
                data['insurer'] = company
                break
    
    # Employee/Group patterns for owner identification
    employee_patterns = [
        r'([^\n]*(?:עובדי|עובדים).*?(?:קבוצת|חברת|אדנל)[^\n]*)',
        r'([^\n]*(?:קבוצת|חברת).*?(?:אדנל|לנדא)[^\n]*)',
        r'([^\n]*(?:אדנל|לנדא).*?(?:עובדי|עובדים)[^\n]*)',
        r'([^\n]*(?:בני משפחתם|בני משפחת)[^\n]*)',
        r'([^\n]*ידבועל.*?אדנל[^\n]*)',  # RTL: "לעובדי אדנל"
    ]
    
    for pattern in employee_patterns:
        matches = re.findall(pattern, text)
        if matches:
            if isinstance(matches[0], tuple):
                owner = ' '.join(matches[0]).strip()
            else:
                owner = matches[0].strip()
            if len(owner) > 5:
                data['owner_name'] = owner
                break
    
    # Policy number patterns - Dynamic search
    policy_patterns = [
        r'(?:פוליסה.*?מספר|מספר.*?פוליסה)[:\s]*([A-Z0-9\-]+)',
        r'פוליסה[:\s]*([A-Z0-9\-]{5,})',
        r'מספר[:\s]*([A-Z0-9\-]{5,})',
        r'([A-Z]{2,}\-[0-9]{4,}\-[0-9]{4})',  # Pattern like XXX-YYYY-ZZZZ
        r'([0-9]{4,})',  # Fallback to any 4+ digit number
    ]
    
    for pattern in policy_patterns:
        matches = re.findall(pattern, text)
        if matches:
            policy_num = matches[0].strip()
            if len(policy_num) >= 4:
                data['policy_number'] = policy_num
                break
    
    # Product type identification - Enhanced patterns
    product_patterns = [
        (r'(?:ביטוח.*?בריאות|בריאות.*?ביטוח|תואירב.*?חוטיב)', 'Health Insurance'),
        (r'(?:ביטוח.*?רכב|רכב.*?ביטוח)', 'Auto Insurance'),
        (r'(?:ביטוח.*?דירה|דירה.*?ביטוח|ביטוח.*?דיור)', 'Home Insurance'),
        (r'(?:ביטוח.*?חיים|חיים.*?ביטוח)', 'Life Insurance'),
        (r'(?:ביטוח.*?נסיעות|נסיעות.*?ביטוח)', 'Travel Insurance'),
        (r'(?:ביטוח.*?קבוצתי|קבוצתי.*?ביטוח|יתצובק.*?תואירב)', 'Group Insurance'),
        (r'(?:ביטוח.*?משלים|משלים.*?ביטוח)', 'Supplementary Insurance'),
        (r'(?:תנאי.*?הביטוח|חוברת.*?תנאי|יאנת.*?תרבוח)', 'Insurance Terms'),
    ]
    
    for pattern, product_type in product_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            data['product_type'] = product_type
            break
    
    # Date patterns - More flexible
    date_patterns = [
        (r'(?:תחילת.*?ביטוח|מתחיל.*?ביטוח)[:\s]*(\d{1,2}\.\d{1,2}\.\d{4})', 'start_date'),
        (r'(?:סיום.*?ביטוח|מסתיים.*?ביטוח)[:\s]*(\d{1,2}\.\d{1,2}\.\d{4})', 'end_date'),
        (r'(?:תקופת.*?ביטוח)[:\s]*(\d{1,2}\.\d{1,2}\.\d{4})', 'start_date'),
        (r'(?:עד.*?תאריך|בתוקף.*?עד)[:\s]*(\d{1,2}\.\d{1,2}\.\d{4})', 'end_date'),
        (r'(\d{1,2}\.\d{1,2}\.\d{4})', 'date_found'),  # Any date
    ]
    
    for pattern, field in date_patterns:
        matches = re.findall(pattern, text)
        if matches and field != 'date_found':
            data[field] = matches[0]
        elif matches and field == 'date_found' and not data.get('start_date'):
            # Use first found date as start date if no specific start date found
            data['start_date'] = matches[0]
    
    # Financial information - Enhanced patterns
    financial_patterns = [
        (r'(?:פרמיה.*?חודשית|תשלום.*?חודשי)[:\s]*(\d+(?:,\d{3})*(?:\.\d{2})?)', 'premium_monthly'),
        (r'(?:פרמיה.*?שנתית|תשלום.*?שנתי)[:\s]*(\d+(?:,\d{3})*(?:\.\d{2})?)', 'premium_annual'),
        (r'(?:השתתפות.*?עצמית|השתתפות)[:\s]*₪?\s*(\d+(?:,\d{3})*)', 'deductible'),
        (r'(?:סכום.*?ביטוח|כיסוי.*?מקסימלי)[:\s]*₪?\s*(\d+(?:,\d{3})*)', 'coverage_limit'),
    ]
    
    for pattern, field in financial_patterns:
        matches = re.findall(pattern, text)
        if matches:
            amount = matches[0].replace(',', '')
            try:
                data[field] = float(amount)
            except:
                pass
    
    # Look for any general amounts if specific fields weren't found
    if not any(data.get(field, 0) for field in ['premium_monthly', 'premium_annual', 'deductible', 'coverage_limit']):
        general_amount_matches = re.findall(r'₪\s*(\d+(?:,\d{3})*)', text)
        if general_amount_matches:
            # Use first found amount as premium_monthly if nothing else was found
            try:
                amount = general_amount_matches[0].replace(',', '')
                data['premium_monthly'] = float(amount)
            except:
                pass
    
    # Contact information - Enhanced patterns
    contact_patterns = [
        (r'(?:דוא"ל|מייל)[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', 'contact_email'),
        (r'(?:טלפון|פקס)[:\s]*(\d{2,3}\-\d{7})', 'contact_phone'),
        (r'(\d{2,3}\-\d{7})', 'phone_found'),  # Any phone number
        (r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', 'email_found'),  # Any email
    ]
    
    for pattern, field in contact_patterns:
        matches = re.findall(pattern, text)
        if matches:
            if field == 'phone_found' and not data.get('contact_phone'):
                data['contact_phone'] = matches[0]
            elif field == 'email_found' and not data.get('contact_email'):
                data['contact_email'] = matches[0]
            elif field not in ['phone_found', 'email_found']:
                data[field] = matches[0]
    
    # Coverage details extraction - Dynamic
    coverage_keywords = [
        'השתלות', 'ניתוחים', 'טיפולים', 'בדיקות', 'רפואה משלימה',
        'רופא משפחה', 'מומחה', 'אשפוז', 'חירום', 'רפואה פרטית',
        'תולתשה', 'םיחותינ', 'םילופיט', 'תוקידב', 'המילשמ האופר',  # RTL variations
        'החפשמ אפור', 'החמומ', 'זופשא', 'םורח', 'תיטרפ האופר'
    ]
    
    coverage_details = {}
    for keyword in coverage_keywords:
        pattern = f'([^\n]*{keyword}[^\n]*)'
        matches = re.findall(pattern, text)
        if matches:
            coverage_details[keyword] = matches[:3]  # Keep up to 3 matches per keyword
    
    if coverage_details:
        data['coverage_details'] = coverage_details
    
    # Agent/Contact person patterns
    agent_patterns = [
        r'(?:סוכן|נציג|איש קשר)[:\s]*([^\n]+)',
        r'([^\n]*דורביט[^\n]*)',  # Insurance agency
        r'([^\n]*תיווך[^\n]*)',   # Brokerage
    ]
    
    for pattern in agent_patterns:
        matches = re.findall(pattern, text)
        if matches:
            data['agent_name'] = matches[0].strip()
            break
    
    # Extract year for fallback dates
    years = re.findall(r'\b(20\d{2})\b', text)
    if years and not data.get('start_date'):
        # Use most common year found
        from collections import Counter
        most_common_year = Counter(years).most_common(1)[0][0]
        data['start_date'] = f'01/01/{most_common_year}'
        data['end_date'] = f'31/12/{most_common_year}'
    
    return data

def _extract_standard_insurance_fields(text: str) -> Dict:
    """Extract fields from English/standard insurance documents"""
    def find(pattern, default=""):
        m = re.search(pattern, text, flags=re.IGNORECASE)
        result = m.group(1).strip() if m else default
        return result

    data = {
        "owner_name": find(r"(?:Insured|Named Insured|Owner|Policy Holder)[:\s]*(.+?)(?:\n|$)") or find(r"Insured[:\s]+(.+?)(?:\n|$)"),
        "insurer": find(r"(?:Company|Insurer|Insurance Company)[:\s]*(.+?)(?:\n|$)") or find(r"(ALLSTATE|STATE FARM|PROGRESSIVE|GEICO|FARMERS|LIBERTY MUTUAL|USAA|AMERICAN FAMILY)", ""),
        "product_type": find(r"(?:Product Type|Coverage Type|Policy Type)[:\s]*(.+?)(?:\n|$)") or find(r"(Home|Auto|Life|Health|Renters?) Insurance", ""),
        "policy_number": find(r"Policy\s*(?:Number|No\.?|#)[:\s]*([A-Z0-9\-]+)") or find(r"Policy Number[:\s]*([A-Z0-9\-]+)"),
        "start_date": find(r"(?:Effective Date|Start Date|Policy Period)[:\s]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{4})") or find(r"Effective Date[:\s]*([A-Za-z]+ [0-9]{1,2}, [0-9]{4})"),
        "end_date": find(r"(?:Expiration Date|End Date|Renewal Date)[:\s]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{4})") or find(r"Expiration Date[:\s]*([A-Za-z]+ [0-9]{1,2}, [0-9]{4})"),
        "premium_monthly": find(r"(?:Monthly Premium|Monthly Payment)[:\s]*\$?([0-9,]+\.?[0-9]*)") or find(r"Premium[:\s]*\$?([0-9,]+\.?[0-9]*)"),
        "premium_annual": find(r"(?:Annual Premium|Yearly Premium)[:\s]*\$?([0-9,]+\.?[0-9]*)"),
        "deductible": find(r"Deductible[:\s]*\$?([0-9,]+\.?[0-9]*)"),
        "coverage_limit": find(r"(?:Total Coverage|Coverage Limit|Total Limit)[:\s]*\$?([0-9,]+\.?[0-9]*)") or find(r"(?:Dwelling Coverage|Coverage)[:\s]*\$?([0-9,]+\.?[0-9]*)"),
        "contact_phone": find(r"(?:Phone|Tel|Contact)[:\s]*([0-9\-\(\)\+\s]+)"),
        "contact_email": find(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"),
    }
    
    return data

def parse_pdf_to_policy_fields(file_path: str, raw_bytes: bytes | None = None, original_filename: str = "") -> Dict:
    import logging
    logger = logging.getLogger(__name__)
    
    text = _text_from_pdf(file_path)
    logger.info(f"Extracted text from PDF (length: {len(text)}, first 500 chars): {repr(text[:500])}")
    
    if not text.strip() and raw_bytes:
        logger.info("No meaningful text extracted, trying OCR...")
        text = _ocr_first_page(raw_bytes)
        logger.info(f"OCR text (length: {len(text)}, first 500 chars): {repr(text[:500])}")
    
    # Use the enhanced policy analyzer for comprehensive analysis
    if text.strip():
        logger.info("Using AI-powered policy analyzer for text analysis")
        
        # Detect policy type from filename or text
        policy_type = "auto"  # default
        if any(word in (original_filename + text).lower() for word in ["home", "house", "property", "בית", "דירה"]):
            policy_type = "home"
        elif any(word in (original_filename + text).lower() for word in ["health", "medical", "בריאות"]):
            policy_type = "health"
        elif any(word in (original_filename + text).lower() for word in ["life", "חיים"]):
            policy_type = "life"
        
        # Use the policy analyzer
        analysis_result = policy_analyzer.analyze_policy_text(text, policy_type)
        
        # Convert analysis result to policy fields format
        data = _convert_analysis_to_policy_fields(analysis_result, original_filename)
    else:
        logger.warning("No text could be extracted from PDF, creating minimal record")
        data = _create_minimal_policy_record(original_filename)
    
    # Store additional metadata
    data.update({
        "original_filename": original_filename,
        "document_type": "pdf",
        "pdf_file_path": file_path,
        "notes": "Imported from PDF with AI analysis"
    })
    
    logger.info(f"Final extracted data with confidence {data['extraction_confidence']}: {data}")
    return data

def _convert_analysis_to_policy_fields(analysis: Dict, filename: str) -> Dict:
    """Convert AI analysis result to policy fields format"""
    basic_info = analysis.get("basic_info", {})
    financial_info = analysis.get("financial_info", {})
    coverage_details = analysis.get("coverage_details", {})
    
    # Map analysis fields to policy model fields
    data = {
        "owner_name": basic_info.get("owner_name") or f"PDF Import ({filename})",
        "insurer": basic_info.get("insurer") or "Unknown",
        "product_type": _normalize_product_type(analysis.get("policy_type", "unknown")),
        "policy_number": basic_info.get("policy_number") or f"PDF-{filename[:15]}",
        "start_date": basic_info.get("start_date") or "2024-01-01",
        "end_date": basic_info.get("end_date") or "2024-12-31",
        "premium_monthly": financial_info.get("premium_monthly", 0.0),
        "premium_annual": financial_info.get("premium_annual", 0.0),
        "deductible": financial_info.get("deductible", 0.0),
        "coverage_limit": _extract_coverage_limit(coverage_details),
        "policy_language": analysis.get("language", "en"),
        "terms_and_conditions": analysis.get("terms_and_conditions", ""),
        "extraction_confidence": analysis.get("extraction_confidence", 0.0),
        "coverage_details": json.dumps(coverage_details) if coverage_details else None,
        "contact_phone": basic_info.get("contact_phone", ""),
        "contact_email": basic_info.get("contact_email", "")
    }
    
    return data

def _normalize_product_type(policy_type: str) -> str:
    """Normalize policy type to standard values"""
    type_mapping = {
        "auto": "auto",
        "car": "auto",
        "vehicle": "auto",
        "home": "home",
        "house": "home",
        "property": "home",
        "health": "health",
        "medical": "health",
        "life": "life",
        "term life": "life",
        "whole life": "life",
        "disability": "disability",
        "income protection": "disability",
        "travel": "travel",
        "renters": "renters",
        "unknown": "general"
    }
    
    return type_mapping.get(policy_type.lower(), "general")

def _extract_coverage_limit(coverage_details: Dict) -> float:
    """Extract the highest coverage limit from coverage details"""
    if not coverage_details:
        return 0.0
    
    max_limit = 0.0
    for coverage_type, coverage_data in coverage_details.items():
        if isinstance(coverage_data, dict):
            amount = coverage_data.get("amount", 0)
        else:
            amount = coverage_data
        
        if isinstance(amount, (int, float)):
            max_limit = max(max_limit, amount)
        elif isinstance(amount, str):
            try:
                # Try to parse numeric value from string
                numeric_value = float(re.sub(r'[^\d.]', '', str(amount)))
                max_limit = max(max_limit, numeric_value)
            except:
                pass
    
    return max_limit

def _create_minimal_policy_record(filename: str) -> Dict:
    """Create a minimal policy record when text extraction fails"""
    return {
        "owner_name": f"PDF Import ({filename})",
        "insurer": "Unknown",
        "product_type": "general",
        "policy_number": f"PDF-{filename[:15]}",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "premium_monthly": 0.0,
        "premium_annual": 0.0,
        "deductible": 0.0,
        "coverage_limit": 0.0,
        "policy_language": "unknown",
        "terms_and_conditions": "Text extraction failed for this document",
        "extraction_confidence": 0.1,
        "coverage_details": None,
        "contact_phone": "",
        "contact_email": ""
    }