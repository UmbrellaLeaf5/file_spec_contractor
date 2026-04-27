import re
from pathlib import Path

from rich.console import Console

from fsc.utils.fs import resolve_output_path, write_spec_atomic

console = Console()

_SPEC_MARKER = re.compile(
  r"## SPEC:\s*(.+?)\s*\n(.*?)(?=\n## SPEC:|\Z)", re.DOTALL
)


def _build_batch_prompt(files: dict[str, str], language: str) -> str:
  prompt = (
    "Generate specifications for ALL files listed below. "
    "For each file, start with the marker `## SPEC: path/to/file.ext`, "
    "then write the specification in the standard format. "
    "Separate specifications with `---`.\n\n"
  )

  for rel_path in sorted(files):
    prompt += f"### FILE: {rel_path}\n"
    prompt += f"### LANG: {language}\n\n"
    prompt += f"```\n{files[rel_path]}\n```\n\n"

  return prompt


def _parse_batch_response(response: str) -> dict[str, str]:
  specs: dict[str, str] = {}

  for match in _SPEC_MARKER.finditer(response):
    path = match.group(1).strip()
    content = match.group(2).strip()

    if content.endswith("---"):
      content = content[:-3].strip()

    specs[path] = content

  return specs


def generate_batch(
  files: dict[str, str],
  system_prompt: str,
  provider,
  cfg,
  project_root: Path,
  src_paths: dict[str, Path],
  dry_run: bool = False,
) -> list[Path]:
  count = len(files)
  console.log(f"Generating specs for {count} files in batch mode ...")

  batch_prompt = _build_batch_prompt(files, cfg.output.language)
  response = provider.generate(system_prompt, batch_prompt)
  parsed = _parse_batch_response(response)

  if not parsed:
    console.print("[yellow]Batch response could not be parsed, will fall back.[/yellow]")
    return []

  results: list[Path] = []

  for rel_path, spec_text in sorted(parsed.items()):
    src = src_paths.get(rel_path)

    if src is None:
      console.print(f"[yellow]Skipping unknown file from batch response: {rel_path}[/yellow]")
      continue

    out_path = resolve_output_path(src, project_root, cfg)

    if not dry_run:
      write_spec_atomic(out_path, spec_text)

    console.log(f"  Saved {rel_path}")
    results.append(out_path)

  return results
