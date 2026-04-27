from pathlib import Path

from fsc.config.loader import apply_cli_overrides, load_merged_config


def test_defaults_merge(tmp_path: Path):
  cfg = load_merged_config(tmp_path)

  assert cfg.project.extensions == [".py"]


def test_cli_overrides(tmp_path: Path):
  cfg = load_merged_config(tmp_path)
  cli = {"extensions": [".py", ".kt"], "output_dir": ".fsc/out"}
  cfg2 = apply_cli_overrides(cfg, cli)

  assert cfg2.project.extensions == [".py", ".kt"]
  assert cfg2.output.output_dir == ".fsc/out"
