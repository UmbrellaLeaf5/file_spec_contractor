import httpx

from fsc.utils.console import console

from .base import BaseProvider


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

    except httpx.HTTPError:
      console.print(
        "[red]Network error connecting to OpenRouter. "
        "Check your internet connection.[/red]"
      )
      raise RuntimeError("Network error connecting to OpenRouter") from None

    if resp.status_code != 200:  # noqa: PLR2004
      self._report_api_error(resp)
      raise RuntimeError("OpenRouter API request failed")

    data = resp.json()
    return data["choices"][0]["message"]["content"]

  def _report_api_error(self, resp: httpx.Response) -> None:
    try:
      body = resp.json()
      error = body.get("error", {})
      code = error.get("code", resp.status_code)
      message = error.get("message", "Unknown error")
      metadata = error.get("metadata", {})
      provider_name = metadata.get("provider_name", "")

    except Exception:
      code = resp.status_code
      message = resp.text[:200] if resp.text else "Unknown error"
      provider_name = ""

    if provider_name:
      console.print(
        f"[red]OpenRouter API error {code}: {message} (provider: {provider_name})[/red]"
      )
    else:
      console.print(f"[red]OpenRouter API error {code}: {message}[/red]")

    console.print(
      "[red]Check your API key, verify model access, or reduce the project size.[/red]"
    )

  def close(self):
    self._client.close()
