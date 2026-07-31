# 📧 .EML File Support Guide

The pipeline now supports `.eml` email files as an alternative to plain text email files!

---

## 🎯 What's New?

- ✅ **Parse .eml files** directly (no need to copy/paste email content)
- ✅ **Extract email metadata** (subject, from, to, date)
- ✅ **Convert HTML emails to text** automatically
- ✅ **Extract PDF attachments** from emails
- ✅ **Auto-process PDF attachments** (no need to manually extract)

---

## 🚀 Quick Start

### Basic Usage: Process .eml with Separate PDF

```bash
python app.py --pdf document.pdf --email message.eml --schema schema.json --output result.json
```

### Auto-Detect PDF from Email Attachment

```bash
python app.py --email message.eml --pdf auto --schema schema.json --output result.json
```

If the .eml file contains PDF attachments, the first PDF will be automatically processed!

### Test Email Parser Standalone

```bash
python email_parser.py message.eml output.txt
```

---

## 📋 Supported Features

### Email Content Extraction

✅ **Plain Text Emails** - Directly extracted  
✅ **HTML Emails** - Automatically converted to clean text  
✅ **Multipart Emails** - Handles both plain and HTML parts  
✅ **Encoded Content** - Decodes various character encodings  

### Email Metadata

✅ **Subject** - Email subject line  
✅ **From** - Sender email address  
✅ **To** - Recipient email addresses  
✅ **CC** - CC'd email addresses  
✅ **Date** - Email timestamp  
✅ **All Headers** - Complete header information  

### Attachments

✅ **PDF Extraction** - Automatically extracts PDF files  
✅ **All File Types** - Saves all attachments to disk  
✅ **Safe Filenames** - Sanitizes attachment names  
✅ **Size Tracking** - Records file sizes  

---

## 💻 Usage Examples

### Example 1: Email with PDF Attachment (Auto-Detect)

Your email has a PDF attached? Use `--pdf auto`:

```bash
python app.py --email "Prospect Data.eml" --pdf auto --schema example_schema.json
```

**What happens:**
1. Parses the .eml file
2. Extracts all PDF attachments to `pipeline_workspace/email_attachments/`
3. Uses the first PDF attachment as input
4. Processes through normal pipeline stages

### Example 2: Email with Separate PDF

You have both an .eml file and a separate PDF:

```bash
python app.py --pdf loss_run.pdf --email correspondence.eml --schema schema.json
```

**What happens:**
1. Parses email content from .eml
2. Uses the specified PDF file
3. Combines both sources for structured extraction

### Example 3: Email Only (No Structured Extraction)

Just extract email content:

```bash
python email_parser.py message.eml extracted_content.txt
```

**What happens:**
1. Parses the .eml file
2. Saves formatted email content to text file
3. Extracts attachments to same directory

### Example 4: Batch Process Multiple .eml Files

Process multiple emails with PDFs:

```bash
for %f in (*.eml) do python app.py --email "%f" --pdf auto --schema schema.json
```

---

## 📂 File Structure After Processing

When you process an .eml file:

```
pipeline_workspace/
├── email_content.txt              # Extracted email text with headers
├── email_attachments/             # Extracted attachments
│   ├── document1.pdf              # PDF attachment 1
│   ├── document2.pdf              # PDF attachment 2
│   └── spreadsheet.xlsx           # Other attachments
├── document1_corrected.pdf        # Processed PDF (if rotation applied)
├── document1_extracted.txt        # Extracted text from PDF
├── structured_output.json         # Final structured data
└── pipeline_report.json           # Pipeline processing report
```

---

## 🔍 Email Content Format

The extracted email text file includes:

```
================================================================================
EMAIL MESSAGE
================================================================================
Subject: Prospect Data for PricingPoint
From: sender@example.com
To: recipient@example.com
CC: cc@example.com
Date: Thu, 30 Jul 2026 03:25:30 +0000
================================================================================

[Email body content - HTML converted to clean text]

================================================================================
ATTACHMENTS
================================================================================
- document.pdf (application/pdf, 245678 bytes)
- data.xlsx (application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, 12345 bytes)
```

---

## 🛠️ Advanced Usage

### Custom Attachment Directory

Modify `app.py` to change where attachments are saved:

```python
attachment_dir = self.work_dir / "my_custom_attachments"
```

### Process Specific PDF from Multiple Attachments

If an email has multiple PDFs and you want a specific one:

