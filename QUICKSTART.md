# 🚀 Quick Start Guide

Get up and running with the Document Processing Pipeline in 5 minutes!

## ⚡ Fast Setup

### 1. Install Prerequisites

**Windows:**
```powershell
# Install Tesseract OCR
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Run installer and add to PATH

# Install Poppler
# Download from: https://github.com/oschwartz10612/poppler-windows/releases
# Extract and add bin\ folder to PATH
```

**macOS:**
```bash
brew install tesseract poppler
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr poppler-utils
```

### 2. Install Python Packages

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy template
copy .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

## 🎯 Basic Usage Examples

### Example 1: Extract Text from PDF

```bash
python app.py --pdf document.pdf
```

**Output:**
- `pipeline_workspace/document_corrected.pdf` - Rotated PDF
- `pipeline_workspace/document_extracted.txt` - Extracted text
- `pipeline_workspace/pipeline_report.json` - Process report

### Example 2: Full Pipeline with Schema

```bash
python app.py --pdf document.pdf --schema example_schema.json --output result.json
```

**Output:**
- All above files plus:
- `result.json` - Structured data matching schema

### Example 3: Process Scanned Document

```bash
python app.py --pdf scanned.pdf --rotation-method ocr --extraction-method schema_ocr
```

Forces OCR-based processing for scanned documents.

### Example 4: Quick Processing (Skip Rotation)

```bash
python app.py --pdf document.pdf --no-rotation --schema example_schema.json
```

Skips rotation stage for already-aligned documents.

## 📝 Test the Pipeline

### Create a test email file:

```bash
echo "Subject: Claim Information > email.txt
echo. >> email.txt
echo Claim Number: CLM-2024-001 >> email.txt
echo Insured: ABC Company >> email.txt
echo Please review the attached loss run. >> email.txt
```

### Run the pipeline:

```bash
python app.py --pdf your_document.pdf --email email.txt --schema example_schema.json --output test_result.json
```

### Check the results:

```bash
type test_result.json
```

## 🔧 Common Commands

### Check Configuration

```bash
python gpu_config.py
```

Shows GPU availability and worker configuration.

### Test Individual Modules

```bash
# Test rotation detection
python pdf_rotation.py document.pdf -o rotated.pdf

# Test document type detection
python -c "from pdf_detector import PDFDetector; d=PDFDetector('document.pdf'); print('Scanned' if d.is_scanned() else 'Digital')"

# Test extraction
python pdf_plumber.py document.pdf output.txt
```

## 📊 Understanding Output

### Pipeline Report (`pipeline_report.json`)

```json
{
  "success": true,
  "duration_seconds": 12.5,
  "pipeline_state": {
    "is_scanned": false,
    "rotation_applied": true,
    "extraction_method": "pdfplumber"
  },
  "outputs": {
    "corrected_pdf": "pipeline_workspace/document_corrected.pdf",
    "extracted_text": "pipeline_workspace/document_extracted.txt",
    "structured_data": "result.json"
  }
}
```

### Structured Output (`result.json`)

```json
{
  "data": {
    "claim_number": "CLM-2024-001",
    "insured_name": "ABC Company",
    "total_incurred": 25000.00,
    "claim_date": "2024-01-15"
  },
  "fieldSources": {
    "claim_number": "EMAIL",
    "insured_name": "PDF",
    "total_incurred": "PDF",
    "claim_date": "PDF"
  },
  "conflicts": [],
  "missingRequiredFields": [],
  "warnings": []
}
```

## 🐛 Troubleshooting

### Issue: "Tesseract not found"

**Solution:**
```bash
# Add to .env file:
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### Issue: "Poppler not found"

**Solution:**
```bash
# Add poppler bin\ to Windows PATH, or set in .env:
POPPLER_PATH=C:\poppler\Library\bin
```

### Issue: "Invalid API key"

**Solution:**
```bash
# Check .env file has correct key:
OPENAI_API_KEY=sk-your-actual-key-here
```

### Issue: "CUDA out of memory"

**Solution:**
Pipeline automatically falls back to CPU. To force CPU mode:
```bash
# Add to .env:
DISABLE_GPU=true
```

## 📚 Next Steps

1. **Customize the Schema**
   - Edit `example_schema.json` to match your document fields
   - Add field aliases for better extraction
   - Define validation rules and allowed values

2. **Optimize Performance**
   - Adjust worker counts in `gpu_config.py`
   - Enable GPU acceleration if available
   - Use `--no-hybrid` for faster (less robust) extraction

3. **Batch Processing**
   - Create a script to process multiple files
   - Use `--work-dir` to organize outputs by document

4. **Integration**
   - Import modules into your own scripts
   - Build custom workflows
   - Add post-processing steps

## 💡 Pro Tips

- **Use `--no-rotation`** if your PDFs are already correctly oriented (saves time)
- **Use `--extraction-method pdfplumber`** for digital PDFs with tables
- **Use `--extraction-method schema_ocr`** for scanned documents
- **Keep intermediate files** (`--work-dir`) for debugging
- **Check `pipeline_report.json`** to understand what happened at each stage

## 🆘 Need Help?

- Check `README.md` for detailed documentation
- Review error messages in console output
- Inspect intermediate files in `pipeline_workspace/`
- Check `pipeline_report.json` for stage-by-stage details

---

**Happy Processing! 🎉**
