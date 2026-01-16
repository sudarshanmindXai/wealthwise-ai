"""
Universal Document Data Extractor

Extracts structured tax data from any document type using LLM.
Works for all taxpayer types: Salaried, Business, Professional, Investor, Landlord.

Design Principle: One extraction pipeline, dynamic prompts per document type.
"""

from typing import Dict, Any, Optional, List
import openai
import json
import io
from enum import Enum

from src.ingest.document_detector import DocumentType


# OpenRouter configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Initialize OpenAI client with OpenRouter
client = openai.OpenAI(
    base_url=OPENROUTER_BASE_URL,
    api_key=OPENROUTER_API_KEY
)


# Extraction prompts per document type
EXTRACTION_PROMPTS = {
    DocumentType.FORM_16: """
Extract the following fields from this Form 16:

**Taxpayer Identity:**
- employee_name: Name of employee
- employee_pan: PAN of employee
- employer_name: Name of employer
- employer_tan: TAN of employer

**Income Details:**
- gross_salary: Gross salary (₹)
- standard_deduction: Standard deduction (₹50,000 typically)
- hra_received: HRA received (₹)
- lta_received: LTA received (₹)
- other_allowances_exempt: Other exempt allowances (₹)

**Deductions (Section 80):**
- deduction_80c_total: Total 80C deduction (₹)
- deduction_80ccd_1b_nps: NPS deduction 80CCD(1B) (₹)
- deduction_80d_self: Medical insurance 80D (₹)

**Taxes Paid:**
- taxes_tds: Total TDS deducted (₹)
- assessment_year: Assessment Year (e.g., "2024-25")
- financial_year: Financial Year (e.g., "2023-24")

**Important:** Extract ONLY values explicitly mentioned. Use null for missing values.
""",
    
    DocumentType.BANK_STATEMENT: """
Extract the following from this Bank Statement:

**Account Details:**
- account_holder_name: Account holder name
- account_number: Account number (last 4 digits only)
- bank_name: Name of bank
- statement_period_from: Start date (YYYY-MM-DD)
- statement_period_to: End date (YYYY-MM-DD)

**Income Detected:**
- interest_earned: Total interest credited (₹)
- dividend_income: Total dividend income (₹)
- rental_income_credits: Rental income detected (₹)
- salary_credits: Salary credits (₹)

**Payments Detected:**
- loan_emi_payments: Total EMI payments (₹)
- insurance_premium_payments: Insurance premium payments (₹)
- investment_payments: Investment payments (PPF, ELSS, etc.) (₹)

**Important:** Sum up all transactions in category. Use null if not found.
""",
    
    DocumentType.PROFIT_LOSS: """
Extract from this Profit & Loss Statement:

**Business Details:**
- business_name: Business name
- financial_year: Financial year

**Revenue:**
- total_revenue: Total revenue/turnover (₹)
- other_income: Other income (₹)

**Expenses:**
- cost_of_goods_sold: COGS (₹)
- operating_expenses: Operating expenses (₹)
- depreciation: Depreciation (₹)
- interest_expense: Interest expense (₹)

**Profit:**
- net_profit: Net profit before tax (₹)
- gross_profit: Gross profit (₹)

**Important:** Extract actual figures. Use null for missing values.
""",
    
    DocumentType.HOME_LOAN_STATEMENT: """
Extract from this Home Loan Statement:

**Loan Details:**
- loan_account_number: Loan account number
- borrower_name: Borrower name
- lender_name: Bank/lender name

**Loan Amount:**
- original_loan_amount: Original loan amount (₹)
- outstanding_balance: Current outstanding (₹)
- loan_sanction_date: Loan sanction date (YYYY-MM-DD)

**Repayment (for financial year):**
- principal_paid: Principal repaid in FY (₹)
- interest_paid: Interest paid in FY (₹)
- total_emi_paid: Total EMI paid in FY (₹)

**Important:** Extract FY-specific values. Use null for missing.
""",
    
    DocumentType.RENTAL_AGREEMENT: """
Extract from this Rental Agreement:

**Property Details:**
- property_address: Full address
- landlord_name: Landlord name
- landlord_pan: Landlord PAN (if mentioned)
- tenant_name: Tenant name

**Rental Details:**
- monthly_rent: Monthly rent amount (₹)
- security_deposit: Security deposit (₹)
- lease_start_date: Lease start date (YYYY-MM-DD)
- lease_end_date: Lease end date (YYYY-MM-DD)
- lease_duration_months: Duration in months

**Important:** Extract exact values. Use null for missing.
""",
    
    DocumentType.INVESTMENT_STATEMENT: """
Extract from this Investment Statement:

**Account Details:**
- account_holder_name: Account holder name
- account_number: Account/policy number
- investment_type: Type (PPF/NPS/ELSS/LIC/EPF)

**Contribution Details (for financial year):**
- contribution_amount: Total contribution in FY (₹)
- employer_contribution: Employer contribution if any (₹)
- opening_balance: Opening balance (₹)
- closing_balance: Closing balance (₹)
- interest_earned: Interest earned in FY (₹)

**Important:** Extract FY-specific values. Use null for missing.
""",
    
    DocumentType.MEDICAL_INSURANCE_RECEIPT: """
Extract from this Medical Insurance Receipt:

**Policy Details:**
- policy_number: Policy number
- insured_name: Name of insured
- insurance_company: Insurance company name

**Premium Details:**
- premium_amount: Premium paid (₹)
- payment_date: Payment date (YYYY-MM-DD)
- policy_period_from: Policy period start (YYYY-MM-DD)
- policy_period_to: Policy period end (YYYY-MM-DD)
- insured_for: Who is insured (self/spouse/parents/children)

**Important:** Extract exact premium. Use null for missing.
"""
}


