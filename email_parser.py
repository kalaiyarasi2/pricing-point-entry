#!/usr/bin/env python3
"""
email_parser.py
===============

Email Parser for .eml files
Extracts email content (subject, body, metadata) and handles attachments.
Supports both plain text and HTML emails.
"""

import email
import os
import re
from pathlib import Path
from email import policy
from email.parser import BytesParser
from typing import Dict, List, Optional, Tuple
from html import unescape
from bs4 import BeautifulSoup


class EmailParser:
    """
    Parses .eml files and extracts structured content.
    """
    
    def __init__(self, eml_path: str):
        """
        Initialize the parser with an .eml file path.
        
        Args:
            eml_path: Path to the .eml file
        """
        self.eml_path = Path(eml_path)
        if not self.eml_path.exists():
            raise FileNotFoundError(f"Email file not found: {eml_path}")
        
        self.message = None
        self.parsed_data = {
            "subject": "",
            "from": "",
            "to": "",
            "cc": "",
            "date": "",
            "body_text": "",
            "body_html": "",
            "attachments": [],
            "raw_headers": {}
        }
    
    def parse(self, save_attachments: bool = True, attachment_dir: str = None) -> Dict:
        """
        Parse the .eml file and extract all content.
        
        Args:
            save_attachments: Whether to save attachments to disk
            attachment_dir: Directory to save attachments (default: same as eml file)
            
        Returns:
            Dictionary with parsed email data
        """
        # Read the .eml file
        with open(self.eml_path, 'rb') as f:
            self.message = BytesParser(policy=policy.default).parse(f)
        
        # Extract headers
        self._extract_headers()
        
        # Extract body
        self._extract_body()
        
        # Extract attachments
        if save_attachments:
            attachment_dir = attachment_dir or self.eml_path.parent
            self._extract_attachments(attachment_dir)
        
        return self.parsed_data
    
    def _extract_headers(self):
        """Extract email headers."""
        self.parsed_data["subject"] = self._decode_header(self.message.get("Subject", ""))
        self.parsed_data["from"] = self._decode_header(self.message.get("From", ""))
        self.parsed_data["to"] = self._decode_header(self.message.get("To", ""))
        self.parsed_data["cc"] = self._decode_header(self.message.get("Cc", ""))
        self.parsed_data["date"] = self._decode_header(self.message.get("Date", ""))
        
        # Store all headers
        for key in self.message.keys():
            self.parsed_data["raw_headers"][key] = self._decode_header(self.message.get(key, ""))
    
    def _decode_header(self, header_value: str) -> str:
        """Decode email header that might be encoded."""
        if not header_value:
            return ""
        
        try:
            # Handle encoded headers
            from email.header import decode_header
            decoded_parts = decode_header(header_value)
            result = []
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        result.append(part.decode(encoding))
                    else:
                        result.append(part.decode('utf-8', errors='ignore'))
                else:
                    result.append(part)
            return ' '.join(result)
        except:
            return str(header_value)
    
    def _extract_body(self):
        """Extract email body (both plain text and HTML)."""
        if self.message.is_multipart():
            for part in self.message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                
                # Skip attachments
                if "attachment" in content_disposition:
                    continue
                
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True)
                        if body:
                            charset = part.get_content_charset() or 'utf-8'
                            self.parsed_data["body_text"] = body.decode(charset, errors='ignore')
                    except:
                        pass
                
                elif content_type == "text/html":
                    try:
                        body = part.get_payload(decode=True)
                        if body:
                            charset = part.get_content_charset() or 'utf-8'
                            self.parsed_data["body_html"] = body.decode(charset, errors='ignore')
                    except:
                        pass
        else:
            # Non-multipart email
            try:
                body = self.message.get_payload(decode=True)
                if body:
                    charset = self.message.get_content_charset() or 'utf-8'
                    content_type = self.message.get_content_type()
                    
                    decoded_body = body.decode(charset, errors='ignore')
                    
                    if content_type == "text/html":
                        self.parsed_data["body_html"] = decoded_body
                    else:
                        self.parsed_data["body_text"] = decoded_body
            except:
                pass
    
    def _extract_attachments(self, attachment_dir: str):
        """Extract and save attachments."""
        attachment_dir = Path(attachment_dir)
        attachment_dir.mkdir(parents=True, exist_ok=True)
        
        for part in self.message.walk():
            content_disposition = str(part.get("Content-Disposition", ""))
            
            if "attachment" in content_disposition:
                filename = part.get_filename()
                
                if filename:
                    filename = self._sanitize_filename(filename)
                    filepath = attachment_dir / filename
                    
                    # Save attachment
                    try:
                        with open(filepath, 'wb') as f:
                            f.write(part.get_payload(decode=True))
                        
                        self.parsed_data["attachments"].append({
                            "filename": filename,
                            "filepath": str(filepath),
                            "content_type": part.get_content_type(),
                            "size": os.path.getsize(filepath)
                        })
                        
                        print(f"   ✓ Saved attachment: {filename}")
                    except Exception as e:
                        print(f"   ✗ Failed to save attachment {filename}: {e}")
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe saving."""
        # Decode if needed
        filename = self._decode_header(filename)
        
        # Remove unsafe characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Limit length
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:200-len(ext)] + ext
        
        return filename
    
    def get_text_content(self, prefer_html: bool = False) -> str:
        """
        Get the email body as plain text.
        
        Args:
            prefer_html: If True and HTML is available, extract text from HTML
            
        Returns:
            Email body as plain text
        """
        if not self.parsed_data["body_text"] and not self.parsed_data["body_html"]:
            return ""
        
        # If we have plain text and don't prefer HTML, return it
        if self.parsed_data["body_text"] and not prefer_html:
            return self.parsed_data["body_text"]
        
        # If we prefer HTML or only have HTML, convert HTML to text
        if self.parsed_data["body_html"]:
            return self._html_to_text(self.parsed_data["body_html"])
        
        # Fallback to plain text
        return self.parsed_data["body_text"]
    
    def _html_to_text(self, html: str) -> str:
        """
        Convert HTML email body to plain text.
        
        Args:
            html: HTML content
            
        Returns:
            Plain text version
        """
        try:
            # Use BeautifulSoup for better HTML parsing
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Break into lines and remove leading/trailing space
            lines = (line.strip() for line in text.splitlines())
            
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return unescape(text)
        except:
            # Fallback: simple tag removal
            text = re.sub(r'<[^>]+>', '', html)
            return unescape(text)
    
    def to_text_file(self, output_path: str, include_headers: bool = True):
        """
        Save email content to a text file.
        
        Args:
            output_path: Path for output text file
            include_headers: Whether to include email headers
        """
        output = []
        
        if include_headers:
            output.append("="*80)
            output.append("EMAIL MESSAGE")
            output.append("="*80)
            output.append(f"Subject: {self.parsed_data['subject']}")
            output.append(f"From: {self.parsed_data['from']}")
            output.append(f"To: {self.parsed_data['to']}")
            if self.parsed_data['cc']:
                output.append(f"CC: {self.parsed_data['cc']}")
            output.append(f"Date: {self.parsed_data['date']}")
            output.append("="*80)
            output.append("")
        
        # Add body
        body_text = self.get_text_content(prefer_html=True)
        output.append(body_text)
        
        # Add attachment info
        if self.parsed_data["attachments"]:
            output.append("")
            output.append("="*80)
            output.append("ATTACHMENTS")
            output.append("="*80)
            for att in self.parsed_data["attachments"]:
                output.append(f"- {att['filename']} ({att['content_type']}, {att['size']} bytes)")
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output))
        
        print(f"   ✓ Email content saved to: {output_path}")
    
    def get_pdf_attachments(self) -> List[str]:
        """
        Get list of PDF attachment file paths.
        
        Returns:
            List of paths to PDF attachments
        """
        return [
            att['filepath'] 
            for att in self.parsed_data["attachments"] 
            if att['filename'].lower().endswith('.pdf')
        ]


def parse_email_file(eml_path: str, output_txt: str = None, 
                     save_attachments: bool = True) -> Tuple[str, Dict, List[str]]:
    """
    Convenience function to parse an email file.
    
    Args:
        eml_path: Path to .eml file
        output_txt: Optional path to save text output
        save_attachments: Whether to save attachments
        
    Returns:
        Tuple of (email_text, parsed_data, pdf_attachments)
    """
    print(f"\n📧 Parsing email file: {eml_path}")
    
    parser = EmailParser(eml_path)
    parsed_data = parser.parse(save_attachments=save_attachments)
    
    print(f"   Subject: {parsed_data['subject']}")
    print(f"   From: {parsed_data['from']}")
    print(f"   Attachments: {len(parsed_data['attachments'])}")
    
    # Get text content
    email_text = parser.get_text_content(prefer_html=True)
    
    # Save to text file if requested
    if output_txt:
        parser.to_text_file(output_txt, include_headers=True)
    
    # Get PDF attachments
    pdf_attachments = parser.get_pdf_attachments()
    if pdf_attachments:
        print(f"   ✓ Found {len(pdf_attachments)} PDF attachment(s)")
    
    return email_text, parsed_data, pdf_attachments


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python email_parser.py <path_to_eml_file> [output_txt]")
        sys.exit(1)
    
    eml_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Parse email
    email_text, parsed_data, pdf_attachments = parse_email_file(
        eml_file, 
        output_txt=output_file,
        save_attachments=True
    )
    
    print(f"\n✓ Email parsed successfully")
    print(f"   Text length: {len(email_text)} characters")
    
    if pdf_attachments:
        print(f"\n📎 PDF Attachments:")
        for pdf in pdf_attachments:
            print(f"   - {pdf}")
