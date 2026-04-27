from pathlib import Path

import typer
from rich.console import Console

from fsc.config.schema import FscConfig
from fsc.prompt_loader import builtin_prompt_text

console = Console()


def init_command(
  yes: bool = typer.Option(
    False, "-y", "--yes", help="Skip confirmations, overwrite existing files"
  ),
) -> None:
  """Create .fsc/ directory with template config and prompt."""

  fsc_dir = Path.cwd() / ".fsc"
  fsc_dir.mkdir(exist_ok=True)

  config_path = fsc_dir / "config.toml"

  if not config_path.exists() or yes:
    config_path.write_text(FscConfig().to_toml())
    console.print("[green]Created .fsc/config.toml[/green]")

  else:
    console.print("[yellow].fsc/config.toml already exists, skipping[/yellow]")

  prompt_path = fsc_dir / "PROMPT.md"

  if not prompt_path.exists() or yes:
    prompt_path.write_text(builtin_prompt_text())
    console.print("[green]Created .fsc/PROMPT.md[/green]")

  else:
    console.print("[yellow].fsc/PROMPT.md already exists, skipping[/yellow]")

  console.print("\n[bold]Done![/bold] Next steps:")
  console.print("  1. Set your API key:")
  console.print("     export OPEN_ROUTER_API_KEY=sk-or-v1-...")
  console.print("  2. Generate specifications:")
  console.print("     fsc generate")
  console.print("  3. Or preview first:")
  console.print("     fsc generate --dry-run")
