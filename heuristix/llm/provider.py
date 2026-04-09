"""Direct LLM providers for high-frequency code generation calls."""
from __future__ import annotations

import json
import os
import subprocess
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from heuristix.config import HeuristiXConfig


class LLMProvider(ABC):
    """Base interface for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, system: str | None = None) -> str:
        """Generate text from a prompt. Returns the raw response string."""
        ...


class ClaudeCLIProvider(LLMProvider):
    """Invoke Claude via the `claude` CLI tool (subprocess)."""

    def __init__(self, model: str = ""):
        self.model = model

    def generate(self, prompt: str, system: str | None = None) -> str:
        cmd = ["claude", "-p"]
        if self.model:
            cmd.extend(["--model", self.model])
        full_prompt = prompt
        if system:
            full_prompt = f"[System: {system}]\n\n{prompt}"
        result = subprocess.run(
            cmd,
            input=full_prompt,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            raise RuntimeError(f"claude CLI failed: {result.stderr.strip()}")
        return result.stdout.strip()


class OpenAIProvider(LLMProvider):
    """OpenAI-compatible API provider (works with any OpenAI-API server)."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        base_url: str = "https://api.openai.com/v1",
        temperature: float = 0.7,
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature

    def generate(self, prompt: str, system: str | None = None) -> str:
        messages: list[dict] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        with httpx.Client(timeout=120) as client:
            resp = client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={"model": self.model, "messages": messages, "temperature": self.temperature},
            )
            resp.raise_for_status()
            data = resp.json()
        return data["choices"][0]["message"]["content"]


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider (localhost:11434)."""

    def __init__(
        self,
        model: str = "llama3",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature

    def generate(self, prompt: str, system: str | None = None) -> str:
        payload: dict = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": self.temperature},
        }
        if system:
            payload["system"] = system

        with httpx.Client(timeout=300) as client:
            resp = client.post(f"{self.base_url}/api/generate", json=payload)
            resp.raise_for_status()
            data = resp.json()
        return data.get("response", "")


def create_provider(
    provider: str,
    model: str = "",
    api_key: str = "",
    temperature: float = 0.7,
    **kwargs: object,
) -> LLMProvider:
    """Factory function to create an LLM provider by name."""
    match provider:
        case "claude_cli":
            return ClaudeCLIProvider(model=model)
        case "openai":
            if not api_key:
                raise ValueError("OpenAI provider requires an api_key")
            return OpenAIProvider(api_key=api_key, model=model or "gpt-4o", temperature=temperature)
        case "ollama":
            return OllamaProvider(model=model or "llama3", temperature=temperature)
        case _:
            raise ValueError(f"Unknown LLM provider: {provider!r}")


def create_provider_for_role(config: "HeuristiXConfig", role: str) -> LLMProvider:
    """Create an LLM provider for a specific role (mutation, crossover, etc.)."""
    role_config = config.llm.get_role(role)
    api_key = role_config.api_key or os.environ.get("OPENAI_API_KEY", "")
    return create_provider(
        provider=role_config.provider,
        model=role_config.model,
        api_key=api_key,
        temperature=role_config.temperature,
    )