def extract_document_data(
    file_content: bytes,
    document_type: DocumentType,
    filename: str,
    file_extension: str
) -> Dict[str, Any]:
    """
    Extract structured data from document using LLM.
    
    Universal extraction pipeline:
    1. Convert document to text/image
    2. Select extraction prompt based on document type
    3. Send to GPT-4 Vision/Turbo
    4. Parse structured JSON response
    5. Add provenance metadata
    
    Args:
        file_content (bytes): Raw file bytes
        document_type (DocumentType): Detected document type
        filename (str): Original filename
        file_extension (str): File extension
    
    Returns:
        Dict with:
            - extracted_data (Dict): Structured data
            - confidence (float): Overall confidence (0.0-1.0)
            - field_confidence (Dict): Per-field confidence
            - source (str): Document type
            - extraction_timestamp (str): When extracted
            - warnings (List[str]): Any warnings
    
    Example:
        >>> result = extract_document_data(pdf_bytes, DocumentType.FORM_16, "f16.pdf", "pdf")
        >>> result["extracted_data"]
        {
            "gross_salary": 1500000,
            "taxes_tds": 180000,
            "deduction_80c_total": 150000,
            ...
        }
    """
    
    # Get extraction prompt for this document type
    extraction_prompt = EXTRACTION_PROMPTS.get(
        document_type,
        "Extract all tax-relevant data from this document as JSON."
    )
    
    # Extract full document text
    document_text = extract_full_text(file_content, file_extension)
    
    # Build LLM prompt
    system_prompt = """You are an expert at extracting structured data from Indian tax documents.

**Instructions:**
1. Extract ONLY the requested fields
2. Use exact values from document (no rounding)
3. For currency, extract numeric value only (no ₹ symbol)
4. For dates, use YYYY-MM-DD format
5. If field not found, use null (not 0)
6. If field is ambiguous, add to "warnings" array
7. Provide confidence score for each field (0.0-1.0)

**Output Format (JSON):**
{
    "extracted_data": {
        "field1": value1,
        "field2": value2,
        ...
    },
    "field_confidence": {
        "field1": 0.95,
        "field2": 0.80,
        ...
    },
    "warnings": [
        "Could not find field X",
        "Field Y has ambiguous value"
    ]
}

**IMPORTANT:** Respond ONLY with valid JSON. No other text."""

    user_prompt = f"""**Document Type:** {document_type.value}

**Extraction Instructions:**
{extraction_prompt}

**Document Content:**
{document_text[:8000]}  
... [truncated if longer]

Extract the data as JSON:"""

    try:
        # Call OpenRouter with GPT-4 Turbo
        response = client.chat.completions.create(
            model="openai/gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,  # Low temperature for accuracy
            max_tokens=2000
        )
        
        # Parse LLM response
        llm_output = response.choices[0].message.content.strip()
        
        # Clean JSON if wrapped in code blocks
        if llm_output.startswith("```"):
            llm_output = llm_output.split("```")[1]
            if llm_output.startswith("json"):
                llm_output = llm_output[4:]
        
        result = json.loads(llm_output)
        
        # Add metadata
        from datetime import datetime
        
        result["source"] = document_type.value
        result["extraction_timestamp"] = datetime.utcnow().isoformat()
        result["filename"] = filename
        
        # Calculate overall confidence (average of field confidences)
        field_confidences = result.get("field_confidence", {}).values()
        if field_confidences:
            result["confidence"] = sum(field_confidences) / len(field_confidences)
        else:
            result["confidence"] = 0.7  # Default moderate confidence
        
        return result
    
    except Exception as e:
        # Return error result
        from datetime import datetime
        
        return {
            "extracted_data": {},
            "field_confidence": {},
            "confidence": 0.0,
            "source": document_type.value,
            "extraction_timestamp": datetime.utcnow().isoformat(),
            "filename": filename,
            "warnings": [f"Extraction failed: {str(e)}"]
        }


