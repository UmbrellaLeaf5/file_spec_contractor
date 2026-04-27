import httpx
from rich.console import Console

from .base import BaseProvider


console = Console(log_path=False)


class OpenRouterProvider(BaseProvider):
  """OpenRouter provider using OpenAI-compatible chat completions."""

  def __init__(
    self,
    api_key: str,
    base_url: str = "https://openrouter.ai/api/v1",
    model: str = "openai/gpt-oss-120b:free",
    timeout: float = 120.0,
  ):
    self.api_key = api_key
    self.base_url = base_url.rstrip("/")
    self.model = model
    self._client = httpx.Client(timeout=timeout)

  def generate(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
    headers = {
      "Authorization": f"Bearer {self.api_key}",
      "Content-Type": "application/json",
    }

    payload = {
      "model": self.model,
      "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
      ],
      "temperature": 0.2,
      **kwargs,
    }

    url = f"{self.base_url}/chat/completions"

    try:
      resp = self._client.post(url, json=payload, headers=headers)
      if resp.status_code != 200:  # noqa: PLR2004
        raise RuntimeError(f"OpenRouter API error {resp.status_code}: {resp.text[:500]}")

      data = resp.json()
      return data["choices"][0]["message"]["content"]

    except httpx.HTTPError as e:
      raise RuntimeError(f"OpenRouter request failed: {e}") from e

  def close(self):
    self._client.close()
