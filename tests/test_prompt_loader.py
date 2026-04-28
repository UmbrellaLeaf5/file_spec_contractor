from pathlib import Path

from fsc.config.schemas import FSCConfig, PromptConfig
from fsc.utils.prompt_loader import (
  builtin_prompt_text,
  load_prompt,
  resolve_prompt_path,
)


def test_missing_prompt_uses_builtin(tmp_path: Path):
  project_root = tmp_path
  cfg = FSCConfig(prompt=PromptConfig(file=".fsc/PROMPT.md"))
  p = resolve_prompt_path(project_root, cfg)

  assert p is None
  text = load_prompt(p)

  assert len(text) > 50  # noqa: PLR2004


def test_load_prompt_from_existing_file(tmp_path: Path):
  prompt_file = tmp_path / "custom.md"
  prompt_file.write_text("# Custom prompt\nBe concise.")

  text = load_prompt(prompt_file)

  assert "Custom prompt" in text


def test_load_prompt_from_empty_file(tmp_path: Path):
  prompt_file = tmp_path / "empty.md"
  prompt_file.write_text("")

  text = load_prompt(prompt_file)

  assert text == ""


def test_builtin_prompt_russian():
  text = builtin_prompt_text("ru")

  assert len(text) > 50  # noqa: PLR2004


def test_builtin_prompt_unknown_language():
  text = builtin_prompt_text("fr")

  assert len(text) > 0


def test_resolve_prompt_path_cli_override_nonexistent(tmp_path: Path):
  cfg = FSCConfig()

  result = resolve_prompt_path(tmp_path, cfg, cli_prompt="nonexistent.md")

  assert result is None


def test_resolve_prompt_path_absolute(tmp_path: Path):
  prompt_file = tmp_path / "prompt.md"
  prompt_file.write_text("# test")

  cfg = FSCConfig()
  result = resolve_prompt_path(tmp_path, cfg, cli_prompt=str(prompt_file))

  assert result == prompt_file


def test_resolve_prompt_path_project_relative(tmp_path: Path):
  fsc_dir = tmp_path / ".fsc"
  fsc_dir.mkdir()
  prompt_file = fsc_dir / "PROMPT.md"
  prompt_file.write_text("# project prompt")

  cfg = FSCConfig(prompt=PromptConfig(file=".fsc/PROMPT.md"))
  result = resolve_prompt_path(tmp_path, cfg)

  assert result == prompt_file