def extract_full_text(file_content: bytes, file_extension: str) -> str:
    """
    Extract full text from document.
    
    Supports:
    - PDF: All pages
    - Images: OCR (placeholder for now)
    - CSV/Excel: All data
    
    Args:
        file_content (bytes): Raw file bytes
        file_extension (str): File extension
    
    Returns:
        str: Full extracted text
    """
    
    file_ext = file_extension.lower().lstrip('.')
    
    try:
        if file_ext == 'pdf':
            # Extract all pages from PDF
            from PyPDF2 import PdfReader
            
            pdf_file = io.BytesIO(file_content)
            reader = PdfReader(pdf_file)
            
            text_parts = []
            for page in reader.pages:
                text_parts.append(page.extract_text())
            
            return "\n\n--- Page Break ---\n\n".join(text_parts)
        
        elif file_ext in ['jpg', 'jpeg', 'png']:
            # For images, return placeholder
            # In production, use pytesseract or GPT-4 Vision
            return "[Image file - OCR not implemented. Use GPT-4 Vision for extraction.]"
        
        else:
            # Try to decode as text
            try:
                return file_content.decode('utf-8', errors='ignore')
            except:
                return "[Binary file - cannot extract text]"
    
    except Exception as e:
        return f"[Error extracting text: {str(e)}]"


