from pathlib import Path

from fsc.config.schema import FSCConfig
from fsc.utils.fs import (
  _encode_path,
  is_spec_fresh,
  resolve_output_path,
  write_spec_atomic,
)


def test_resolve_output_path_adjacent(tmp_path: Path):
  src = tmp_path / "src" / "app.py"
  src.parent.mkdir(parents=True, exist_ok=True)

  cfg = FSCConfig()
  cfg.output.output_mode = "adjacent"

  result = resolve_output_path(src, tmp_path, cfg)
  assert result == tmp_path / "src" / "app.py.fsc.md"


def test_resolve_output_path_mirror(tmp_path: Path):
  src = tmp_path / "src" / "app.py"
  src.parent.mkdir(parents=True, exist_ok=True)

  cfg = FSCConfig()
  cfg.output.output_mode = "mirror"
  cfg.output.output_dir = str(tmp_path / ".fsc" / "specs")

  result = resolve_output_path(src, tmp_path, cfg)
  assert result == tmp_path / ".fsc" / "specs" / "src" / "app.py.fsc.md"


def test_resolve_output_path_batch(tmp_path: Path):
  src = tmp_path / "src" / "app.py"
  src.parent.mkdir(parents=True, exist_ok=True)

  cfg = FSCConfig()
  cfg.output.output_mode = "batch"
  cfg.output.output_dir = str(tmp_path / ".fsc" / "batches")
  cfg.output.batch_size = 50

  result = resolve_output_path(src, tmp_path, cfg, file_index=0)
  assert result == tmp_path / ".fsc" / "batches" / "batch-1" / "src__app.py.fsc.md"


def test_resolve_output_path_batch_custom_size(tmp_path: Path):
  cfg = FSCConfig()
  cfg.output.output_mode = "batch"
  cfg.output.output_dir = str(tmp_path / ".fsc" / "batches")
  cfg.output.batch_size = 10

  paths = []

  for i in range(25):
    src = tmp_path / f"file_{i}.py"
    src.write_text("pass")
    result = resolve_output_path(src, tmp_path, cfg, file_index=i)
    paths.append(result)

  folders = {p.parent.name for p in paths}

  assert folders == {"batch-1", "batch-2", "batch-3"}
  assert len([p for p in paths if p.parent.name == "batch-1"]) == 10  # noqa: PLR2004
  assert len([p for p in paths if p.parent.name == "batch-2"]) == 10  # noqa: PLR2004
  assert len([p for p in paths if p.parent.name == "batch-3"]) == 5  # noqa: PLR2004


def test_write_spec_atomic_creates_parents(tmp_path: Path):
  path = tmp_path / "a" / "b" / "c" / "file.py.fsc.md"
  write_spec_atomic(path, "content")

  assert path.exists()
  assert path.read_text() == "content"


def test_write_spec_atomic_overwrites(tmp_path: Path):
  path = tmp_path / "spec.py.fsc.md"
  write_spec_atomic(path, "first")
  write_spec_atomic(path, "second")

  assert path.read_text() == "second"


def test_is_spec_fresh_no_spec(tmp_path: Path):
  src = tmp_path / "app.py"
  src.write_text("x = 1")

  cfg = FSCConfig()
  cfg.output.output_dir = str(tmp_path / ".fsc" / "specs")
  assert is_spec_fresh(src, tmp_path, cfg) is False


def test_is_spec_fresh_spec_newer(tmp_path: Path):
  src = tmp_path / "app.py"
  src.write_text("x = 1")

  cfg = FSCConfig()
  cfg.output.output_dir = str(tmp_path / ".fsc" / "specs")
  spec_path = resolve_output_path(src, tmp_path, cfg)
  spec_path.parent.mkdir(parents=True, exist_ok=True)
  spec_path.write_text("spec")

  assert is_spec_fresh(src, tmp_path, cfg) is True


def test_encode_path():
  assert _encode_path("src/app.py") == "src__app.py.fsc.md"
  assert _encode_path("src\\controllers\\user.py") == "src__controllers__user.py.fsc.md"
  assert _encode_path("app.py") == "app.py.fsc.md"
  assert _encode_path("deep/nested/path/file.kt") == "deep__nested__path__file.kt.fsc.md"
