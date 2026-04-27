from pathlib import Path

from fsc.prompt_loader import builtin_prompt_text, load_prompt, resolve_prompt_path


def test_missing_prompt_uses_builtin(tmp_path: Path):
    project_root = tmp_path
    cfg = {"prompt": {"file": ".fsc/PROMPT.md"}}
    p = resolve_prompt_path(project_root, cfg)
    assert p is None
    text = load_prompt(p)
    assert len(text) > 50
