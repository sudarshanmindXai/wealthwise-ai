"""
Document Type Detection Module

Automatically identifies the type of uploaded tax document.
Uses rule-based detection first, with optional LLM fallback.
Supports all taxpayer types: Salaried, Business, Professional, Investor, Landlord.

Universal approach: One detector for all document types.
"""

from typing import Optional, Dict, Any, List
import os
import re
import json
from enum import Enum


class DocumentType(str, Enum):
    """Supported document types across all taxpayer categories."""
    
    # Salaried
    FORM_16 = "form16"
    SALARY_SLIP = "salary_slip"
    FORM_26AS = "form26as"
    
    # Business
    PROFIT_LOSS = "profit_loss"
    BALANCE_SHEET = "balance_sheet"
    GST_RETURN = "gst_return"
    INVOICE = "invoice"
    
    # Professional
    FEE_RECEIPT = "fee_receipt"
    EXPENSE_BILL = "expense_bill"
    
    # Investor
    BROKER_STATEMENT = "broker_statement"
    DEMAT_STATEMENT = "demat_statement"
    DIVIDEND_VOUCHER = "dividend_voucher"
    
    # Landlord
    RENTAL_AGREEMENT = "rental_agreement"
    RENT_RECEIPT = "rent_receipt"
    PROPERTY_TAX_RECEIPT = "property_tax_receipt"
    
    # Universal
    BANK_STATEMENT = "bank_statement"
    INVESTMENT_STATEMENT = "investment_statement"
    HOME_LOAN_STATEMENT = "home_loan_statement"
    MEDICAL_INSURANCE_RECEIPT = "medical_insurance_receipt"
    EDUCATION_LOAN_STATEMENT = "education_loan_statement"
    
    # Unknown
    UNKNOWN = "unknown"


# OpenRouter configuration - used as fallback
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Rule-based detection patterns
FILENAME_PATTERNS = {
    DocumentType.FORM_16: [r"form\s*16", r"form16", r"tds\s*certificate"],
    DocumentType.SALARY_SLIP: [r"salary\s*slip", r"payslip", r"pay\s*slip"],
    DocumentType.BANK_STATEMENT: [r"bank\s*statement", r"bank_stmt", r"statement.*bank", r"hdfc.*statement", r"icici.*statement", r"sbi.*statement", r"axis.*statement"],
    DocumentType.BROKER_STATEMENT: [r"zerodha", r"groww", r"upstox", r"angel", r"pnl", r"p&l", r"profit.*loss", r"tradebook", r"contract.*note"],
    DocumentType.INVESTMENT_STATEMENT: [r"elss", r"ppf", r"nps", r"lic", r"mutual\s*fund", r"sip", r"mf\s*statement"],
    DocumentType.RENTAL_AGREEMENT: [r"rent.*agreement", r"lease.*agreement", r"tenancy"],
    DocumentType.RENT_RECEIPT: [r"rent\s*receipt"],
    DocumentType.HOME_LOAN_STATEMENT: [r"home\s*loan", r"housing\s*loan", r"mortgage"],
    DocumentType.MEDICAL_INSURANCE_RECEIPT: [r"health\s*insurance", r"medical\s*insurance", r"mediclaim"],
    DocumentType.DEMAT_STATEMENT: [r"demat", r"cdsl", r"nsdl"],
}

