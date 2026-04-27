import os
from pathlib import Path

import typer
from rich.console import Console

from fsc.config.loader import apply_cli_overrides, load_merged_config
from fsc.prompt_loader import load_prompt, resolve_prompt_path
from fsc.providers.deepseek import DeepSeekProvider
from fsc.spec.generator import generate_for_files
from fsc.utils.fs import scan_files


console = Console()


def generate_command(
  files: list[Path] | None = typer.Option(
    None, "--file", help="Files to generate specs for"
  ),
  extensions: list[str] | None = typer.Option(
    None, "--extensions", help="File extensions to include"
  ),
  exclude_dirs: list[str] | None = typer.Option(None, "--exclude-dirs"),
  exclude_files: list[str] | None = typer.Option(None, "--exclude-files"),
  provider: str | None = typer.Option(None, "--provider"),
  output_mode: str | None = typer.Option(None, "--output-mode"),
  output_dir: Path | None = typer.Option(None, "--output-dir"),
  prompt_file: Path | None = typer.Option(None, "--prompt-file"),
  language: str | None = typer.Option(None, "--language"),
  dry_run: bool = typer.Option(False, "--dry-run"),
  verbose: bool = typer.Option(False, "--verbose"),
) -> None:
  """Generate .fsc.md specifications for project files."""

  project_root = Path.cwd()
  cfg = load_merged_config(project_root)

  cli_args = dict(
    extensions=extensions,
    exclude_dirs=exclude_dirs,
    exclude_files=exclude_files,
    provider=provider,
    output_mode=output_mode,
    output_dir=str(output_dir) if output_dir else None,
    prompt_file=str(prompt_file) if prompt_file else None,
    language=language,
  )

  cfg = apply_cli_overrides(cfg, cli_args)

  if verbose:
    console.log("Using configuration:")
    console.log(cfg.to_dict())

  prompt_path = resolve_prompt_path(project_root, cfg, cli_prompt=cfg.prompt.file)
  prompt_text = load_prompt(prompt_path)

  api_key = os.environ.get("DEEPSEEK_API_KEY") or cfg.api.deepseek_api_key

  if not api_key:
    console.print(
      "[red]DeepSeek API key not found. "
      "Set DEEPSEEK_API_KEY or add api.deepseek_api_key to config.[/red]"
    )

    raise typer.Exit(code=2)

  provider_client = DeepSeekProvider(api_key=api_key)

  if files:
    targets = list(files)

  else:
    targets = scan_files(
      project_root,
      extensions=cfg.project.extensions,
      exclude_dirs=cfg.project.exclude_dirs,
      exclude_files=cfg.project.exclude_files,
    )

  if not targets:
    console.print("[yellow]No files found to process.[/yellow]")
    raise typer.Exit()

  results = generate_for_files(
    targets,
    prompt_text,
    provider_client,
    cfg,
    project_root=project_root,
    dry_run=dry_run,
  )

  console.print(f"[green]Done. Processed {len(results)} files.[/green]")
