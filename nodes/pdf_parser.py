import base64
import json
import re
from typing import Any, Dict, List
from openai import OpenAI
import requests

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
        Similar to suggestion_node.py pattern - passes image directly to LLM for parsing.
        
        Args:
            base64_string: Base64-encoded PDF/image content
            filename: Optional filename for logging/debugging purposes
            
        Returns:
            Dictionary with structured lab data
        """
        print(f"\n[PDF Parser] Parsing PDF/image from base64 using LLM (filename: {filename})...")
        print(f"[PDF Parser] Base64 data length: {len(base64_string)} characters")
        print(f"[PDF Parser] Calling LLM to parse image and extract structured data...")
        
        # Use LLM directly to parse the PDF/image (similar to suggestion_node.py)
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
                                "url": f"data:application/pdf;base64,{base64_string}"
                            }
                        },
                        {
                            "type": "text",
                            "text": "Please extract all lab data from this PDF/image according to the schema provided in the system prompt. Extract all test results, patient information, dates, and any other relevant data."
                        }
                    ]
                }
            ],
            temperature=0,
            max_tokens=2000,  # Increased for PDF/image parsing
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
