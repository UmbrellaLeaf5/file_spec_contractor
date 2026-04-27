import os
import time
from pathlib import Path

import pytest
from fsc.main import app
from fsc.utils.env import load_dotenv
from typer.testing import CliRunner


runner = CliRunner()
_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _get_api_key() -> str:
  key = os.environ.get("OPEN_ROUTER_API_KEY", "")

  if key:
    return key

  return load_dotenv(_PROJECT_ROOT).get("OPEN_ROUTER_API_KEY", "")


def test_full_pipeline_dry_run(tmp_path: Path, monkeypatch):
  monkeypatch.chdir(tmp_path)
  monkeypatch.setenv("OPEN_ROUTER_API_KEY", "test-key")

  (tmp_path / "app.py").write_text(
    'def greet(name: str) -> str:\n    return f"Hello, {name}!"\n'
  )

  runner.invoke(app, ["init", "-y"])

  result = runner.invoke(
    app,
    ["generate", "--file", str(tmp_path / "app.py"), "--dry-run", "--verbose"],
  )

  assert "Found 1 files" in result.stdout
  assert "bulk" in result.stdout.lower()


def test_full_pipeline_cache(tmp_path: Path, monkeypatch):
  api_key = _get_api_key()

  if not api_key:
    pytest.skip("OPEN_ROUTER_API_KEY not set")

  monkeypatch.chdir(tmp_path)
  monkeypatch.setenv("OPEN_ROUTER_API_KEY", api_key)

  src = tmp_path / "app.py"
  src.write_text('def greet(name: str) -> str:\n    return f"Hello, {name}!"\n')

  runner.invoke(app, ["init", "-y"])

  first = runner.invoke(
    app,
    ["generate", "--file", str(src), "--force-per-file"],
  )

  assert first.exit_code == 0

  time.sleep(0.1)

  second = runner.invoke(
    app,
    ["generate", "--file", str(src), "--force-per-file"],
  )

  assert second.exit_code == 0
  assert "Skipping" in second.stdout or "up to date" in second.stdout


def test_full_pipeline_force(tmp_path: Path, monkeypatch):
  api_key = _get_api_key()

  if not api_key:
    pytest.skip("OPEN_ROUTER_API_KEY not set")

  monkeypatch.chdir(tmp_path)
  monkeypatch.setenv("OPEN_ROUTER_API_KEY", api_key)

  (tmp_path / "app.py").write_text(
    'def greet(name: str) -> str:\n    return f"Hello, {name}!"\n'
  )

  runner.invoke(app, ["init", "-y"])

  first = runner.invoke(
    app,
    ["generate", "--file", str(tmp_path / "app.py"), "--force-per-file"],
  )

  assert first.exit_code == 0

  forced = runner.invoke(
    app,
    ["generate", "--file", str(tmp_path / "app.py"), "--force-per-file", "-f"],
  )

  assert forced.exit_code == 0
  assert "Generating" in forced.stdout or "generating" in forced.stdout.lower()


def test_generate_help_shows_batch_mode(tmp_path: Path, monkeypatch):
  monkeypatch.chdir(tmp_path)

  result = runner.invoke(app, ["generate", "--help"])

  assert result.exit_code == 0
  assert "bulk" in result.stdout.lower()


def test_init_help_shows_examples(tmp_path: Path, monkeypatch):
  monkeypatch.chdir(tmp_path)

  result = runner.invoke(app, ["init", "--help"])

  assert result.exit_code == 0
  assert "examples" in result.stdout.lower()
