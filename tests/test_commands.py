from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from fsc.main import app


runner = CliRunner()


def test_generate_without_init(tmp_path: Path, monkeypatch):
  monkeypatch.chdir(tmp_path)

  result = runner.invoke(app, ["generate", "--help"])

  assert result.exit_code == 0


def test_generate_missing_api_key(tmp_path: Path, monkeypatch):
  monkeypatch.chdir(tmp_path)
  monkeypatch.delenv("OPEN_ROUTER_API_KEY", raising=False)
  monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

  (tmp_path / "app.py").write_text("x = 1")

  runner.invoke(app, ["init", "-y"])

  result = runner.invoke(app, ["generate", "--files", str(tmp_path / "app.py")])

  assert result.exit_code != 0
  assert "API key not found" in result.stdout


def test_generate_negative_concurrency(tmp_path: Path, monkeypatch):
  monkeypatch.chdir(tmp_path)

  result = runner.invoke(app, ["generate", "--concurrency", "-1"])

  assert result.exit_code != 0


def test_generate_zero_concurrency(tmp_path: Path, monkeypatch):
  monkeypatch.chdir(tmp_path)

  result = runner.invoke(app, ["generate", "--concurrency", "0"])

  assert result.exit_code != 0


def test_generate_parallel_without_concurrency(tmp_path: Path, monkeypatch):
  monkeypatch.chdir(tmp_path)
  monkeypatch.setenv("OPEN_ROUTER_API_KEY", "test-key")

  (tmp_path / "app.py").write_text("x = 1")

  runner.invoke(app, ["init", "-y"])

  result = runner.invoke(app, ["generate", "--gen-mode", "per-file-parallel"])

  assert result.exit_code != 0
  assert "requires --concurrency" in result.stdout


def test_init_twice_without_yes(tmp_path: Path, monkeypatch):
  monkeypatch.chdir(tmp_path)

  runner.invoke(app, ["init", "-y"])
  result = runner.invoke(app, ["init"])

  assert "already configured" in result.stdout.lower()


def test_reinit_full_cycle(tmp_path: Path, monkeypatch):
  monkeypatch.chdir(tmp_path)

  runner.invoke(app, ["init", "-y"])
  (tmp_path / "spec.py.fsc.md").write_text("stale")

  result = runner.invoke(app, ["reinit", "-y"])

  assert result.exit_code == 0
  assert (tmp_path / ".fsc" / "config.toml").exists()
  assert not (tmp_path / "spec.py.fsc.md").exists()


def test_reinit_preserves_custom_config(tmp_path: Path, monkeypatch):
  monkeypatch.chdir(tmp_path)

  result = runner.invoke(
    app, ["reinit", "-y", "--extensions", ".py", "--extensions", ".kt"]
  )

  assert result.exit_code == 0

  content = (tmp_path / ".fsc" / "config.toml").read_text()

  assert '".py"' in content
  assert '".kt"' in content


def test_deinit_removes_fsc_dir(tmp_path: Path, monkeypatch):
  monkeypatch.chdir(tmp_path)

  runner.invoke(app, ["init", "-y"])
  assert (tmp_path / ".fsc").exists()

  runner.invoke(app, ["deinit", "-y"])

  assert not (tmp_path / ".fsc").exists()


def test_deinit_removes_specs(tmp_path: Path, monkeypatch):
  monkeypatch.chdir(tmp_path)

  runner.invoke(app, ["init", "-y"])
  spec = tmp_path / "app.py.fsc.md"
  spec.write_text("stale")

  runner.invoke(app, ["deinit", "-y"])

  assert not spec.exists()
  assert not (tmp_path / ".fsc").exists()


def test_deinit_idempotent(tmp_path: Path, monkeypatch):
  monkeypatch.chdir(tmp_path)

  runner.invoke(app, ["deinit", "-y"])
  result = runner.invoke(app, ["deinit", "-y"])

  assert result.exit_code == 0


def test_generate_warns_bulk_unreliable(tmp_path: Path, monkeypatch):
  monkeypatch.chdir(tmp_path)
  monkeypatch.setenv("OPEN_ROUTER_API_KEY", "test-key")

  (tmp_path / "app.py").write_text("x = 1")
  runner.invoke(app, ["init", "-y"])

  dummy_bulk = "## SPEC: app.py\n# app.py\n\n## Purpose\nGenerated.\n"

  with patch(
    "fsc.providers.openrouter.OpenRouterProvider.generate", return_value=dummy_bulk
  ):
    result = runner.invoke(
      app, ["generate", "--gen-mode", "bulk", "--files", str(tmp_path / "app.py")]
    )

  assert result.exit_code == 0
  assert "bulk mode can be unreliable" in result.stdout


def test_generate_warns_concurrency_in_bulk(tmp_path: Path, monkeypatch):
  monkeypatch.chdir(tmp_path)
  monkeypatch.setenv("OPEN_ROUTER_API_KEY", "test-key")

  (tmp_path / "app.py").write_text("x = 1")
  runner.invoke(app, ["init", "-y"])

  dummy_bulk = "## SPEC: app.py\n# app.py\n\n## Purpose\nGenerated.\n"

  with patch(
    "fsc.providers.openrouter.OpenRouterProvider.generate", return_value=dummy_bulk
  ):
    result = runner.invoke(
      app,
      [
        "generate", "--gen-mode", "bulk", "-c", "5",
        "--files", str(tmp_path / "app.py"),
      ],
    )

  assert result.exit_code == 0
  assert "has no effect in bulk mode" in result.stdout


def test_generate_warns_batch_size_without_batch_mode(tmp_path: Path, monkeypatch):
  monkeypatch.chdir(tmp_path)
  monkeypatch.setenv("OPEN_ROUTER_API_KEY", "test-key")

  (tmp_path / "app.py").write_text("x = 1")
  runner.invoke(app, ["init", "-y"])

  dummy_spec = "# app.py\n\n## Purpose\nGenerated.\n"

  with patch(
    "fsc.providers.openrouter.OpenRouterProvider.generate", return_value=dummy_spec
  ):
    result = runner.invoke(
      app, ["generate", "--batch-size", "30", "--files", str(tmp_path / "app.py")]
    )

  assert result.exit_code == 0
  assert "has no effect unless" in result.stdout


def test_generate_warns_non_en_language(tmp_path: Path, monkeypatch):
  monkeypatch.chdir(tmp_path)
  monkeypatch.setenv("OPEN_ROUTER_API_KEY", "test-key")

  (tmp_path / "app.py").write_text("x = 1")
  runner.invoke(app, ["init", "-y", "--language", "ru"])

  dummy_spec = "# app.py\n\n## Purpose\nGenerated.\n"

  with patch(
    "fsc.providers.openrouter.OpenRouterProvider.generate", return_value=dummy_spec
  ):
    result = runner.invoke(
      app, ["generate", "--files", str(tmp_path / "app.py")]
    )

  assert result.exit_code == 0
  assert "may not be supported by all models" in result.stdout
