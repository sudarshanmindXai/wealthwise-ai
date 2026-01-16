# Document Ingestion System - Implementation Guide

## Overview

The WealthWise AI platform now includes a **universal document extraction system** that can automatically extract tax-related data from uploaded PDFs using GPT-4 Vision. This guide explains how the system works and how to use it.

---

## Features

### ✅ Implemented in v2.0

- **Universal Document Detection**: Automatically identifies document type from 20+ supported formats
- **GPT-4 Vision Extraction**: Intelligent data extraction from complex layouts
- **Multi-Document Upload**: Process multiple documents simultaneously
- **Confidence Scoring**: Each extracted field has a confidence score (0-1)
- **Provenance Tracking**: Full audit trail (source document, timestamp, confidence)
- **User Verification UI**: Review and edit extracted data before applying to tax forms
- **Field Mapping**: Automatic mapping to TaxFacts schema
- **Dark Theme Integration**: Extraction UI follows WealthWise design system

---

## Supported Document Types

### Salaried Employees
- **Form 16**: TDS certificate from employer
- **Bank Statement**: Transaction history for interest income
- **Investment Statement**: 80C/80D deductions (PPF, ELSS, LIC, NPS)
- **Medical Insurance Premium Receipt**: 80D deductions

### Business & Professional
- **Profit & Loss Statement**: Business income/expenses
- **Balance Sheet**: Assets and liabilities
- **Business Bank Statement**: Business transactions
- **GST Returns**: Business turnover verification

### Property Owners
- **Rental Agreement**: Rental income details
- **Home Loan Interest Certificate**: Section 24 deductions
- **Home Loan Principal Certificate**: 80C deductions
- **Property Tax Receipt**: Property tax paid

### Investors
- **Capital Gains Statement**: STCG/LTCG from equity
- **Dividend Statement**: Dividend income
- **Mutual Fund Statement**: Investment details
- **Interest Certificate**: Interest from FD/bonds

### Others
- **Pension Statement**: Family pension income
- **Advance Tax Receipt**: Tax payments made
- **Form 26AS**: TDS summary from all sources

---

## How It Works

### Step 1: Document Detection

When a user uploads a PDF, the system:

1. **Extracts text** from the PDF using PyPDF2
2. **Sends a preview** (first 2000 characters) to GPT-4 Turbo
3. **Classifies the document** as one of 20+ types
4. **Returns confidence score** (0-1) and reasoning

**Implementation:** `src/ingest/document_detector.py`

```python
from src.ingest.document_detector import detect_document_type

result = detect_document_type(
    pdf_path="path/to/form16.pdf",
    openrouter_api_key="sk-or-v1-..."
)

# Result:
{
  "document_type": "form_16",
  "confidence": 0.95,
  "reasoning": "Contains PAN, TAN, Form 16 Part A/B headers",
  "suggestions": "Verify employer details match your records"
}
```

### Step 2: Data Extraction

Once the document type is known:

1. **Selects extraction prompt** based on document type
2. **Sends PDF to GPT-4 Vision** (for complex layouts) or GPT-4 Turbo (for text)
3. **Extracts structured data** in JSON format
4. **Returns extracted fields** with warnings for missing/unclear data

**Implementation:** `src/ingest/universal_extractor.py`

```python
from src.ingest.universal_extractor import extract_document_data

result = extract_document_data(
    pdf_path="path/to/form16.pdf",
    document_type="form_16",
    openrouter_api_key="sk-or-v1-..."
)

# Result:
{
  "extracted_data": {
    "employer_name": "ABC Corp",
    "employee_pan": "ABCDE1234F",
    "gross_salary": 1500000,
    "tds_deducted": 150000,
    "financial_year": "2024-25"
  },
  "field_confidence": {
    "gross_salary": 0.95,
    "tds_deducted": 0.90
  },
  "warnings": [],
  "source": "form_16_abc_corp.pdf",
  "extraction_timestamp": "2025-01-15T10:30:00"
}
```

