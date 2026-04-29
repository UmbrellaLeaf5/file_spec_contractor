from collections.abc import Iterator
from contextlib import contextmanager

from fsc.providers.base import BaseProvider
from fsc.providers.deepseek import DeepSeekProvider
from fsc.providers.openrouter import OpenRouterProvider


_PROVIDER_REGISTRY: dict[str, dict] = {
  "deepseek": {
    "cls": DeepSeekProvider,
    "env_key": "DEEPSEEK_API_KEY",
    "display": "DeepSeek",
  },
  "openrouter": {
    "cls": OpenRouterProvider,
    "env_key": "OPEN_ROUTER_API_KEY",
    "display": "OpenRouter",
  },
}


def get_provider_info(name: str) -> dict | None:
  return _PROVIDER_REGISTRY.get(name)


def create_provider(name: str, api_key: str, model: str | None = None) -> BaseProvider:
  info = get_provider_info(name)

  if info is None:
    raise ValueError(
      f"Unknown provider: {name}. Available: {', '.join(_PROVIDER_REGISTRY)}"
    )

  provider = info["cls"](api_key=api_key)

  if model is not None:
    provider.model = model

  return provider


def close_provider(provider: BaseProvider):
  provider.close()


@contextmanager
def provider_context(
  name: str, api_key: str, model: str | None = None
) -> Iterator[BaseProvider]:
  provider = create_provider(name, api_key, model)

  try:
    yield provider

  finally:
    close_provider(provider)