def map_extracted_to_taxfacts(extracted_data: Dict[str, Any], document_type: DocumentType) -> Dict[str, Any]:
    """
    Map extracted document data to TaxFacts schema fields.
    
    This function knows which TaxFacts fields to populate based on document type.
    
    Args:
        extracted_data (Dict): Raw extracted data
        document_type (DocumentType): Type of document
    
    Returns:
        Dict: Mapped to TaxFacts field names
    
    Example:
        >>> extracted = {"gross_salary": 1500000, "taxes_tds": 180000}
        >>> mapped = map_extracted_to_taxfacts(extracted, DocumentType.FORM_16)
        >>> mapped
        {
            "salary_gross": 1500000,
            "taxes_tds": 180000,
            "salary_standard_deduction_claim": True
        }
    """
    
    mapped = {}
    
    if document_type == DocumentType.FORM_16:
        # Map Form 16 fields to TaxFacts
        if "gross_salary" in extracted_data:
            mapped["salary_gross"] = extracted_data["gross_salary"]
        
        if "standard_deduction" in extracted_data and extracted_data["standard_deduction"]:
            mapped["salary_standard_deduction_claim"] = True
        
        if "hra_received" in extracted_data or "lta_received" in extracted_data or "other_allowances_exempt" in extracted_data:
            hra = extracted_data.get("hra_received") or 0
            lta = extracted_data.get("lta_received") or 0
            other_exempt = extracted_data.get("other_allowances_exempt") or 0
            total_exempt = hra + lta + other_exempt
            mapped["salary_exempt_allowances"] = total_exempt
        
        if "deduction_80c_total" in extracted_data:
            mapped["deduction_80c"] = extracted_data["deduction_80c_total"]
        
        if "deduction_80ccd_1b_nps" in extracted_data:
            mapped["deduction_80ccd_1b"] = extracted_data["deduction_80ccd_1b_nps"]
        
        if "deduction_80d_self" in extracted_data:
            mapped["deduction_80d_self"] = extracted_data["deduction_80d_self"]
        
        if "taxes_tds" in extracted_data:
            mapped["taxes_tds"] = extracted_data["taxes_tds"]
        
        if "assessment_year" in extracted_data:
            mapped["assessment_year"] = extracted_data["assessment_year"]
    
    elif document_type == DocumentType.BANK_STATEMENT:
        # Map Bank Statement to TaxFacts
        if "interest_earned" in extracted_data:
            mapped["other_income_savings_interest"] = extracted_data["interest_earned"]
        
        if "dividend_income" in extracted_data:
            mapped["other_income_dividends"] = extracted_data["dividend_income"]
        
        if "rental_income_credits" in extracted_data:
            mapped["property_letout_net_income"] = extracted_data["rental_income_credits"]
    
    elif document_type == DocumentType.PROFIT_LOSS:
        # Map P&L to TaxFacts
        if "net_profit" in extracted_data:
            mapped["business_non_presumptive_profit"] = extracted_data["net_profit"]
            mapped["business_has_income"] = True
    
    elif document_type == DocumentType.HOME_LOAN_STATEMENT:
        # Map Home Loan to TaxFacts
        if "interest_paid" in extracted_data:
            mapped["home_loan_interest_paid"] = extracted_data["interest_paid"]
        
        if "principal_paid" in extracted_data:
            mapped["home_loan_principal_paid"] = extracted_data["principal_paid"]
        
        if "outstanding_balance" in extracted_data:
            mapped["home_loan_amount"] = extracted_data["outstanding_balance"]
    
    elif document_type == DocumentType.RENTAL_AGREEMENT:
        # Map Rental Agreement to TaxFacts
        if "monthly_rent" in extracted_data and "lease_duration_months" in extracted_data:
            annual_rent = extracted_data["monthly_rent"] * min(extracted_data["lease_duration_months"], 12)
            mapped["property_letout_net_income"] = annual_rent
            mapped["property_count"] = 1
    
    elif document_type == DocumentType.INVESTMENT_STATEMENT:
        # Map Investment Statement to TaxFacts
        investment_type = extracted_data.get("investment_type", "").lower()
        contribution = extracted_data.get("contribution_amount", 0)
        
        if "ppf" in investment_type:
            mapped["investment_ppf_amount"] = contribution
            mapped["deduction_80c"] = contribution
        elif "nps" in investment_type:
            mapped["investment_nps_amount"] = contribution
            mapped["deduction_80ccd_1b"] = contribution
        elif "elss" in investment_type:
            mapped["investment_elss_amount"] = contribution
            mapped["deduction_80c"] = contribution
        elif "lic" in investment_type or "life insurance" in investment_type:
            mapped["investment_lic_premium"] = contribution
            mapped["deduction_80c"] = contribution
    
    elif document_type == DocumentType.MEDICAL_INSURANCE_RECEIPT:
        # Map Medical Insurance to TaxFacts
        if "premium_amount" in extracted_data:
            insured_for = extracted_data.get("insured_for", "self").lower()
            
            if "self" in insured_for or "spouse" in insured_for:
                mapped["deduction_80d_self"] = extracted_data["premium_amount"]
            elif "parent" in insured_for:
                mapped["deduction_80d_parents"] = extracted_data["premium_amount"]
    
    # Add source provenance
    mapped["_source"] = document_type.value
    
    return mapped
