"""
Custom DeepEval-compatible LLM wrapper that routes evaluations through NetMind.

Based on the "using custom LLMs" guidance from the DeepEval documentation,
this class subclasses `DeepEvalBaseLLM` and implements the `generate` helpers
so any metric can call into the NetMind-hosted DeepSeek model instead of OpenAI.
"""

from __future__ import annotations

import ast
import asyncio
import logging
import os
import json
import re
from typing import Optional, Type, Any

from deepeval.models.base_model import DeepEvalBaseLLM
from openai import OpenAI
from pydantic import BaseModel, ValidationError

# Configure logger
logger = logging.getLogger(__name__)

NETMIND_BASE_URL = "https://api.netmind.ai/inference-api/openai/v1"
DEFAULT_MODEL = "deepseek-ai/DeepSeek-V3.2-Exp"
DEFAULT_NETMIND_KEY = "6ecc3bdc2980400a8786fd512ad487e7"


class NetMindLLM(DeepEvalBaseLLM):
    """Minimal adapter that lets DeepEval metrics use NetMind as the judge LLM."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        api_key: Optional[str] = None,
        system_prompt: str = "You are a strict evaluator. Judge fairly and respond concisely.",
        temperature: float = 0.0,
        max_tokens: int = 4096,  # Increased from 512 to prevent JSON truncation
        max_retries: int = 3,
    ) -> None:
        self.model = model
        self.api_key = api_key or os.getenv("NETMIND_API_KEY", DEFAULT_NETMIND_KEY)
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self._client: Optional[OpenAI] = None

    def load_model(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(base_url=NETMIND_BASE_URL, api_key=self.api_key)
        return self._client

    def _build_messages(self, prompt: str, schema: Optional[Type[BaseModel]]) -> list[dict]:
        system_content = self.system_prompt
        if schema is not None:
            schema_json = json.dumps(schema.model_json_schema(), ensure_ascii=False)
            system_content += (
                "\n\nRespond ONLY with valid JSON that strictly matches this schema:\n"
                f"{schema_json}"
            )
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt},
        ]

    def _complete(
        self, 
        prompt: str, 
        schema: Optional[Type[BaseModel]] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        client = self.load_model()
        response = client.chat.completions.create(
            model=self.model,
            messages=self._build_messages(prompt, schema),
            temperature=self.temperature,
            max_tokens=max_tokens or self.max_tokens,
        )
        return response.choices[0].message.content.strip()

    def _maybe_apply_schema(
        self,
        text: str,
        schema: Optional[Type[BaseModel]],
        prompt: Optional[str] = None,
        retry_count: int = 0,
    ) -> object:
        if schema is None:
            return text

        result, last_error = self._try_schema_validation(schema, text)
        if result is not None:
            return result

        for candidate in self._schema_json_candidates(text):
            if candidate == text:
                continue
            candidate_result, last_error = self._try_schema_validation(schema, candidate)
            if candidate_result is not None:
                return candidate_result

        # If we still can't parse and we have retries left, try again with more tokens
        if retry_count < self.max_retries and prompt is not None:
            # Check if the error is due to truncated JSON (EOF errors)
            error_msg = str(last_error) if last_error else ""
            if "EOF" in error_msg or "truncat" in error_msg.lower() or "unexpect" in error_msg.lower():
                # Increase max_tokens for retry
                new_max_tokens = self.max_tokens * (2 ** (retry_count + 1))
                logger.warning(f"JSON truncation detected. Retrying with max_tokens={new_max_tokens} (attempt {retry_count + 1}/{self.max_retries})")
                
                # Retry the API call with more tokens
                retry_text = self._complete(prompt, schema, max_tokens=new_max_tokens)
                return self._maybe_apply_schema(retry_text, schema, prompt, retry_count + 1)

        if last_error is not None:
            raise last_error
        raise ValidationError.from_exception_data(  # type: ignore[arg-type]
            "NetMindLLM",
            [],
        )

    def generate(self, prompt: str, schema: Optional[Type[BaseModel]] = None, **_: object) -> object:
        """Synchronous generation API used by DeepEval metrics."""
        text = self._complete(prompt, schema)
        return self._maybe_apply_schema(text, schema, prompt, retry_count=0)

    async def a_generate(
        self,
        prompt: str,
        schema: Optional[Type[BaseModel]] = None,
        **_: object,
    ) -> object:
        """Async version required by DeepEval; offloads to a thread."""
        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(None, self._complete, prompt, schema, None)
        return self._maybe_apply_schema(text, schema, prompt, retry_count=0)

    def get_model_name(self) -> str:
        return f"NetMind:{self.model}"

    @staticmethod
    def _schema_json_candidates(raw_text: str) -> list[str]:
        stripped = raw_text.strip()
        fence_stripped = NetMindLLM._strip_code_fence(stripped)
        brace_from_fence = NetMindLLM._extract_json_object(fence_stripped)
        brace_from_stripped = NetMindLLM._extract_json_object(stripped)
        fenced_blocks = NetMindLLM._extract_code_fence_blocks(raw_text)
        json_payloads = NetMindLLM._find_json_payloads(stripped)
        json_payloads_from_fence = NetMindLLM._find_json_payloads(fence_stripped)
        
        # Try to repair truncated JSON
        repaired = NetMindLLM._attempt_json_repair(stripped)
        repaired_fence = NetMindLLM._attempt_json_repair(fence_stripped)
        repaired_brace = NetMindLLM._attempt_json_repair(brace_from_stripped)

        candidates: list[str] = [
            stripped,
            fence_stripped,
            brace_from_fence,
            brace_from_stripped,
            *fenced_blocks,
            *json_payloads,
            *json_payloads_from_fence,
        ]
        
        # Add repaired versions if they exist
        if repaired:
            candidates.append(repaired)
        if repaired_fence:
            candidates.append(repaired_fence)
        if repaired_brace:
            candidates.append(repaired_brace)

        unique_candidates: list[str] = []
        seen: set[str] = set()
        for candidate in candidates:
            candidate = candidate.strip()
            if not candidate or candidate in seen:
                continue
            seen.add(candidate)
            unique_candidates.append(candidate)
        return unique_candidates

    @staticmethod
    def _strip_code_fence(text: str) -> str:
        stripped = text.strip()
        if stripped.startswith("```"):
            stripped = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", stripped)
            stripped = re.sub(r"\s*```$", "", stripped)
        return stripped.strip()

    @staticmethod
    def _extract_json_object(text: str) -> str:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1]
        return text

    @staticmethod
    def _extract_code_fence_blocks(text: str) -> list[str]:
        pattern = re.compile(r"```(?:json|JSON)?\s*(.*?)```", re.DOTALL)
        blocks = []
        for match in pattern.finditer(text):
            block = match.group(1).strip()
            if block:
                blocks.append(block)
        return blocks

    @staticmethod
    def _find_json_payloads(text: str) -> list[str]:
        decoder = json.JSONDecoder()
        payloads: list[str] = []
        idx = 0
        length = len(text)

        while idx < length:
            brace_idx = text.find("{", idx)
            if brace_idx == -1:
                break
            try:
                obj, relative_end = decoder.raw_decode(text[brace_idx:])
            except json.JSONDecodeError:
                idx = brace_idx + 1
                continue

            payloads.append(json.dumps(obj, ensure_ascii=False))
            idx = brace_idx + relative_end

        return payloads
    
    @staticmethod
    def _attempt_json_repair(text: str) -> Optional[str]:
        """
        Attempt to repair truncated JSON by closing unclosed strings, arrays, and objects.
        This is a best-effort approach for handling EOF errors.
        """
        try:
            # Try to parse as-is first
            json.loads(text)
            return text
        except json.JSONDecodeError:
            pass
        
        # Count unclosed braces and brackets
        open_braces = text.count('{') - text.count('}')
        open_brackets = text.count('[') - text.count(']')
        
        # Check if we're in the middle of a string (odd number of quotes after last complete structure)
        last_quote = text.rfind('"')
        if last_quote > 0:
            # Count quotes before the last quote to see if we're in a string
            quotes_before = text[:last_quote].count('"')
            # Check for escaped quotes
            escaped_quotes = text[:last_quote].count('\\"')
            effective_quotes = quotes_before - escaped_quotes
            
            if effective_quotes % 2 == 1:  # We're inside an unclosed string
                text += '"'
        
        # Close any unclosed arrays and objects
        text += ']' * open_brackets
        text += '}' * open_braces
        
        try:
            json.loads(text)
            return text
        except json.JSONDecodeError:
            return None

    def _try_schema_validation(
        self,
        schema: Type[BaseModel],
        payload: str,
    ) -> tuple[Optional[object], Optional[ValidationError]]:
        try:
            return schema.model_validate_json(payload), None
        except ValidationError as json_error:
            last_error: Optional[ValidationError] = json_error
        except ValueError:
            last_error = None

        python_obj = self._coerce_to_python_obj(payload)
        if python_obj is None:
            return None, last_error

        try:
            return schema.model_validate(python_obj), None
        except ValidationError as python_error:
            return None, python_error

    @staticmethod
    def _coerce_to_python_obj(text: str) -> Optional[Any]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        sanitized = NetMindLLM._remove_trailing_commas(text)
        if sanitized != text:
            try:
                return json.loads(sanitized)
            except json.JSONDecodeError:
                pass

        try:
            return ast.literal_eval(text)
        except (ValueError, SyntaxError):
            pass

        if sanitized != text:
            try:
                return ast.literal_eval(sanitized)
            except (ValueError, SyntaxError):
                pass

        return None

    @staticmethod
    def _remove_trailing_commas(text: str) -> str:
        return re.sub(r",\s*(\]|\})", r"\1", text)


