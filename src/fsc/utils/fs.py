import fnmatch
import os
from pathlib import Path

from fsc.config.schema import FSCConfig


def scan_files(
  root: Path,
  extensions: list[str],
  exclude_dirs: list[str],
  exclude_files: list[str],
) -> list[Path]:
  ex_dirs_set = set(exclude_dirs or [])
  results = []

  for p in sorted(root.rglob("*")):
    if any(parent.name in ex_dirs_set for parent in p.parents):
      continue

    if p.is_dir():
      continue

    if not any(p.suffix == ext for ext in extensions):
      continue

    if any(fnmatch.fnmatch(p.name, pattern) for pattern in exclude_files):
      continue

    if ".git" in p.parts:
      continue

    results.append(p)

  return results


def resolve_output_path(src_path: Path, project_root: Path, cfg: FSCConfig) -> Path:
  if cfg.output.output_mode == "adjacent":
    return src_path.with_name(src_path.stem + ".fsc.md")

  out_dir = Path(cfg.output.output_dir)
  rel = src_path.relative_to(project_root)
  target = out_dir / rel

  return target.with_suffix(".fsc.md")


def write_spec_atomic(path: Path, text: str) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  tmp = path.with_suffix(path.suffix + ".tmp")
  tmp.write_text(text, encoding="utf-8")

  os.replace(tmp, path)
