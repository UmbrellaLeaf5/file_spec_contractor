import httpx

from fsc.providers.openai_compatible import OpenAICompatibleProvider
from fsc.utils.console import console


class DeepSeekProvider(OpenAICompatibleProvider):
  """DeepSeek API provider using OpenAI-compatible chat completions."""

  provider_name = "DeepSeek"

  def __init__(
    self,
    api_key: str,
    model: str = "deepseek-chat",
    timeout: float = 60.0,
  ):
    super().__init__(
      api_key=api_key,
      base_url="https://api.deepseek.com/v1",
      model=model,
      timeout=timeout,
    )

  def _report_api_error(self, resp: httpx.Response) -> None:
    try:
      body = resp.json()
      error = body.get("error", {})
      message = error.get("message", f"HTTP {resp.status_code}")

    except Exception:
      message = resp.text[:200] if resp.text else f"HTTP {resp.status_code}"

    console.print(f"[red]DeepSeek API error: {message}[/red]")
    console.print("[red]Check your API key or try again later.[/red]")
