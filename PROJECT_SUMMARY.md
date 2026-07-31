# 📊 Project Summary: Document Processing Pipeline

## 🎯 Project Overview

A comprehensive, production-ready Python pipeline for extracting structured data from PDF documents using intelligent document analysis, OCR, and LLM-based extraction.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         app.py (Orchestrator)                    │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
        ┌────────────────────────────────────────────┐
        │  Stage 1: Pre-processing (Rotation Fix)    │
        │  - pdf_rotation.py (fast, digital PDFs)    │
        │  - auto_rotation_ocr.py (OCR, scanned)     │
        └────────────────────────────────────────────┘
                                 │
                                 ▼
        ┌────────────────────────────────────────────┐
        │  Stage 2: Detection (Type Identification)  │
        │  - pdf_detector.py                         │
        │  - Determines: Digital vs Scanned          │
        └────────────────────────────────────────────┘
                                 │
                                 ▼
        ┌────────────────────────────────────────────┐
        │  Stage 3: Extraction (Text/Tables)         │
        │  - pdf_plumber.py (digital, table-aware)   │
        │  - schema_ocr.py (scanned, layout-aware)   │
        └────────────────────────────────────────────┘
                                 │
                                 ▼
        ┌────────────────────────────────────────────┐
        │  Stage 4: Structured Extraction            │
        │  - main.py (LLM + schema mapping)          │
        │  - Field extraction, validation, repair    │
        └────────────────────────────────────────────┘
                                 │
                                 ▼
                          📄 JSON Output
```

---

## 📁 File Structure

```
Pricing Point Entry/
│
├── 🎛️ Core Pipeline Files
│   ├── app.py                      # Main orchestrator (ENTRY POINT)
│   ├── pdf_rotation.py             # Simple rotation fix (digital PDFs)
│   ├── auto_rotation_ocr.py        # OCR-based rotation (scanned PDFs)
│   ├── pdf_detector.py             # Document type detection
│   ├── pdf_plumber.py              # Text/table extraction
│   ├── schema_ocr.py               # Layout-preserving OCR
│   ├── main.py                     # Structured field extraction
│   └── gpu_config.py               # Hardware optimization
│
├── 📋 Configuration Files
│   ├── requirements.txt            # Python dependencies
│   ├── .env.example                # Environment template
│   ├── example_schema.json         # Sample extraction schema
│   └── .gitignore                  # Git ignore rules
│
├── 📚 Documentation
│   ├── README.md                   # Main documentation
│   ├── QUICKSTART.md               # Quick start guide
│   └── PROJECT_SUMMARY.md          # This file
│
└── 🧪 Testing & Setup
    ├── test_installation.py        # Installation verification
    └── check_setup.bat             # Windows setup checker
```

---

## 🔄 Pipeline Flow

### Stage 1: Pre-processing
**Purpose:** Fix misaligned/rotated pages  
**Modules:** `pdf_rotation.py`, `auto_rotation_ocr.py`  
**Output:** Corrected PDF

```python
# Auto-detects best method based on document type
if document_is_scanned:
    use_ocr_rotation()  # Comprehensive, slower
else:
    use_simple_rotation()  # Fast, text-based
```

### Stage 2: Detection
**Purpose:** Identify document type  
**Module:** `pdf_detector.py`  
**Output:** Boolean flag (is_scanned)

```python
detector = PDFDetector(pdf_path)
is_scanned = detector.is_scanned()
# Checks for extractable text vs image content
```

### Stage 3: Extraction
**Purpose:** Extract text and tables  
**Modules:** `pdf_plumber.py`, `schema_ocr.py`  
**Output:** Text file with preserved layout

```python
if is_scanned:
    use_schema_ocr()  # OCR with layout preservation
else:
    use_pdfplumber()  # Direct extraction, table-aware
```

### Stage 4: Structured Extraction
**Purpose:** Map to JSON schema using LLM  
**Module:** `main.py`  
**Output:** Structured JSON with validated fields

```python
# Schema-driven extraction
llm_client.extract(documents, schema_config)
# Returns validated JSON matching schema
```

---

## 🛠️ Key Technologies

### PDF Processing
- **PyMuPDF (fitz)** - Fast PDF manipulation
- **pypdf** - PDF reading/writing
- **pdfplumber** - Table-aware text extraction

### OCR & Vision
- **Tesseract** - Open-source OCR engine
- **OpenCV** - Image processing, skew detection
- **pdf2image** - PDF to image conversion
- **rostaing-ocr** - Layout-preserving OCR (optional)

### AI/LLM
- **OpenAI API** - Structured field extraction
- **GPT-4o** - Default model (configurable)

### Infrastructure
- **ThreadPoolExecutor** - Parallel page processing
- **jsonschema** - Schema validation
- **python-dotenv** - Configuration management

---

## 🚀 Usage Examples

### Basic Text Extraction
```bash
python app.py --pdf document.pdf
```

### Full Pipeline with Schema
```bash
python app.py \
    --pdf loss_run.pdf \
    --email correspondence.txt \
    --schema claim_schema.json \
    --output extracted_data.json
