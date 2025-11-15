import base64
import json
import re
from typing import Any, Dict, List
from openai import OpenAI
import requests
import fitz  # PyMuPDF
from io import BytesIO

NETMIND_API_KEY = "6ecc3bdc2980400a8786fd512ad487e7"

class NetMindLabExtractor:
    """
    Extract structured lab data from text or PDF using NetMind's LLM.
    """

    def __init__(
        self,
        model: str = "Qwen/Qwen3-VL-235B-A22B-Instruct",
    ):
        # Read key from arg or env
        self.model = model
        self.api_key = NETMIND_API_KEY
        
        self.client = OpenAI(
            base_url="https://api.netmind.ai/inference-api/openai/v1",
            api_key=self.api_key,
        )

        # System prompt that defines the JSON schema
        self.system_prompt = """
You are a medical laboratory report parser.

Given the plain text of a lab report, extract all information into a single JSON
object with this exact schema (keys and nesting must match):

{
  "patient": {
    "dob": string or null,
    "age": integer or null,
    "gender": string or null,
    "fasting": boolean or null
  },
  "specimen": {
    "date_collected": string or null,
    "date_received": string or null,
    "date_entered": string or null,
    "date_reported": string or null
  },
  "physician": {
    "ordering": string or null,
    "referring": string or null,
    "id": string or null,
    "npi": string or null
  },
  "tests": [
    {
      "panel": string or null,
      "name": string,
      "result": number or null,
      "unit": string or null,
      "reference_range": string or null,
      "flag": string or null
    }
  ],
  "raw_text": string
}

Rules:
- Always return VALID JSON ONLY (no markdown, no explanation).
- 'result' must be numeric where possible (e.g. 151, 4.3).
- If a field is missing, set it to null.
- Include every test you can find, including Lipoprotein(a).
- raw_text must contain the full original text you received.
"""

    # ------------ core LLM call ------------

    def extract_from_text(self, report_text: str) -> Dict[str, Any]:
        """
        Call NetMind chat completion to turn report_text into structured JSON.
        """
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": report_text},
            ],
            temperature=0,
            max_tokens=1200,
        )

        content = completion.choices[0].message.content
        extracted_data = self._safe_json_loads(content)
        
        # Print extracted data
        print("\n" + "="*80)
        print("EXTRACTED LAB DATA:")
        print("="*80)
        print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
        print("="*80 + "\n")
        
        return extracted_data

    # ------------ optional: PDF → text using NetMind parse-pdf ------------

    def extract_from_pdf_url(self, pdf_url: str) -> Dict[str, Any]:
        """
        1) Use NetMind's parse-pdf endpoint to OCR/parse a PDF from a URL
        2) Join all sentences to plain text
        3) Run the LLM extractor on that text
        """
        print(f"\n[PDF Parser] Parsing PDF from URL: {pdf_url}...")
        
        resp = requests.post(
            "https://api.netmind.ai/inference-api/agent/v1/parse-pdf",
            headers={
                "Authorization": NETMIND_API_KEY,
                "Content-Type": "application/json",
            },
            json={"url": pdf_url, "format": "json"},
            timeout=90,
        )
        resp.raise_for_status()
        chunks: List[dict] = resp.json()
        
        print(f"[PDF Parser] PDF parsed successfully. Extracted {len(chunks)} text chunks.")

        # Concatenate all sentences into a single text block
        text_lines = [
            c.get("sentence", "") for c in chunks if c.get("sentence")
        ]
        merged_text = "\n".join(text_lines)
        
        print(f"[PDF Parser] Merged text length: {len(merged_text)} characters")
        print(f"[PDF Parser] Calling LLM to extract structured data...")

        return self.extract_from_text(merged_text)

    # ------------ optional: base64 PDF → text using NetMind parse-pdf ------------

    def extract_from_base64(self, base64_string: str, filename: str = "document.pdf") -> Dict[str, Any]:
        """
        Use LLM directly to parse base64-encoded PDF/image and extract structured lab data.
        If the input is a PDF, converts all pages to PNG before passing to LLM.
        
        Args:
            base64_string: Base64-encoded PDF/image content
            filename: Optional filename for logging/debugging purposes
            
        Returns:
            Dictionary with structured lab data
        """
        print(f"\n[PDF Parser] Parsing document from base64 (filename: {filename})...")
        print(f"[PDF Parser] Base64 data length: {len(base64_string)} characters")
        
        # Decode base64 to bytes to check file type
        try:
            file_bytes = base64.b64decode(base64_string)
        except Exception as e:
            raise ValueError(f"Failed to decode base64 string: {str(e)}")
        
        # Check if it's a PDF by magic bytes
        is_pdf = file_bytes.startswith(b'%PDF')
        
        if is_pdf:
            print(f"[PDF Parser] Detected PDF format - converting all pages to PNG...")
            return self._extract_from_pdf_bytes(file_bytes)
        else:
            print(f"[PDF Parser] Detected image format - processing directly...")
            return self._extract_from_image_base64(base64_string)
    
    def _extract_from_pdf_bytes(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """
        Convert PDF pages to PNG and extract data from each page, then merge results.
        
        Args:
            pdf_bytes: Raw PDF bytes
            
        Returns:
            Dictionary with merged structured lab data from all pages
        """
        # Open PDF with PyMuPDF
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        num_pages = pdf_document.page_count
        print(f"[PDF Parser] PDF has {num_pages} page(s)")
        
        # Store results from each page
        all_page_results = []
        
        # Process each page
        for page_num in range(num_pages):
            print(f"[PDF Parser] Processing page {page_num + 1}/{num_pages}...")
            
            page = pdf_document[page_num]
            
            # Render page to PNG at 150 DPI
            # Default is 72 DPI, so zoom factor = 150/72 ≈ 2.08
            zoom = 150 / 72
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert pixmap to PNG bytes
            png_bytes = pix.tobytes("png")
            
            # Convert PNG to base64
            png_base64 = base64.b64encode(png_bytes).decode('utf-8')
            
            print(f"[PDF Parser] Page {page_num + 1} converted to PNG ({len(png_base64)} base64 chars)")
            
            # Extract data from this PNG page
            page_data = self._extract_from_image_base64(png_base64, page_num=page_num + 1)
            all_page_results.append(page_data)
        
        pdf_document.close()
        
        # Merge results from all pages
        print(f"[PDF Parser] Merging results from {num_pages} page(s)...")
        merged_data = self._merge_page_results(all_page_results)
        
        return merged_data
    
    def _extract_from_image_base64(self, base64_string: str, page_num: int = None) -> Dict[str, Any]:
        """
        Extract structured data from a base64-encoded image using LLM.
        
        Args:
            base64_string: Base64-encoded image (PNG, JPEG, etc.)
            page_num: Optional page number for logging
            
        Returns:
            Dictionary with structured lab data
        """
        page_info = f" (page {page_num})" if page_num else ""
        print(f"[PDF Parser] Calling LLM to extract structured data{page_info}...")
        
        # Pass the base64 image directly to the LLM using vision API format
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_string}"
                            }
                        },
                        {
                            "type": "text",
                            "text": "Please extract all lab data from this image according to the schema provided in the system prompt. Extract all test results, patient information, dates, and any other relevant data."
                        }
                    ]
                }
            ],
            temperature=0,
            max_tokens=2000,
        )
        
        content = completion.choices[0].message.content
        extracted_data = self._safe_json_loads(content)
        
        # Print extracted data
        print("\n" + "="*80)
        print(f"EXTRACTED LAB DATA{page_info}:")
        print("="*80)
        print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
        print("="*80 + "\n")
        
        return extracted_data
    
    def _merge_page_results(self, page_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge extracted data from multiple pages.
        - Use patient/specimen/physician info from first page
        - Concatenate all tests from all pages
        - Combine raw_text from all pages
        
        Args:
            page_results: List of extracted data dictionaries, one per page
            
        Returns:
            Merged dictionary with all data
        """
        if not page_results:
            return {}
        
        if len(page_results) == 1:
            return page_results[0]
        
        # Start with first page as base
        merged = page_results[0].copy()
        
        # Collect all tests from all pages
        all_tests = []
        all_raw_text = []
        
        for page_data in page_results:
            if "tests" in page_data and isinstance(page_data["tests"], list):
                all_tests.extend(page_data["tests"])
            if "raw_text" in page_data:
                all_raw_text.append(page_data["raw_text"])
        
        # Update merged data
        merged["tests"] = all_tests
        merged["raw_text"] = "\n\n--- PAGE BREAK ---\n\n".join(all_raw_text)
        
        print(f"[PDF Parser] Merged {len(all_tests)} total tests from {len(page_results)} pages")
        
        return merged

    # ------------ helper: robust JSON parsing ------------

    @staticmethod
    def _safe_json_loads(raw: str) -> Dict[str, Any]:
        """
        Try to parse JSON; if the model wrapped it with extra text,
        strip markdown code blocks and extract JSON.
        Similar to suggestion_node.py JSON extraction pattern.
        """
        # Strip whitespace first
        content = raw.strip()
        
        # Handle markdown code blocks (similar to suggestion_node.py)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        # Try direct JSON parse
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Fallback: extract JSON object using regex
            match = re.search(r"\{.*\}", content, flags=re.DOTALL)
            if not match:
                raise ValueError(f"Model did not return valid JSON: {content[:200]!r}...")
            return json.loads(match.group(0))
