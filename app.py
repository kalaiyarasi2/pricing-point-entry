#!/usr/bin/env python3
"""
app.py
======

Unified Document Processing Pipeline
Orchestrates the complete flow from PDF input to structured JSON output.

Pipeline Stages:
1. Pre-processing → Fix orientation (pdf_rotation.py or auto_rotation_ocr.py)
2. Detection → Determine if digital or scanned (pdf_detector.py)
3. Extraction → Extract text/tables (pdf_plumber.py or schema_ocr.py)
4. Structured Extraction → Extract fields using LLM + schema (main.py)

Usage:
    python app.py --pdf input.pdf --email email.txt --schema schema.json --output result.json
"""

import argparse
import json
import os
import re
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

# Import pipeline modules
from pdf_detector import PDFDetector
from pdf_rotation import auto_rotate_pdf_content
from auto_rotation_ocr import run_pipeline_preserve_layout, run_pipeline
from pdf_plumber import extract_pdf_hybrid, extract_pdf_with_pdfplumber
from schema_ocr import SchemaOCRExtractor
from email_parser import parse_email_file
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
LOGGER = logging.getLogger("app")

# ---------------------------------------------------------------------------
# PDF filename client-name detection
# ---------------------------------------------------------------------------

# Words that appear in GHQ filenames but are NOT client names.
# Anything in the stem that isn't one of these is treated as a client-name token.
_FILENAME_STOP_WORDS: set = {
    "ghq", "resourcing", "edge", "group", "health", "questionnaire",
    "prospect", "data", "for", "pricingpoint", "aura", "od", "at",
    "uw", "stage", "acct", "name", "tlw", "industrial",
    "and", "the", "of", "pdf", "form", "doc",
    "document", "new", "coverage", "medical", "insurance", "benefit",
    "benefits", "plan", "quote", "rfp", "proposal", "census",
}


def _filename_has_client_name(pdf_path: Path) -> bool:
    """
    Return True when the PDF filename appears to encode a client/company name.

    Strategy: tokenise the stem on underscores, spaces, hyphens, and percent-
    encoded spaces (%20), lower-case each token, and check whether at least one
    token is NOT in the stop-word list and is longer than 2 characters.  That
    surviving token is assumed to be a client-name fragment.

    Examples that return True
    -------------------------
    GHQ_Resourcing_Edge_DirectorCorps.pdf        → "DirectorCorps"
    Summit Health Questionnaire.pdf              → "Summit" (non-stop)
    GHQ_Resourcing_Edge_5498LLC Perspective Planning Partners.pdf → "Perspective", "Planning", "Partners"

    Examples that return False
    --------------------------
    GHQ_form.pdf                                 → all tokens are stop words
    """
    stem = pdf_path.stem
    # Decode percent-encoding and normalise separators
    stem = stem.replace("%20", " ").replace("_", " ").replace("-", " ")
    tokens = re.split(r"\s+", stem)
    for token in tokens:
        clean = re.sub(r"[^a-zA-Z0-9]", "", token).lower()
        if len(clean) > 2 and clean not in _FILENAME_STOP_WORDS:
            return True
    return False


# ---------------------------------------------------------------------------
# Print Name extraction from PDF text
# ---------------------------------------------------------------------------

# In GHQ / Resourcing Edge documents, pdfplumber reads the signature block
# top-to-bottom, producing this layout:
#
#   Melissa Burleson           OneDigital
#   Print Name                 Print Name of Company
#
# i.e. the PERSON'S name appears on the line ABOVE the "Print Name" label.
# The same-line "Print Name of Company" column must be ignored.
#
# Pattern A (primary): capture the left column of the line immediately
# preceding a line that contains "Print Name" but NOT "Print Name of Company".
# Left column ends at the first run of 2+ spaces (pdfplumber column separator).
_PRINT_NAME_ABOVE_PATTERN = re.compile(
    r"""
    ^[ \t]*                          # start of line (optional indent)
    ([A-Z][A-Za-z'\-]+               # first word, capital-initial
     (?:[ \t][A-Za-z'\-]+)*)         # zero or more single-space-separated words
    (?:[ \t]{2,}[^\n]*)?             # optionally followed by 2+ spaces + company column
    \n                               # end of the name line
    [ \t]*Print\s+Name               # next line starts with "Print Name"
    (?![ \t]+of[ \t]+Company)        # …but NOT "Print Name of Company"
    """,
    re.VERBOSE | re.MULTILINE,
)

