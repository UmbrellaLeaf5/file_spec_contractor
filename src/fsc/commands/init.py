from pathlib import Path

from rich.console import Console

from fsc.config.schema import FscConfig


console = Console()


def init_command() -> None:
  """Создаёт .fsc/ с шаблонами config.toml и PROMPT.md."""

  fsc_dir = Path.cwd() / ".fsc"
  fsc_dir.mkdir(exist_ok=True)

  config_path = fsc_dir / "config.toml"

  if not config_path.exists():
    config_path.write_text(FscConfig().to_toml())
    console.print("[green]Created .fsc/config.toml[/green]")

  else:
    console.print("[yellow].fsc/config.toml already exists, skipping[/yellow]")

  prompt_path = fsc_dir / "PROMPT.md"

  if not prompt_path.exists():
    prompt_path.write_text("")
    console.print("[green]Created .fsc/PROMPT.md[/green]")

  else:
    console.print("[yellow].fsc/PROMPT.md already exists, skipping[/yellow]")

  console.print("\n[bold]Done![/bold] Set your API key:")
  console.print("  export DEEPSEEK_API_KEY=sk-...")