```bash
# First, extract to see what's available
python email_parser.py message.eml

# Then specify the exact PDF
python app.py --pdf "pipeline_workspace/email_attachments/specific_document.pdf" --email message.eml
```

### Prefer HTML Email Content

The parser automatically uses HTML if available and converts it to clean text. This preserves formatting better than plain text in most cases.

---

## 🧪 Testing Your .eml Files

### Test 1: Check if .eml is Valid

```bash
python email_parser.py your_file.eml
```

Should show:
- Subject
- From/To addresses
- Number of attachments
- PDF attachments found

### Test 2: Verify PDF Extraction

```bash
python email_parser.py your_file.eml output.txt
```

Check the `email_attachments/` directory for extracted PDFs.

### Test 3: Full Pipeline Test

```bash
python app.py --email your_file.eml --pdf auto --schema example_schema.json
```

---

## 📊 .eml vs .txt Email Comparison

| Feature | .txt Email | .eml Email |
|---------|-----------|------------|
| Manual copy/paste required | ✅ Yes | ❌ No |
| Preserves metadata | ❌ No | ✅ Yes |
| Extracts attachments | ❌ No | ✅ Yes |
| HTML email support | ❌ Limited | ✅ Full |
| Auto-detect PDFs | ❌ No | ✅ Yes |
| Encoding handling | ⚠️ Basic | ✅ Advanced |

---

## 🔧 Troubleshooting

### Issue: "No module named 'bs4'"

**Solution:**
```bash
pip install beautifulsoup4
```

Or reinstall requirements:
```bash
pip install -r requirements.txt
```

### Issue: "No PDF attachments found"

**Possible causes:**
1. .eml file has no attachments
2. Attachments are not PDFs
3. PDFs are embedded inline (not as attachments)

**Solution:**
Specify PDF manually:
```bash
python app.py --pdf document.pdf --email message.eml
```

### Issue: Garbled Email Text

**Possible causes:**
- Complex HTML formatting
- Special character encoding

**Solution:**
The parser handles most encodings automatically. Check the output file to verify.

### Issue: Attachment Names with Special Characters

The parser automatically sanitizes filenames, replacing unsafe characters with underscores.

---

## 🎓 Real-World Example

### Scenario: Insurance Claim Email with Loss Run

You receive an email with:
- Client details in email body
- Loss run PDF attached
- Need to extract claim data

**Steps:**

1. Save the email as `.eml` from Outlook/Gmail
2. Run the pipeline:
   ```bash
   python app.py --email claim_email.eml --pdf auto --schema claim_schema.json --output claim_data.json
   ```

3. **Pipeline automatically:**
   - Extracts client details from email body
   - Finds and processes the loss run PDF
   - Maps everything to your schema
   - Outputs structured JSON

**Result:**
```json
{
  "data": {
    "client_name": "TLW Construction",
    "account_manager": "Cathy Mindeman",
    "effective_date": "2026-10-01",
    "claim_count": 15,
    ...
  },
  "fieldSources": {
    "client_name": "EMAIL",
    "effective_date": "EMAIL",
    "claim_count": "PDF",
    ...
  }
}
```

---

## 🚀 Best Practices

1. **Use `--pdf auto`** when email has PDF attachment(s)
2. **Check email_content.txt** to see what was extracted
3. **Verify attachments** in `email_attachments/` directory
4. **Name your schema fields** to match both email and PDF content
5. **Set sourcePriority** in schema to prefer EMAIL or PDF for conflicting fields

---

## 📝 Schema Configuration for Email + PDF

Update your schema to specify which fields come from which source:

```json
{
  "fields": {
    "client_name": {
      "type": "string",
      "sources": ["EMAIL", "PDF"],
      "sourcePriority": ["EMAIL", "PDF"],
      "description": "Usually in email body"
    },
    "claim_amount": {
      "type": "number",
      "sources": ["PDF"],
      "description": "Only in PDF loss run"
    },
    "account_manager": {
      "type": "string",
      "sources": ["EMAIL"],
      "description": "From email metadata or body"
    }
  }
}
```

---

## 🎉 Summary

The pipeline now seamlessly handles .eml files:
- ✅ No manual email content copying
- ✅ Automatic PDF attachment extraction
- ✅ HTML email conversion
- ✅ Complete metadata preservation
- ✅ Backward compatible with .txt files

**Start using .eml files today for a better workflow! 📧**