# Content patterns for detection
CONTENT_PATTERNS = {
    DocumentType.FORM_16: [r"form\s*no\.\s*16", r"certificate.*tds", r"income.*tax.*department", r"employer.*tan", r"assessment\s*year"],
    DocumentType.SALARY_SLIP: [r"basic\s*salary", r"gross\s*salary", r"net\s*pay", r"provident\s*fund", r"hra"],
    DocumentType.BANK_STATEMENT: [r"opening\s*balance", r"closing\s*balance", r"transaction\s*date", r"withdrawal", r"deposit", r"cheque.*number", r"value\s*date"],
    DocumentType.BROKER_STATEMENT: [r"realized\s*profit", r"unrealized", r"ltcg", r"stcg", r"capital\s*gain", r"buy.*sell", r"trade\s*date", r"settlement"],
    DocumentType.INVESTMENT_STATEMENT: [r"contribution", r"interest\s*earned", r"ppf.*account", r"nps.*tier", r"elss.*fund", r"nav", r"units"],
    DocumentType.RENTAL_AGREEMENT: [r"landlord", r"tenant", r"monthly\s*rent", r"security\s*deposit", r"lease\s*period"],
    DocumentType.HOME_LOAN_STATEMENT: [r"principal", r"interest\s*paid", r"emi", r"outstanding\s*balance", r"loan\s*account"],
    DocumentType.MEDICAL_INSURANCE_RECEIPT: [r"policy\s*number", r"premium", r"sum\s*insured", r"coverage"],
}


def detect_document_type_local(
    file_content: bytes,
    filename: str,
    file_extension: str
) -> Dict[str, Any]:
    """
    Detect document type using rule-based local analysis.
    No API calls - works offline.
    
    Returns:
        Dict with document_type, confidence, reasoning, suggestions
    """
    filename_lower = filename.lower()
    ext = file_extension.lower().lstrip('.')
    
    # Extract text content for analysis
    text_content = ""
    try:
        if ext == 'csv':
            text_content = file_content.decode('utf-8', errors='ignore').lower()
        elif ext in ['xlsx', 'xls']:
            # For Excel, we check filename patterns primarily
            text_content = filename_lower
        elif ext == 'pdf':
            # Try to extract text from PDF
            try:
                import io
                from PyPDF2 import PdfReader
                pdf_file = io.BytesIO(file_content)
                reader = PdfReader(pdf_file)
                if len(reader.pages) > 0:
                    text_content = reader.pages[0].extract_text().lower()
            except:
                text_content = ""
        else:
            text_content = file_content.decode('utf-8', errors='ignore').lower()
    except:
        text_content = ""
    
    # Score each document type
    scores: Dict[DocumentType, float] = {}
    reasoning_parts: Dict[DocumentType, List[str]] = {}
    
    for doc_type, patterns in FILENAME_PATTERNS.items():
        scores[doc_type] = 0
        reasoning_parts[doc_type] = []
        
        for pattern in patterns:
            if re.search(pattern, filename_lower, re.IGNORECASE):
                scores[doc_type] += 0.4
                reasoning_parts[doc_type].append(f"Filename matches '{pattern}'")
    
    for doc_type, patterns in CONTENT_PATTERNS.items():
        if doc_type not in scores:
            scores[doc_type] = 0
            reasoning_parts[doc_type] = []
        
        for pattern in patterns:
            if re.search(pattern, text_content, re.IGNORECASE):
                scores[doc_type] += 0.15
                reasoning_parts[doc_type].append(f"Content matches '{pattern}'")
    
    # Find best match
    if scores:
        best_type = max(scores, key=scores.get)
        best_score = min(scores[best_type], 0.95)  # Cap at 0.95
        
        if best_score >= 0.3:
            # Get suggestions (other high-scoring types)
            suggestions = [
                dt.value for dt, score in sorted(scores.items(), key=lambda x: -x[1])
                if dt != best_type and score >= 0.3
            ][:2]
            
            return {
                "document_type": best_type.value,
                "confidence": best_score,
                "reasoning": "; ".join(reasoning_parts.get(best_type, [])[:3]) or "Pattern matching",
                "suggestions": suggestions
            }
    
    return {
        "document_type": DocumentType.UNKNOWN.value,
        "confidence": 0.0,
        "reasoning": "No matching patterns found",
        "suggestions": []
    }


