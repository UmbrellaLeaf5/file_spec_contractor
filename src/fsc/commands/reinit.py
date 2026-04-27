from pathlib import Path

import typer

from fsc.commands.deinit import deinit_command
from fsc.commands.init import _do_init


def reinit_command(
  directory: Path | None = typer.Argument(
    None, help="Target directory (default: current directory)"
  ),
  yes: bool = typer.Option(
    False, "-y", "--yes", help="Skip confirmations, overwrite existing files"
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
  force_per_file: bool | None = typer.Option(
    None, "--force-per-file", help="Force per-file generation instead of batch"
  ),
) -> None:
  """deinit + init: remove all and recreate .fsc/ from scratch."""

  deinit_command(directory=directory)
  print()

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
    force_per_file=force_per_file,
  )

  _do_init(True, cli_args, directory)
