import re
from pathlib import Path

from fsc.config.schemas import FSCConfig
from fsc.providers.base import BaseProvider
from fsc.utils.console import console
from fsc.utils.fs import resolve_output_path, write_spec_atomic
from fsc.utils.progress import make_file_progress, make_spinner


_SPEC_MARKER = re.compile(r"## SPEC:\s*(.+?)\s*\n(.*?)(?=\n## SPEC:|\Z)", re.DOTALL)


def _build_batch_prompt(files: dict[str, str], language: str) -> str:
  prompt = (
    "Generate specifications for ALL files listed below. "
    "For each file, start with the marker `## SPEC: path/to/file.ext` "
    "followed by a mandatory header `# path/to/file.ext` on the next line, "
    "then write the specification in the standard format. "
    "Separate specifications with `---`.\n\n"
    "Expected format for EACH file:\n\n"
    "## SPEC: src/app.py\n"
    "# src/app.py\n\n"
    "## Purpose\n"
    "...\n"
    "---\n\n"
  )

  for rel_path in sorted(files):
    normalized = rel_path.replace("\\", "/")
    prompt += f"### FILE: {normalized}\n"
    prompt += f"### LANG: {language}\n\n"
    prompt += f"```\n{files[rel_path]}\n```\n\n"

  return prompt


def _parse_batch_response(response: str) -> dict[str, str]:
  specs: dict[str, str] = {}

  for match in _SPEC_MARKER.finditer(response):
    path = match.group(1).strip().replace("\\", "/")
    content = match.group(2).strip()

    if content.endswith("---"):
      content = content[:-3].strip()

    specs[path] = content

  return specs


def _save_bulk_results(
  parsed: dict[str, str],
  src_paths_norm: dict[str, Path],
  project_root: Path,
  cfg: FSCConfig,
  dry_run: bool,
  show_progress: bool,
) -> tuple[list[Path], int]:
  results: list[Path] = []
  file_index = 0

  if show_progress:
    with make_file_progress(len(parsed), "Saving specs") as progress:
      task = progress.add_task("", total=len(parsed))

      for rel_path, spec_text in sorted(parsed.items()):
        src = src_paths_norm.get(rel_path)

        if src is None:
          console.print(
            f"[yellow]Skipping unknown file from bulk response: {rel_path}[/yellow]"
          )

          continue

        out_path = resolve_output_path(src, project_root, cfg, file_index=file_index)
        file_index += 1

        if not dry_run:
          write_spec_atomic(out_path, spec_text)

        results.append(out_path)
        progress.update(task, advance=1)

  else:
    for rel_path, spec_text in sorted(parsed.items()):
      src = src_paths_norm.get(rel_path)

      if src is None:
        console.print(
          f"[yellow]Skipping unknown file from bulk response: {rel_path}[/yellow]"
        )

        continue

      out_path = resolve_output_path(src, project_root, cfg, file_index=file_index)
      file_index += 1

      if not dry_run:
        write_spec_atomic(out_path, spec_text)

      console.log(f"  Saved {rel_path}")
      results.append(out_path)

  return results, file_index


def generate_bulk(
  files: dict[str, str],
  system_prompt: str,
  provider: BaseProvider,
  cfg: FSCConfig,
  project_root: Path,
  src_paths: dict[str, Path],
  dry_run: bool = False,
  show_progress: bool = False,
) -> tuple[list[Path], set[str]]:
  if not src_paths:
    console.print("[yellow]Batch skipped: no valid source paths.[/yellow]")

    return [], set()

  if dry_run:
    console.print(
      "[yellow]Bulk mode is not compatible with --dry-run. "
      "Switching to per-file dry run.[/yellow]"
    )

    return [], set()

  src_paths_norm = {k.replace("\\", "/"): v for k, v in src_paths.items()}

  count = len(files)

  batch_prompt = _build_batch_prompt(files, cfg.output.language)

  if show_progress:
    with make_spinner(f"Generating specs for {count} files in bulk mode ..."):
      response = provider.generate(system_prompt, batch_prompt)

  else:
    console.log(f"Generating specs for {count} files in bulk mode ...")
    response = provider.generate(system_prompt, batch_prompt)

  parsed = _parse_batch_response(response)

  if not parsed:
    console.print("[yellow]Batch response could not be parsed, will fall back.[/yellow]")
    return [], set()

  results, _ = _save_bulk_results(
    parsed,
    src_paths_norm,
    project_root,
    cfg,
    dry_run,
    show_progress,
  )

  missing = set(files) - set(parsed)

  if missing:
    console.log(f"Bulk missed {len(missing)} files, will retry them.")

  return results, missing