def detect_document_type(
    file_content: bytes,
    filename: str,
    file_extension: str
) -> Dict[str, Any]:
    """
    Detect the type of tax document.
    
    Uses local rule-based detection first, then falls back to LLM if needed.
    
    Workflow:
    1. Try local rule-based detection
    2. If confidence >= 0.5, return result
    3. Otherwise, try LLM if API key is available
    4. Return best result
    
    Args:
        file_content (bytes): Raw file content
        filename (str): Original filename
        file_extension (str): File extension (pdf, jpg, png, etc.)
    
    Returns:
        Dict with:
            - document_type (str): Detected type
            - confidence (float): Confidence score (0.0-1.0)
            - reasoning (str): Why classified this way
            - suggestions (List[str]): Alternative possibilities
    
    Example:
        >>> result = detect_document_type(pdf_bytes, "form16.pdf", "pdf")
        >>> result
        {
            "document_type": "form16",
            "confidence": 0.95,
            "reasoning": "Contains 'Form 16' header, employer TAN, employee PAN",
            "suggestions": []
        }
    """
    
    # Try local rule-based detection first
    local_result = detect_document_type_local(file_content, filename, file_extension)
    
    # If local detection is confident enough, return it
    if local_result["confidence"] >= 0.5:
        return local_result
    
    # If no API key, return local result even if low confidence
    if not OPENROUTER_API_KEY:
        return local_result
    
    # Try LLM for better detection
    try:
        import openai
        client = openai.OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY
        )
        
        # Extract text preview (first 2000 chars for classification)
        text_preview = extract_text_preview(file_content, file_extension)
        
        # Build LLM prompt
        prompt = f"""You are a tax document classifier for Indian income tax documents.

Analyze this document and classify it into ONE of these types:

**Salaried Income:**
- form16: Form 16 (TDS certificate from employer)
- salary_slip: Monthly salary slip
- form26as: Form 26AS (Annual tax statement)

**Business Income:**
- profit_loss: Profit & Loss Statement
- balance_sheet: Balance Sheet
- gst_return: GST Return (GSTR-1/3B)
- invoice: Business invoice

**Professional Income:**
- fee_receipt: Professional fee receipt
- expense_bill: Business expense bill

**Investment Income:**
- broker_statement: Stock broker statement
- demat_statement: Demat account statement
- dividend_voucher: Dividend voucher

**Rental Income:**
- rental_agreement: Rental/lease agreement
- rent_receipt: Rent receipt
- property_tax_receipt: Property tax receipt

**Universal (All Types):**
- bank_statement: Bank account statement
- investment_statement: Investment statement (PPF, NPS, ELSS, LIC)
- home_loan_statement: Home loan statement
- medical_insurance_receipt: Health/medical insurance receipt
- education_loan_statement: Education loan statement

**Unknown:**
- unknown: Cannot classify confidently

---

**Document Details:**
Filename: {filename}
Extension: {file_extension}

**Document Content Preview:**
{text_preview}

---

**Output Format (JSON):**
{{
    "document_type": "<type from list above>",
    "confidence": <0.0 to 1.0>,
    "reasoning": "<why you classified this way>",
    "suggestions": ["<alternative types if unsure>"]
}}

**Instructions:**
1. Confidence > 0.8: You're very sure
2. Confidence 0.5-0.8: Likely but needs verification
3. Confidence < 0.5: Use "unknown" type
4. Look for keywords: "Form 16", "TAN", "PAN", "Profit & Loss", "GST", "Bank Statement", etc.
5. Consider document structure and layout

Respond ONLY with valid JSON, no other text."""

    try:
        # Call OpenRouter with GPT-4 Turbo
        response = client.chat.completions.create(
            model="openai/gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Indian tax document classifier. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,  # Low temperature for consistent classification
            max_tokens=500
        )
        
        # Parse LLM response
        llm_output = response.choices[0].message.content.strip()
        
        # Clean JSON if wrapped in code blocks
        if llm_output.startswith("```"):
            llm_output = llm_output.split("```")[1]
            if llm_output.startswith("json"):
                llm_output = llm_output[4:]
        
        result = json.loads(llm_output)
        
        # Validate document_type
        if result["document_type"] not in [dt.value for dt in DocumentType]:
            result["document_type"] = DocumentType.UNKNOWN.value
            result["confidence"] = 0.0
            result["reasoning"] = f"Invalid type '{result['document_type']}' returned by LLM"
        
        return result
    
    except Exception as e:
        # Fallback to local result if LLM fails
        if local_result["confidence"] > 0:
            return local_result
        return {
            "document_type": DocumentType.UNKNOWN.value,
            "confidence": 0.0,
            "reasoning": f"Error during classification: {str(e)}",
            "suggestions": []
        }


