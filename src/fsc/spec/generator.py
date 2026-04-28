import shutil
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from rich.console import Console

from fsc.config.enums import GenerationMode, OutputMode
from fsc.config.schema import FSCConfig
from fsc.providers.base import BaseProvider
from fsc.spec.bulk_generator import generate_bulk
from fsc.utils.fs import resolve_output_path, write_spec_atomic


console = Console(log_path=False)


def _find_fresh_spec_in_any_mode(
  src_path: Path, project_root: Path, cfg: FSCConfig
) -> Path | None:
  src_mtime = src_path.stat().st_mtime
  original_mode = cfg.output.output_mode

  for mode in OutputMode:
    cfg.output.output_mode = mode
    spec = resolve_output_path(src_path, project_root, cfg)

    if spec.exists() and spec.stat().st_mtime >= src_mtime:
      cfg.output.output_mode = original_mode
      return spec

  cfg.output.output_mode = original_mode
  return None


def _read_file_safe(path: Path) -> str:
  try:
    return path.read_text(encoding="utf-8")

  except Exception:
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

  sorted_paths = sorted(file_data)
  index_map = {path: i for i, path in enumerate(sorted_paths)}

  if gen_mode == GenerationMode.bulk:
    if file_count > 0:
      try:
        bulk_results, missing = generate_bulk(
          file_data, prompt_template, provider, cfg, project_root, src_paths, dry_run
        )

      except KeyboardInterrupt:
        console.print("\n[yellow]Bulk generation interrupted.[/yellow]")
        return []

      if missing:
        retry_data = {k: file_data[k] for k in sorted(missing)}
        retry_paths = {k: src_paths[k] for k in sorted(missing)}

        console.log(f"Retrying {len(retry_data)} missed files in per-file mode ...")

        retry_results = []

        for rel_path, code in retry_data.items():
          try:
            out = _process_one_file(
              retry_paths[rel_path],
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
              retry_results.append(out)

          except Exception as e:
            console.print(f"[red]Error processing {rel_path}: {e}[/red]")

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

  console.log(f"Processing {file_count} files in {gen_mode.value} mode ...")

  if concurrency > 1:
    results: list[Path] = []

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
      futures = {}

      for rel_path, code in file_data.items():
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

      try:
        for future in as_completed(futures):
          rel_path = futures[future]

          try:
            out = future.result()

            if out is not None:
              results.append(out)

          except Exception as e:
            console.print(f"[red]Error processing {rel_path}: {e}[/red]")

      except KeyboardInterrupt:
        console.print(
          f"\n[yellow]Interrupted. Saved {len(results)} of {file_count} files.[/yellow]"
        )

        for f in futures:
          f.cancel()

        return results

    console.print(f"[green]Done. Processed {len(results)} files.[/green]")

    return results

  results = []

  try:
    for rel_path, code in file_data.items():
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
        index_map[rel_path],
      )

      if out is not None:
        results.append(out)

  except KeyboardInterrupt:
    console.print(
      f"\n[yellow]Interrupted. Saved {len(results)} of {file_count} files.[/yellow]"
    )
    return results

  console.print(f"[green]Done. Processed {len(results)} files.[/green]")

  return results
