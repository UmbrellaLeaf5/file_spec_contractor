import shutil
from pathlib import Path

import typer

from fsc.commands.init import _confirm_destructive
from fsc.utils.console import console
from fsc.utils.fs import find_spec_files


def deinit_command(
  directory: Path | None = typer.Argument(
    None, help="Target directory (default: current directory)"
  ),
  yes: bool = typer.Option(False, "-y", "--yes", help="Skip confirmation prompts"),
) -> None:
  """Remove .fsc/ and all generated *.fsc.md files from project."""

  root = Path(directory).resolve() if directory else Path.cwd()
  removed_dirs = 0
  removed_files = 0

  fsc_dir = root / ".fsc"

  if fsc_dir.exists():
    _confirm_destructive(yes)
    shutil.rmtree(fsc_dir)
    console.print("[green]Removed .fsc/[/green]")
    removed_dirs += 1

  else:
    console.print("[yellow].fsc/ not found, skipping[/yellow]")

  for spec in find_spec_files(root):
    spec.unlink()

    try:
      rel = spec.relative_to(root)

    except ValueError:
      rel = spec

    console.print(f"[green]Removed {rel}[/green]")
    removed_files += 1

  if removed_dirs == 0 and removed_files == 0:
    console.print("[yellow]Nothing to remove.[/yellow]")

  else:
    console.print(
      f"\n[bold]Done![/bold] Removed {removed_dirs} director"
      f"{'y' if removed_dirs == 1 else 'ies'} and "
      f"{removed_files} file{'s' if removed_files != 1 else ''}."
    )
