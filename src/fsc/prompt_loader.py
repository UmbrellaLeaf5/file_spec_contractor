import importlib.resources
from pathlib import Path

from rich.console import Console

from fsc.config.schema import FSCConfig


console = Console()


def resolve_prompt_path(
  project_root: Path, cfg: FSCConfig, cli_prompt: str | None = None
) -> Path | None:
  if cli_prompt:
    p = Path(cli_prompt)

    if p.is_absolute():
      return p

    candidate = project_root / p

    if candidate.exists():
      return candidate

    return None

  prompt_rel = cfg.prompt.file

  if prompt_rel:
    candidate = project_root / prompt_rel

    if candidate.exists():
      return candidate

  return None


def load_prompt(path: Path | None, language: str = "en") -> str:
  if path and path.exists():
    return path.read_text(encoding="utf-8")

  console.print(
    "[yellow]Warning: prompt file not found; using builtin prompt. "
    "You can create .fsc/PROMPT.md via `fsc init`.[/yellow]"
  )

  return builtin_prompt_text(language)


def builtin_prompt_text(language: str = "en") -> str:
  """Возвращает встроенный промпт для указанного языка (последнюю версию)."""

  try:
    resources = importlib.resources.files("fsc.prompts")
    prefix = f"fsc_{language}_"
    versions: list[tuple[int, str]] = []

    for entry in resources.iterdir():
      name = entry.name

      if name.startswith(prefix) and name.endswith(".md"):
        ver_str = name[len(prefix) : -len(".md")]

        try:
          ver = int(ver_str)
          text = entry.read_text(encoding="utf-8")
          versions.append((ver, text))

        except ValueError:
          continue

    if versions:
      return max(versions, key=lambda x: x[0])[1]

  except Exception:
    pass

  return (
    "You are a technical writer. Create a concise specification for the "
    "provided source file. Follow the structure: Purpose, Dependencies, "
    "Public API, Implementation Notes, Handle with Care, Code Style."
  )
