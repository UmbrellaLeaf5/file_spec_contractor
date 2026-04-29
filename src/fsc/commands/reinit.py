from pathlib import Path

from fsc.commands._options import CliTyperArguments, CliTyperOptions
from fsc.commands.init import do_init
from fsc.config.loader import CLIConfigOverrides


def reinit_command(
  directory: Path | None = CliTyperArguments.DIRECTORY,
  # bool flags:
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
  """Remove all artifacts and recreate .fsc/ from scratch."""

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

  do_init(force=True, yes=yes, overrides=overrides, target_dir=directory)
