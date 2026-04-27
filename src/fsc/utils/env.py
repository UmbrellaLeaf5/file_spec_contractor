from pathlib import Path

from dotenv import dotenv_values


def load_dotenv(directory: Path) -> dict[str, str]:
  """Загружает переменные из .env файла в указанной директории."""
  env_path = directory / ".env"

  if not env_path.exists():
    return {}

  return dotenv_values(env_path)
