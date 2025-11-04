from typing import List, Dict, Any
from app.core.config import settings
import ollama

class OllamaLLM:
    def __init__(self, model: str | None = None):
        self.model = model or settings.OLLAMA_MODEL_PRIMARY
        self.host = settings.OLLAMA_HOST
        # the python client reads OLLAMA_HOST env automatically, but we call with host to be explicit
        self.client = ollama.Client(host=self.host)

    def chat_json(self, messages: List[Dict[str, str]], force_model: str | None = None) -> str:
        """
        Ask the model to return STRICT JSON. If it fails, retry with fallback model.
        """
        model_to_use = force_model or self.model
        try:
            return self._invoke(messages, model_to_use)
        except Exception:
            if model_to_use != settings.OLLAMA_MODEL_FALLBACK:
                # retry with fallback
                return self._invoke(messages, settings.OLLAMA_MODEL_FALLBACK)
            raise

    def _invoke(self, messages: List[Dict[str, str]], model: str) -> str:
        resp = self.client.chat(model=model, messages=messages, options={
            "temperature": settings.TEMPERATURE,
        })
        content = resp["message"]["content"].strip()
        print("\n\n========== RAW OLLAMA OUTPUT ==========\n")
        print(content[:2000])  # show first 2000 chars
        print("\n======================================\n")
        return content
