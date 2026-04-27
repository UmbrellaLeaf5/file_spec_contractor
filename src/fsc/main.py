import typer

from fsc.commands.deinit import deinit_command
from fsc.commands.generate import generate_command
from fsc.commands.init import init_command
from fsc.commands.reinit import reinit_command


app = typer.Typer(
  help="FileSpecContractor - token-saving contracts for your codebase.",
  epilog="hhttps://github.com/UmbrellaLeaf5/file_spec_contractor",
)

app.command(
  name="generate",
  short_help="Generate .fsc.md specifications for project files.",
  help=(
    "Generate compact .fsc.md specifications for project source files.\n\n"
    "Modes:\n"
    "  batch (default) - all files in a single LLM request for consistent,\n"
    "    cross-referenced specifications.\n"
    "  per-file (--force-per-file) - each file individually, sequential or\n"
    "    parallel (-c N).\n\n"
    "Output modes:\n"
    "  mirror (default) - preserve directory structure under output directory.\n"
    "  adjacent - save .fsc.md next to each source file.\n\n"
    "Config priority: CLI > .fsc/config.toml > ~/.config/fsc/config.toml\n\n"
    "Examples:\n"
    "  fsc generate\n"
    "  fsc generate --file src/machine.py\n"
    "  fsc generate --extensions .py .kt --language ru\n"
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
    "After init, set your API key and run fsc generate.\n\n"
    "Examples:\n"
    "  fsc init\n"
    "  fsc init --yes          # overwrite existing files"
  ),
)(init_command)

app.command(name="deinit")(deinit_command)
app.command(name="reinit")(reinit_command)


def main() -> None:
  app()


if __name__ == "__main__":
  main()
