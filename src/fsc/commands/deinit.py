import shutil
from pathlib import Path

from rich.console import Console


console = Console()


def deinit_command() -> None:
  """Remove .fsc/ and all generated .fsc.md files from project."""

  cwd = Path.cwd()
  removed_dirs = 0
  removed_files = 0

  fsc_dir = cwd / ".fsc"

  if fsc_dir.exists():
    shutil.rmtree(fsc_dir)
    console.print("[green]Removed .fsc/[/green]")
    removed_dirs += 1

  else:
    console.print("[yellow].fsc/ not found, skipping[/yellow]")

  for spec in sorted(cwd.rglob("*.fsc.md")):
    spec.unlink()

    try:
      rel = spec.relative_to(cwd)

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
