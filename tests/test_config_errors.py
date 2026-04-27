from pathlib import Path

import pytest
import tomllib
from fsc.config.loader import load_merged_config


def test_missing_config_falls_back_to_defaults(tmp_path: Path):
  cfg = load_merged_config(tmp_path)
  assert cfg.project.extensions == [".py"]


def test_empty_config_file(tmp_path: Path):
  fsc_dir = tmp_path / ".fsc"
  fsc_dir.mkdir()
  (fsc_dir / "config.toml").write_text("")

  cfg = load_merged_config(tmp_path)
  assert cfg.project.extensions == [".py"]


def test_invalid_toml_syntax(tmp_path: Path):
  fsc_dir = tmp_path / ".fsc"
  fsc_dir.mkdir()
  (fsc_dir / "config.toml").write_text("[project]\nextensions = [")

  with pytest.raises(tomllib.TOMLDecodeError):
    load_merged_config(tmp_path)


def test_wrong_types_in_config(tmp_path: Path):
  fsc_dir = tmp_path / ".fsc"
  fsc_dir.mkdir()
  (fsc_dir / "config.toml").write_text('[project]\nextensions = ".py"\n')

  with pytest.raises(ValueError, match="valid list"):
    load_merged_config(tmp_path)


def test_extensions_without_dot(tmp_path: Path):
  fsc_dir = tmp_path / ".fsc"
  fsc_dir.mkdir()
  (fsc_dir / "config.toml").write_text('[project]\nextensions = ["py", "kt"]\n')

  with pytest.raises(ValueError, match="must start with"):
    load_merged_config(tmp_path)


def test_negative_concurrency(tmp_path: Path):
  fsc_dir = tmp_path / ".fsc"
  fsc_dir.mkdir()
  (fsc_dir / "config.toml").write_text("[runtime]\nconcurrency = -5\n")

  with pytest.raises(ValueError, match="greater than or equal to 1"):
    load_merged_config(tmp_path)


def test_unknown_provider_in_config(tmp_path: Path):
  fsc_dir = tmp_path / ".fsc"
  fsc_dir.mkdir()
  (fsc_dir / "config.toml").write_text('[api]\nprovider = "unknown"\n')

  cfg = load_merged_config(tmp_path)
  assert cfg.api.provider == "unknown"


def test_missing_section_uses_defaults(tmp_path: Path):
  fsc_dir = tmp_path / ".fsc"
  fsc_dir.mkdir()
  (fsc_dir / "config.toml").write_text('[output]\nlanguage = "ru"\n')

  cfg = load_merged_config(tmp_path)
  assert cfg.output.language == "ru"
  assert cfg.project.extensions == [".py"]


def test_negative_batch_size(tmp_path: Path):
  fsc_dir = tmp_path / ".fsc"
  fsc_dir.mkdir()
  (fsc_dir / "config.toml").write_text("[output]\nbatch_size = -10\n")

  with pytest.raises(ValueError, match="greater than 0"):
    load_merged_config(tmp_path)


def test_batch_size_string(tmp_path: Path):
  fsc_dir = tmp_path / ".fsc"
  fsc_dir.mkdir()
  (fsc_dir / "config.toml").write_text('[output]\nbatch_size = "abc"\n')

  with pytest.raises(ValueError, match="valid integer"):
    load_merged_config(tmp_path)
