import shutil
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import charset_normalizer

from fsc.config.enums import GenerationMode, OutputMode
from fsc.config.schemas import FSCConfig
from fsc.providers.base import BaseProvider
from fsc.spec.bulk_generator import generate_bulk
from fsc.utils.console import console
from fsc.utils.fs import resolve_output_path, write_spec_atomic
from fsc.utils.progress import make_file_progress


def _find_fresh_spec_in_any_mode(
  src_path: Path, project_root: Path, cfg: FSCConfig
) -> Path | None:
  src_mtime = src_path.stat().st_mtime

  for mode in OutputMode:
    spec = resolve_output_path(src_path, project_root, cfg, output_mode=mode)

    if spec.exists() and spec.stat().st_mtime >= src_mtime:
      return spec

  return None


def _read_file_safe(path: Path) -> str:
  try:
    return path.read_text(encoding="utf-8")

  except UnicodeDecodeError:
    result = charset_normalizer.from_path(str(path))

    if result.best():
      return str(result.best())

    return path.read_text(encoding="latin-1")


def _build_user_prompt(file_path: str, language: str, code: str) -> str:
  return (
    f"Generate specification for the following file.\n\n"
    f"FILE: {file_path}\n"
    f"LANG: {language}\n\n"
    f"```\n{code}\n```"
  )


def _resolve_rel(path: Path, project_root: Path) -> str:
  try:
    return str(path.relative_to(project_root))

  except ValueError:
    return str(path)


def _process_one_file(
  src_path: Path,
  rel_path: str,
  code: str,
  language: str,
  system_prompt: str,
  provider: BaseProvider,
  cfg: FSCConfig,
  project_root: Path,
  dry_run: bool,
  file_index: int = 0,
) -> Path | None:
  user_prompt = _build_user_prompt(rel_path, language, code)

  if dry_run:
    console.log(f"Would generate spec for {rel_path}")
    return resolve_output_path(src_path, project_root, cfg, file_index=file_index)

  console.log(f"Generating spec for {rel_path} ...")
  spec_text = provider.generate(system_prompt, user_prompt)
  out_path = resolve_output_path(src_path, project_root, cfg, file_index=file_index)

  if not dry_run:
    write_spec_atomic(out_path, spec_text)

  return out_path


def _try_process(
  rel_path: str,
  code: str,
  src_paths: dict[str, Path],
  cfg: FSCConfig,
  prompt_template: str,
  provider: BaseProvider,
  project_root: Path,
  dry_run: bool,
  index_map: dict[str, int],
  results: list[Path],
) -> None:
  """Call _process_one_file with the standard argument set and collect result."""

  try:
    out = _process_one_file(
      src_paths[rel_path],
      rel_path,
      code,
      cfg.output.language,
      prompt_template,
      provider,
      cfg,
      project_root,
      dry_run,
      index_map.get(rel_path, 0),
    )

    if out is not None:
      results.append(out)

  except Exception as e:
    console.print(f"[red]Error processing {rel_path}: {e}[/red]")


def _run_sequential(
  data: dict[str, str],
  src_paths: dict[str, Path],
  cfg: FSCConfig,
  prompt_template: str,
  provider: BaseProvider,
  project_root: Path,
  dry_run: bool,
  index_map: dict[str, int],
  show_progress: bool,
  description: str = "Generating specs",
) -> list[Path]:
  """Process files one-by-one, optionally showing a progress bar."""
  results: list[Path] = []

  if show_progress:
    with make_file_progress(len(data), description) as progress:
      task = progress.add_task("", total=len(data))

      try:
        for rel_path, code in data.items():
          progress.update(task, description=f"Processing {rel_path}")
          _try_process(
            rel_path,
            code,
            src_paths,
            cfg,
            prompt_template,
            provider,
            project_root,
            dry_run,
            index_map,
            results,
          )
          progress.update(task, advance=1)

      except KeyboardInterrupt:
        return results

  else:
    console.log(f"Processing {len(data)} files ...")

    try:
      for rel_path, code in data.items():
        _try_process(
          rel_path,
          code,
          src_paths,
          cfg,
          prompt_template,
          provider,
          project_root,
          dry_run,
          index_map,
          results,
        )

    except KeyboardInterrupt:
      return results

  return results


def _submit_futures(
  executor: ThreadPoolExecutor,
  data: dict[str, str],
  src_paths: dict[str, Path],
  cfg: FSCConfig,
  prompt_template: str,
  provider: BaseProvider,
  project_root: Path,
  dry_run: bool,
  index_map: dict[str, int],
) -> dict:
  futures = {}

  for rel_path, code in data.items():
    future = executor.submit(
      _process_one_file,
      src_paths[rel_path],
      rel_path,
      code,
      cfg.output.language,
      prompt_template,
      provider,
      cfg,
      project_root,
      dry_run,
      index_map[rel_path],
    )

    futures[future] = rel_path

  return futures


def _collect_future_result(future, rel_path, results) -> None:
  """Get result from a completed future and append to results if valid."""
  try:
    out = future.result()

    if out is not None:
      results.append(out)

  except Exception as e:
    console.print(f"[red]Error processing {rel_path}: {e}[/red]")


def _run_parallel(
  data: dict[str, str],
  src_paths: dict[str, Path],
  cfg: FSCConfig,
  prompt_template: str,
  provider: BaseProvider,
  project_root: Path,
  dry_run: bool,
  index_map: dict[str, int],
  concurrency: int,
  show_progress: bool,
) -> list[Path]:
  """Process files concurrently via thread pool, optionally with progress."""
  results: list[Path] = []

  if show_progress:
    with make_file_progress(len(data), "Generating specs") as progress:
      task = progress.add_task("", total=len(data))

      with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = _submit_futures(
          executor,
          data,
          src_paths,
          cfg,
          prompt_template,
          provider,
          project_root,
          dry_run,
          index_map,
        )

        try:
          for future in as_completed(futures):
            rel_path = futures[future]
            _collect_future_result(future, rel_path, results)
            progress.update(task, advance=1)

        except KeyboardInterrupt:
          for f in futures:
            f.cancel()
          return results

  else:
    console.log(f"Processing {len(data)} files ...")

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
      futures = _submit_futures(
        executor,
        data,
        src_paths,
        cfg,
        prompt_template,
        provider,
        project_root,
        dry_run,
        index_map,
      )

      try:
        for future in as_completed(futures):
          rel_path = futures[future]
          _collect_future_result(future, rel_path, results)

      except KeyboardInterrupt:
        for f in futures:
          f.cancel()
        return results

  console.print(f"[green]Done. Processed {len(results)} files.[/green]")

  return results


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
        rel_path = _resolve_rel(src_path, project_root).replace("\\", "/")
        console.log(f"Skipping {rel_path} (spec is up to date)")
        skipped += 1

        continue

      moved = _find_fresh_spec_in_any_mode(src_path, project_root, cfg)

      if moved and moved != current_spec:
        current_spec.parent.mkdir(parents=True, exist_ok=True)

        shutil.move(str(moved), str(current_spec))

        rel_path = _resolve_rel(src_path, project_root).replace("\\", "/")
        console.log(f"Moved spec for {rel_path} (output mode changed)")
        skipped += 1

        continue

    code = _read_file_safe(src_path)
    rel_path = _resolve_rel(src_path, project_root).replace("\\", "/")
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
