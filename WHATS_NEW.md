# 🎉 What's New - .EML File Support

## New Feature: Direct .eml Email File Processing

The pipeline now supports `.eml` email files as an alternative to plain text email files!

---

## 🚀 Quick Examples

### Before (Old Way):
```bash
# Step 1: Open email, copy content, save to text file
# Step 2: Save PDF attachments manually
# Step 3: Run pipeline
python app.py --pdf attachment.pdf --email email.txt --schema schema.json
```

### Now (New Way):
```bash
# Just save email as .eml and run!
python app.py --email message.eml --pdf auto --schema schema.json
```

**That's it!** The pipeline automatically:
- ✅ Extracts email content (subject, body, metadata)
- ✅ Finds and extracts PDF attachments
- ✅ Processes everything together

---

## 📋 New Capabilities

### 1. Auto-Detect PDFs from Email
```bash
python app.py --email message.eml --pdf auto --schema schema.json
```

### 2. Parse Email Content with Headers
```bash
python email_parser.py message.eml output.txt
```

### 3. Extract All Attachments
Automatically saves to `pipeline_workspace/email_attachments/`

---

## 📦 New Files Added

1. **`email_parser.py`** - Complete .eml parsing module
   - Handles plain text and HTML emails
   - Extracts attachments
   - Converts HTML to clean text
   - Preserves all metadata

2. **`EML_SUPPORT.md`** - Comprehensive .eml usage guide

3. **Updated `app.py`** - Integrated .eml support
   - New `--pdf auto` option
   - Automatic attachment processing
   - Backward compatible with .txt files

---

## 🔄 Updated Pipeline Flow

```
📧 .eml Email File
    ↓
📎 Extract Attachments (PDFs, etc.)
    ↓
📄 Extract Email Content
    ├─ Subject, From, To, Date
    ├─ Body (HTML → Clean Text)
    └─ Metadata
    ↓
[Normal Pipeline Stages]
    ↓
📋 Structured JSON Output
```

---

## 💡 Why Use .eml Files?

| Benefit | Description |
|---------|-------------|
| **No Manual Work** | No need to copy/paste email content |
| **Preserve Metadata** | Subject, sender, date automatically extracted |
| **Attachment Handling** | PDFs automatically extracted and processed |
| **HTML Support** | Converts rich HTML emails to clean text |
| **Better Accuracy** | No copy/paste errors or formatting loss |

---

## 🛠️ Installation Update

New dependency required:

```bash
pip install beautifulsoup4
```

Or reinstall all requirements:

```bash
pip install -r requirements.txt
```

---

## 📚 Documentation

- **Full Guide:** [EML_SUPPORT.md](EML_SUPPORT.md)
- **Quick Start:** See updated [QUICKSTART.md](QUICKSTART.md)
- **Main Docs:** See updated [README.md](README.md)

---

## 🧪 Test It Now

### Get your .eml file:

**Outlook:**
1. Open email
2. File → Save As
3. Save as type: "Outlook Message Format (.msg)" or drag to folder to get .eml

**Gmail:**
1. Open email
2. Three dots menu → Download message
3. Saves as .eml file

**Thunderbird:**
1. Right-click email
2. Save As → .eml

### Run the pipeline:
```bash
python app.py --email your_email.eml --pdf auto --schema example_schema.json
```

---

## 🔄 Backward Compatibility

**Still works with .txt email files!**

```bash
# Old way still supported
python app.py --pdf document.pdf --email email.txt --schema schema.json
```

---

## 🎯 Real-World Use Case

### Scenario: Insurance Prospect Email

You receive an email:
- **Subject:** Prospect Data for PricingPoint
- **Body:** Client details, effective dates, coverage info
- **Attachment:** Loss run PDF

### Before:
1. ❌ Open email
2. ❌ Copy/paste content to text file
3. ❌ Download PDF attachment
4. ❌ Run pipeline with both files

### Now:
1. ✅ Save email as .eml (one click)
2. ✅ Run: `python app.py --email prospect.eml --pdf auto --schema schema.json`
3. ✅ Done!

---

## 📊 What Gets Extracted

### From Email:
- Client name
- Contact information
- Account manager
- Effective dates
- Notes and comments
- Any structured data in email body

### From PDF Attachment:
- Claim numbers
- Loss amounts
- Dates of loss
- Tables and structured data
- Financial information

### Combined Output:
```json
{
  "data": {
    "client_name": "TLW Construction",        // from EMAIL
    "account_manager": "Cathy Mindeman",      // from EMAIL
    "effective_date": "2026-10-01",           // from EMAIL
    "total_claims": 15,                       // from PDF
    "total_incurred": 125000.00               // from PDF
  },
  "fieldSources": {
    "client_name": "EMAIL",
    "total_claims": "PDF"
  }
}
```

---

## 🚀 Get Started

1. **Update dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Test with your .eml file:**
   ```bash
   python app.py --email your_email.eml --pdf auto --schema example_schema.json
   ```

3. **Read the guide:**
   Check [EML_SUPPORT.md](EML_SUPPORT.md) for details

---

## 🆕 New Command Options

### `--pdf auto`
Auto-detect and use PDF from email attachments

### `--email *.eml`
Accepts both .txt and .eml email files

---

## 🎉 Start Using .eml Files Today!

No more manual email content copying. Just save and process! 📧

**Questions?** Check [EML_SUPPORT.md](EML_SUPPORT.md) or [QUICKSTART.md](QUICKSTART.md)
