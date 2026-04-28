import os
from pathlib import Path

import pytest
from fsc.config.enums import GenerationMode
from fsc.config.schemas import FSCConfig
from fsc.providers.openrouter import OpenRouterProvider
from fsc.spec.generator import generate_for_files
from fsc.utils.env import load_dotenv
from fsc.utils.prompt_loader import load_prompt


def _get_openrouter_key() -> str:
  key = os.environ.get("OPEN_ROUTER_API_KEY", "")

  if key:
    return key

  dotenv = load_dotenv(Path.cwd())

  return dotenv.get("OPEN_ROUTER_API_KEY", "")


def test_openrouter_generate_single_file(tmp_path: Path):
  api_key = _get_openrouter_key()

  if not api_key:
    pytest.skip("OPEN_ROUTER_API_KEY not set in env or .env")

  src = tmp_path / "app.py"
  src.write_text(
    "def greet(name: str) -> str:\n"
    '    return f"Hello, {name}!"\n\n'
    "class Calculator:\n"
    "    def add(self, a: int, b: int) -> int:\n"
    "        return a + b\n"
  )

  cfg = FSCConfig()
  cfg.output.output_dir = str(tmp_path / ".fsc" / "specs")
  prompt_text = load_prompt(None, "en")
  provider = OpenRouterProvider(api_key=api_key)

  results = generate_for_files(
    [src],
    prompt_text,
    provider,
    cfg,
    project_root=tmp_path,
    concurrency=1,
    gen_mode=GenerationMode.per_file,
  )

  assert len(results) == 1
  spec_path = results[0]
  assert spec_path.exists()
  content = spec_path.read_text(encoding="utf-8")
  assert len(content) > 200  # noqa: PLR2004
  assert "greet" in content or "Calculator" in content


def test_openrouter_generate_batch(tmp_path: Path):
  api_key = _get_openrouter_key()

  if not api_key:
    pytest.skip("OPEN_ROUTER_API_KEY not set in env or .env")

  app = tmp_path / "app.py"
  app.write_text("def greet(name: str) -> str:\n    return f'Hello, {name}!'\n")

  utils = tmp_path / "utils.py"
  utils.write_text("def add(a: int, b: int) -> int:\n    return a + b\n")

  cfg = FSCConfig()
  cfg.output.output_dir = str(tmp_path / ".fsc" / "specs")
  prompt_text = load_prompt(None, "en")
  provider = OpenRouterProvider(api_key=api_key)

  results = generate_for_files(
    [app, utils],
    prompt_text,
    provider,
    cfg,
    project_root=tmp_path,
    concurrency=1,
    gen_mode=GenerationMode.bulk,
  )

  assert len(results) == 2  # noqa: PLR2004

  for spec_path in results:
    assert spec_path.exists()
    content = spec_path.read_text(encoding="utf-8")
    assert len(content) > 100  # noqa: PLR2004
