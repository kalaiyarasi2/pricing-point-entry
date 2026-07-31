# 🪟 Windows Installation Guide

Step-by-step installation guide for Windows users.

## 📋 Prerequisites

- Windows 10 or later
- Administrator access (for some installations)
- Internet connection

---

## Step 1: Install Python 3.8+

### Option A: Download from Python.org (Recommended)

1. Go to https://www.python.org/downloads/
2. Download Python 3.11 or later (3.9, 3.10 also work)
3. Run the installer
4. ⚠️ **IMPORTANT:** Check "Add Python to PATH" during installation
5. Click "Install Now"

### Verify Installation

```cmd
python --version
```

Should show: `Python 3.11.x` (or your version)

---

## Step 2: Install Tesseract OCR

### Download & Install

1. Go to: https://github.com/UB-Mannheim/tesseract/wiki
2. Download the latest installer (e.g., `tesseract-ocr-w64-setup-5.3.3.exe`)
3. Run the installer
4. **Note the installation path** (default: `C:\Program Files\Tesseract-OCR`)
5. Optional: During installation, select additional language packs if needed

### Add to PATH (if not automatic)

1. Open "Environment Variables":
   - Press `Win + R`
   - Type `sysdm.cpl` and press Enter
   - Go to "Advanced" tab → "Environment Variables"
2. Under "System variables", find "Path"
3. Click "Edit" → "New"
4. Add: `C:\Program Files\Tesseract-OCR`
5. Click "OK" on all dialogs

### Verify Installation

```cmd
tesseract --version
```

Should show version information.

---

## Step 3: Install Poppler

### Download Poppler

1. Go to: https://github.com/oschwartz10612/poppler-windows/releases
2. Download the latest release (e.g., `Release-24.02.0-0.zip`)
3. Extract to a permanent location (e.g., `C:\poppler`)

### Add to PATH

1. Open "Environment Variables" (same as Step 2)
2. Under "System variables", find "Path"
3. Click "Edit" → "New"
4. Add: `C:\poppler\Library\bin` (adjust path if different)
5. Click "OK" on all dialogs

### Verify Installation

```cmd
pdfinfo -v
```

Should show version information.

---

## Step 4: Install Project Dependencies

### Clone or Download Project

```cmd
cd C:\Users\YourName\Documents
git clone [repository-url]
cd "Pricing Point Entry"
```

Or download and extract ZIP file.

### Create Virtual Environment (Recommended)

```cmd
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your command prompt.

### Install Python Packages

```cmd
pip install -r requirements.txt
```

This will install:
- PyMuPDF, pypdf, pdfplumber
- Pillow, opencv-python, pytesseract
- pdf2image, openai
- jsonschema, python-dotenv

---

## Step 5: Configure Environment

### Create .env File

```cmd
copy .env.example .env
```

### Edit .env File

Open `.env` in Notepad or your preferred text editor:

```bash
# Required: Add your OpenAI API key
OPENAI_API_KEY=sk-your-actual-key-here
OPENAI_MODEL=gpt-4o

# Optional: Only if Tesseract/Poppler not in PATH
# TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
# POPPLER_PATH=C:\poppler\Library\bin
```

### Get OpenAI API Key

1. Go to: https://platform.openai.com/api-keys
2. Sign in or create account
3. Click "Create new secret key"
4. Copy the key and paste into `.env` file

---

## Step 6: Verify Installation

### Run Check Script

```cmd
python test_installation.py
```

or

```cmd
check_setup.bat
```

### Expected Output

```
================================================================================
  INSTALLATION VERIFICATION
================================================================================

📋 Testing Core Dependencies:
  ✓ Python Version                            [PASS]
    → Python 3.11.5 (OK)
  ✓ PyMuPDF                                   [PASS]
  ✓ pypdf                                     [PASS]
  ✓ pdfplumber                                [PASS]
  ...

🔧 Testing External Tools:
  ✓ Tesseract OCR                             [PASS]
  ✓ Poppler                                   [PASS]

