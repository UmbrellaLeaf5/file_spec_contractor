from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from rich.console import Console

from fsc.config.schema import FSCConfig
from fsc.providers.base import BaseProvider
from fsc.spec.batch_generator import generate_batch
from fsc.utils.fs import is_spec_fresh, resolve_output_path, write_spec_atomic


console = Console()


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
  concurrency: int = 3,
  force_per_file: bool = False,
  force: bool = False,
) -> list[Path]:
  file_data: dict[str, str] = {}
  src_paths: dict[str, Path] = {}
  skipped = 0

  for src_path in files:
    if not force and is_spec_fresh(src_path, project_root, cfg):
      rel_path = _resolve_rel(src_path, project_root)
      console.log(f"Skipping {rel_path} (spec is up to date)")
      skipped += 1
      continue

    code = _read_file_safe(src_path)
    rel_path = _resolve_rel(src_path, project_root)
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

  if not force_per_file:
    mode = "batch"

    if file_count > 0:
      try:
        results = generate_batch(
          file_data, prompt_template, provider, cfg, project_root, src_paths, dry_run
        )

      except KeyboardInterrupt:
        console.print("\n[yellow]Batch generation interrupted.[/yellow]")
        return []

      if results:
        console.print(f"[green]Done. Processed {len(results)} files.[/green]")
        return results

      console.print("[yellow]Falling back to per-file generation.[/yellow]")

  else:
    mode = "per-file"

  console.log(f"Processing {file_count} files in {mode} mode ...")

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
