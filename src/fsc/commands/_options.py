from pathlib import Path

import typer


class CliTyperArguments:
  DIRECTORY: Path | None = typer.Argument(
    None, help="Target directory (default: current directory)"
  )


class CliTyperOptions:
  # bool flags:
  DRY_RUN: bool = typer.Option(False, "--dry-run")
  FORCE: bool = typer.Option(
    False, "-f", "--force", help="Regenerate all specs, ignoring cache"
  )
  NO_PROGRESS: bool = typer.Option(
    False, "--no-progress", help="Disable progress bars during generation"
  )
  VERBOSE: bool = typer.Option(False, "--verbose")
  YES: bool = typer.Option(False, "-y", "--yes", help="Skip confirmation prompt")
  # list flags:
  EXTENSIONS: list[str] | None = typer.Option(
    None, "--extensions", help="File extensions to include"
  )
  EXCLUDE_DIRS: list[str] | None = typer.Option(None, "--exclude-dirs")
  EXCLUDE_FILES: list[str] | None = typer.Option(None, "--exclude-files")
  FILES: list[Path] | None = typer.Option(
    None, "--files", help="Files to generate specs for"
  )
  # path flags:
  OUTPUT_DIR: Path | None = typer.Option(None, "--output-dir")
  PROMPT_FILE: Path | None = typer.Option(None, "--prompt-file")
  # str flags:
  API_KEY: str | None = typer.Option(
    None, "--api-key", help="API key for the selected provider"
  )
  GEN_MODE: str | None = typer.Option(
    None,
    "--gen-mode",
    help="Generation mode: per-file (default), bulk, per-file-parallel",
  )
  LANGUAGE: str | None = typer.Option(None, "--language")
  MODEL: str | None = typer.Option(
    None, "--model", help="Model name for the selected provider"
  )
  PROVIDER: str | None = typer.Option(None, "--provider")
  OUTPUT_MODE: str | None = typer.Option(None, "--output-mode")
  # int flags:
  BATCH_SIZE: int | None = typer.Option(
    None, "--batch-size", help="Files per batch folder (batch output mode)"
  )
  CONCURRENCY: int | None = typer.Option(
    None, "-c", "--concurrency", help="Parallel requests for per-file mode (default: 3)"
  )
