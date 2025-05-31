import os, requests
from typing import List, Dict, Tuple

class LLMProvider:
    """
    Uniform wrapper around DeepSeek, OpenAI-compatible, and Anthropic Claude.
    Returns (success, payload_or_error) tuples.
    """

    PROVIDERS = {
        "DeepSeek": {
            "models": ["deepseek-chat", "deepseek-coder"],
            "api_url": "https://api.deepseek.com/v1/chat/completions",
            "env_key": "DEEPSEEK_API_KEY",
        },
        "OpenAI": {
            "models": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
            "api_url": "https://api.openai.com/v1/chat/completions",
            "env_key": "OPENAI_API_KEY",
        },
        "Claude": {
            "models": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
            "api_url": "https://api.anthropic.com/v1/messages",
            "env_key": "ANTHROPIC_API_KEY",
        },
    }

    # ---------- public helpers ----------
    @classmethod
    def get_api_key(cls, provider: str) -> str | None:
        return os.getenv(cls.PROVIDERS[provider]["env_key"])

    @classmethod
    def make_request(
        cls,
        provider: str,
        model: str,
        messages: List[Dict],
        temperature: float,
        max_tokens: int,
    ) -> Tuple[bool, Dict]:
        key = cls.get_api_key(provider)
        if not key:
            return False, {"error": f"API key not found for {provider}"}

        try:
            if provider == "Claude":
                return cls._anthropic(key, model, messages, temperature, max_tokens)
            return cls._openai_like(provider, key, model, messages, temperature, max_tokens)
        except Exception as exc:
            return False, {"error": str(exc)}

    # ---------- private impls ----------
    @classmethod
    def _anthropic(
        cls, key: str, model: str, messages: List[Dict], temperature: float, max_tokens: int
    ) -> Tuple[bool, Dict]:
        headers = {
            "x-api-key": key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }

        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_messages = [m for m in messages if m["role"] != "system"]

        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": user_messages,
        }
        if system_msg:
            payload["system"] = system_msg

        r = requests.post(cls.PROVIDERS["Claude"]["api_url"], headers=headers, json=payload)
        if r.status_code == 200:
            data = r.json()
            return True, {"content": data["content"][0]["text"], "usage": data["usage"]}
        return False, {"error": f"API error {r.status_code}: {r.text}"}

    @classmethod
    def _openai_like(
        cls,
        provider: str,
        key: str,
        model: str,
        messages: List[Dict],
        temperature: float,
        max_tokens: int,
    ) -> Tuple[bool, Dict]:
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        r = requests.post(cls.PROVIDERS[provider]["api_url"], headers=headers, json=payload)
        if r.status_code == 200:
            data = r.json()
            return True, {
                "content": data["choices"][0]["message"]["content"],
                "usage": data["usage"],
            }
        return False, {"error": f"API error {r.status_code}: {r.text}"}
