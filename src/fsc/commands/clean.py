from pathlib import Path

import typer

from fsc.utils.console import console
from fsc.utils.fs import find_spec_files


def clean_command(
  directory: Path | None = typer.Argument(
    None, help="Target directory (default: current directory)"
  ),
  yes: bool = typer.Option(False, "-y", "--yes", help="Skip confirmation prompt"),
) -> None:
  """Remove all generated *.fsc.md files, keep .fsc/ configuration."""

  root = Path(directory).resolve() if directory else Path.cwd()
  specs = find_spec_files(root)

  if not specs:
    console.print("[yellow]No *.fsc.md files found.[/yellow]")
    return

  console.print(f"Found {len(specs)} *.fsc.md file{'s' if len(specs) != 1 else ''}:")

  for spec in specs:
    try:
      rel = spec.relative_to(root)

    except ValueError:
      rel = spec

    console.print(f"  {rel}")

  if not yes:
    typer.confirm("Remove these files?", abort=True)

  removed = 0

  for spec in specs:
    spec.unlink()
    removed += 1

  console.print(f"\n[green]Removed {removed} file{'s' if removed != 1 else ''}.[/green]")
