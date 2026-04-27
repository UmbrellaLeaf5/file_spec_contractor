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

# Overwrite existing config
fsc init --yes

# Remove all fsc artifacts (.fsc/ and *.fsc.md files)
fsc deinit

# Recreate configuration from scratch (deinit + init)
fsc reinit

# Generate specifications for current directory (scan mode, batch by default)
fsc generate

# Generate for specific files
fsc generate --file src/machine.py

# Generate with custom extensions
fsc generate --extensions .py .kt

# Force per-file mode with parallel requests
fsc generate --force-per-file -c 5

# Preview what would be generated (no files written)
fsc generate --dry-run --verbose

# Enable verbose output
fsc generate --verbose

# Russian language specifications
fsc generate --language ru
```

### Generation Modes

| Mode                    | Flag                    | Behaviour                                                                       |
| ----------------------- | ----------------------- | ------------------------------------------------------------------------------- |
| **batch**               | _(default)_             | All files in a single LLM request. Consistent, cross-referenced specifications. |
| **per-file sequential** | `--force-per-file`      | Each file separately, one at a time.                                            |
| **per-file parallel**   | `--force-per-file -c N` | N files simultaneously via thread pool. Fastest for large projects.             |

If batch mode fails to produce parsable output, `fsc` automatically falls back to per-file generation.

### Options

| Option                | Description                                              |
| --------------------- | -------------------------------------------------------- |
| `--file`              | Specific files to generate specs for (repeatable)        |
| `--extensions`        | File extensions to include (default: `.py`)              |
| `--exclude-dirs`      | Directories to skip                                      |
| `--exclude-files`     | File patterns to skip                                    |
| `-c`, `--concurrency` | Parallel requests for per-file mode (default: `1`)       |
| `--force-per-file`    | Force per-file generation instead of batch               |
| `--output-mode`       | `mirror` (default) or `adjacent`                         |
| `--output-dir`        | Output directory for mirror mode (default: `.fsc/specs`) |
| `--prompt-file`       | Custom system prompt file                                |
| `--language`          | Output language: `en` (default) or `ru`                  |
| `--dry-run`           | Preview without writing files                            |
| `--verbose`           | Detailed output                                          |

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
output_mode = "mirror"   # "mirror" or "adjacent"
output_dir = ".fsc/specs"

# LLM provider and API keys
[api]
provider = "openrouter"        # "openrouter" or "deepseek"
deepseek_api_key = ""          # for DeepSeek provider
openrouter_api_key = ""        # for OpenRouter provider

# Custom system prompt file (relative to project root)
[prompt]
file = ".fsc/PROMPT.md"

# Generation runtime settings
[runtime]
concurrency = 1            # parallel threads for per-file mode
force_per_file = false     # skip batch mode, use per-file
```

### API Key

**OpenRouter** (default):

```bash
export OPEN_ROUTER_API_KEY=sk-or-v1-...
```

Or in `~/.config/fsc/config.toml`:

```toml
[api]
openrouter_api_key = "sk-or-v1-..."
```

**DeepSeek** (alternative):

```bash
export DEEPSEEK_API_KEY=sk-...
```

Or in config:

```toml
[api]
provider = "deepseek"
deepseek_api_key = "sk-..."
```

Environment variables always take priority over config files.

### Providers

| Provider                 | Model                      | Free | Env var               |
| ------------------------ | -------------------------- | ---- | --------------------- |
| **OpenRouter** (default) | `openai/gpt-oss-120b:free` | yes  | `OPEN_ROUTER_API_KEY` |
| DeepSeek                 | `deepseek-chat`            | yes  | `DEEPSEEK_API_KEY`    |

Switch provider via config or CLI:

```bash
fsc generate --provider deepseek
```

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
- [x] OpenRouter API integration (free model)
- [x] Multi-provider support with `--provider` flag
- [x] Batch generation mode (all files in one request)
- [x] Parallel per-file generation (`--force-per-file -c N`)
- [x] Configuration file support (TOML)
- [x] Dual output modes (`adjacent` / `mirror`)
- [x] Prompt resolution (project file → built-in fallback)
- [x] Multi-language prompt support (en, ru)
- [x] Installable CLI entry point (`fsc`)
- [ ] `--update` flag for incremental regeneration
- [ ] Rich progress bars for large projects
- [ ] Local model support (Ollama, LM Studio)
- [ ] VS Code extension (generate specs from context menu / command palette)
