import os
from pathlib import Path

import typer

from fsc.commands._options import CliTyperOptions
from fsc.config.enums import GenerationMode, OutputMode
from fsc.config.loader import CLIConfigOverrides, apply_cli_overrides, load_merged_config
from fsc.providers.factory import get_provider_info, provider_context
from fsc.spec.generator import generate_for_files
from fsc.utils.console import console
from fsc.utils.env import load_dotenv
from fsc.utils.fs import scan_files
from fsc.utils.prompt_loader import load_prompt, resolve_prompt_path


def generate_command(
  # bool flags:
  dry_run: bool = CliTyperOptions.DRY_RUN,
  force: bool = CliTyperOptions.FORCE,
  no_progress: bool = CliTyperOptions.NO_PROGRESS,
  verbose: bool = CliTyperOptions.VERBOSE,
  # list flags:
  extensions: list[str] | None = CliTyperOptions.EXTENSIONS,
  exclude_dirs: list[str] | None = CliTyperOptions.EXCLUDE_DIRS,
  exclude_files: list[str] | None = CliTyperOptions.EXCLUDE_FILES,
  files: list[Path] | None = CliTyperOptions.FILES,
  # path flags:
  output_dir: Path | None = CliTyperOptions.OUTPUT_DIR,
  prompt_file: Path | None = CliTyperOptions.PROMPT_FILE,
  # str flags:
  api_key: str | None = CliTyperOptions.API_KEY,
  gen_mode: str | None = CliTyperOptions.GEN_MODE,
  model: str | None = CliTyperOptions.MODEL,
  provider: str | None = CliTyperOptions.PROVIDER,
  output_mode: str | None = CliTyperOptions.OUTPUT_MODE,
  # int flags:
  batch_size: int | None = CliTyperOptions.BATCH_SIZE,
  concurrency: int | None = CliTyperOptions.CONCURRENCY,
) -> None:
  """Generate .fsc.md specifications for project files."""

  project_root = Path.cwd()
  cfg = load_merged_config(project_root)

  overrides = CLIConfigOverrides(
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
    generation_mode=gen_mode,
    no_progress=no_progress,
  )

  cfg = apply_cli_overrides(cfg, overrides)

  if verbose:
    console.log("Using configuration:")
    console.log(cfg.to_dict())

  prompt_path = resolve_prompt_path(project_root, cfg, cli_prompt=cfg.prompt.file)
  prompt_text = load_prompt(prompt_path, cfg.output.language)

  lang = cfg.output.language

  _LANG_KEYWORDS = {"ru": "русс", "en": "engl"}

  if lang in _LANG_KEYWORDS and _LANG_KEYWORDS[lang] not in prompt_text.lower():
    console.print(
      f"[yellow]Warning: language is set to '{lang}' but PROMPT.md does not appear "
      f"to be in {lang.upper()}. "
      f"Run `fsc init --language {lang} --yes` to regenerate.[/yellow]"
    )

  if lang != "en":
    console.print(
      f"[yellow]Warning: language '{lang}' may not be supported by all models. "
      "Output may still be in English.[/yellow]"
    )

  provider_name = cfg.api.provider
  provider_info = get_provider_info(provider_name)

  if provider_info is None:
    console.print(f"[red]Unknown provider: {provider_name}[/red]")
    raise typer.Exit(code=2)

  dotenv = load_dotenv(project_root)
  env_key = provider_info["env_key"]
  env_value = os.environ.get(env_key, "")
  resolved = api_key or env_value or dotenv.get(env_key, "")

  if not resolved:
    console.print(
      f"[red]{provider_info['display']} API key not found. "
      f"Use --api-key, set {env_key}, or add to .env[/red]"
    )
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

  if dry_run and cfg.runtime.generation_mode == GenerationMode.bulk:
    console.print(
      "[yellow]Bulk mode is not compatible with --dry-run. "
      "Switching to per-file dry run.[/yellow]"
    )
    cfg.runtime.generation_mode = GenerationMode.per_file

  if not dry_run and cfg.runtime.generation_mode == GenerationMode.bulk:
    console.print(
      "[yellow]Warning: bulk mode can be unreliable - models may skip files, "
      "sections, or prompt instructions. Per-file mode is recommended.[/yellow]"
    )

  if (
    cfg.runtime.generation_mode == GenerationMode.per_file_parallel
    and concurrency is None
  ):
    console.print(
      "[red]per-file-parallel generation mode requires --concurrency / -c flag.[/red]"
    )

    raise typer.Exit(code=2)

  if concurrency is not None and cfg.runtime.generation_mode == GenerationMode.bulk:
    console.print(
      "[yellow]Warning: --concurrency / -c has no effect in bulk mode. "
      "Use --gen-mode per-file or per-file-parallel.[/yellow]"
    )

  if batch_size is not None and cfg.output.output_mode != OutputMode.batch:
    console.print(
      "[yellow]Warning: --batch-size has no effect unless "
      "--output-mode batch is also set.[/yellow]"
    )

  console.log(
    f"Found {len(targets)} files. Mode: {cfg.runtime.generation_mode.value}."
    f" Concurrency: {cfg.runtime.concurrency}."
  )

  try:
    with provider_context(provider_name, resolved, cfg.api.model) as provider_client:
      generate_for_files(
        targets,
        prompt_text,
        provider_client,
        cfg,
        project_root=project_root,
        dry_run=dry_run,
        concurrency=cfg.runtime.concurrency,
        gen_mode=cfg.runtime.generation_mode,
        force=force,
      )

  except KeyboardInterrupt:
    console.print("\n[yellow]Interrupted. Any completed specs have been saved.[/yellow]")

  except RuntimeError:
    raise typer.Exit(code=2) from None
