from collections.abc import Iterable
from pathlib import Path

from rich.console import Console

from fsc.config.schema import FscConfig
from fsc.providers.base import BaseProvider
from fsc.utils.fs import resolve_output_path, write_spec_atomic


console = Console()


def _read_file_safe(path: Path) -> str:
  try:
    return path.read_text(encoding="utf-8")

  except Exception:
    return path.read_text(encoding="latin-1")


def _build_user_prompt(file_path: str, language: str, code: str) -> str:
  """Создаёт пользовательский промпт с метаданными и кодом."""

  return (
    f"Generate specification for the following file.\n\n"
    f"FILE: {file_path}\n"
    f"LANG: {language}\n\n"
    f"```\n{code}\n```"
  )


def generate_for_files(
  files: Iterable[Path],
  prompt_template: str,
  provider: BaseProvider,
  cfg: FscConfig,
  project_root: Path,
  dry_run: bool = False,
) -> list[Path]:
  results = []

  for src_path in files:
    code = _read_file_safe(src_path)

    try:
      rel_path = str(src_path.relative_to(project_root))

    except ValueError:
      rel_path = str(src_path)

    user_prompt = _build_user_prompt(rel_path, cfg.output.language, code)

    console.log(f"Generating spec for {rel_path} ...")

    spec_text = provider.generate(prompt_template, user_prompt)
    out_path = resolve_output_path(src_path, project_root, cfg)

    if not dry_run:
      write_spec_atomic(out_path, spec_text)

    results.append(out_path)

  return results
