import shutil
from pathlib import Path

import typer

from fsc.config.loader import load_merged_config
from fsc.utils.console import console
from fsc.utils.fs import find_spec_files


def clean_command(
  directory: Path | None = typer.Argument(
    None, help="Target directory (default: current directory)"
  ),
  yes: bool = typer.Option(False, "-y", "--yes", help="Skip confirmation prompt"),
) -> None:
  """Remove all generated *.fsc.md files and output directory, keep .fsc/ config."""

  root = Path(directory).resolve() if directory else Path.cwd()
  specs = find_spec_files(root)
  cfg = load_merged_config(root)
  output_dir = (root / cfg.output.output_dir).resolve()
  has_output_dir = output_dir.exists()

  if not specs and not has_output_dir:
    console.print("[yellow]No *.fsc.md files or output directory found.[/yellow]")
    return

  if specs:
    console.print(f"Found {len(specs)} *.fsc.md file{'s' if len(specs) != 1 else ''}:")

    for spec in specs:
      try:
        rel = spec.relative_to(root)

      except ValueError:
        rel = spec

      console.print(f"  {rel}")

  if has_output_dir:
    try:
      rel = output_dir.relative_to(root)

    except ValueError:
      rel = output_dir

    console.print(f"  {rel}/ (output directory)")

  if not yes:
    typer.confirm("Remove these files and directories?", abort=True)

  removed = 0

  for spec in specs:
    spec.unlink()
    removed += 1

  if has_output_dir:
    shutil.rmtree(output_dir)
    console.print("[green]Removed output directory[/green]")

  console.print(f"\n[green]Removed {removed} file{'s' if removed != 1 else ''}.[/green]")