# Pattern B (fallback): handles the rarer case where the name appears AFTER
# the "Print Name" label on the same or next line (some form designs).
# Uses a minimum of 2 spaces as separator guard so "Print Name" following
# label whitespace cannot be captured as the person name.
_PRINT_NAME_AFTER_PATTERN = re.compile(
    r"""
    \bPrint\s+Name\b                 # the label
    (?!\s+of\s+Company)              # skip "Print Name of Company"
    [ \t]{2,}                        # at least 2 spaces (not the label on the next col)
    ([A-Z][A-Za-z'\-]+(?:[ \t]+[A-Z][A-Za-z'\-]+)+)   # same-line name
    |
    \bPrint\s+Name\b
    (?!\s+of\s+Company)
    [ \t]*\n[ \t]*
    ([A-Z][A-Za-z'\-]+(?:[ \t]+[A-Z][A-Za-z'\-]+)+)  # next-line name
    """,
    re.VERBOSE | re.MULTILINE,
)

# Pattern C (last resort): scan for a capitalised 2+-word name immediately
# after the Authorized Signature / certification block heading.
_CERT_BLOCK_PATTERN = re.compile(
    r"""
    (?:CERTIFICATION\s+&\s+SIGNATURE|Authorized\s+Signature)
    [\s\S]{0,600}?                   # up to 600 chars of intervening text
    \n[ \t]*([A-Z][A-Za-z'\-]+       # capitalised first word on its own line
             (?:[ \t]+[A-Za-z'\-]+)+)  # at least one more word
    [ \t]*\n                         # end of line
    [ \t]*Print\s+Name               # confirmed by "Print Name" on the line below
    """,
    re.VERBOSE | re.IGNORECASE,
)

# Words that must never be returned as a person name (form labels mistaken for names)
_LABEL_BLACKLIST: set = {"print name", "authorized signature", "print name of company"}


def _extract_print_name_from_pdf(extracted_text: str) -> Optional[str]:
    """
    Scan the extracted PDF text for the signer's printed name.

    GHQ / Resourcing Edge documents place the name on the line ABOVE the
    'Print Name' label (the name is the filled-in form value; the label is
    printed beneath it).  Three patterns are tried in order:

    A) Line immediately above 'Print Name' label (primary — covers all screenshots)
    B) Name on the same or next line after 'Print Name' label (alternate layouts)
    C) Name line confirmed by 'Print Name' label below, within the certification block

    When the preceding line contains two columns separated by wide whitespace
    (e.g. "Melissa Burleson           OneDigital"), only the left column is
    kept — that is the person name; the right column is the company name.

    The document tail (last 40 %) is searched first because the signature
    block always appears at the end.
    """
    tail_start = max(0, int(len(extracted_text) * 0.60))
    search_zones: List[str] = [extracted_text[tail_start:], extracted_text]

    for zone in search_zones:
        # Pattern A — name on line above "Print Name" label (most common layout)
        m = _PRINT_NAME_ABOVE_PATTERN.search(zone)
        if m:
            raw = m.group(1).strip()
            # If two columns were captured, keep only the left one
            # (columns are separated by 2+ spaces in pdfplumber layout output)
            left_col = re.split(r"[ \t]{2,}", raw)[0].strip()
            if left_col and len(left_col.split()) >= 2 and left_col.lower() not in _LABEL_BLACKLIST:
                LOGGER.info(f"   → Print Name found (above-label pattern): '{left_col}'")
                return left_col

        # Pattern B — name on same / next line after label
        m = _PRINT_NAME_AFTER_PATTERN.search(zone)
        if m:
            raw = (m.group(1) or m.group(2) or "").strip()
            left_col = re.split(r"[ \t]{2,}", raw)[0].strip()
            if left_col and len(left_col.split()) >= 2 and left_col.lower() not in _LABEL_BLACKLIST:
                LOGGER.info(f"   → Print Name found (after-label pattern): '{left_col}'")
                return left_col

        # Pattern C — certification block + confirmed by label below
        m = _CERT_BLOCK_PATTERN.search(zone)
        if m:
            raw = m.group(1).strip()
            left_col = re.split(r"[ \t]{2,}", raw)[0].strip()
            if left_col and len(left_col.split()) >= 2 and left_col.lower() not in _LABEL_BLACKLIST:
                LOGGER.info(f"   → Print Name found (cert-block pattern): '{left_col}'")
                return left_col

    return None


