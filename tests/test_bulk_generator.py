from fsc.spec.bulk_generator import _build_batch_prompt, _parse_batch_response


def test_build_batch_prompt_empty():
  result = _build_batch_prompt({}, "en")

  assert "Generate specifications for ALL files" in result
  assert "### FILE:" not in result


def test_build_batch_prompt_single_file():
  files = {"src/app.py": "print('hello')"}
  result = _build_batch_prompt(files, "en")

  assert "### FILE: src/app.py" in result
  assert "### LANG: en" in result
  assert "print('hello')" in result


def test_build_batch_prompt_multiple_files():
  files = {"z.py": "z", "a.py": "a", "m.py": "m"}
  result = _build_batch_prompt(files, "ru")

  a_pos = result.index("### FILE: a.py")
  m_pos = result.index("### FILE: m.py")
  z_pos = result.index("### FILE: z.py")

  assert a_pos < m_pos < z_pos
  assert "### LANG: ru" in result


def test_parse_batch_response_valid():
  response = (
    "## SPEC: src/app.py\n"
    "# Purpose\nContent here.\n\n"
    "---\n"
    "## SPEC: src/utils.py\n"
    "# Purpose\nOther content.\n\n"
    "---"
  )

  result = _parse_batch_response(response)

  assert len(result) == 2  # noqa: PLR2004
  assert "src/app.py" in result
  assert "src/utils.py" in result
  assert "Content here." in result["src/app.py"]
  assert "Other content." in result["src/utils.py"]


def test_parse_batch_response_empty():
  result = _parse_batch_response("")

  assert result == {}


def test_parse_batch_response_no_markers():
  result = _parse_batch_response("Just some text without markers")

  assert result == {}


def test_parse_batch_response_malformed():
  response = "## SPEC: file.py\nsome content\n## SPEC: broken\noops"

  result = _parse_batch_response(response)

  assert "file.py" in result
  assert "some content" in result["file.py"]


def test_parse_batch_response_trailing_separator():
  response = "## SPEC: only.py\none file\n---"

  result = _parse_batch_response(response)

  assert len(result) == 1
  assert "only.py" in result
  assert result["only.py"] == "one file"
