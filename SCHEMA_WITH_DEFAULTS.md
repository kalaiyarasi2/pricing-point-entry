# ✅ Updated Schema with Default Values

## 🎯 Default Values Added (Yellow Highlighted Fields)

Based on your requirements, the following fields now have **default values** that will always be populated:

| Field Name | Default Value | When Used |
|------------|---------------|-----------|
| **% of Ownership** | `"1%"` | Always (unless found in document) |
| **INC / Exc** | `"No"` | Always (unless found in document) |
| **Ownership Option** | `"Publically Traded"` | Always (unless found in document) |
| **Prospect Type** | `"New Prospect"` | Always (unless found in document) |
| **Share File Client Folder Link** | `"Need to Capture in SF"` | Always (unless found in document) |

---

## 📋 Complete Field List with Expected Output

When you process a document, here's what you'll get:

### ✅ **Always Populated (with defaults if not found):**

1. **percentage_of_ownership**: "1%" (default) or extracted value
2. **inc_exc**: "No" (default) or extracted value
3. **ownership_option**: "Publically Traded" (default) or extracted value
4. **prospect_type**: "New Prospect" (default) or extracted value
5. **share_file_client_folder_link**: "Need to Capture in SF" (default) or extracted value

### 📄 **From Documents (when available):**

6. **location_name**: From GHQ or Email
7. **address**: From GHQ
8. **city**: From GHQ
9. **state**: From GHQ
10. **zipcode**: From GHQ
11. **county**: From GHQ (if available)
12. **states_where_operating**: From GHQ
13. **fed_tax_id**: From GHQ or Email
14. **naics_number**: From Email
15. **sic_number**: From Email
16. **description_of_operations**: From GHQ or Email
17. **corporation_type**: From GHQ
18. **lead_source**: From Email
19. **current_carrier_tpa**: From GHQ or Email
20. **additional_carrier**: From GHQ or Email
21. **carrier**: From GHQ or Email
22. **current_pr_peo_provider**: From GHQ
23. **renewal_date_of_current_coverage**: From GHQ or Email
24. **requested_effective_date**: From GHQ or Email
25. **payroll_frequency**: From GHQ
26. **dba**: From GHQ
27. **first_name**: From GHQ
28. **last_name**: From GHQ
29. **title**: From GHQ
30. **contact_type**: From GHQ
31. **email**: From GHQ
32. **phone**: From GHQ
33. **cellphone**: From GHQ
34. **website**: From GHQ

---

## 🎯 Expected Output Example

With the updated schema, your output will look like this:

```json
{
  "success": true,
  "data": {
    "location_name": "TLW Construction",
    "dba": "",
    "first_name": "",
    "last_name": "",
    "title": "",
    "contact_type": "",
    "email": "",
    "phone": "",
    "cellphone": "",
    "address": "2085 E Technology Circle, #100",
    "city": "Tempe",
    "state": "AZ",
    "zipcode": "85284",
    "county": "Maricopa",
    "states_where_operating": "AZ",
    "website": "",
    "fed_tax_id": "86-0455130",
    "corporation_type": "Other",
    "description_of_operations": "Commercial & Residential Construction",
    "naics_number": "236220",
    "sic_number": "2390",
    "prospect_type": "PEO",
    "lead_source": "Employee Referral",
    "current_carrier_tpa": "BCBS",
    "additional_carrier": "Nationwide",
    "carrier": "",
    "current_pr_peo_provider": "Resourcing Edge",
    "renewal_date_of_current_coverage": "2026-10-01",
    "requested_effective_date": "2026-10-01",
    "payroll_frequency": "Other",
    "percentage_of_ownership": "1%",                          ⬅️ DEFAULT
    "ownership_option": "Publically Traded",                 ⬅️ DEFAULT
    "inc_exc": "No",                                         ⬅️ DEFAULT
    "share_file_client_folder_link": "Need to Capture in SF" ⬅️ DEFAULT
  }
}
```

**Note:** If "prospect_type" is found in the document (like "PEO"), it will use that value instead of the default "New Prospect".

---

## 🚀 How to Use

```bash
# Full pipeline with .eml file
python app.py \
  --pdf "input\document.pdf" \
  --email "input\email.eml" \
  --schema prospect_schema.json \
  --output result.json

# Direct extraction from already extracted text
python main.py \
  --pdf-text "extracted_pdf.txt" \
  --email-text "extracted_email.txt" \
  --schema prospect_schema.json \
  --output result.json \
  --model gpt-4o
```

---

## ✅ Updated Schema: `prospect_schema.json`

The schema has been updated with these changes:

### 1. **percentage_of_ownership**
```json
{
  "type": "string",
  "default": "1%",
  "sources": ["EMAIL", "PDF"]
}
```

### 2. **inc_exc**
```json
{
  "type": "string",
  "default": "No",
  "allowedValues": ["Included", "Excluded", "INC", "EXC", "Yes", "No"],
  "sources": ["EMAIL", "PDF"]
}
```

### 3. **ownership_option**
```json
{
  "type": "string",
  "default": "Publically Traded",
  "sources": ["EMAIL", "PDF"]
}
```

### 4. **prospect_type**
```json
{
  "type": "string",
  "default": "New Prospect",
  "allowedValues": ["PEO", "ASO", "Hybrid", "Direct", "New Prospect", "Other"],
  "sources": ["EMAIL", "PDF"]
}
```

### 5. **share_file_client_folder_link**
```json
{
  "type": "string",
  "default": "Need to Capture in SF",
  "sources": ["EMAIL"]
}
```

---

## 📊 Summary

✅ **5 fields now have default values** (as per yellow highlights)  
✅ **Schema is updated** in `prospect_schema.json`  
✅ **Ready for production use**  

The system will:
1. Try to extract the value from documents first
2. If not found, use the default value
3. Always populate these 5 fields (never empty)

---

## 🎉 Schema is Production Ready!

Your `prospect_schema.json` now:
- ✅ Has all 34 required fields
- ✅ Has 5 default values for yellow-highlighted fields
- ✅ Maps to your exact field names
- ✅ Works with both GHQ PDFs and .eml emails

**Start processing your documents with consistent default values!** 🚀
