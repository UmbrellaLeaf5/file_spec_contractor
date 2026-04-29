from abc import abstractmethod

import httpx

from fsc.providers.base import BaseProvider
from fsc.utils.console import console


class OpenAICompatibleProvider(BaseProvider):
  """Abstract provider for OpenAI-compatible chat completions APIs.

  Subclasses must define ``provider_name`` and ``_report_api_error()``.
  """

  provider_name: str

  def __init__(
    self,
    api_key: str,
    base_url: str,
    model: str,
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
        f"[red]Network error connecting to {self.provider_name}. "
        "Check your internet connection.[/red]"
      )
      raise RuntimeError(
        f"Network error connecting to {self.provider_name}"
      ) from None

    if resp.status_code != 200:  # noqa: PLR2004
      self._report_api_error(resp)
      raise RuntimeError(f"{self.provider_name} API request failed")

    data = resp.json()
    return data["choices"][0]["message"]["content"]

  @abstractmethod
  def _report_api_error(self, resp: httpx.Response) -> None:
    ...

  def close(self) -> None:
    self._client.close()
