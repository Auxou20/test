from __future__ import annotations
import httpx, json
from typing import List, Dict, Optional
from .config import OLLAMA_BASE_URL, LLM_MODEL, EMBED_MODEL

class OllamaClient:
    def __init__(self, base_url: str = OLLAMA_BASE_URL):
        self.base_url = base_url.rstrip('/')

    def chat(self, messages: List[Dict[str, str]], model: Optional[str]=None, temperature: float=0.2) -> str:
        url = f"{self.base_url}/api/chat"
        payload = {"model": model or LLM_MODEL, "messages": messages, "options": {"temperature": temperature}}
        with httpx.Client(timeout=120.0) as client:
            r = client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
        # Non-stream response: 'message' field
        if isinstance(data, dict) and "message" in data:
            return data["message"].get("content", "")
        # Streamed? Aggregate 'message' chunks if needed
        if isinstance(data, list):
            txt = "".join([d.get("message", {}).get("content", "") for d in data])
            return txt
        return ""

    def embed(self, texts: List[str], model: Optional[str]=None):
        url = f"{self.base_url}/api/embeddings"
        payload = {"model": model or EMBED_MODEL, "input": texts}
        with httpx.Client(timeout=120.0) as client:
            r = client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
        # Return list of vectors (shape: [n, dim])
        if isinstance(texts, str):
            return [data.get("embedding", [])]
        else:
            return [d.get("embedding", []) for d in data.get("data", [])]

ollama = OllamaClient()
