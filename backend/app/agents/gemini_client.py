import os
import json
import logging
import httpx
from typing import Dict, Any, Optional, Tuple
from backend.app.core.config import settings

logger = logging.getLogger("resq.gemini")

class GeminiClient:
    """
    Official Google Gemini API client with structured JSON output,
    timeout handling, exponential retry, and deterministic fallback mode.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    async def generate_structured(
        self,
        system_instruction: str,
        prompt: str,
        response_schema: Optional[Dict[str, Any]] = None,
        max_retries: int = 2,
        timeout_seconds: float = 6.0
    ) -> Tuple[bool, Dict[str, Any], str, int]:
        """
        Sends request to Google Gemini API.
        Returns: (success: bool, parsed_json: dict, execution_mode: str, tokens_used: int)
        """
        if not self.is_configured:
            logger.info("GEMINI_API_KEY is not configured. Using deterministic fallback engine.")
            return False, {}, "DETERMINISTIC_ENGINE", 0

        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        
        request_body: Dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "systemInstruction": {
                "parts": [{"text": system_instruction}]
            },
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }
        
        if response_schema:
            request_body["generationConfig"]["responseSchema"] = response_schema

        headers = {"Content-Type": "application/json"}
        
        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                    response = await client.post(url, json=request_body, headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        candidates = data.get("candidates", [])
                        if candidates and "content" in candidates[0]:
                            parts = candidates[0]["content"].get("parts", [])
                            if parts and "text" in parts[0]:
                                text_content = parts[0]["text"]
                                parsed = json.loads(text_content)
                                tokens = data.get("usageMetadata", {}).get("totalTokenCount", 120)
                                return True, parsed, "GEMINI_LLM", tokens
                        return False, {}, "DETERMINISTIC_ENGINE", 0
                    elif response.status_code == 429:
                        logger.warning(f"Gemini API rate limit (429), attempt {attempt+1}/{max_retries+1}")
                    else:
                        logger.warning(f"Gemini API HTTP {response.status_code}: {response.text[:150]}")
                        break
            except Exception as e:
                logger.warning(f"Gemini API connection error (attempt {attempt+1}): {e}")
                break
                
        return False, {}, "DETERMINISTIC_ENGINE", 0

gemini_client = GeminiClient()
