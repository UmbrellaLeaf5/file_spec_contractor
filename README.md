# FileSpecContractor (fsc)

[![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python)](https://python.org)
[![Typer](https://img.shields.io/badge/Typer-0.15+-blue)](https://typer.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.0+-purple)](https://docs.pydantic.dev/)
[![Rich](https://img.shields.io/badge/Rich-13.0+-brightgreen)](https://rich.readthedocs.io/)
[![httpx](https://img.shields.io/badge/httpx-0.24+-orange)](https://www.python-httpx.org/)
[![python-dotenv](https://img.shields.io/badge/dotenv-1.0+-yellow)](https://github.com/theskumar/python-dotenv)
[![License](https://img.shields.io/badge/License-Unlicense-lightgrey)](https://unlicense.org)
[![Tests](https://github.com/UmbrellaLeaf5/file_spec_contractor/workflows/Tests/badge.svg)](https://github.com/UmbrellaLeaf5/file_spec_contractor/actions/workflows/tests.yml)

> Token-saving contracts for your codebase.

`fsc` is a command-line tool that generates descriptive specifications for your code files - compact "contracts" that help LLMs understand your project without burning through free-tier token limits.

## Why?

Free LLM models have strict context limits. Feeding them your entire codebase is expensive and often impossible. `fsc` creates lightweight `.fsc.md` files that capture the **public API and critical implementation details** of each file - enough for an agent to work with, small enough to fit in context.

Born from the frustration of trying to vibe-code on a student laptop.

## Installation

```bash
# Install with uv
uv tool install file_spec_contractor

# Or with pip
pip install file_spec_contractor
```

After installation, the `fsc` command is available globally:

```bash
fsc --help
```

### For Scala users

The `fsc` command may conflict with the [Scala Fast Offline Compiler](https://www.scala-lang.org/) which also uses the `fsc` name. If both are installed, use the full package name instead:

```bash
file-spec-contractor init
file-spec-contractor generate
file-spec-contractor --help

# or with underscore
file_spec_contractor init
file_spec_contractor generate
```

`fsc` automatically detects Scala environments and shows a warning if a conflict is possible.

## Usage

```bash
# Set up configuration with defaults
fsc init

# Init in a specific directory
fsc init /path/to/project

# Init with custom settings
fsc init --extensions .py --extensions .kt --language ru

# Init with a different provider
fsc init --provider deepseek

# Recreate from scratch (removes existing .fsc/ and specs)
fsc init --force

# Same without confirmation prompt
fsc init --force -y

# Remove all fsc artifacts (.fsc/ and *.fsc.md files)
fsc deinit

# Remove only generated specs, keep config
fsc clean

# Skip confirmation
fsc clean -y

# Recreate configuration from scratch (deinit + init)
fsc reinit

# Reinit with custom flags
fsc reinit --extensions .py --extensions .kt --language ru

# Init with custom model
fsc init --model deepseek-reasoner

# Generate specifications for current directory (scan mode, bulk by default)
fsc generate

# Generate with a specific model
fsc generate --model openai/gpt-4o-mini

# Generate for specific files
fsc generate --file src/machine.py

# Generate with custom extensions
fsc generate --extensions .py .kt

# Force per-file mode with parallel requests
fsc generate --force-per-file -c 5

# Preview what would be generated (no files written)
fsc generate --dry-run --verbose

# Regenerate all specs ignoring cache
fsc generate -f

# Check version
fsc --version
```

### Generation Modes

| Mode                    | Flag                    | Behaviour                                                                       |
| ----------------------- | ----------------------- | ------------------------------------------------------------------------------- |
| **bulk**                | _(default)_             | All files in a single LLM request. Consistent, cross-referenced specifications. |
| **per-file sequential** | `--force-per-file`      | Each file separately, one at a time.                                            |
| **per-file parallel**   | `--force-per-file -c N` | N files simultaneously via thread pool. Fastest for large projects.             |

If bulk mode fails to produce parsable output, `fsc` automatically falls back to per-file generation.

### Commands

| Command        | Description                                                                                                                            |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `init [dir]`   | Create `.fsc/` with config and prompt. Accepts optional target directory and all config flags. Use `--force` to recreate from scratch. |
| `clean [dir]`  | Remove `*.fsc.md` files, keep `.fsc/` configuration.                                                                                   |
| `deinit [dir]` | Remove `.fsc/` and all `*.fsc.md` files. Prompts for confirmation unless `-y`.                                                         |
| `reinit [dir]` | `init --force` equivalent. Removes all artifacts, then creates fresh `.fsc/`. Prompts for confirmation unless `-y`.                    |
| `generate`     | Generate `*.fsc.md` specifications.                                                                                                    |

### Options

All options below are available on `generate`, `init`, and `reinit` (except `--file`, `--dry-run`, `--verbose` which are `generate`-only).

| Option                | Description                                                        |
| --------------------- | ------------------------------------------------------------------ |
| `--force`             | Recreate config from scratch (`init`/`reinit`)                     |
| `-y`, `--yes`         | Skip confirmation prompts on destructive operations                |
| `--file`              | Specific files to generate specs for (`generate` only, repeatable) |
| `--extensions`        | File extensions to include (default: `.py`)                        |
| `--exclude-dirs`      | Directories to skip                                                |
| `--exclude-files`     | File patterns to skip                                              |
| `--provider`          | LLM provider: `openrouter` (default) or `deepseek`                 |
| `--model`             | Model name for the selected provider                               |
| `--api-key`           | API key for the selected provider                                  |
| `--output-mode`       | `mirror` (default), `adjacent`, or `batch`                         |
| `--output-dir`        | Output directory for mirror/batch mode (default: `.fsc/specs`)     |
| `--batch-size`        | Files per folder in batch mode (default: `50`)                     |
| `--prompt-file`       | Custom system prompt file                                          |
| `--language`          | Prompt language: `en` (default) or `ru` (`init`/`reinit` only)     |
| `-c`, `--concurrency` | Parallel requests for per-file mode (default: `3`)                 |
| `--force-per-file`    | Force per-file generation instead of bulk                          |
| `-f`, `--force`       | Regenerate all specs, ignoring cache                               |
| `--dry-run`           | Preview without writing files or calling API (`generate` only)     |
| `--verbose`           | Detailed output (`generate` only)                                  |
| `--version`           | Show version and exit                                              |

## Configuration

`fsc` looks for configuration in this order (later sources override earlier ones):

1. CLI arguments (highest priority)
2. `.fsc/config.toml` in your project root
3. `~/.config/fsc/config.toml` for user-wide settings

### Creating config

```bash
fsc init
```

This creates:

- `.fsc/config.toml` - project configuration
- `.fsc/PROMPT.md` - custom system prompt (optional, built-in prompt is used as fallback)

### Example `.fsc/config.toml`

```toml
# Which files to scan and which to skip
[project]
extensions = [".py", ".kt"]
exclude_dirs = [".venv", "venv", ".git", "__pycache__", "tests"]
exclude_files = ["setup.py", "conftest.py"]

# Output language and mode
[output]
language = "en"          # "en" or "ru"
output_mode = "mirror"   # "mirror", "adjacent", or "batch"
output_dir = ".fsc/specs"
batch_size = 50          # files per folder (batch mode)

# LLM provider
[api]
provider = "openrouter"        # "openrouter" or "deepseek"
model = ""                     # model name; empty = provider default

# Custom system prompt file (relative to project root)
[prompt]
file = ".fsc/PROMPT.md"

# Generation runtime settings
[runtime]
concurrency = 3            # parallel threads for per-file mode
force_per_file = false     # skip bulk mode, use per-file
```

### API Key

API keys are **never stored in config files**. Three ways to provide them (in priority order):

1. **CLI flag** - `--api-key` (highest priority)
2. **Environment variable** - `OPEN_ROUTER_API_KEY` / `DEEPSEEK_API_KEY`
3. **`.env` file** in project root (lowest priority)

**OpenRouter** (default):

```bash
# Option 1: CLI flag
fsc generate --api-key sk-or-v1-...

# Option 2: environment variable
export OPEN_ROUTER_API_KEY=sk-or-v1-...

# Option 3: .env file
echo "OPEN_ROUTER_API_KEY=sk-or-v1-..." > .env
```

**DeepSeek** (alternative):

```bash
fsc generate --provider deepseek --api-key sk-...
# or: export DEEPSEEK_API_KEY=sk-...
# or: echo "DEEPSEEK_API_KEY=sk-..." > .env
```

### Providers

| Provider                 | Model                      | Free | Env var               |
| ------------------------ | -------------------------- | ---- | --------------------- |
| **OpenRouter** (default) | `openai/gpt-oss-120b:free` | yes  | `OPEN_ROUTER_API_KEY` |
| DeepSeek                 | `deepseek-chat`            | no   | `DEEPSEEK_API_KEY`    |

Switch provider via config or CLI:

```bash
fsc generate --provider deepseek
```

### Output Modes

| Mode       | Behaviour                                                                                                                                                                                                     |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `adjacent` | Saves `file.fsc.md` right next to `file.py`                                                                                                                                                                   |
| `mirror`   | Saves to `output_dir`, preserving directory structure (e.g., `src/machine.py` → `.fsc/specs/src/machine.fsc.md`)                                                                                              |
| `batch`    | Groups specs into numbered folders `batch-1/`, `batch-2/`, etc. File names encode the original path (e.g., `src/machine.py` → `src__machine.fsc.md`). Folder size controlled by `batch_size` (default: `50`). |

**Batch mode example** (`batch_size = 50`, 120 files):

```
.fsc/batches/
├── batch-1/
│   ├── src__controllers__UserController.fsc.md
│   └── ... (49 more files)
├── batch-2/
│   ├── src__models__Product.fsc.md
│   └── ... (49 more files)
└── batch-3/
    └── ... (20 files)
```

Configure via CLI or config:

```bash
fsc init --output-mode batch --batch-size 100
fsc generate --output-mode batch --batch-size 50
```

When output mode is changed, existing specs are automatically moved to the new location instead of being regenerated.

```toml
# .fsc/config.toml
[output]
output_mode = "batch"
output_dir = ".fsc/batches"
batch_size = 50
```

### Prompt

`fsc` sends a system prompt to the LLM that defines the specification format. Built-in prompts are versioned per language: `fsc_en_5.md`, `fsc_ru_5.md`. The latest version is always used. Resolution order:

1. `--prompt-file` CLI argument
2. `.fsc/PROMPT.md` in project root
3. Built-in prompt from the package

If no prompt file is found, a warning is shown and the built-in prompt is used.

## How It Works

1. Scans your project for files matching configured extensions
2. Sends all files in a single request to the LLM (bulk mode, default) or one-by-one (per-file mode)
3. The LLM generates structured `.fsc.md` specifications
4. Saves the specifications as `file.<ext>.fsc.md` - ready to be fed to any LLM agent
5. On subsequent runs, skips unchanged files. If output mode changed, moves specs instead of regenerating.

## Specification Format

Each generated spec follows this structure:

- **Purpose** - what this file does
- **Dependencies** - external libs and internal modules
- **Public API** - all public methods with signatures and notes
- **Implementation Notes** - sentinels, patterns, non-obvious details
- **Handle with Care** - contracts that are easy to break
- **Code Style** - conventions used in this file

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) for dependency management
- OpenRouter or DeepSeek API key (see [API Key](#api-key))
- `.env` file support via [python-dotenv](https://github.com/theskumar/python-dotenv)

## Tech Stack

| Component  | Library                                                     |
| ---------- | ----------------------------------------------------------- |
| CLI        | [Typer](https://typer.tiangolo.com/)                        |
| Validation | [Pydantic](https://docs.pydantic.dev/)                      |
| Logging    | [Rich](https://rich.readthedocs.io/)                        |
| HTTP       | [httpx](https://www.python-httpx.org/)                      |
| Config     | [python-dotenv](https://github.com/theskumar/python-dotenv) |
| Testing    | [pytest](https://docs.pytest.org/)                          |

## Development

```bash
# Clone and install in editable mode
git clone https://github.com/UmbrellaLeaf5/file_spec_contractor.git
cd file_spec_contractor
uv sync

# Run all tests (63 tests)
uv run pytest

# Run specific test file
uv run pytest tests/test_deepseek.py -v

# Run CLI in dev
uv run fsc --help

# Build package
uv build
```

## Roadmap

- [x] Core CLI with `init`, `generate`, `deinit`, `reinit` commands
- [x] DeepSeek API integration
- [x] OpenRouter API integration (free `gpt-oss-120b` model)
- [x] Multi-provider support with `--provider` flag
- [x] Bulk generation mode (all files in one request with fallback)
- [x] Parallel per-file generation (`--force-per-file -c N`)
- [x] Spec caching with `--force` to regenerate
- [x] Configuration file support (TOML) with Pydantic validation
- [x] `.env` file support for API keys (via python-dotenv)
- [x] All config flags available on `init`, `reinit`, and `generate`
- [x] Batch output mode, mirror, and adjacent
- [x] Prompt resolution (project file → built-in fallback, per-language)
- [x] Multi-language prompt support (en, ru)
- [x] Installable CLI entry point (`fsc`)
- [x] Graceful shutdown on Ctrl+C
- [x] 63 tests (unit, integration, CLI)
- [x] Spec auto-move on output mode change (no wasted regeneration)
- [x] `fsc --version` and setuptools-scm versioning
- [x] `fsc init <dir>` - initialise in any directory
- [x] CI pipeline with GitHub Actions
- [x] `--force` / `--yes` / confirmation prompts for destructive commands
- [x] PyPI publish automation
- [ ] `--update` flag for incremental regeneration
- [x] clean command just to delete all specs
- [ ] Rich progress bars for large projects
- [ ] Local model support (Ollama, LM Studio)
- [x] check if Scala is used and make warning not to use short name
- [x] add long name usage (file-spec-contractor or file_spec_contractor instead of fsc)
- [x] Publish to PyPI (`pip install file_spec_contractor`)
- [ ] VS Code extension (generate specs from context menu / command palette)
