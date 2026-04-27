from pathlib import Path

import tomllib


DEFAULTS: dict = {
  "project": {
    "extensions": [".py"],
    "exclude_dirs": [".venv", "venv", ".git", "__pycache__", "tests"],
    "exclude_files": [],
  },
  "output": {
    "language": "en",
    "output_mode": "mirror",
    "output_dir": ".fsc/specs",
  },
  "api": {
    "provider": "deepseek",
    "deepseek_api_key": "",
  },
  "prompt": {"file": ".fsc/PROMPT.md"},
}


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


def load_merged_config(project_root: Path) -> dict:
  cfg = deep_update({}, DEFAULTS)
  user = load_user_config()
  project = load_project_config(project_root)
  if user:
    cfg = deep_update(cfg, user)
  if project:
    cfg = deep_update(cfg, project)
  return cfg


def apply_cli_overrides(cfg: dict, cli_args: dict) -> dict:
  if cli_args.get("extensions"):
    cfg.setdefault("project", {})["extensions"] = cli_args["extensions"]
  if cli_args.get("exclude_dirs"):
    cfg.setdefault("project", {})["exclude_dirs"] = cli_args["exclude_dirs"]
  if cli_args.get("exclude_files"):
    cfg.setdefault("project", {})["exclude_files"] = cli_args["exclude_files"]
  if cli_args.get("provider"):
    cfg.setdefault("api", {})["provider"] = cli_args["provider"]
  if cli_args.get("output_mode"):
    cfg.setdefault("output", {})["output_mode"] = cli_args["output_mode"]
  if cli_args.get("output_dir"):
    cfg.setdefault("output", {})["output_dir"] = cli_args["output_dir"]
  if cli_args.get("prompt_file"):
    cfg.setdefault("prompt", {})["file"] = cli_args["prompt_file"]
  if cli_args.get("language"):
    cfg.setdefault("output", {})["language"] = cli_args["language"]
  return cfg
