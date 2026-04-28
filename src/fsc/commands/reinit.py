from pathlib import Path

import typer

from fsc.commands.init import _do_init


def reinit_command(
  directory: Path | None = typer.Argument(
    None, help="Target directory (default: current directory)"
  ),
  yes: bool = typer.Option(
    False, "-y", "--yes", help="Skip confirmation prompts"
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
  prompt_file: Path | None = typer.Option(None, "--prompt-file"),
  language: str | None = typer.Option(None, "--language"),
  concurrency: int | None = typer.Option(
    None, "-c", "--concurrency", help="Parallel requests for per-file mode (default: 3)"
  ),
  gen_mode: str | None = typer.Option(
    None, "--gen-mode", help="Generation mode: bulk (default), per-file, per-file-parallel"
  ),
) -> None:
  """Remove all artifacts and recreate .fsc/ from scratch."""

  cli_args = dict(
    extensions=extensions,
    exclude_dirs=exclude_dirs,
    exclude_files=exclude_files,
    provider=provider,
    model=model,
    output_mode=output_mode,
    output_dir=str(output_dir) if output_dir else None,
    prompt_file=str(prompt_file) if prompt_file else None,
    language=language,
    concurrency=concurrency,
    generation_mode=gen_mode,
  )

  _do_init(True, yes, cli_args, directory)