def extract_text_preview(file_content: bytes, file_extension: str, max_chars: int = 2000) -> str:
    """
    Extract text preview from document for classification.
    
    Supports:
    - PDF: Extract first page text
    - Images (JPG, PNG): OCR first page
    - CSV/Excel: Extract headers and first rows
    
    Args:
        file_content (bytes): Raw file bytes
        file_extension (str): File extension
        max_chars (int): Maximum characters to extract
    
    Returns:
        str: Text preview
    """
    
    file_ext = file_extension.lower().lstrip('.')
    
    try:
        if file_ext == 'pdf':
            # Extract PDF text using PyPDF2
            import io
            from PyPDF2 import PdfReader
            
            pdf_file = io.BytesIO(file_content)
            reader = PdfReader(pdf_file)
            
            if len(reader.pages) > 0:
                text = reader.pages[0].extract_text()
                return text[:max_chars]
            else:
                return "[Empty PDF]"
        
        elif file_ext in ['jpg', 'jpeg', 'png']:
            # For images, return a placeholder
            # In production, use OCR (pytesseract) or send image to GPT-4 Vision
            return f"[Image file: {file_extension}. OCR not implemented yet. Use GPT-4 Vision for classification.]"
        
        elif file_ext in ['csv', 'xls', 'xlsx']:
            # For spreadsheets, return headers
            return f"[Spreadsheet file: {file_extension}. Use pandas to extract headers.]"
        
        else:
            # Try to decode as text
            try:
                text = file_content.decode('utf-8', errors='ignore')
                return text[:max_chars]
            except:
                return f"[Binary file: {file_extension}]"
    
    except Exception as e:
        return f"[Error extracting text: {str(e)}]"


def get_document_description(doc_type: DocumentType) -> str:
    """Get human-readable description of document type."""
    
    descriptions = {
        DocumentType.FORM_16: "Form 16 - TDS Certificate from Employer",
        DocumentType.SALARY_SLIP: "Monthly Salary Slip",
        DocumentType.FORM_26AS: "Form 26AS - Annual Tax Statement",
        DocumentType.PROFIT_LOSS: "Profit & Loss Statement (Business)",
        DocumentType.BALANCE_SHEET: "Balance Sheet (Business)",
        DocumentType.GST_RETURN: "GST Return (GSTR-1/3B)",
        DocumentType.INVOICE: "Business Invoice",
        DocumentType.FEE_RECEIPT: "Professional Fee Receipt",
        DocumentType.EXPENSE_BILL: "Business Expense Bill",
        DocumentType.BROKER_STATEMENT: "Stock Broker Statement",
        DocumentType.DEMAT_STATEMENT: "Demat Account Statement",
        DocumentType.DIVIDEND_VOUCHER: "Dividend Voucher",
        DocumentType.RENTAL_AGREEMENT: "Rental/Lease Agreement",
        DocumentType.RENT_RECEIPT: "Rent Receipt",
        DocumentType.PROPERTY_TAX_RECEIPT: "Property Tax Receipt",
        DocumentType.BANK_STATEMENT: "Bank Account Statement",
        DocumentType.INVESTMENT_STATEMENT: "Investment Statement (PPF/NPS/ELSS/LIC)",
        DocumentType.HOME_LOAN_STATEMENT: "Home Loan Statement",
        DocumentType.MEDICAL_INSURANCE_RECEIPT: "Health Insurance Receipt",
        DocumentType.EDUCATION_LOAN_STATEMENT: "Education Loan Statement",
        DocumentType.UNKNOWN: "Unknown Document Type"
    }
    
    return descriptions.get(doc_type, "Unknown Document")
