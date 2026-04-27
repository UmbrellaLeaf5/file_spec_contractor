from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """Абстрактный базовый класс для всех LLM-провайдеров."""

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """
        Генерирует ответ на основе системного и пользовательского промптов.

        Args:
            system_prompt: Инструкция для модели.
            user_prompt: Пользовательский запрос.

        Returns:
            Сгенерированный текст.
        """
        ...
