import os
import shutil
from pathlib import Path


WARNING = """
[yellow]Warning: Scala development environment detected.

The `fsc` command may conflict with the Scala Fast Offline Compiler (fsc).

We strongly recommend using the full command name instead:

  file-spec-contractor init
  file-spec-contractor generate
  file-spec-contractor --help

Or with underscore:

  file_spec_contractor init
  file_spec_contractor generate
[/yellow]"""


def detect() -> bool:
  scala_env_vars = {"SCALA_HOME", "SCALA_VERSION", "SCALAC_HOME"}

  if scala_env_vars & set(os.environ):
    return True

  if shutil.which("scalac") or shutil.which("scala"):
    return True

  scala_paths = [
    Path("/usr/local/scala"),
    Path("/opt/scala"),
    Path.home() / ".sdkman",
    Path("C:/Program Files/Scala"),
    Path("C:/Program Files (x86)/Scala"),
  ]

  for p in scala_paths:
    if p.exists():
      return True

  cwd = Path.cwd()

  if (cwd / "build.sbt").exists():
    return True

  try:
    return bool(list(cwd.rglob("*.scala")))

  except Exception:
    return False
