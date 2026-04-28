import httpx

from fsc.utils.console import console

from .base import BaseProvider


class DeepSeekProvider(BaseProvider):
  """DeepSeek API provider using OpenAI-compatible chat completions."""

  def __init__(
    self,
    api_key: str,
    base_url: str = "https://api.deepseek.com/v1",
    model: str = "deepseek-chat",
    timeout: float = 60.0,
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
        "[red]Network error connecting to DeepSeek. Check your internet connection.[/red]"
      )
      raise RuntimeError("Network error connecting to DeepSeek") from None

    if resp.status_code != 200:  # noqa: PLR2004
      self._report_api_error(resp)
      raise RuntimeError("DeepSeek API request failed")

    data = resp.json()
    return data["choices"][0]["message"]["content"]

  def _report_api_error(self, resp: httpx.Response) -> None:
    try:
      body = resp.json()
      error = body.get("error", {})
      message = error.get("message", f"HTTP {resp.status_code}")

    except Exception:
      message = f"HTTP {resp.status_code}"

    console.print(f"[red]DeepSeek API error: {message}[/red]")
    console.print("[red]Check your API key or try again later.[/red]")

  def close(self):
    self._client.close()
