from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn

from fsc.utils.console import console


def make_spinner(description: str) -> Progress:
  """Indeterminate spinner for waiting on LLM responses."""

  return Progress(
    SpinnerColumn(),
    TextColumn(f"[progress.description]{description}"),
    console=console,
    transient=True,
  )


def make_file_progress(total: int, description: str) -> Progress:
  """Deterministic bar: description  27% ████░░░░  12/45."""

  return Progress(
    TextColumn(f"[progress.description]{description}"),
    BarColumn(),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    TextColumn("{task.completed}/{task.total}"),
    console=console,
  )
