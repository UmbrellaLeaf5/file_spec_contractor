from pathlib import Path

import tomllib

from fsc.config.enums import GenerationMode, OutputMode
from fsc.config.schemas import CLIConfigOverrides, FSCConfig


def _load_toml(path: Path) -> dict:
  if not path.exists():
    return {}

  with path.open("rb") as f:
    return tomllib.load(f)


def load_user_config() -> dict:
  home = Path.home()
  cfg_path = home / ".config" / "fsc" / "config.toml"
  return _load_toml(cfg_path)


def load_project_config(project_root: Path) -> dict:
  cfg_path = project_root / ".fsc" / "config.toml"
  return _load_toml(cfg_path)


def deep_update(dst: dict, src: dict) -> dict:
  for k, v in src.items():
    if isinstance(v, dict) and isinstance(dst.get(k), dict):
      dst[k] = deep_update(dst.get(k, {}), v)

    else:
      dst[k] = v

  return dst


def load_merged_config(project_root: Path) -> FSCConfig:
  cfg = FSCConfig().to_dict()
  user = load_user_config()
  project = load_project_config(project_root)

  if user:
    cfg = deep_update(cfg, user)

  if project:
    cfg = deep_update(cfg, project)

  return FSCConfig.from_dict(cfg)


def apply_cli_overrides(cfg: FSCConfig, overrides: CLIConfigOverrides) -> FSCConfig:
  if overrides.extensions:
    cfg.project.extensions = overrides.extensions

  if overrides.exclude_dirs:
    cfg.project.exclude_dirs = overrides.exclude_dirs

  if overrides.exclude_files:
    cfg.project.exclude_files = overrides.exclude_files

  if overrides.provider:
    cfg.api.provider = overrides.provider

  if overrides.model is not None:
    cfg.api.model = overrides.model

  if overrides.output_mode:
    cfg.output.output_mode = OutputMode(overrides.output_mode)

  if overrides.output_dir:
    cfg.output.output_dir = overrides.output_dir

  if overrides.batch_size:
    cfg.output.batch_size = overrides.batch_size

  if overrides.prompt_file:
    cfg.prompt.file = overrides.prompt_file

  if overrides.language:
    cfg.output.language = overrides.language

  if overrides.concurrency:
    cfg.runtime.concurrency = overrides.concurrency

  if overrides.generation_mode:
    cfg.runtime.generation_mode = GenerationMode(overrides.generation_mode)

  return cfg
