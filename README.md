# FileSpecContractor (fsc)

> Token-saving contracts for your codebase.

**⚠️ Note: This project is currently in active development and is not yet available for installation. This README describes the planned functionality.**

`fsc` is a command-line tool that generates descriptive specifications for your code files — compact "contracts" that help LLMs understand your project without burning through free-tier token limits.

## Why?

Free LLM models (DeepSeek, Mistral, GigaChat) have strict context limits. Feeding them your entire codebase is expensive and often impossible. `fsc` creates lightweight `.fsc.md` files that capture the **public API and critical implementation details** of each file — enough for an agent to work with, small enough to fit in context.

Born from the frustration of trying to vibe-code on a student laptop.

## Planned Installation

```bash
uv tool install file-spec-contractor
```

Or with pip:

```bash
pip install file-spec-contractor
```

Once installed, the tool will be available as `fsc`.

## Planned Usage

```bash
# Set up configuration
fsc init

# Generate specifications for current directory
fsc generate

# Generate for specific file
fsc generate --file src/machine.py

# Generate with custom extensions
fsc generate --extensions .py .kt --exclude tests

# Use a different model provider
fsc generate --provider gigachat
```

## Planned Configuration

`fsc` will look for configuration in this order (later sources override earlier ones):

1. CLI arguments (highest priority)
2. `.fsc/config.toml` in your project root
3. `~/.config/fsc/config.toml` for user-wide settings

Example `.fsc/config.toml`:

```toml
[project]
extensions = [".py", ".kt", ".java"]
exclude_dirs = ["venv", ".git", "__pycache__", "tests/fixtures"]
exclude_files = ["setup.py", "conftest.py"]

[output]
# Output language for specifications ("en" or "ru")
language = "en"
# Where to save generated specs:
# - "adjacent": file.py → file.fsc.md (saved next to the source file)
# - "mirror": save to a separate folder, mirroring project structure
output_mode = "mirror"
output_dir = ".fsc/specs"

[api]
# Default provider (deepseek, mistral, gigachat, etc.)
provider = "deepseek"
# API keys for different providers (or use environment variables)
deepseek_api_key = "your-key-here"
mistral_api_key = "your-key-here"
gigachat_api_key = "your-key-here"
```

### Output Modes

| Mode       | Behavior                                                                                                         |
| ---------- | ---------------------------------------------------------------------------------------------------------------- |
| `adjacent` | Saves `file.fsc.md` right next to `file.py`                                                                      |
| `mirror`   | Saves to `output_dir`, preserving directory structure (e.g., `src/machine.py` → `.fsc/specs/src/machine.fsc.md`) |

## How It Will Work

1. Scans your project for files matching configured extensions
2. For each file, analyzes its public API, dependencies, and implementation quirks
3. Generates a structured `.fsc.md` file using the selected LLM provider
4. Saves the specification — ready to be fed to any LLM agent

## Specification Format

Each generated spec will follow a strict structure:

- **Purpose**: What this file does
- **Dependencies**: External libs and internal modules
- **Public API**: All public methods with signatures and notes
- **Implementation Notes**: Sentinels, patterns, non-obvious details
- **Handle with Care**: Contracts that are easy to break
- **Code Style**: Conventions used in this file

## Planned Requirements

- Python 3.12+
- API key for at least one supported provider

## Roadmap

- [ ] Core CLI with `init` and `generate` commands
- [ ] DeepSeek API integration
- [ ] Configuration file support (TOML)
- [ ] Dual output modes (`adjacent` / `mirror`)
- [ ] Progress display with `rich`
- [ ] `--update` flag for incremental regeneration
- [ ] Multi-provider support
- [ ] Local model support (via Ollama, LM Studio)
- [ ] VS Code extension (generate specs from context menu / command palette)
