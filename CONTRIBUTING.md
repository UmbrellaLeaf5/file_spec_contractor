# Contributing

## Commit message format

```
<type>(<scope>): <subject>

[optional body]
```

### Type (required)

| Type       | Description                                 |
| ---------- | ------------------------------------------- |
| `feat`     | New user-facing feature                     |
| `fix`      | Bug fix                                     |
| `docs`     | Documentation changes                       |
| `refactor` | Code restructuring without behaviour change |
| `test`     | Adding or modifying tests                   |
| `chore`    | Routine tasks, tooling, maintenance         |

### Scope (optional)

A module or component affected by the commit:

- `cli` - command-line interface, flags, help text
- `config` - TOML loader, schemas, overrides
- `providers` - LLM provider logic (OpenRouter, DeepSeek, factory)
- `spec` - specification generation (bulk, per-file, resolver)
- `utils` - helper modules (file system, env, prompts)
- `tests` - test infrastructure
- `docs` - README, AGENTS.md, CONTRIBUTING.md

### Subject (required)

Concise imperative statement summarizing the change. Use lowercase.

### Body (optional)

Detailed explanation of what and why. Use this to provide context - motivation, edge cases, trade-offs.

### Examples

```
fix(providers): missing resp.text fallback in DeepSeek error handler

Error responses that were not valid JSON (HTML errors, empty body)
showed a bare HTTP status code instead of the response text.
```

```
feat(cli): add --gen-mode per-file-parallel flag
```

```
refactor(config): extract CLI options into shared _options.py
```

```
docs(readme): update generation mode defaults to per-file
```

---

## Pull request guidelines

- **Title:** start with a capitalized imperative verb.
  - Good: `Add --output-mode batch support`
  - Good: `Fix spec caching when output_dir is missing`
  - Avoid: `fixed bug`, `new feature`, `updated documentation`
- **Description:** summarise the change, link related issues, mention any breaking changes.

---

## Before contributing

Run all three checks - in this order:

```bash
ruff check src/fsc/ tests/
pyright src/fsc/
uv run pytest -k "not openrouter_generate and not full_pipeline_cache and not full_pipeline_force"
```

Unsorted imports are auto-fixed with `ruff check --fix`. Any lint or type error must be resolved before committing.
