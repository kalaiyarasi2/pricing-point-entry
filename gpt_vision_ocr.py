#!/usr/bin/env python3
"""
GPT Vision OCR Fallback
Uses PyMuPDF to render PDF pages as images, base64 encodes them, and sends them
to GPT-4o (Vision) to extract structured text when other methods fail.
"""

import os
import fitz
import base64
from openai import OpenAI
import logging

LOGGER = logging.getLogger("gpt_vision_ocr")

class GPTVisionExtractor:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY must be provided or set in environment.")
        self.client = OpenAI(api_key=self.api_key)

    def extract_text_from_pdf(self, pdf_path: str, max_pages: int = 25) -> str:
        LOGGER.info(f"[GPT Vision] Starting fallback OCR extraction for: {pdf_path}")
        
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            LOGGER.error(f"[GPT Vision] Failed to open PDF: {e}")
            raise

        total_pages = len(doc)
        pages_to_process = min(total_pages, max_pages)
        LOGGER.info(f"[GPT Vision] Document has {total_pages} pages. Processing first {pages_to_process} pages.")

        base64_images = []
        for page_num in range(pages_to_process):
            page = doc.load_page(page_num)
            # Use reasonable DPI to balance quality and token size
            pix = page.get_pixmap(dpi=150)
            img_bytes = pix.tobytes("png")
            b64_img = base64.b64encode(img_bytes).decode("utf-8")
            base64_images.append(b64_img)
            
        doc.close()

        if not base64_images:
            return ""

        # Prepare messages for GPT-4o
        content = [
            {
                "type": "text",
                "text": (
                    "Please extract all the text from the following document pages. "
                    "Preserve the document layout as much as possible, including tables, columns, and spacing. "
                    "Return ONLY the extracted text, with no markdown code blocks or conversational filler."
                )
            }
        ]
        
        for b64 in base64_images:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{b64}",
                    "detail": "high"
                }
            })

        LOGGER.info("[GPT Vision] Sending images to GPT-4o for extraction...")
        try:
            response = self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o"),
                messages=[{"role": "user", "content": content}],
                max_tokens=4096,
                temperature=0.0,
            )
            extracted_text = response.choices[0].message.content
            if extracted_text:
                # Remove typical markdown wrapping if present
                if extracted_text.startswith("```"):
                    extracted_text = "\n".join(extracted_text.split("\n")[1:-1])
            LOGGER.info(f"[GPT Vision] Successfully extracted {len(extracted_text)} characters.")
            return extracted_text
        except Exception as e:
            LOGGER.error(f"[GPT Vision] API call failed: {e}")
            raise