### Step 3: Field Mapping

The extracted data is mapped to the TaxFacts schema:

```python
from src.ingest.universal_extractor import map_extracted_to_taxfacts

mapped_data = map_extracted_to_taxfacts(
    extracted_data=result["extracted_data"],
    document_type="form_16"
)

# Mapped to TaxFacts:
{
  "salary_gross": 1500000,
  "taxes_tds": 150000,
  "assessment_year": "2024-25"
}
```

---

## UI Flow

### 1. Upload Documents

After entering basic income details (Stage 1), users see the **"Upload Documents (Optional)"** section:

- **File Uploader**: Accepts multiple PDFs
- **Drag & Drop**: Modern file upload interface
- **Auto-Processing**: Files are analyzed immediately upon upload

### 2. Review Extracted Data

For each uploaded document:

- **Document Type Badge**: Shows detected type with confidence
- **Extracted Fields**: Displayed in expandable cards
- **Confidence Indicators**:
  - 🟢 Green: >80% confidence (high)
  - 🟡 Yellow: 50-80% confidence (medium)
  - 🔴 Red: <50% confidence (low - verify carefully)
- **Source Attribution**: Each field shows originating document
- **Warnings**: Highlighted if data is unclear or missing

### 3. Verify & Apply

Users can:

- **Review** all extracted fields
- **Edit** any incorrect values directly in the UI
- **Apply to Form**: One-click population of Stage 1/2 fields
- **Re-upload**: If document quality is poor

### 4. Conflict Resolution (Future)

When multiple documents provide different values for the same field:

- System will highlight the conflict
- Show all sources and confidence scores
- Let user choose which value to use

---

## Technical Architecture

### Universal Extraction Pipeline

```
┌─────────────┐
│ Upload PDF  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│ Document Detector       │ (GPT-4 Turbo)
│ - Extract text preview  │
│ - Classify document     │
│ - Return confidence     │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│ Universal Extractor     │ (GPT-4 Vision/Turbo)
│ - Load extraction prompt│
│ - Extract structured data│
│ - Add confidence scores │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│ Field Mapper            │
│ - Map to TaxFacts       │
│ - Add provenance        │
│ - Return verified data  │
└─────────────────────────┘
```

### OpenRouter Integration

The system uses OpenRouter as a unified gateway to multiple LLM providers:

- **API Key**: Single key for all models
- **Models Used**:
  - `openai/gpt-4-turbo` - Document classification
  - `openai/gpt-4-vision-preview` - Complex layout extraction
- **Cost-Effective**: Pay only for what you use
- **Fallback Support**: Can switch models if one fails

**Configuration:**

```python
# streamlit_app.py
OPENROUTER_API_KEY = "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"
```

---

## Example: Form 16 Extraction

### Input Document
```
Form 16 - Part A
Financial Year: 2024-25
Employer: ABC Corporation
PAN: AAAAA1234A
TAN: DELA12345F

Employee Details:
Name: John Doe
PAN: ABCDE1234F

Income Chargeable under Salaries: ₹15,00,000
Tax Deducted at Source: ₹1,50,000
```

### Extraction Prompt (Simplified)

```
You are extracting data from an Indian Income Tax Form 16.
Extract the following fields in JSON format:

{
  "employer_name": "Company name",
  "employer_pan": "PAN of employer",
  "employer_tan": "TAN of employer",
  "employee_name": "Employee name",
  "employee_pan": "Employee PAN",
  "financial_year": "FY (e.g., 2024-25)",
  "gross_salary": "Total salary (numeric)",
  "tds_deducted": "TDS amount (numeric)",
  "standard_deduction": "Standard deduction if mentioned"
}

Rules:
- Extract numbers only (remove ₹, commas)
- Use null if field not found
- Verify PAN format (10 characters)
```

### Extracted Result

