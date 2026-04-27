from pathlib import Path

import typer
from rich.console import Console

from fsc.config.loader import apply_cli_overrides
from fsc.config.schema import FSCConfig
from fsc.prompt_loader import builtin_prompt_text


console = Console()


def _do_init(yes: bool, cli_args: dict) -> None:
  fsc_dir = Path.cwd() / ".fsc"
  config_path = fsc_dir / "config.toml"

  if config_path.exists() and not yes:
    console.print(
      "[yellow]FileSpecContractor is already configured (.fsc/config.toml exists).\n"
      "Use --yes to overwrite or fsc reinit to recreate.[/yellow]"
    )
    return

  fsc_dir.mkdir(exist_ok=True)

  cfg = FSCConfig()
  cfg = apply_cli_overrides(cfg, cli_args)
  config_path.write_text(cfg.to_toml())
  console.print("[green]Created .fsc/config.toml[/green]")

  prompt_path = fsc_dir / "PROMPT.md"

  if not prompt_path.exists() or yes:
    prompt_path.write_text(builtin_prompt_text(cfg.output.language), encoding="utf-8")
    console.print("[green]Created .fsc/PROMPT.md[/green]")

  else:
    console.print("[yellow].fsc/PROMPT.md already exists, skipping[/yellow]")

  console.print("\n[bold]Done![/bold] Next steps:")
  console.print("  1. Set your API key (pick one):")
  console.print("     export OPEN_ROUTER_API_KEY=sk-or-v1-...")
  console.print("     or use --api-key flag: fsc generate --api-key sk-or-v1-...")
  console.print("     or create .env file with OPEN_ROUTER_API_KEY=...")
  console.print("  2. Generate specifications:")
  console.print("     fsc generate")
  console.print("  3. Or preview first:")
  console.print("     fsc generate --dry-run")


def init_command(
  yes: bool = typer.Option(
    False, "-y", "--yes", help="Skip confirmations, overwrite existing files"
  ),
  extensions: list[str] | None = typer.Option(
    None, "--extensions", help="File extensions to include"
  ),
  exclude_dirs: list[str] | None = typer.Option(None, "--exclude-dirs"),
  exclude_files: list[str] | None = typer.Option(None, "--exclude-files"),
  provider: str | None = typer.Option(None, "--provider"),
  output_mode: str | None = typer.Option(None, "--output-mode"),
  output_dir: Path | None = typer.Option(None, "--output-dir"),
  batch_size: int | None = typer.Option(
    None, "--batch-size", help="Files per batch folder (batch output mode)"
  ),
  prompt_file: Path | None = typer.Option(None, "--prompt-file"),
  language: str | None = typer.Option(None, "--language"),
  concurrency: int = typer.Option(
    1, "-c", "--concurrency", help="Parallel requests for per-file mode"
  ),
  force_per_file: bool = typer.Option(
    False, "--force-per-file", help="Force per-file generation instead of batch"
  ),
) -> None:
  """Create .fsc/ directory with template config and prompt."""

  cli_args = dict(
    extensions=extensions,
    exclude_dirs=exclude_dirs,
    exclude_files=exclude_files,
    provider=provider,
    output_mode=output_mode,
    output_dir=str(output_dir) if output_dir else None,
    batch_size=batch_size,
    prompt_file=str(prompt_file) if prompt_file else None,
    language=language,
    concurrency=concurrency,
    force_per_file=force_per_file,
  )

  _do_init(yes, cli_args)