⚙️  Testing Configuration:
  ✓ Environment File                          [PASS]
    → .env file configured with API key

✓ ALL TESTS PASSED - Installation is ready!
```

---

## Step 7: Test the Pipeline

### Create Test Files

Create a test email file:

```cmd
echo Subject: Test Claim > test_email.txt
echo. >> test_email.txt
echo Claim Number: TEST-001 >> test_email.txt
echo Insured: ABC Company >> test_email.txt
```

### Run Basic Test

```cmd
python app.py --pdf "your_document.pdf"
```

### Run Full Pipeline Test

```cmd
python app.py --pdf "your_document.pdf" --email test_email.txt --schema example_schema.json --output result.json
```

---

## 🔧 Troubleshooting

### Issue: Python not recognized

**Solution:**
1. Reinstall Python and check "Add to PATH"
2. Or manually add Python to PATH:
   - Default location: `C:\Users\YourName\AppData\Local\Programs\Python\Python311`

### Issue: Tesseract not found

**Solution:**
```cmd
# Add to .env file:
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### Issue: Poppler not found

**Solution:**
```cmd
# Add to .env file:
POPPLER_PATH=C:\poppler\Library\bin
```

### Issue: pip install fails

**Solution:**
```cmd
# Upgrade pip first
python -m pip install --upgrade pip

# Then retry
pip install -r requirements.txt
```

### Issue: Permission denied errors

**Solution:**
- Run Command Prompt as Administrator
- Or install packages with `--user` flag:
  ```cmd
  pip install --user -r requirements.txt
  ```

### Issue: SSL Certificate errors

**Solution:**
```cmd
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

---

## 🎯 Quick Command Reference

### Activate Virtual Environment
```cmd
venv\Scripts\activate
```

### Deactivate Virtual Environment
```cmd
deactivate
```

### Update Dependencies
```cmd
pip install --upgrade -r requirements.txt
```

### Check Python Path
```cmd
where python
```

### Check Tesseract Path
```cmd
where tesseract
```

### Check Poppler Path
```cmd
where pdfinfo
```

---

## 📁 Recommended Directory Structure

```
C:\Users\YourName\Documents\
└── Pricing Point Entry\
    ├── venv\                    # Virtual environment
    ├── app.py                   # Main script
    ├── .env                     # Your configuration (not in git)
    ├── requirements.txt         # Dependencies
    ├── documents\               # Input PDFs
    ├── outputs\                 # Results
    └── pipeline_workspace\      # Temporary files
```

---

## 🚀 Next Steps

1. ✅ Installation complete
2. 📖 Read QUICKSTART.md for usage examples
3. 📄 Try processing your first document
4. 🔧 Customize example_schema.json for your needs
5. 📊 Review outputs in pipeline_workspace/

---

## 🆘 Getting Help

### Check Logs
```cmd
# Run with debug output
python app.py --pdf document.pdf --debug
```

### Test Individual Components
```cmd
# Test rotation
python pdf_rotation.py test.pdf -o rotated.pdf

# Test extraction
python pdf_plumber.py test.pdf output.txt

# Test detection
python pdf_detector.py
```

### Common Paths to Check

- Python: `C:\Users\YourName\AppData\Local\Programs\Python\Python311`
- Tesseract: `C:\Program Files\Tesseract-OCR`
- Poppler: `C:\poppler\Library\bin`
- Virtual Environment: `.\venv\Scripts`

---

## ✅ Installation Checklist

- [ ] Python 3.8+ installed and in PATH
- [ ] Tesseract OCR installed
- [ ] Poppler installed
- [ ] Virtual environment created
- [ ] Requirements installed (`pip install -r requirements.txt`)
- [ ] .env file created and configured
- [ ] OpenAI API key added to .env
- [ ] test_installation.py passes all tests
- [ ] Successfully processed test document

---

**Installation complete! Ready to process documents! 🎉**
