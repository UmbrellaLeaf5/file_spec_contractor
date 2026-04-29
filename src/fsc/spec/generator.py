import shutil
from collections.abc import Iterable
from pathlib import Path

from fsc.config.enums import GenerationMode, OutputMode
from fsc.config.schemas import FSCConfig
from fsc.providers.base import BaseProvider
from fsc.spec.bulk_generator import generate_bulk
from fsc.spec.engine import _run_parallel, _run_sequential
from fsc.utils.console import console
from fsc.utils.fs import read_file_safe, resolve_output_path, resolve_rel


def _find_fresh_spec_in_any_mode(
  src_path: Path, project_root: Path, cfg: FSCConfig
) -> Path | None:
  src_mtime = src_path.stat().st_mtime

  for mode in OutputMode:
    spec = resolve_output_path(src_path, project_root, cfg, output_mode=mode)

    if spec.exists() and spec.stat().st_mtime >= src_mtime:
      return spec

  return None


def generate_for_files(
  files: Iterable[Path],
  prompt_template: str,
  provider: BaseProvider,
  cfg: FSCConfig,
  project_root: Path,
  dry_run: bool = False,
  concurrency: int | None = None,
  gen_mode: GenerationMode | None = None,
  force: bool = False,
) -> list[Path]:
  if concurrency is None:
    concurrency = cfg.runtime.concurrency

  if gen_mode is None:
    gen_mode = cfg.runtime.generation_mode

  file_data: dict[str, str] = {}
  src_paths: dict[str, Path] = {}
  skipped = 0

  for src_path in files:
    if not force:
      current_spec = resolve_output_path(src_path, project_root, cfg)

      if (
        current_spec.exists() and current_spec.stat().st_mtime >= src_path.stat().st_mtime
      ):
        rel_path = resolve_rel(src_path, project_root).replace("\\", "/")
        console.log(f"Skipping {rel_path} (spec is up to date)")
        skipped += 1

        continue

      moved = _find_fresh_spec_in_any_mode(src_path, project_root, cfg)

      if moved and moved != current_spec:
        current_spec.parent.mkdir(parents=True, exist_ok=True)

        shutil.move(str(moved), str(current_spec))

        rel_path = resolve_rel(src_path, project_root).replace("\\", "/")
        console.log(f"Moved spec for {rel_path} (output mode changed)")
        skipped += 1

        continue

    code = read_file_safe(src_path)
    rel_path = resolve_rel(src_path, project_root).replace("\\", "/")
    file_data[rel_path] = code
    src_paths[rel_path] = src_path

  file_count = len(file_data)

  if file_count == 0:
    if skipped > 0:
      console.print(f"[green]All {skipped} files are up to date.[/green]")

    return []

  if skipped > 0:
    console.log(f"Skipped {skipped} up-to-date files.")

  show_progress = not dry_run and not cfg.runtime.no_progress

  sorted_paths = sorted(file_data)
  index_map = {path: i for i, path in enumerate(sorted_paths)}

  if gen_mode == GenerationMode.bulk:
    if file_count > 0:
      try:
        bulk_results, missing = generate_bulk(
          file_data,
          prompt_template,
          provider,
          cfg,
          project_root,
          src_paths,
          dry_run,
          show_progress,
        )

      except KeyboardInterrupt:
        console.print("\n[yellow]Bulk generation interrupted.[/yellow]")
        return []

      if missing:
        retry_data = {k: file_data[k] for k in sorted(missing)}
        retry_paths = {k: src_paths[k] for k in sorted(missing)}

        console.log(f"Retrying {len(retry_data)} missed files in per-file mode ...")

        retry_results = _run_sequential(
          retry_data,
          retry_paths,
          cfg,
          prompt_template,
          provider,
          project_root,
          dry_run,
          index_map,
          show_progress,
          description="Retrying missed files",
        )

        results = bulk_results + retry_results

        if len(results) < file_count:
          console.print(
            f"[yellow]Could not generate specs for "
            f"{file_count - len(results)} files.[/yellow]"
          )

        console.print(
          f"[green]Done. Processed {len(results)} files. "
          f"({len(bulk_results)} from bulk + {len(retry_results)} from retry)[/green]"
        )

        return results

      if bulk_results:
        console.print(f"[green]Done. Processed {len(bulk_results)} files.[/green]")
        return bulk_results

      console.print("[yellow]Falling back to per-file generation.[/yellow]")

  if concurrency > 1:
    return _run_parallel(
      file_data,
      src_paths,
      cfg,
      prompt_template,
      provider,
      project_root,
      dry_run,
      index_map,
      concurrency,
      show_progress,
    )

  results = _run_sequential(
    file_data,
    src_paths,
    cfg,
    prompt_template,
    provider,
    project_root,
    dry_run,
    index_map,
    show_progress,
  )

  console.print(f"[green]Done. Processed {len(results)} files.[/green]")

  return results
