# 🚀 START HERE - Document Processing Pipeline

Welcome! This guide will get you up and running in minutes.

---

## 📖 What is This?

An intelligent pipeline that:
1. **Fixes rotated/skewed PDFs** automatically
2. **Extracts text and tables** while preserving layout
3. **Maps data to JSON schemas** using AI
4. **Validates and repairs** extracted data

Perfect for processing insurance claims, invoices, forms, and any structured documents.

---

## 🎯 Quick Links

| What do you want to do? | Read this |
|-------------------------|-----------|
| 🪟 Install on Windows | [INSTALL_WINDOWS.md](INSTALL_WINDOWS.md) |
| ⚡ Get started quickly | [QUICKSTART.md](QUICKSTART.md) |
| 📚 Detailed documentation | [README.md](README.md) |
| 📊 System overview | [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) |

---

## ⚡ 3-Minute Setup

### 1. Install Prerequisites

**Windows:**
- Python 3.8+ ([download](https://www.python.org/downloads/))
- Tesseract OCR ([download](https://github.com/UB-Mannheim/tesseract/wiki))
- Poppler ([download](https://github.com/oschwartz10612/poppler-windows/releases))

**macOS:**
```bash
brew install python tesseract poppler
```

**Linux:**
```bash
sudo apt-get install python3 tesseract-ocr poppler-utils
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure

```bash
# Copy template
copy .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

### 4. Test Installation

```bash
python test_installation.py
```

### 5. Process Your First Document

```bash
python app.py --pdf your_document.pdf
```

---

## 📁 Project Files Overview

### 🎯 Entry Points
- **`app.py`** - Main pipeline (START HERE for processing)
- **`test_installation.py`** - Verify setup
- **`check_setup.bat`** - Windows setup checker

### 📚 Documentation
- **`START_HERE.md`** - You are here!
- **`QUICKSTART.md`** - 5-minute guide
- **`README.md`** - Full documentation
- **`INSTALL_WINDOWS.md`** - Windows setup guide
- **`PROJECT_SUMMARY.md`** - Architecture overview

### ⚙️ Core Modules
- **`pdf_rotation.py`** - Fix page orientation
- **`pdf_detector.py`** - Detect document type
- **`pdf_plumber.py`** - Extract text/tables
- **`schema_ocr.py`** - OCR with layout preservation
- **`main.py`** - Structured extraction
- **`gpu_config.py`** - Performance optimization

### 🔧 Configuration
- **`requirements.txt`** - Python dependencies
- **`.env.example`** - Configuration template
- **`example_schema.json`** - Sample extraction schema

---

## 🎮 Common Commands

### Basic Processing
```bash
# Extract text only
python app.py --pdf document.pdf

# Full pipeline with schema
python app.py --pdf document.pdf --schema example_schema.json --output result.json

# With email content
python app.py --pdf document.pdf --email email.txt --schema example_schema.json
```

### Advanced Options
```bash
# Skip rotation (if already aligned)
python app.py --pdf document.pdf --no-rotation

# Force OCR extraction
python app.py --pdf document.pdf --extraction-method schema_ocr

# Use custom working directory
python app.py --pdf document.pdf --work-dir my_workspace

# Clean up after processing
python app.py --pdf document.pdf --clean
```

---

## 🔍 Understanding Output

### Pipeline Creates These Files:

```
pipeline_workspace/
├── document_corrected.pdf      # Rotated/fixed PDF
├── document_extracted.txt      # Extracted text with layout
├── structured_output.json      # Mapped data (if schema provided)
└── pipeline_report.json        # Processing summary
```

### Example Output (`result.json`):
```json
{
  "data": {
    "claim_number": "CLM-2024-001",
    "insured_name": "ABC Company",
    "total_incurred": 25000.00,
    "claim_date": "2024-01-15"
  },
  "fieldSources": {
    "claim_number": "PDF",
    "insured_name": "PDF",
    "total_incurred": "PDF",
    "claim_date": "PDF"
  },
  "conflicts": [],
  "missingRequiredFields": [],
  "warnings": []
}
```

---

## 🎯 The 4 Pipeline Stages

### Stage 1: Pre-processing ⚙️
**Fixes:** Rotated, skewed, or misaligned pages  
**Methods:** Simple (fast) or OCR-based (comprehensive)

### Stage 2: Detection 🔍
**Determines:** Is this a digital PDF or scanned image?  
**Selects:** Best extraction method automatically

### Stage 3: Extraction 📄
**Extracts:** Text, tables, and layout  
**Preserves:** Document structure and formatting

### Stage 4: Structured Extraction 🤖
**Maps:** Extracted text to your JSON schema  
**Validates:** Data against rules and types  
**Reports:** Sources, conflicts, missing fields

---

## 🧪 Verify Everything Works

### Run All Tests
```bash
python test_installation.py
```

### Test Individual Stages
```bash
# Test rotation
python pdf_rotation.py test.pdf -o rotated.pdf

# Test detection
python -c "from pdf_detector import PDFDetector; print(PDFDetector('test.pdf').analyze())"

# Test extraction
python pdf_plumber.py test.pdf output.txt
```

---

## 🆘 Troubleshooting

### ❌ "Python not recognized"
→ Add Python to PATH during installation

### ❌ "Tesseract not found"
→ Install Tesseract and add to PATH, or set in `.env`:
```
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### ❌ "Poppler not found"
→ Install Poppler and add to PATH, or set in `.env`:
```
POPPLER_PATH=C:\poppler\Library\bin
```

### ❌ "Invalid API key"
→ Check `.env` has correct OpenAI key:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### ❌ "Module not found"
→ Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 📖 Learning Path

### For Beginners
1. ✅ Follow INSTALL_WINDOWS.md (Windows) or README.md (Mac/Linux)
2. ✅ Run `python test_installation.py`
3. ✅ Process a test document: `python app.py --pdf test.pdf`
4. ✅ Review output files in `pipeline_workspace/`

### For Advanced Users
1. 📊 Read PROJECT_SUMMARY.md for architecture
2. 🔧 Customize `example_schema.json` for your fields
3. ⚡ Optimize performance via `gpu_config.py`
4. 🔗 Import modules into your own scripts

### For Developers
1. 🏗️ Study module source code
2. 🧪 Write custom extraction schemas
3. 🔌 Integrate with your systems
4. 🚀 Extend with new features

---

## 💡 Pro Tips

1. **Start Simple** - Process one document without schema first
2. **Use Auto-Detection** - Let the pipeline choose methods
3. **Check Logs** - Console shows detailed progress
4. **Save Intermediate Files** - Keep `pipeline_workspace/` for debugging
5. **Test Your Schema** - Start with 1-2 fields, then expand

---

## 🎓 Example Workflows

### Workflow 1: Quick Text Extraction
```bash
# Just get text, no structured extraction
python app.py --pdf report.pdf
# Output: pipeline_workspace/report_extracted.txt
```

### Workflow 2: Insurance Claims
```bash
# Process loss run with claim schema
python app.py --pdf loss_run.pdf --schema claim_schema.json --output claims.json
```

### Workflow 3: Batch Processing
```bash
# Process multiple files (create a batch script)
for %f in (*.pdf) do python app.py --pdf "%f" --schema schema.json
```

### Workflow 4: High-Quality OCR
```bash
# Force comprehensive OCR for scanned docs
python app.py --pdf scanned.pdf --rotation-method ocr --extraction-method schema_ocr
```

---

## 🚀 Ready to Start?

1. ✅ Installation complete? Run `python test_installation.py`
2. 📄 Have a PDF? Try `python app.py --pdf your_file.pdf`
3. 🎯 Need structured data? Create/customize a schema
4. 📚 Questions? Check the documentation links above

---

## 📞 Need Help?

- 📖 Read [QUICKSTART.md](QUICKSTART.md) for examples
- 📚 Check [README.md](README.md) for detailed docs
- 🐛 Review error messages and logs
- 🔍 Inspect `pipeline_report.json` for details

---

## 🎉 You're All Set!

The pipeline is ready to process documents. Start with:

```bash
python app.py --pdf your_document.pdf
```

**Good luck! 🚀**
