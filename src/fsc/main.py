import importlib.metadata

import typer
from rich.console import Console

from fsc.commands.deinit import deinit_command
from fsc.commands.generate import generate_command
from fsc.commands.init import init_command
from fsc.commands.reinit import reinit_command


console = Console(log_path=False)


app = typer.Typer(
  help="FileSpecContractor - token-saving contracts for your codebase.",
  epilog="https://github.com/UmbrellaLeaf5/file_spec_contractor",
  invoke_without_command=True,
)


@app.callback()
def _version_callback(
  version: bool = typer.Option(
    False,
    "--version",
    help="Show version and exit",
    is_eager=True,
  ),
) -> None:
  if version:
    console.print(f"fsc {_get_version()}")
    raise typer.Exit()


def _get_version() -> str:
  try:
    return importlib.metadata.version("file-spec-contractor")

  except importlib.metadata.PackageNotFoundError:
    return "unknown"


app.command(
  name="generate",
  short_help="Generate .fsc.md specifications for project files.",
  help=(
    "Generate compact .fsc.md specifications for project source files.\n\n"
    "Modes:\n"
    "  bulk (default) - all files in a single LLM request for consistent,\n"
    "    cross-referenced specifications.\n"
    "  per-file (--force-per-file) - each file individually, sequential or\n"
    "    parallel (-c N).\n\n"
    "Output modes:\n"
    "  mirror (default) - preserve directory structure under output directory.\n"
    "  adjacent - save .fsc.md next to each source file.\n"
    "  batch - group specs into numbered folders (batch-N/) with encoded paths.\n\n"
    "Config priority: CLI > .fsc/config.toml > ~/.config/fsc/config.toml\n\n"
    "Examples:\n"
    "  fsc generate\n"
    "  fsc generate --file src/machine.py\n"
    "  fsc generate --extensions .py .kt\n"
    "  fsc generate --force-per-file -c 5\n"
    "  fsc generate --dry-run --verbose\n"
    "  fsc generate --output-mode adjacent"
  ),
)(generate_command)

app.command(
  name="init",
  short_help="Create .fsc/ directory with template config and prompt.",
  help=(
    "Initialize FileSpecContractor in the current directory.\n\n"
    "Creates .fsc/config.toml with default settings and .fsc/PROMPT.md\n"
    "pre-populated with the latest built-in prompt.\n\n"
    "All generate flags (--extensions, --language, --provider, etc.) can be\n"
    "used to customize the initial configuration.\n\n"
    "After init, set your API key and run fsc generate.\n\n"
    "Examples:\n"
    "  fsc init\n"
    "  fsc init --yes              # overwrite existing files\n"
    "  fsc init --extensions .py .kt --language ru\n"
    "  fsc init --provider deepseek"
  ),
)(init_command)

app.command(
  name="deinit",
  help=(
    "Remove .fsc/ and all generated .fsc.md files from the project tree.\n\n"
    "Examples:\n"
    "  fsc deinit\n"
    "  fsc deinit && fsc reinit  # clean start"
  ),
)(deinit_command)

app.command(
  name="reinit",
  help=(
    "deinit + init: remove all artifacts and recreate .fsc/ from scratch.\n\n"
    "Accepts all the same flags as init to customize the new config.\n\n"
    "Examples:\n"
    "  fsc reinit\n"
    "  fsc reinit --extensions .py .kt --language ru\n"
    "  fsc reinit --provider deepseek"
  ),
)(reinit_command)


def main() -> None:
  try:
    app()

  except KeyboardInterrupt as ex:
    console.print("\n[yellow]Interrupted by user. Shutting down.[/yellow]")
    raise typer.Exit(code=130) from ex


if __name__ == "__main__":
  main()
