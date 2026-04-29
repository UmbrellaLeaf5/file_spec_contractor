import httpx

from fsc.providers.openai_compatible import OpenAICompatibleProvider
from fsc.utils.console import console


class OpenRouterProvider(OpenAICompatibleProvider):
  """OpenRouter provider using OpenAI-compatible chat completions."""

  provider_name = "OpenRouter"

  def __init__(
    self,
    api_key: str,
    model: str = "openai/gpt-oss-120b:free",
    timeout: float = 120.0,
  ):
    super().__init__(
      api_key=api_key,
      base_url="https://openrouter.ai/api/v1",
      model=model,
      timeout=timeout,
    )

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
        f"[red]OpenRouter API error {code}: {message}"
        f" (provider: {provider_name})[/red]"
      )
    else:
      console.print(f"[red]OpenRouter API error {code}: {message}[/red]")

    console.print(
      "[red]Check your API key, verify model access, "
      "or reduce the project size.[/red]"
    )
