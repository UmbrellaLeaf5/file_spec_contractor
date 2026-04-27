import importlib.resources
from pathlib import Path

from rich.console import Console

from fsc.config.schema import FscConfig


console = Console()


def resolve_prompt_path(
  project_root: Path, cfg: FscConfig, cli_prompt: str | None = None
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


def load_prompt(path: Path | None) -> str:
  if path and path.exists():
    text = path.read_text(encoding="utf-8")
    return text

  console.print(
    "[yellow]Warning: prompt file not found; using builtin prompt. "
    "You can create .fsc/PROMPT.md via `fsc init`.[/yellow]"
  )

  try:
    return importlib.resources.read_text("fsc.prompts", "primary.md")

  except Exception:
    return (
      "You are a technical writer. Create a concise specification for the "
      "provided source file. Follow the structure: Purpose, Dependencies, "
      "Public API, Implementation Notes, Handle with Care, Code Style."
    )
