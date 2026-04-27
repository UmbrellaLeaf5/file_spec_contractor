import os
from pathlib import Path

import typer
from rich.console import Console

from fsc.config.loader import apply_cli_overrides, load_merged_config
from fsc.prompt_loader import load_prompt, resolve_prompt_path
from fsc.providers.deepseek import DeepSeekProvider
from fsc.providers.openrouter import OpenRouterProvider
from fsc.spec.generator import generate_for_files
from fsc.utils.env import load_dotenv
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
  model: str | None = typer.Option(
    None, "--model", help="Model name for the selected provider"
  ),
  output_mode: str | None = typer.Option(None, "--output-mode"),
  output_dir: Path | None = typer.Option(None, "--output-dir"),
  batch_size: int | None = typer.Option(
    None, "--batch-size", help="Files per batch folder (batch output mode)"
  ),
  prompt_file: Path | None = typer.Option(None, "--prompt-file"),
  concurrency: int | None = typer.Option(
    None, "-c", "--concurrency", help="Parallel requests for per-file mode (default: 3)"
  ),
  force_per_file: bool | None = typer.Option(
    None, "--force-per-file", help="Force per-file generation instead of batch"
  ),
  api_key: str | None = typer.Option(
    None, "--api-key", help="API key for the selected provider"
  ),
  force: bool = typer.Option(
    False, "-f", "--force", help="Regenerate all specs, ignoring cache"
  ),
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
    model=model,
    output_mode=output_mode,
    output_dir=str(output_dir) if output_dir else None,
    batch_size=batch_size,
    prompt_file=str(prompt_file) if prompt_file else None,
    concurrency=concurrency,
    force_per_file=force_per_file,
  )

  cfg = apply_cli_overrides(cfg, cli_args)

  if verbose:
    console.log("Using configuration:")
    console.log(cfg.to_dict())

  prompt_path = resolve_prompt_path(project_root, cfg, cli_prompt=cfg.prompt.file)
  prompt_text = load_prompt(prompt_path, cfg.output.language)

  lang = cfg.output.language

  if lang == "ru" and "русс" not in prompt_text.lower():
    console.print(
      "[yellow]Warning: language is set to 'ru' but PROMPT.md does not appear "
      "to be in Russian. Run `fsc init --language ru --yes` to regenerate.[/yellow]"
    )

  if lang == "en" and "engl" not in prompt_text.lower():
    console.print(
      "[yellow]Warning: language is set to 'en' but PROMPT.md does not appear "
      "to be in English. Run `fsc init --language en --yes` to regenerate.[/yellow]"
    )

  provider_name = cfg.api.provider
  dotenv = load_dotenv(project_root)

  if provider_name == "deepseek":
    env_key = os.environ.get("DEEPSEEK_API_KEY", "")
    resolved = api_key or env_key or dotenv.get("DEEPSEEK_API_KEY", "")

    if not resolved:
      console.print(
        "[red]DeepSeek API key not found. "
        "Use --api-key, set DEEPSEEK_API_KEY, or add to .env[/red]"
      )
      raise typer.Exit(code=2)

    provider_client = DeepSeekProvider(api_key=resolved)

    if cfg.api.model:
      provider_client.model = cfg.api.model

  elif provider_name == "openrouter":
    env_key = os.environ.get("OPEN_ROUTER_API_KEY", "")
    resolved = api_key or env_key or dotenv.get("OPEN_ROUTER_API_KEY", "")

    if not resolved:
      console.print(
        "[red]OpenRouter API key not found. "
        "Use --api-key, set OPEN_ROUTER_API_KEY, or add to .env[/red]"
      )
      raise typer.Exit(code=2)

    provider_client = OpenRouterProvider(api_key=resolved)

    if cfg.api.model:
      provider_client.model = cfg.api.model

  else:
    console.print(f"[red]Unknown provider: {provider_name}[/red]")
    raise typer.Exit(code=2)

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

  mode = "per-file" if cfg.runtime.force_per_file else "bulk"

  if dry_run and not cfg.runtime.force_per_file:
    console.print(
      "[yellow]Bulk mode is not compatible with --dry-run. "
      "Switching to per-file dry run.[/yellow]"
    )
    cfg.runtime.force_per_file = True
    mode = "per-file"

  console.log(
    f"Found {len(targets)} files. Mode: {mode}. Concurrency: {cfg.runtime.concurrency}."
  )

  try:
    generate_for_files(
      targets,
      prompt_text,
      provider_client,
      cfg,
      project_root=project_root,
      dry_run=dry_run,
      concurrency=cfg.runtime.concurrency,
      force_per_file=cfg.runtime.force_per_file,
      force=force,
    )

  except KeyboardInterrupt:
    console.print("\n[yellow]Interrupted. Any completed specs have been saved.[/yellow]")
