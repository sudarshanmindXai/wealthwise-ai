"""
Document Type Detection Module

Automatically identifies the type of uploaded tax document using LLM.
Supports all taxpayer types: Salaried, Business, Professional, Investor, Landlord.

Universal approach: One detector for all document types.
"""

from typing import Optional, Dict, Any
import openai
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


# OpenRouter configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Initialize OpenAI client with OpenRouter
client = openai.OpenAI(
    base_url=OPENROUTER_BASE_URL,
    api_key=OPENROUTER_API_KEY
)


def detect_document_type(
    file_content: bytes,
    filename: str,
    file_extension: str
) -> Dict[str, Any]:
    """
    Detect the type of tax document using LLM analysis.
    
    Workflow:
    1. Extract text from document (if PDF/image)
    2. Send first page/snippet to LLM
    3. LLM classifies document type
    4. Return type + confidence
    
    Args:
        file_content (bytes): Raw file content
        filename (str): Original filename
        file_extension (str): File extension (pdf, jpg, png, etc.)
    
    Returns:
        Dict with:
            - document_type (str): Detected type
            - confidence (float): Confidence score (0.0-1.0)
            - reasoning (str): Why LLM classified this way
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
        # Fallback: Return unknown with error details
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
