import shutil
from pathlib import Path

import typer

from fsc.commands._options import CliTyperArguments, CliTyperOptions
from fsc.config.loader import CLIConfigOverrides, apply_cli_overrides
from fsc.config.schemas import FSCConfig
from fsc.utils.console import console
from fsc.utils.fs import find_spec_files
from fsc.utils.prompt_loader import builtin_prompt_text


def init_command(
  directory: Path | None = CliTyperArguments.DIRECTORY,
  # bool flags:
  force: bool = CliTyperOptions.FORCE,
  yes: bool = CliTyperOptions.YES,
  # list flags:
  extensions: list[str] | None = CliTyperOptions.EXTENSIONS,
  exclude_dirs: list[str] | None = CliTyperOptions.EXCLUDE_DIRS,
  exclude_files: list[str] | None = CliTyperOptions.EXCLUDE_FILES,
  # path flags:
  output_dir: Path | None = CliTyperOptions.OUTPUT_DIR,
  prompt_file: Path | None = CliTyperOptions.PROMPT_FILE,
  # str flags:
  gen_mode: str | None = CliTyperOptions.GEN_MODE,
  provider: str | None = CliTyperOptions.PROVIDER,
  model: str | None = CliTyperOptions.MODEL,
  output_mode: str | None = CliTyperOptions.OUTPUT_MODE,
  language: str | None = CliTyperOptions.LANGUAGE,
  # int flags:
  batch_size: int | None = CliTyperOptions.BATCH_SIZE,
  concurrency: int | None = CliTyperOptions.CONCURRENCY,
) -> None:
  """Create .fsc/ directory with template config and prompt."""

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
    language=language,
    concurrency=concurrency,
    generation_mode=gen_mode,
  )

  do_init(force=force, yes=yes, overrides=overrides, target_dir=directory)


def _count_fsc_artifacts(root: Path) -> int:
  count = 0

  if (root / ".fsc").exists():
    count += 1

  count += len(find_spec_files(root))

  return count


def _remove_fsc_artifacts(root: Path) -> int:
  removed = 0
  fsc_dir = root / ".fsc"

  if fsc_dir.exists():
    shutil.rmtree(fsc_dir)
    removed += 1

  for spec in find_spec_files(root):
    spec.unlink()
    removed += 1

  return removed


def _confirm_destructive(yes: bool) -> None:
  if yes:
    return

  typer.confirm(
    "This will remove all existing .fsc/ configuration and *.fsc.md files. Continue?",
    abort=True,
  )


def do_init(
  force: bool,
  yes: bool,
  overrides: CLIConfigOverrides,
  target_dir: Path | None = None,
) -> None:
  root = Path(target_dir).resolve() if target_dir else Path.cwd()
  root.mkdir(parents=True, exist_ok=True)
  fsc_dir = root / ".fsc"
  config_path = fsc_dir / "config.toml"

  if config_path.exists() and not force:
    console.print(
      "[yellow]FileSpecContractor is already configured (.fsc/config.toml exists).\n"
      "Use --force to recreate from scratch.[/yellow]"
    )
    return

  if force:
    artifact_count = _count_fsc_artifacts(root)

    if artifact_count > 0:
      _confirm_destructive(yes)
      removed = _remove_fsc_artifacts(root)

      console.print(
        f"[green]Removed {removed} existing artifact"
        f"{'s' if removed != 1 else ''}.[/green]"
      )

  fsc_dir.mkdir(parents=True, exist_ok=True)

  cfg = FSCConfig()

  cfg = apply_cli_overrides(cfg, overrides)

  config_path.write_text(cfg.to_toml())
  console.print("[green]Created .fsc/config.toml[/green]")

  prompt_path = fsc_dir / "PROMPT.md"
  prompt_path.write_text(builtin_prompt_text(cfg.output.language), encoding="utf-8")
  console.print("[green]Created .fsc/PROMPT.md[/green]")

  console.print("\n[bold]Done![/bold] Next steps:")
  console.print("  1. Set your API key (pick one):")
  console.print("     export OPEN_ROUTER_API_KEY=sk-or-v1-...")
  console.print("     or use --api-key flag: fsc generate --api-key sk-or-v1-...")
  console.print("     or create .env file with OPEN_ROUTER_API_KEY=...")
  console.print("  2. Generate specifications:")
  console.print("     fsc generate")
  console.print("  3. Or preview first:")
  console.print("     fsc generate --dry-run")