```json
{
  "employer_name": "ABC Corporation",
  "employer_pan": "AAAAA1234A",
  "employer_tan": "DELA12345F",
  "employee_name": "John Doe",
  "employee_pan": "ABCDE1234F",
  "financial_year": "2024-25",
  "gross_salary": 1500000,
  "tds_deducted": 150000,
  "standard_deduction": 50000
}
```

### Mapped to TaxFacts

```json
{
  "assessment_year": "2024-25",
  "salary_gross": 1500000,
  "taxes_tds": 150000,
  "salary_standard_deduction_claim": true
}
```

---

## Error Handling

### Common Issues

1. **Low Confidence (<50%)**
   - **Cause**: Poor scan quality, handwritten text, non-standard format
   - **Solution**: System flags for manual verification
   - **UI**: Shows red confidence indicator

2. **Document Type "Unknown"**
   - **Cause**: Unsupported format or corrupted PDF
   - **Solution**: User sees warning, can re-upload or enter manually
   - **UI**: "⚠️ Could not identify document type"

3. **Missing Fields**
   - **Cause**: Field not present in document
   - **Solution**: Extraction returns null, user fills manually
   - **UI**: Field remains empty, no auto-population

4. **Extraction Timeout**
   - **Cause**: Large PDF or slow API response
   - **Solution**: Spinner shows progress, timeout after 30 seconds
   - **UI**: Error message with retry option

---

## Security & Privacy

### Data Handling

- ✅ **No Storage**: Uploaded PDFs are processed in-memory, then deleted
- ✅ **Temporary Files**: Saved only during processing, immediately unlinked
- ✅ **API Key Security**: OpenRouter key stored locally, not transmitted to WealthWise servers
- ✅ **User Control**: All extracted data is verifiable/editable before use
- ✅ **Audit Trail**: Every field tracks its source for compliance

### OpenRouter Privacy

- **Data Retention**: OpenRouter does not train on user data
- **Encryption**: All API calls use HTTPS
- **Model Selection**: Can choose privacy-focused models if needed

---

## Future Enhancements (v2.1)

### Planned Features

1. **Bulk Upload**: Process entire tax folder at once
2. **Conflict Resolution UI**: When multiple docs have different values
3. **Template Learning**: Improve accuracy for common formats
4. **OCR Preprocessing**: Better handling of scanned documents
5. **Multi-Page Extraction**: Extract from 50+ page statements
6. **Historical Comparison**: Compare with previous year's data

### Advanced Extraction

- **Table Extraction**: Bank statements with 100+ transactions
- **Signature Verification**: Validate document authenticity
- **Cross-Document Validation**: Check consistency across uploads
- **Smart Suggestions**: "You uploaded Form 16 but no 80C receipts - add investments?"

---

## Developer Guide

### Adding a New Document Type

1. **Add to DocumentType Enum** (`document_detector.py`):

```python
class DocumentType(str, Enum):
    # ... existing types
    NEW_DOCUMENT = "new_document"
```

2. **Create Extraction Prompt** (`universal_extractor.py`):

```python
EXTRACTION_PROMPTS = {
    # ... existing prompts
    DocumentType.NEW_DOCUMENT: """
    You are extracting from [Document Name].
    Extract these fields:
    - field_1: Description
    - field_2: Description
    ...
    """
}
```

3. **Add Field Mapping** (`universal_extractor.py`):

```python
def map_extracted_to_taxfacts(extracted_data, doc_type):
    # ... existing mappings
    elif doc_type == DocumentType.NEW_DOCUMENT:
        taxfacts["new_field"] = extracted_data.get("field_1")
```

4. **Test Extraction**:

```python
result = extract_document_data(
    "test/sample_new_doc.pdf",
    DocumentType.NEW_DOCUMENT,
    openrouter_api_key="..."
)
assert result["extracted_data"]["field_1"] is not None
```

---

## API Reference

### `detect_document_type(pdf_path, openrouter_api_key)`

