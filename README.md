# FileSpecContractor (fsc)

> Token-saving contracts for your codebase.

`fsc` is a command-line tool that generates descriptive specifications for your code files - compact "contracts" that help LLMs understand your project without burning through free-tier token limits.

## Why?

Free LLM models have strict context limits. Feeding them your entire codebase is expensive and often impossible. `fsc` creates lightweight `.fsc.md` files that capture the **public API and critical implementation details** of each file - enough for an agent to work with, small enough to fit in context.

Born from the frustration of trying to vibe-code on a student laptop.

## Installation

### From source

```bash
git clone <repo-url>
cd file_spec_contractor
uv sync
```

After install, the `fsc` command becomes available in the project's virtual environment:

```bash
uv run fsc --help
```

### Install as a global tool

```bash
uv tool install .
```

Now `fsc` is available system-wide:

```bash
fsc --help
```

## Usage

```bash
# Set up configuration in current directory
fsc init

# Remove all fsc artifacts (.fsc/ and *.fsc.md files)
fsc deinit

# Recreate configuration from scratch (deinit + init)
fsc reinit

# Generate specifications for current directory (scan mode)
fsc generate

# Generate for specific files
fsc generate --file src/machine.py

# Generate with custom extensions
fsc generate --extensions .py .kt

# Preview what would be generated (no API calls, no files written)
fsc generate --dry-run --verbose

# Enable verbose output
fsc generate --verbose
```

### Options

| Option            | Description                                              |
| ----------------- | -------------------------------------------------------- |
| `--file`          | Specific files to generate specs for (repeatable)        |
| `--extensions`    | File extensions to include (default: `.py`)              |
| `--exclude-dirs`  | Directories to skip                                      |
| `--exclude-files` | File patterns to skip                                    |
| `--output-mode`   | `mirror` (default) or `adjacent`                         |
| `--output-dir`    | Output directory for mirror mode (default: `.fsc/specs`) |
| `--prompt-file`   | Custom system prompt file                                |
| `--language`      | Output language: `en` (default) or `ru`                  |
| `--dry-run`       | Preview without calling API or writing files             |
| `--verbose`       | Detailed output                                          |

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
[project]
extensions = [".py", ".kt"]
exclude_dirs = [".venv", "venv", ".git", "__pycache__", "tests"]
exclude_files = ["setup.py", "conftest.py"]

[output]
language = "en"
output_mode = "mirror"
output_dir = ".fsc/specs"

[api]
provider = "deepseek"
deepseek_api_key = ""
```

### API Key

Set your DeepSeek API key via environment variable:

```bash
export DEEPSEEK_API_KEY=sk-...
```

Or add it to `~/.config/fsc/config.toml`:

```toml
[api]
deepseek_api_key = "sk-..."
```

The environment variable takes priority over the config file.

### Output Modes

| Mode       | Behavior                                                                                                         |
| ---------- | ---------------------------------------------------------------------------------------------------------------- |
| `adjacent` | Saves `file.fsc.md` right next to `file.py`                                                                      |
| `mirror`   | Saves to `output_dir`, preserving directory structure (e.g., `src/machine.py` → `.fsc/specs/src/machine.fsc.md`) |

### Prompt

`fsc` sends a system prompt to the LLM that defines the specification format. Built-in prompts are versioned per language: `fsc_eng_5.md`, `fsc_ru_5.md`. The latest version is always used. Resolution order:

1. `--prompt-file` CLI argument
2. `.fsc/PROMPT.md` in project root
3. Built-in prompt from the package

If no prompt file is found, a warning is shown and the built-in prompt is used.

## How It Works

1. Scans your project for files matching configured extensions
2. For each file, sends the code with a system prompt to the LLM provider
3. The LLM generates a structured `.fsc.md` specification
4. Saves the specification - ready to be fed to any LLM agent

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
- DeepSeek API key

## Tech Stack

| Component | Library                                |
| --------- | -------------------------------------- |
| CLI       | [Typer](https://typer.tiangolo.com/)   |
| Logging   | [Rich](https://rich.readthedocs.io/)   |
| HTTP      | [httpx](https://www.python-httpx.org/) |
| Testing   | [pytest](https://docs.pytest.org/)     |

## Development

```bash
# Install dependencies (including dev)
uv sync --dev

# Run tests
uv run python -m pytest tests/

# Run specific test
uv run python -m pytest tests/test_deepseek.py -v

# Run CLI in dev
uv run fsc --help
```

## Roadmap

- [x] Core CLI with `init` and `generate` commands
- [x] DeepSeek API integration
- [x] Configuration file support (TOML)
- [x] Dual output modes (`adjacent` / `mirror`)
- [x] Prompt resolution (project file → built-in fallback)
- [x] Multi-language prompt support (en, ru)
- [x] Installable CLI entry point (`fsc`)
- [ ] Concurrency with progress display (`rich`)
- [ ] `--update` flag for incremental regeneration
- [ ] Multi-provider support (Mistral, GigaChat, etc.)
- [ ] Local model support (Ollama, LM Studio)
- [ ] VS Code extension (generate specs from context menu / command palette)
