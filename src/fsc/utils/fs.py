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


def _encode_path(rel_path: str) -> str:
  encoded = rel_path.replace("\\", "__").replace("/", "__")
  return encoded + ".fsc.md"


def resolve_output_path(
  src_path: Path,
  project_root: Path,
  cfg: FSCConfig,
  file_index: int | None = None,
) -> Path:
  if cfg.output.output_mode == "adjacent":
    return src_path.with_name(src_path.name + ".fsc.md")

  try:
    rel = src_path.relative_to(project_root)

  except ValueError:
    rel = src_path

  if cfg.output.output_mode == "batch":
    if file_index is None:
      file_index = 0

    batch_num = (file_index // cfg.output.batch_size) + 1
    encoded = _encode_path(str(rel))
    out_dir = Path(cfg.output.output_dir)

    return out_dir / f"batch-{batch_num}" / encoded

  out_dir = Path(cfg.output.output_dir)
  target = out_dir / rel
  return target.with_suffix(target.suffix + ".fsc.md")


def write_spec_atomic(path: Path, text: str) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  tmp = path.with_suffix(path.suffix + ".tmp")
  tmp.write_text(text, encoding="utf-8")

  os.replace(tmp, path)


def is_spec_fresh(src_path: Path, project_root: Path, cfg: FSCConfig) -> bool:
  spec_path = resolve_output_path(src_path, project_root, cfg)

  if not spec_path.exists():
    return False

  return spec_path.stat().st_mtime >= src_path.stat().st_mtime


def find_spec_files(root: Path) -> list[Path]:
  return sorted(root.rglob("*.fsc.md"))
