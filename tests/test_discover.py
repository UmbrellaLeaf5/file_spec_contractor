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


def test_scan_empty_directory(tmp_path: Path):
  found = scan_files(tmp_path, extensions=[".py"], exclude_dirs=[], exclude_files=[])

  assert found == []


def test_scan_no_matching_extensions(tmp_path: Path):
  (tmp_path / "file.txt").write_text("text")
  (tmp_path / "doc.md").write_text("# doc")

  found = scan_files(tmp_path, extensions=[".py"], exclude_dirs=[], exclude_files=[])

  assert found == []


def test_scan_nested_excluded_dirs(tmp_path: Path):
  (tmp_path / "main.py").write_text("x = 1")

  venv = tmp_path / "venv"
  deep = venv / "lib" / "site-packages" / "pkg"
  deep.mkdir(parents=True)
  (deep / "nested.py").write_text("y = 2")

  found = scan_files(
    tmp_path, extensions=[".py"], exclude_dirs=["venv"], exclude_files=[]
  )

  names = {p.name for p in found}

  assert "main.py" in names
  assert "nested.py" not in names


def test_scan_exclude_files_pattern(tmp_path: Path):
  (tmp_path / "test_app.py").write_text("pass")
  (tmp_path / "test_utils.py").write_text("pass")
  (tmp_path / "setup.py").write_text("pass")
  (tmp_path / "main.py").write_text("pass")

  found = scan_files(
    tmp_path,
    extensions=[".py"],
    exclude_dirs=[],
    exclude_files=["test_*.py", "setup.py"],
  )

  names = {p.name for p in found}

  assert "main.py" in names
  assert "test_app.py" not in names
  assert "test_utils.py" not in names
  assert "setup.py" not in names


def test_scan_very_deep_nesting(tmp_path: Path):
  current = tmp_path

  for i in range(20):
    current = current / f"level_{i}"
    current.mkdir()

  deep_file = current / "deep.py"
  deep_file.write_text("pass")

  found = scan_files(tmp_path, extensions=[".py"], exclude_dirs=[], exclude_files=[])

  assert any(p.name == "deep.py" for p in found)


def test_scan_many_files(tmp_path: Path):
  for i in range(100):
    (tmp_path / f"file_{i}.py").write_text(f"#{i}")

  found = scan_files(tmp_path, extensions=[".py"], exclude_dirs=[], exclude_files=[])

  assert len(found) == 100  # noqa: PLR2004
