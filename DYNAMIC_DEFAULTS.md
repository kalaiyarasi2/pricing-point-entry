# ✅ Dynamic Defaults - Smart Field Population

## 🎯 **Problem Solved**

When GHQ PDFs are blank forms (not filled out), the system now provides **intelligent default values** that match expected business patterns.

---

## 📋 **All Fields with Default Values**

| Field | Default Value | Reason |
|-------|---------------|--------|
| **% of Ownership** | `"1%"` | Standard default ownership |
| **INC / Exc** | `"No"` | Default exclusion status |
| **Ownership Option** | `"Publically Traded"` | Common ownership type |
| **Prospect Type** | `"New Prospect"` | Default for new clients |
| **Share File Client Folder Link** | `"Need to Capture in SF"` | Reminder to capture |
| **DBA** | `"No DBA"` | No doing-business-as name |
| **Website** | `"No Website"` | No website exists |
| **Current PR/PEO Provider** | `"No Carrier"` | No current provider |
| **Payroll Frequency** | `"No Payroll Frequency In GHQ"` | Not specified in GHQ |
| **Corporation Type** | `"Others"` | Default entity type |

---

## 🔄 **Smart Extraction Rules Added**

### 1. **Description of Operations**
- **Smart extraction**: If not directly found, extract from SIC code description
- **Example**: `"2390 - Miscellaneous Fabricated Textile Products"` → `"Miscellaneous Fabricated Textile Products"`
- **Sources**: Email SIC field, PDF tables

### 2. **Blank Form Detection**
- System recognizes when GHQ fields are empty
- Automatically applies defaults instead of leaving blank
- Handles patterns like "No DBA", "No Website", "No Carrier"

### 3. **Priority Handling**
- Email data takes priority over blank GHQ forms
- If both sources have data, uses sourcePriority setting
- Tracks which source provided each field value

---

## 📊 **Expected Output with Defaults**

### Scenario: Email + Blank GHQ PDF

```json
{
  "location_name": "TLW Construction",              // From EMAIL
  "dba": "No DBA",                                  // ⬅️ DEFAULT (not in blank GHQ)
  "first_name": "",                                 // Not found anywhere
  "last_name": "",                                  // Not found anywhere
  "title": "",                                      // Not found anywhere
  "contact_type": "",                               // Not found anywhere
  "email": "",                                      // Not found anywhere
  "phone": "",                                      // Not found anywhere
  "cellphone": "",                                  // Not found anywhere
  "address": "2085 E Technology Circle, #100",      // From EMAIL
  "city": "Tempe",                                  // From EMAIL
  "state": "AZ",                                    // From EMAIL
  "zipcode": "85284",                               // From EMAIL
  "county": "",                                     // Not found
  "states_where_operating": "AZ",                   // From PDF/EMAIL
  "website": "No Website",                          // ⬅️ DEFAULT (not in blank GHQ)
  "fed_tax_id": "86-0455130",                       // From EMAIL
  "corporation_type": "Others",                     // ⬅️ DEFAULT
  "description_of_operations": "Miscellaneous Fabricated Textile Products",  // ⬅️ From SIC code
  "naics_number": "236220",                         // From EMAIL
  "sic_number": "2390",                             // From EMAIL
  "prospect_type": "PEO",                           // From EMAIL (overrides default)
  "lead_source": "Employee Referral",               // From EMAIL
  "current_carrier_tpa": "BCBS",                    // From EMAIL
  "additional_carrier": "Nationwide",               // From EMAIL
  "carrier": "",                                    // Not found
  "current_pr_peo_provider": "No Carrier",          // ⬅️ DEFAULT (not in blank GHQ)
  "renewal_date_of_current_coverage": "2026-10-01", // From EMAIL
  "requested_effective_date": "2026-10-01",         // From EMAIL
  "payroll_frequency": "No Payroll Frequency In GHQ", // ⬅️ DEFAULT
  "percentage_of_ownership": "1%",                  // ⬅️ DEFAULT
  "ownership_option": "Publically Traded",          // ⬅️ DEFAULT
  "inc_exc": "No",                                  // ⬅️ DEFAULT
  "share_file_client_folder_link": "Need to Capture in SF"  // ⬅️ DEFAULT
}
```

---

## 🎯 **Comparison: Before vs After**

| Field | Before (No Default) | After (With Default) |
|-------|-------------------|---------------------|
| dba | "" (empty) | "No DBA" ✅ |
| website | "" (empty) | "No Website" ✅ |
| current_pr_peo_provider | "" (empty) | "No Carrier" ✅ |
| payroll_frequency | "Other" | "No Payroll Frequency In GHQ" ✅ |
| corporation_type | "Other" | "Others" ✅ |
| description_of_operations | "" (empty) | "Miscellaneous Fabricated Textile Products" ✅ |
| percentage_of_ownership | "" (empty) | "1%" ✅ |
| ownership_option | "" (empty) | "Publically Traded" ✅ |
| inc_exc | "Included" | "No" ✅ |
| share_file_client_folder_link | "" (empty) | "Need to Capture in SF" ✅ |

---

## 🔍 **How It Works**

### 1. **Primary Extraction**
- System first tries to extract from EMAIL and PDF
- Uses smart pattern matching and aliases

### 2. **SIC Code Intelligence**
- If "description_of_operations" is empty
- Looks for SIC code with description (e.g., "2390 - Miscellaneous Fabricated Textile Products")
- Extracts the descriptive part as operations description

### 3. **Default Application**
- If field not found in any source
- Applies configured default value
- Marks source as "DEFAULT" in fieldSources

### 4. **Smart Pattern Recognition**
- Recognizes "No [Field]" patterns as valid data
- Distinguishes between "not found" and "explicitly none"
- Handles blank form fields appropriately

---

## ✅ **Benefits**

1. **No Empty Fields**: Critical fields always have meaningful values
2. **Business Logic**: Defaults match real-world business scenarios
3. **Traceability**: Source tracking shows which fields used defaults
4. **Consistency**: Same defaults across all extractions
5. **Flexibility**: Can override defaults when data is found

---

## 🚀 **Usage**

The defaults work automatically with your existing command:

```bash
# Process email + blank GHQ
python app.py \
  --pdf "input/blank_ghq.pdf" \
  --email "input/prospect_email.eml" \
  --schema prospect_schema.json \
  --output result.json
```

Or directly:

```bash
python main.py \
  --pdf-text "extracted_pdf.txt" \
  --email-text "extracted_email.txt" \
  --schema prospect_schema.json \
  --output result.json \
  --model gpt-4o
```

---

## 📝 **Schema Updates Made**

1. Added `"default"` values to 10 fields
2. Updated `globalRules` with smart extraction logic
3. Enhanced `description_of_operations` to extract from SIC code
4. Added `allowedValues` for new default values

---

## 🎉 **Result**

**Your schema now intelligently handles:**
- ✅ Blank GHQ forms
- ✅ Missing contact information
- ✅ Partial data extraction
- ✅ Business-appropriate defaults
- ✅ Smart field derivation (SIC → Description)

**No more empty critical fields!** 🚀
