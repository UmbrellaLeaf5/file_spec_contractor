from fsc.commands.deinit import deinit_command
from fsc.commands.init import init_command


def reinit_command() -> None:
  """deinit + init: remove all and recreate .fsc/ again."""

  deinit_command()
  print()
  init_command()