**Parameters:**
- `pdf_path` (str): Absolute path to PDF file
- `openrouter_api_key` (str): OpenRouter API key

**Returns:**
```python
{
  "document_type": str,  # DocumentType enum value
  "confidence": float,   # 0.0 to 1.0
  "reasoning": str,      # Why this classification
  "suggestions": str     # What to verify
}
```

### `extract_document_data(pdf_path, document_type, openrouter_api_key)`

**Parameters:**
- `pdf_path` (str): Absolute path to PDF file
- `document_type` (DocumentType): Detected document type
- `openrouter_api_key` (str): OpenRouter API key

**Returns:**
```python
{
  "extracted_data": dict,        # Field names → values
  "field_confidence": dict,      # Field names → confidence
  "warnings": List[str],         # Issues found
  "source": str,                 # Original filename
  "extraction_timestamp": str    # ISO 8601 timestamp
}
```

### `map_extracted_to_taxfacts(extracted_data, document_type)`

**Parameters:**
- `extracted_data` (dict): Output from `extract_document_data`
- `document_type` (DocumentType): Document type

**Returns:**
```python
{
  "salary_gross": float,
  "taxes_tds": float,
  # ... other TaxFacts fields
}
```

---

## Troubleshooting

### Issue: "Cannot connect to OpenRouter"

**Solution:**
1. Check internet connection
2. Verify API key is correct
3. Test with: `curl https://openrouter.ai/api/v1/models -H "Authorization: Bearer YOUR_KEY"`

### Issue: "Extraction quality is poor"

**Solution:**
1. Ensure PDF is text-based (not scanned image)
2. Use higher resolution scans (300+ DPI)
3. Try re-uploading with better lighting/contrast
4. Manual entry may be faster for unclear documents

### Issue: "Confidence scores always low"

**Solution:**
1. Check document format matches standard templates
2. Ensure PDF is not password-protected
3. Verify document language is English (or Hindi for supported docs)

---

## Configuration

### Environment Variables

```bash
# .env file (if using python-dotenv)
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

### Feature Flags

```python
# streamlit_app.py
DOCUMENT_UPLOAD_ENABLED = True  # Enable/disable feature
MAX_FILE_SIZE_MB = 10           # Maximum PDF size
EXTRACTION_TIMEOUT = 30         # Seconds before timeout
```

---

## Performance

### Typical Processing Times

- **Detection**: 2-4 seconds (text extraction + LLM classification)
- **Extraction**: 5-10 seconds (GPT-4 Vision processing)
- **Mapping**: <1 second (pure Python logic)
- **Total**: ~10-15 seconds per document

### Optimization Tips

- Process documents in parallel (future enhancement)
- Cache common document templates
- Use GPT-4 Turbo for text-only documents (faster + cheaper)

---

## Cost Estimate

### OpenRouter Pricing (approximate)

- **GPT-4 Turbo**: $0.01 per 1K tokens (~$0.02 per document detection)
- **GPT-4 Vision**: $0.03 per 1K tokens (~$0.10 per document extraction)
- **Total per Form 16**: ~$0.12

### Monthly Costs (estimates)

- **10 users/month**: ~$12/month
- **100 users/month**: ~$120/month
- **1000 users/month**: ~$1200/month

---

## Summary

The document ingestion system provides a **universal, intelligent, and user-verified** approach to extracting tax data from PDFs. Key principles:

1. **Universal Pipeline**: One extractor for all document types
2. **LLM for Extraction Only**: Tax calculations remain deterministic
3. **User Verification Required**: All extracted data is flagged for review
4. **Full Provenance**: Every field tracks its source document
5. **Dark Theme Native**: Professional finance-grade UI

**Next Steps:**
- Try uploading a Form 16
- Review extracted data quality
- Provide feedback on extraction accuracy
- Report any document types that fail to extract properly

---

**Built with ❤️ for Indian taxpayers. Professional. Precise. Secure.**
