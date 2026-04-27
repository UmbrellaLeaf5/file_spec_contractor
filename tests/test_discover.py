from pathlib import Path

from fsc.utils.fs import scan_files


def test_scan_respects_extensions(tmp_path: Path):
  d = tmp_path / "src"
  d.mkdir()

  (d / "a.py").write_text("print(1)")
  (d / "b.txt").write_text("x")

  found = scan_files(tmp_path, extensions=[".py"], exclude_dirs=[], exclude_files=[])

  assert any(p.name == "a.py" for p in found)
  assert all(p.suffix == ".py" for p in found)


def test_scan_excludes_venv(tmp_path: Path):
  (tmp_path / "main.py").write_text("x = 1")

  venv = tmp_path / "venv"
  venv.mkdir()

  (venv / "lib.py").write_text("y = 2")

  found = scan_files(
    tmp_path, extensions=[".py"], exclude_dirs=["venv"], exclude_files=[]
  )

  names = {p.name for p in found}

  assert "main.py" in names
  assert "lib.py" not in names