def _split_name(full_name: str) -> Tuple[str, str]:
    """
    Split a full name into (first_name, last_name).

    Handles:
      "Melissa Burleson"        → ("Melissa", "Burleson")
      "CJ Teply"                → ("CJ", "Teply")
      "Erin Johnson"            → ("Erin", "Johnson")
      "Mary Jo Smith"           → ("Mary Jo", "Smith")   # compound first name
      Single word               → (word, "")
    """
    parts = full_name.strip().split()
    if len(parts) == 0:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    # Last token is the last name; everything before is the first name
    last_name = parts[-1]
    first_name = " ".join(parts[:-1])
    return first_name, last_name


class PipelineConfig:
    """Configuration for the entire pipeline."""
    
    def __init__(self):
        # Pre-processing settings
        self.enable_rotation_fix = True
        self.rotation_method = "auto"  # "auto", "simple", "ocr", "skip"
        self.rotation_dpi = 200
        self.rotation_osd_min_conf = 8.0
        
        # Detection settings
        self.text_threshold = 50
        self.pages_to_check = 3
        
        # Extraction settings
        self.extraction_method = "auto"  # "auto", "pdfplumber", "schema_ocr"
        self.extraction_dpi = 300
        self.use_hybrid_extraction = True
        self.save_debug_output = True
        
        # Structured extraction settings
        self.enable_structured_extraction = True
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.temperature = 0.0
        self.max_retries = 3
        
        # Output settings
        self.work_dir = "pipeline_workspace"
        self.keep_intermediate_files = True


