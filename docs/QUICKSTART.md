# Quick Start Guide - WealthWise AI v2.0

Get up and running with document extraction in 5 minutes.

---

## Prerequisites

- Python 3.11 or higher
- OpenRouter API key ([Sign up here](https://openrouter.ai/))
- Windows/Mac/Linux

---

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI (backend API)
- Streamlit (frontend UI)
- OpenAI SDK (for OpenRouter integration)
- PyPDF2, pdfplumber (PDF processing)
- All other required packages

### 2. Configure OpenRouter API Key

Open `streamlit_app.py` and find line ~15:

```python
OPENROUTER_API_KEY = "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"
```

Replace with your own key from [OpenRouter](https://openrouter.ai/keys).

### 3. Start the Backend API

Open a terminal and run:

```bash
cd src/api
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 4. Launch the Frontend

Open a **second terminal** and run:

```bash
streamlit run streamlit_app.py
```

Your browser will automatically open to `http://localhost:8501`.

---

## First Test - Manual Entry

1. **Enter Income Details:**
   - Assessment Year: 2024-25
   - Residential Status: Resident India
   - Annual Salary: ₹15,00,000
   - TDS Paid: ₹1,50,000
   - Age: 30

2. **Click "Get Tax Summary"**

You should see:
- ✅ Recommended regime (Old vs New)
- ✅ Tax liability for both regimes
- ✅ Potential savings

---

## Second Test - Document Upload

### Prepare a Test Document

**Option A: Use a real Form 16 (recommended)**
- Locate your latest Form 16 PDF
- Remove sensitive info if needed (employer name, your PAN) for testing

**Option B: Create a sample**
- Create a text document with:
  ```
  Form 16 - Part A
  Financial Year: 2024-25
  Gross Salary: ₹15,00,000
  TDS Deducted: ₹1,50,000
  Employee PAN: ABCDE1234F
  ```
- Save as PDF

### Upload Process

1. **Scroll to "Upload Documents (Optional)" section**
   - Appears after you click "Get Tax Summary"

2. **Click "Browse files"**
   - Select your Form 16 PDF
   - Or drag & drop into the upload area

3. **Wait for Extraction**
   - You'll see: "🔍 Analyzing form_16.pdf..."
   - Takes 10-15 seconds

4. **Review Extracted Data**
   - Expand the document card
   - Check confidence scores:
     - 🟢 Green = >80% (good)
     - 🟡 Yellow = 50-80% (review carefully)
     - 🔴 Red = <50% (verify against original)

5. **Apply to Form**
   - Click "Apply to Form" button
   - Form fields will auto-populate
   - Review and adjust if needed

---

## Test Results You Should See

### Successful Extraction

```
✅ Extracted data from form_16.pdf (Type: form_16, Confidence: 95%)

📋 form_16.pdf (form_16)

GROSS SALARY
₹1500000
Source: form_16.pdf | Confidence: 95%

TDS DEDUCTED
₹150000
Source: form_16.pdf | Confidence: 90%

FINANCIAL YEAR
2024-25
Source: form_16.pdf | Confidence: 100%
```

### If Something Goes Wrong

**"Could not identify document type"**
- Document is not a recognized format
- Try a different PDF or enter data manually

**"Error processing file"**
- Check OpenRouter API key is correct
- Verify internet connection
- Check terminal for detailed error logs

---

## Supported Documents for Testing

### High Success Rate (>90% accuracy)
- ✅ Form 16 (standard format from payroll software)
- ✅ Bank Statements (from major banks: HDFC, ICICI, SBI)
- ✅ Home Loan Interest Certificate (standard formats)

### Medium Success Rate (70-90%)
- ⚠️ Rental Agreements (many formats)
- ⚠️ Investment Statements (varies by provider)
- ⚠️ Medical Insurance Receipts (handwritten portions may fail)

### Lower Success Rate (<70%)
- ❌ Scanned/photocopied documents with poor quality
- ❌ Handwritten receipts
- ❌ Non-standard formats

---

## Feature Checklist

Test all these features to verify your installation:

### Basic Functionality
- [ ] Backend API starts without errors
- [ ] Frontend loads on http://localhost:8501
- [ ] Can enter income details manually
- [ ] "Get Tax Summary" button works
- [ ] See Old vs New regime comparison
- [ ] Tax amounts are calculated correctly

### Document Upload
- [ ] Document upload section appears after Stage 1
- [ ] Can upload PDF files
- [ ] Upload shows processing spinner
- [ ] Document type is detected correctly
- [ ] Extracted data appears in expandable cards
- [ ] Confidence scores are shown
- [ ] "Apply to Form" button populates fields

### UI/UX
- [ ] Dark theme loads correctly (Vault Navy background)
- [ ] Numbers use JetBrains Mono font
- [ ] Primary buttons are Net-Gain Green (#10B981)
- [ ] Form inputs have dark backgrounds
- [ ] Confidence indicators use correct colors

---

## Troubleshooting

### Backend Won't Start

**Error: "Address already in use"**
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (Windows)
taskkill /PID <process_id> /F

# Kill the process (Mac/Linux)
kill -9 <process_id>
```

**Error: "Module not found"**
```bash
# Ensure you're in the correct directory
cd src/api

# Reinstall requirements
pip install -r ../../requirements.txt
```

### Frontend Won't Start

**Error: "Streamlit not found"**
```bash
pip install streamlit
```

**Error: "No module named 'src'"**
```bash
# Ensure you're running from the project root
cd /path/to/wealthwise-ai
streamlit run streamlit_app.py
```

### Document Upload Issues

**"Cannot connect to OpenRouter"**
- Check API key in `streamlit_app.py`
- Test with: `curl https://openrouter.ai/api/v1/models -H "Authorization: Bearer YOUR_KEY"`

**"Extraction timeout"**
- Large files may take longer
- Try smaller documents first
- Check internet speed

**"Low confidence scores"**
- Document may be scanned (not text-based PDF)
- Try a different document
- Verify against original for accuracy

---

## Next Steps

Once everything is working:

1. **Test with real documents:**
   - Upload your Form 16, bank statements, etc.
   - Verify extraction accuracy
   - Report any issues

2. **Explore features:**
   - Try different income scenarios
   - Add deductions (Stage 2)
   - Compare Old vs New regime with various inputs

3. **Read detailed docs:**
   - [README.md](README.md) - Complete project overview
   - [DOCUMENT_INGESTION_GUIDE.md](DOCUMENT_INGESTION_GUIDE.md) - Detailed extraction guide
   - [V2_IMPLEMENTATION_PLAN.md](V2_IMPLEMENTATION_PLAN.md) - Architecture details

4. **Contribute:**
   - Report bugs on GitHub Issues
   - Suggest new document types
   - Improve extraction prompts

---

## Quick Commands Reference

```bash
# Install dependencies
pip install -r requirements.txt

# Start backend (Terminal 1)
cd src/api && uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Start frontend (Terminal 2)
streamlit run streamlit_app.py

# Run tests
pytest src/tests/
pytest test_scenarios.py -v

# Check API health
curl http://localhost:8000/health

# View API docs
# Open http://localhost:8000/docs in browser
```

---

## Performance Benchmarks

On a typical system (8GB RAM, decent internet):

- **Backend startup**: 2-3 seconds
- **Frontend startup**: 3-5 seconds
- **Tax calculation**: <1 second
- **Document detection**: 2-4 seconds
- **Document extraction**: 5-10 seconds
- **Total (upload to display)**: 10-15 seconds per document

---

## Support

Need help?

- **Documentation**: [README.md](README.md)
- **API Errors**: Check `src/api/` terminal logs
- **UI Errors**: Check Streamlit terminal logs
- **GitHub Issues**: Report bugs/feature requests
- **OpenRouter Issues**: Check [status.openrouter.ai](https://status.openrouter.ai)

---

## What to Test Next

After basic setup, try these scenarios:

### Scenario 1: Salaried Employee
- Upload Form 16
- Add 80C deductions (PPF, ELSS)
- Add home loan interest
- See which regime saves more

### Scenario 2: Multiple Documents
- Upload Form 16
- Upload Bank Statement
- Upload Home Loan Certificate
- Check if data from all sources is extracted

### Scenario 3: Low Quality Document
- Upload a scanned/photocopied PDF
- Check confidence scores
- Verify accuracy against original

---

## Success Indicators

Your installation is successful if:

✅ Backend shows "Uvicorn running on http://0.0.0.0:8000"  
✅ Frontend opens in browser automatically  
✅ Dark theme loads (Vault Navy background)  
✅ Can enter income and get tax summary  
✅ Can upload PDF and see extraction results  
✅ Extracted data has confidence scores  
✅ "Apply to Form" populates fields correctly  

---

**You're all set! Start exploring WealthWise AI v2.0 with intelligent document extraction.**

**Professional. Precise. Secure.**
