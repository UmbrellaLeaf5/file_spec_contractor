from abc import ABC, abstractmethod


class BaseProvider(ABC):
  """Абстрактный базовый класс для всех LLM-провайдеров."""

  model: str

  @abstractmethod
  def generate(self, system_prompt: str, user_prompt: str, **kwargs) -> str: ...

  @abstractmethod
  def close(self) -> None:
    """Release resources (httpx client, etc.). Override in subclasses."""