class DocumentProcessingPipeline:
    """Main pipeline orchestrator."""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.work_dir = Path(config.work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        # Pipeline state tracking
        self.state = {
            "stage": None,
            "pdf_path": None,
            "is_scanned": None,
            "rotation_applied": False,
            "extraction_method": None,
            "extracted_text_path": None,
            "structured_data": None,
            "errors": [],
            "warnings": []
        }
    
    def run(self, pdf_path: str, email_path: Optional[str] = None, 
            schema_path: Optional[str] = None, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute the complete pipeline.
        
        Args:
            pdf_path: Path to input PDF file (or can be auto-detected from .eml attachments)
            email_path: Optional path to email text file or .eml file
            schema_path: Optional path to JSON schema for structured extraction
            output_path: Optional path for final JSON output
            
        Returns:
            Dictionary with pipeline results and metadata
        """
        start_time = datetime.now()
        LOGGER.info("="*80)
        LOGGER.info("DOCUMENT PROCESSING PIPELINE STARTED")
        LOGGER.info("="*80)
        
        try:
            # Handle .eml files and extract attachments
            pdf_attachments = []
            email_text_path = None
            
            if email_path and email_path.lower().endswith('.eml'):
                LOGGER.info(f"\n📧 Processing .eml file: {email_path}")
                email_text_path, pdf_attachments = self._process_eml_file(email_path)
                
                # If no PDF was provided, use the first PDF attachment
                if not pdf_path or pdf_path == "auto":
                    if pdf_attachments:
                        pdf_path = pdf_attachments[0]
                        LOGGER.info(f"Using PDF from email attachment: {pdf_path}")
                    else:
                        raise FileNotFoundError("No PDF provided and no PDF attachments found in .eml file")
            
            # Validate inputs
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            self.state["pdf_path"] = str(pdf_path)
            self.state["email_source"] = str(email_path) if email_path else None
            self.state["pdf_attachments"] = [str(p) for p in pdf_attachments]
            
            # Stage 1: Pre-processing (Rotation Fix)
            corrected_pdf = self._stage_preprocessing(pdf_path)
            
            # Stage 2: Detection (Digital vs Scanned)
            is_scanned = self._stage_detection(corrected_pdf)
            
            # Stage 3: Extraction (Text/Tables)
            extracted_text_path = self._stage_extraction(corrected_pdf, is_scanned)
            
            # Stage 4: Structured Extraction (LLM + Schema)
            if self.config.enable_structured_extraction and schema_path:
                # Use email text from .eml if available, otherwise use provided email path
                final_email_path = email_text_path if email_text_path else email_path
                structured_data = self._stage_structured_extraction(
                    extracted_text_path, final_email_path, schema_path, output_path
                )
            else:
                structured_data = None
                LOGGER.info("Structured extraction skipped (no schema provided or disabled)")
            
            # Finalize results
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = {
                "success": True,
                "duration_seconds": round(duration, 2),
                "pipeline_state": self.state,
                "outputs": {
                    "corrected_pdf": str(corrected_pdf),
                    "extracted_text": str(extracted_text_path),
                    "structured_data": structured_data if structured_data else None,
                    "final_output": output_path if output_path else None
                },
                "timestamp": datetime.now().isoformat()
            }
            
            LOGGER.info("="*80)
            LOGGER.info(f"PIPELINE COMPLETED SUCCESSFULLY in {duration:.2f}s")
            LOGGER.info("="*80)
            
            return result
            
        except Exception as e:
            LOGGER.error(f"Pipeline failed: {e}", exc_info=True)
            self.state["errors"].append(str(e))
            return {
                "success": False,
                "error": str(e),
                "pipeline_state": self.state,
                "timestamp": datetime.now().isoformat()
            }
    
    def _process_eml_file(self, eml_path: str) -> Tuple[Optional[Path], list]:
        """
        Process .eml file and extract email content and PDF attachments.
        
        Args:
            eml_path: Path to .eml file
            
        Returns:
            Tuple of (email_text_path, list_of_pdf_attachments)
        """
        LOGGER.info("\n" + "="*80)
        LOGGER.info("PROCESSING .EML FILE")
        LOGGER.info("="*80)
        
        try:
            # Create attachment directory in workspace
            attachment_dir = self.work_dir / "email_attachments"
            attachment_dir.mkdir(parents=True, exist_ok=True)
            
            # Parse email
            email_text, parsed_data, pdf_attachments = parse_email_file(
                eml_path,
                output_txt=None,  # We'll save it ourselves
                save_attachments=True
            )
            
            # Save email text
            email_text_path = self.work_dir / "email_content.txt"
            
            with open(email_text_path, 'w', encoding='utf-8') as f:
                # Write headers
                f.write("="*80 + "\n")
                f.write("EMAIL MESSAGE\n")
                f.write("="*80 + "\n")
                f.write(f"Subject: {parsed_data['subject']}\n")
                f.write(f"From: {parsed_data['from']}\n")
                f.write(f"To: {parsed_data['to']}\n")
                if parsed_data['cc']:
                    f.write(f"CC: {parsed_data['cc']}\n")
                f.write(f"Date: {parsed_data['date']}\n")
                f.write("="*80 + "\n\n")
                
                # Write body
                f.write(email_text)
                
                # Write attachment info
                if parsed_data['attachments']:
                    f.write("\n\n" + "="*80 + "\n")
                    f.write("ATTACHMENTS\n")
                    f.write("="*80 + "\n")
                    for att in parsed_data['attachments']:
                        f.write(f"- {att['filename']} ({att['content_type']}, {att['size']} bytes)\n")
            
            LOGGER.info(f"✓ Email content saved: {email_text_path}")
            LOGGER.info(f"✓ Found {len(pdf_attachments)} PDF attachment(s)")
            
            # Convert attachment paths to Path objects
            pdf_paths = [Path(p) for p in pdf_attachments]
            
            return email_text_path, pdf_paths
            
        except Exception as e:
            LOGGER.error(f"Failed to process .eml file: {e}")
            self.state["warnings"].append(f"Email processing failed: {e}")
            return None, []
    
    def _stage_preprocessing(self, pdf_path: Path) -> Path:
        """
        Stage 1: Pre-processing - Fix PDF orientation.
        
        Returns:
            Path to corrected PDF
        """
        self.state["stage"] = "preprocessing"
        LOGGER.info("\n" + "="*80)
        LOGGER.info("STAGE 1: PRE-PROCESSING (Rotation Fix)")
        LOGGER.info("="*80)
        
        if not self.config.enable_rotation_fix or self.config.rotation_method == "skip":
            LOGGER.info("Rotation fix disabled, using original PDF")
            return pdf_path
        
        corrected_pdf = self.work_dir / f"{pdf_path.stem}_corrected.pdf"
        
        try:
            if self.config.rotation_method == "auto":
                # Auto-detect best method
                LOGGER.info("Auto-detecting rotation method...")
                detector = PDFDetector(str(pdf_path))
                is_scanned = detector.is_scanned(pages_to_check=1)
                
                if is_scanned:
                    LOGGER.info("Using OCR-based rotation (document appears scanned)")
                    method = "ocr"
                else:
                    LOGGER.info("Using simple rotation (document is digital)")
                    method = "simple"
            else:
                method = self.config.rotation_method
            
            if method == "simple":
                # Use pdf_rotation.py (fast, for digital PDFs)
                LOGGER.info("Running simple rotation fix...")
                rotated = auto_rotate_pdf_content(str(pdf_path), str(corrected_pdf))
                self.state["rotation_applied"] = rotated
                
            elif method == "ocr":
                # Use auto_rotation_ocr.py (comprehensive, for scanned PDFs)
                LOGGER.info("Running OCR-based rotation fix...")
                result_pdf, reports = run_pipeline_preserve_layout(
                    pdf_path=str(pdf_path),
                    work_dir=str(self.work_dir / "rotation_workspace"),
                    output_pdf=str(corrected_pdf),
                    dpi=self.config.rotation_dpi,
                    osd_min_conf=self.config.rotation_osd_min_conf
                )
                self.state["rotation_applied"] = any(r.get('applied_rotate', 0) != 0 for r in reports)
            
            if corrected_pdf.exists():
                LOGGER.info(f"✓ Corrected PDF saved: {corrected_pdf}")
                return corrected_pdf
            else:
                LOGGER.warning("Rotation fix failed, using original PDF")
                return pdf_path
                
        except Exception as e:
            LOGGER.error(f"Pre-processing failed: {e}")
            self.state["warnings"].append(f"Rotation fix failed: {e}")
            return pdf_path
    
    def _stage_detection(self, pdf_path: Path) -> bool:
        """
        Stage 2: Detection - Determine if PDF is digital or scanned.
        
        Returns:
            True if scanned, False if digital
        """
        self.state["stage"] = "detection"
        LOGGER.info("\n" + "="*80)
        LOGGER.info("STAGE 2: DETECTION (Digital vs Scanned)")
        LOGGER.info("="*80)
        
        try:
            detector = PDFDetector(str(pdf_path))
            is_scanned = detector.is_scanned(
                text_threshold=self.config.text_threshold,
                pages_to_check=self.config.pages_to_check
            )
            
            self.state["is_scanned"] = is_scanned
            
            pdf_type = "SCANNED (Image-based)" if is_scanned else "DIGITAL (Text-based)"
            recommended = "OCR Extraction" if is_scanned else "Digital Extraction"
            
            LOGGER.info(f"Document Type: {pdf_type}")
            LOGGER.info(f"Recommended Method: {recommended}")
            
            return is_scanned
            
        except Exception as e:
            LOGGER.error(f"Detection failed: {e}")
            self.state["warnings"].append(f"Detection failed: {e}, assuming scanned")
            return True  # Default to OCR if unsure
    
    def _stage_extraction(self, pdf_path: Path, is_scanned: bool) -> Path:
        """
        Stage 3: Extraction - Extract text and tables from PDF.
        
        Returns:
            Path to extracted text file
        """
        self.state["stage"] = "extraction"
        LOGGER.info("\n" + "="*80)
        LOGGER.info("STAGE 3: EXTRACTION (Text/Tables)")
        LOGGER.info("="*80)
        
        extracted_text_path = self.work_dir / f"{pdf_path.stem}_extracted.txt"
        
        try:
            # Determine extraction method
            if self.config.extraction_method == "auto":
                if is_scanned:
                    method = "schema_ocr"
                else:
                    method = "pdfplumber"
            else:
                method = self.config.extraction_method
            
            self.state["extraction_method"] = method
            LOGGER.info(f"Using extraction method: {method}")
            
            if method == "pdfplumber":
                # Use pdf_plumber.py (best for digital PDFs with tables)
                LOGGER.info("Running pdfplumber extraction...")
                
                if self.config.use_hybrid_extraction:
                    text, pages, info = extract_pdf_hybrid(
                        str(pdf_path),
                        output_txt=str(extracted_text_path)
                    )
                    LOGGER.info(f"Hybrid extraction info: {info}")
                else:
                    text, pages = extract_pdf_with_pdfplumber(
                        str(pdf_path),
                        output_txt=str(extracted_text_path)
                    )
                
                LOGGER.info(f"✓ Extracted {len(pages)} pages, {len(text)} characters")
                
            elif method == "schema_ocr":
                # Use schema_ocr.py (best for scanned PDFs)
                LOGGER.info("Running rostaing-ocr extraction...")
                
                extractor = SchemaOCRExtractor(str(pdf_path))
                text = extractor.extract_layout_text(
                    save_debug_output=self.config.save_debug_output
                )
                
                # Save extracted text
                with open(extracted_text_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                
                LOGGER.info(f"✓ Extracted {len(text)} characters")
            
            if extracted_text_path.exists():
                LOGGER.info(f"✓ Extracted text saved: {extracted_text_path}")
                self.state["extracted_text_path"] = str(extracted_text_path)
                return extracted_text_path
            else:
                raise Exception("Extraction produced no output file")
                
        except Exception as e:
            LOGGER.error(f"Extraction failed: {e}")
            self.state["errors"].append(f"Extraction failed: {e}")
            raise
    
    def _stage_structured_extraction(self, pdf_text_path: Path, 
                                    email_path: Optional[str],
                                    schema_path: str,
                                    output_path: Optional[str]) -> Dict[str, Any]:
        """
        Stage 4: Structured Extraction - Extract specific fields using LLM + schema.
        
        Returns:
            Dictionary with structured data
        """
        self.state["stage"] = "structured_extraction"
        LOGGER.info("\n" + "="*80)
        LOGGER.info("STAGE 4: STRUCTURED EXTRACTION (LLM + Schema)")
        LOGGER.info("="*80)
        
        try:
            # Import main.py functionality
            from main import AppConfig, DocumentLoader, SchemaLoader, LlmClient
            from main import DynamicSchemaBuilder, Draft7Validator
            
            # Prepare output path
            if not output_path:
                output_path = self.work_dir / "structured_output.json"
            else:
                output_path = Path(output_path)
            
            # Create email file if not provided
            if not email_path:
                email_path = self.work_dir / "empty_email.txt"
                email_path.write_text("No email content provided.", encoding='utf-8')
            
            LOGGER.info(f"PDF Text: {pdf_text_path}")
            LOGGER.info(f"Email: {email_path}")
            LOGGER.info(f"Schema: {schema_path}")
            LOGGER.info(f"Output: {output_path}")
            
            # Load documents
            loader = DocumentLoader()
            pdf_doc = loader.load(Path(pdf_text_path), "PDF")
            email_doc = loader.load(Path(email_path), "EMAIL")
            
            # Load schema
            schema_loader = SchemaLoader()
            schema_config = schema_loader.load(Path(schema_path))
            
            # Initialize LLM client
            llm_client = LlmClient(
                api_key=self.config.api_key,
                model=self.config.model,
                temperature=self.config.temperature
            )
            
            # Prepare documents for extraction
            documents = [
                {
                    "document_type": pdf_doc.document_type,
                    "file_name": pdf_doc.file_name,
                    "text": pdf_doc.text,
                    "char_count": pdf_doc.char_count,
                    "warnings": pdf_doc.warnings
                },
                {
                    "document_type": email_doc.document_type,
                    "file_name": email_doc.file_name,
                    "text": email_doc.text,
                    "char_count": email_doc.char_count,
                    "warnings": email_doc.warnings
                }
            ]
            
            LOGGER.info("Sending extraction request to LLM...")
            
            # Extract data
            response_text = llm_client.extract(documents, schema_config)
            
            # Parse response
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as e:
                LOGGER.error(f"Failed to parse LLM response: {e}")
                raise
            
            # Validate against schema
            schema_builder = DynamicSchemaBuilder()
            data_schema = schema_builder.build_data_schema(schema_config.get("fields", {}))
            
            validator = Draft7Validator(data_schema)
            validation_errors = list(validator.iter_errors(result.get("data", {})))
            
            if validation_errors:
                LOGGER.warning(f"Validation found {len(validation_errors)} issues")
                for err in validation_errors[:5]:  # Show first 5
                    LOGGER.warning(f"  - {err.message}")
                
                # Attempt repair
                if self.config.max_retries > 0:
                    LOGGER.info("Attempting to repair invalid response...")
                    error_messages = [err.message for err in validation_errors]
                    response_text = llm_client.repair(
                        schema_config, response_text, error_messages
                    )
                    result = json.loads(response_text)
            
            # ---------------------------------------------------------------
            # Client-name check: if the PDF filename encodes a client name,
            # extract the signer's Print Name from the document text and use
            # it to populate first_name / last_name when the LLM left them
            # blank (or didn't find them).
            # ---------------------------------------------------------------
            original_pdf_path = Path(self.state.get("pdf_path", ""))
            if _filename_has_client_name(original_pdf_path):
                LOGGER.info("\n" + "─" * 60)
                LOGGER.info("CLIENT NAME DETECTED IN PDF FILENAME")
                LOGGER.info("Attempting Print Name extraction from document…")
                LOGGER.info("─" * 60)

                try:
                    pdf_text_content = Path(pdf_text_path).read_text(encoding="utf-8", errors="ignore")
                    full_name = _extract_print_name_from_pdf(pdf_text_content)

                    if full_name:
                        first, last = _split_name(full_name)
                        data = result.setdefault("data", {})
                        field_sources = result.setdefault("fieldSources", {})

                        # Only override fields that the LLM left empty
                        changed: List[str] = []
                        if not data.get("first_name") and first:
                            data["first_name"] = first
                            field_sources["first_name"] = "PDF_PRINT_NAME"
                            changed.append(f"first_name='{first}'")
                        if not data.get("last_name") and last:
                            data["last_name"] = last
                            field_sources["last_name"] = "PDF_PRINT_NAME"
                            changed.append(f"last_name='{last}'")

                        if changed:
                            LOGGER.info(f"   ✓ Overrode: {', '.join(changed)}")
                            result.setdefault("warnings", []).append(
                                f"first_name/last_name populated from PDF Print Name field "
                                f"('{full_name}') because filename indicated a client document."
                            )
                        else:
                            LOGGER.info(
                                "   ℹ LLM already populated first_name/last_name — "
                                "Print Name extraction not applied."
                            )
                    else:
                        LOGGER.warning(
                            "   ⚠ Print Name not found in document text; "
                            "first_name/last_name left as extracted by LLM."
                        )
                except Exception as exc:
                    LOGGER.warning(f"   ⚠ Print Name extraction error: {exc}")
            else:
                LOGGER.info(
                    "PDF filename does not indicate a client-specific document; "
                    "skipping Print Name extraction."
                )

            # Save output
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            LOGGER.info(f"✓ Structured data saved: {output_path}")
            
            # Summary
            data = result.get("data", {})
            conflicts = result.get("conflicts", [])
            missing = result.get("missingRequiredFields", [])
            warnings = result.get("warnings", [])
            
            LOGGER.info(f"Extracted {len(data)} fields")
            if conflicts:
                LOGGER.warning(f"Found {len(conflicts)} conflicts")
            if missing:
                LOGGER.warning(f"Missing {len(missing)} required fields: {missing}")
            if warnings:
                LOGGER.warning(f"Warnings: {len(warnings)}")
            
            self.state["structured_data"] = str(output_path)
            return result
            
        except Exception as e:
            LOGGER.error(f"Structured extraction failed: {e}")
            self.state["errors"].append(f"Structured extraction failed: {e}")
            raise


def main():
    """Command-line interface for the pipeline."""
    parser = argparse.ArgumentParser(
        description="Unified Document Processing Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic extraction (no structured output)
  python app.py --pdf document.pdf
  
  # Process .eml file with PDF attachment (auto-detect PDF)
  python app.py --email message.eml --pdf auto --schema schema.json --output result.json
  
  # Process .eml file and specific PDF
  python app.py --pdf document.pdf --email message.eml --schema schema.json --output result.json
  
  # Full pipeline with text email
  python app.py --pdf document.pdf --email email.txt --schema schema.json --output result.json
  
  # Skip rotation fix
  python app.py --pdf document.pdf --no-rotation
  
  # Force specific extraction method
  python app.py --pdf document.pdf --extraction-method schema_ocr
        """
    )
    
    # Required arguments
    parser.add_argument("--pdf", help="Path to input PDF file (or 'auto' to use PDF from .eml attachment)")
    
    # Optional arguments
    parser.add_argument("--email", help="Path to email text file or .eml file (supports .eml format with attachments)")
    parser.add_argument("--schema", help="Path to JSON schema for structured extraction")
    parser.add_argument("--output", help="Path for final JSON output")
    
    # Pipeline configuration
    parser.add_argument("--no-rotation", action="store_true", 
                       help="Skip rotation fix stage")
    parser.add_argument("--rotation-method", 
                       choices=["auto", "simple", "ocr", "skip"],
                       default="auto",
                       help="Rotation fix method (default: auto)")
    parser.add_argument("--extraction-method",
                       choices=["auto", "pdfplumber", "schema_ocr"],
                       default="auto",
                       help="Extraction method (default: auto)")
    parser.add_argument("--no-hybrid", action="store_true",
                       help="Disable hybrid extraction (pdfplumber only)")
    parser.add_argument("--work-dir", default="pipeline_workspace",
                       help="Working directory for intermediate files")
    parser.add_argument("--clean", action="store_true",
                       help="Remove intermediate files after completion")
    
    # LLM settings
    parser.add_argument("--model", help="LLM model name (default: from env)")
    parser.add_argument("--api-key", help="API key (default: from env)")
    
    args = parser.parse_args()
    
    # Build configuration
    config = PipelineConfig()
    
    if args.no_rotation:
        config.enable_rotation_fix = False
    else:
        config.rotation_method = args.rotation_method
    
    config.extraction_method = args.extraction_method
    config.use_hybrid_extraction = not args.no_hybrid
    config.work_dir = args.work_dir
    config.keep_intermediate_files = not args.clean
    
    if args.model:
        config.model = args.model
    if args.api_key:
        config.api_key = args.api_key
    
    # Validate schema requirement
    if not args.schema:
        LOGGER.warning("No schema provided - will skip structured extraction stage")
        config.enable_structured_extraction = False
    
    # Validate PDF requirement (can be 'auto' if using .eml)
    if not args.pdf:
        if args.email and args.email.lower().endswith('.eml'):
            args.pdf = "auto"  # Will auto-detect from .eml attachments
        else:
            LOGGER.error("--pdf is required (or use --email with .eml file containing PDF attachment)")
            sys.exit(2)
    
    # Run pipeline
    pipeline = DocumentProcessingPipeline(config)
    result = pipeline.run(
        pdf_path=args.pdf,
        email_path=args.email,
        schema_path=args.schema,
        output_path=args.output
    )
    
    # Save pipeline report
    report_path = Path(config.work_dir) / "pipeline_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    LOGGER.info(f"\nPipeline report saved: {report_path}")
    
    # Exit with appropriate code
    if result["success"]:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
