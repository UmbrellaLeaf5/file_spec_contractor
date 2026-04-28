from pathlib import Path

import tomllib

from fsc.config.enums import GenerationMode
from fsc.config.schemas import FSCConfig


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


def apply_cli_overrides(cfg: FSCConfig, cli_args: dict) -> FSCConfig:
  if cli_args.get("extensions"):
    cfg.project.extensions = cli_args["extensions"]

  if cli_args.get("exclude_dirs"):
    cfg.project.exclude_dirs = cli_args["exclude_dirs"]

  if cli_args.get("exclude_files"):
    cfg.project.exclude_files = cli_args["exclude_files"]

  if cli_args.get("provider"):
    cfg.api.provider = cli_args["provider"]

  if cli_args.get("model"):
    cfg.api.model = cli_args["model"]

  if cli_args.get("output_mode"):
    cfg.output.output_mode = cli_args["output_mode"]

  if cli_args.get("output_dir"):
    cfg.output.output_dir = cli_args["output_dir"]

  if cli_args.get("batch_size") is not None:
    cfg.output.batch_size = cli_args["batch_size"]

  if cli_args.get("prompt_file"):
    cfg.prompt.file = cli_args["prompt_file"]

  if cli_args.get("language"):
    cfg.output.language = cli_args["language"]

  if cli_args.get("concurrency") is not None:
    cfg.runtime.concurrency = cli_args["concurrency"]

  if cli_args.get("generation_mode"):
    cfg.runtime.generation_mode = GenerationMode(cli_args["generation_mode"])

  return cfg
