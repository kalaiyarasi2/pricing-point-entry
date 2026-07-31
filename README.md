# 📄 Document Processing Pipeline

A comprehensive, modular Python pipeline for extracting structured data from PDF documents using OCR, text extraction, and LLM-based schema mapping.

## 🎯 Overview

This pipeline processes PDF documents through four intelligent stages:

1. **Pre-processing** → Auto-rotate misaligned pages
2. **Detection** → Identify digital vs scanned documents
3. **Extraction** → Extract text/tables with layout preservation
4. **Structured Extraction** → Map to JSON schema using LLM

## ✨ Features

- 🔄 **Automatic orientation correction** for rotated/skewed documents
- 🔍 **Smart document detection** (digital vs scanned)
- 📊 **Table-aware extraction** preserving structure and layout
- 🤖 **LLM-powered structured extraction** with schema validation
- ⚡ **Parallel processing** for multi-page documents
- 🎛️ **Flexible configuration** with intelligent auto-detection
- 🔧 **GPU acceleration support** with automatic CPU fallback

## 📦 Installation

### Prerequisites

1. **Python 3.8+**
   ```bash
   python --version
   ```

2. **Tesseract OCR** (for OCR processing)
   - Windows: [Download installer](https://github.com/UB-Mannheim/tesseract/wiki)
   - macOS: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`

3. **Poppler** (for PDF to image conversion)
   - Windows: [Download binaries](https://github.com/oschwartz10612/poppler-windows/releases) and add to PATH
   - macOS: `brew install poppler`
   - Linux: `sudo apt-get install poppler-utils`

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Configuration

1. Copy the environment template:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-api-key-here
   OPENAI_MODEL=gpt-4o
   ```

3. (Optional) Configure Tesseract/Poppler paths if not in system PATH

## 🚀 Quick Start

### Basic Usage

Extract text from a PDF:
```bash
python app.py --pdf document.pdf
```

### Full Pipeline with Structured Extraction

```bash
python app.py --pdf document.pdf --email email.txt --schema schema.json --output result.json
```

### Skip Rotation Fix

```bash
python app.py --pdf document.pdf --no-rotation
```

### Force Specific Extraction Method

```bash
python app.py --pdf document.pdf --extraction-method schema_ocr
```

## 📚 Module Documentation

### `app.py` - Main Pipeline Orchestrator
Coordinates all stages and manages the complete workflow.

**Key Functions:**
- `DocumentProcessingPipeline.run()` - Execute full pipeline
- `_stage_preprocessing()` - Stage 1: Fix orientation
- `_stage_detection()` - Stage 2: Detect document type
- `_stage_extraction()` - Stage 3: Extract text/tables
- `_stage_structured_extraction()` - Stage 4: Schema-based extraction

### `pdf_rotation.py` - Simple Rotation Fix
Fast orientation correction for digital PDFs using text block analysis.

**Usage:**
```python
from pdf_rotation import auto_rotate_pdf_content
rotated = auto_rotate_pdf_content("input.pdf", "output.pdf")
```

### `auto_rotation_ocr.py` - OCR-Based Rotation
Comprehensive rotation and deskew for scanned documents.

**Features:**
- Tesseract OSD for coarse rotation (90° increments)
- OpenCV for fine skew correction
- Multi-attempt validation
- Parallel page processing

**Usage:**
```python
from auto_rotation_ocr import run_pipeline_preserve_layout
pdf, reports = run_pipeline_preserve_layout("input.pdf", output_pdf="corrected.pdf")
```

### `pdf_detector.py` - Document Type Detection
Determines if a PDF contains extractable text or requires OCR.

**Usage:**
```python
from pdf_detector import PDFDetector
detector = PDFDetector("document.pdf")
is_scanned = detector.is_scanned()
print("OCR required" if is_scanned else "Digital extraction OK")
```

### `pdf_plumber.py` - Digital Extraction
Advanced text and table extraction with layout preservation.

**Features:**
- Table detection and formatting
- Watermark removal
- Reversed text correction
- Hybrid extraction with PyMuPDF fallback
- Parallel page processing

**Usage:**
```python
from pdf_plumber import extract_pdf_hybrid
text, pages, info = extract_pdf_hybrid("document.pdf", output_txt="output.txt")
```

### `schema_ocr.py` - Layout-Preserving OCR
Uses rostaing-ocr for structure-aware text extraction.

**Features:**
- Preserves tables and column layouts
- Schema mapping with LLM or regex
- GPU optimization

**Usage:**
```python
from schema_ocr import SchemaOCRExtractor
extractor = SchemaOCRExtractor("document.pdf")
text = extractor.extract_layout_text()
```

### `main.py` - Structured Extraction Engine
Schema-driven field extraction using LLM.

**Features:**
- Fully dynamic JSON schema configuration
- Field validation and auto-repair
- Source tracking and conflict detection
- Security (prompt injection resistance)

**Usage:**
```bash
python main.py --pdf-text extracted.txt --email-text email.txt --schema schema.json --output result.json
```

### `gpu_config.py` - Hardware Optimization
Manages GPU detection, worker pools, and CPU fallback.

**Features:**
- Automatic GPU detection
- Optimal worker count calculation
- VRAM management
- Platform-aware configuration

## 🛠️ Command-Line Options

```
python app.py [OPTIONS]

Required:
  --pdf PATH              Input PDF file

Optional:
  --email PATH            Email text file (for structured extraction)
  --schema PATH           JSON schema for field extraction
  --output PATH           Output JSON file path
  
Pipeline Control:
  --no-rotation           Skip rotation fix stage
  --rotation-method       Rotation method: auto|simple|ocr|skip
  --extraction-method     Extraction method: auto|pdfplumber|schema_ocr
  --no-hybrid             Disable hybrid extraction fallback
  --work-dir PATH         Working directory (default: pipeline_workspace)
  --clean                 Remove intermediate files after completion
  
LLM Settings:
  --model MODEL           LLM model name (default: from .env)
  --api-key KEY           API key (default: from .env)
```

## 📋 Schema Configuration

Create a JSON schema file to define extraction fields:

```json
{
  "schemaVersion": "1.0",
  "fields": {
    "claim_number": {
      "type": "string",
      "required": true,
      "sources": ["PDF"],
      "aliases": ["Claim #", "Claim Number", "Claim ID"],
      "description": "Unique claim identifier"
    },
    "total_amount": {
      "type": "number",
      "required": true,
      "sources": ["PDF"],
      "format": "currency",
      "aliases": ["Total", "Amount", "Total Amount"]
    },
    "claim_date": {
      "type": "string",
      "required": false,
      "format": "date",
      "outputFormat": "YYYY-MM-DD",
      "aliases": ["Date", "Claim Date", "Loss Date"]
    }
  },
  "documentTypes": {
    "PDF": "Primary document",
    "EMAIL": "Email content"
  },
  "globalRules": [
    "Extract only data explicitly present in documents",
    "Use null for missing optional fields",
    "Preserve exact formatting for identifiers"
  ],
  "outputSettings": {
    "includeFieldSources": true,
    "includeConflicts": true,
    "includeMissingRequiredFields": true,
    "includeWarnings": true
  }
}
```

## 🎛️ Performance Tuning

### Worker Thread Configuration

The pipeline automatically detects optimal worker counts, but you can customize:

```python
from gpu_config import update_config

# Set custom worker count for PDF rendering
update_config("pdf_rendering", max_workers=16)

# Set custom worker count for OCR
update_config("ocr", max_workers=4)
```

### GPU Optimization

Enable GPU acceleration for rostaing-ocr:

```bash
# In .env file
CUDA_VISIBLE_DEVICES=0
GPU_MEMORY_FRACTION=0.8
```

Disable GPU if needed:
```bash
DISABLE_GPU=true
```

## 📊 Output Format

### Pipeline Report
```json
{
  "success": true,
  "duration_seconds": 45.2,
  "pipeline_state": {
    "stage": "structured_extraction",
    "pdf_path": "document.pdf",
    "is_scanned": false,
    "rotation_applied": true,
    "extraction_method": "pdfplumber",
    "extracted_text_path": "pipeline_workspace/document_extracted.txt"
  },
  "outputs": {
    "corrected_pdf": "pipeline_workspace/document_corrected.pdf",
    "extracted_text": "pipeline_workspace/document_extracted.txt",
    "structured_data": "pipeline_workspace/structured_output.json"
  },
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

### Structured Extraction Output
```json
{
  "data": {
    "claim_number": "CLM-2024-001",
    "total_amount": 15000.00,
    "claim_date": "2024-01-10"
  },
  "fieldSources": {
    "claim_number": "PDF",
    "total_amount": "PDF",
    "claim_date": "PDF"
  },
  "conflicts": [],
  "missingRequiredFields": [],
  "warnings": []
}
```

## 🔍 Troubleshooting

### Tesseract Not Found
```
Error: pytesseract.pytesseract.TesseractNotFoundError
```
**Solution:** Install Tesseract OCR and set `TESSERACT_PATH` in `.env`

### Poppler Not Found
```
Error: Unable to get page count. Is poppler installed?
```
**Solution:** Install Poppler and add to PATH or set `POPPLER_PATH` in `.env`

### GPU Out of Memory
```
Error: CUDA out of memory
```
**Solution:** Pipeline auto-falls back to CPU. To force CPU: `DISABLE_GPU=true`

### LLM API Errors
```
Error: Invalid API key
```
**Solution:** Check `OPENAI_API_KEY` in `.env` file

## 🧪 Testing

Run individual modules:

```bash
# Test rotation detection
python pdf_rotation.py input.pdf -o output.pdf

# Test document detection
python pdf_detector.py

# Test extraction
python pdf_plumber.py document.pdf output.txt --hybrid

# Test OCR pipeline
python auto_rotation_ocr.py
```

## 📁 Project Structure

```
Pricing Point Entry/
├── app.py                    # Main pipeline orchestrator
├── pdf_rotation.py          # Simple rotation fix
├── auto_rotation_ocr.py     # OCR-based rotation
├── pdf_detector.py          # Document type detection
├── pdf_plumber.py           # Digital extraction
├── schema_ocr.py            # Layout-preserving OCR
├── main.py                  # Structured extraction
├── gpu_config.py            # Hardware optimization
├── requirements.txt         # Python dependencies
├── .env.example             # Configuration template
├── README.md                # This file
└── pipeline_workspace/      # Working directory (auto-created)
```

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

- Built using PyMuPDF, pdfplumber, Tesseract, OpenCV
- LLM integration via OpenAI API
- GPU optimization support

---

**Need help?** Open an issue or check the troubleshooting section above.