```

### Force Specific Methods
```bash
# Use OCR-based rotation for scanned docs
python app.py --pdf scanned.pdf --rotation-method ocr

# Use schema_ocr for extraction
python app.py --pdf document.pdf --extraction-method schema_ocr
```

### Skip Stages
```bash
# Skip rotation if document is already aligned
python app.py --pdf document.pdf --no-rotation

# Extract only (no structured mapping)
python app.py --pdf document.pdf
```

---

## ⚙️ Configuration

### Environment Variables (.env)
```bash
# Required for Stage 4
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o

# Optional system paths (Windows)
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
POPPLER_PATH=C:\poppler\Library\bin

# Performance tuning
DISABLE_GPU=false
GPU_MEMORY_FRACTION=0.8
```

### Schema Configuration (JSON)
```json
{
  "fields": {
    "claim_number": {
      "type": "string",
      "required": true,
      "sources": ["PDF", "EMAIL"],
      "aliases": ["Claim #", "Claim Number"]
    }
  }
}
```

---

## 📊 Performance Characteristics

### Processing Speed (Typical)

| Document Type | Pages | Time (approx) | Bottleneck |
|--------------|-------|---------------|------------|
| Digital PDF  | 1-10  | 5-15 sec     | LLM API    |
| Digital PDF  | 50+   | 30-60 sec    | Extraction |
| Scanned PDF  | 1-10  | 20-45 sec    | OCR        |
| Scanned PDF  | 50+   | 2-5 min      | OCR        |

### Optimization Features
- ✅ Parallel page processing
- ✅ GPU acceleration (optional)
- ✅ Automatic CPU fallback
- ✅ Smart stage skipping
- ✅ Hybrid extraction (fallback logic)

---

## 🎯 Use Cases

### Insurance Claims Processing
- Extract claim numbers, dates, amounts
- Parse loss run reports
- Process policy documents

### Document Digitization
- Convert scanned forms to structured data
- Extract tables from reports
- Normalize multi-format documents

### Data Entry Automation
- Replace manual data entry
- Validate extracted data against schemas
- Flag missing or conflicting information

### Compliance & Audit
- Extract specific fields for reporting
- Track data sources (PDF vs email)
- Maintain audit trail of changes

---

## 🔒 Security Features

### API Key Protection
- Environment-based configuration
- No hardcoded credentials
- .gitignore for sensitive files

### Data Handling
- Local processing (data never leaves your system except LLM calls)
- Configurable output retention
- Secure file handling

### Validation
- Schema-based input validation
- Output validation and repair
- Error handling and logging

---

## 🧪 Testing & Validation

### Installation Check
```bash
python test_installation.py
# or on Windows:
check_setup.bat
```

### Module Testing
```bash
# Test individual components
python pdf_detector.py
python pdf_rotation.py test.pdf -o output.pdf
python pdf_plumber.py test.pdf output.txt
```

---

## 📈 Metrics & Reporting

### Pipeline Report (JSON)
```json
{
  "success": true,
  "duration_seconds": 23.4,
  "pipeline_state": {
    "stage": "completed",
    "is_scanned": false,
    "rotation_applied": true,
    "extraction_method": "pdfplumber"
  }
}
```

### Extraction Quality Metrics
- Field sources tracked
- Conflicts detected and reported
- Missing required fields flagged
- Validation errors captured

---

## 🔮 Future Enhancements

### Potential Additions
- [ ] Batch processing interface
- [ ] Web UI for document upload
- [ ] Database integration
- [ ] Custom OCR model training
- [ ] Multi-language support
- [ ] Advanced table parsing
- [ ] Document classification
- [ ] Version control for extractions

---

## 📞 Support & Maintenance

### Common Issues
1. **Tesseract not found** → Install and configure PATH
2. **Poppler not found** → Install and configure PATH
3. **GPU errors** → Automatic CPU fallback enabled
4. **LLM timeouts** → Adjust LLM_TIMEOUT in .env

### Logs & Debugging
- Console output shows stage-by-stage progress
- Intermediate files saved in `pipeline_workspace/`
- Pipeline report saved as JSON
- Enable debug mode with `--debug` flag

---

## 🏆 Key Strengths

1. **Modular Design** - Each stage is independent
2. **Intelligent Auto-detection** - Adapts to document type
3. **Robust Error Handling** - Graceful fallbacks
4. **Parallel Processing** - Fast multi-page handling
5. **Schema-Driven** - Fully configurable extraction
6. **Production-Ready** - Comprehensive logging and reporting

---

## 📝 License & Credits

**Dependencies:**
- PyMuPDF, pdfplumber, Tesseract, OpenCV
- OpenAI API
- Python standard library

**Acknowledgments:**
Built for automated document processing in insurance and financial services.

---

**Version:** 1.0  
**Last Updated:** 2024  
**Status:** Production Ready ✅
