from dataclasses import asdict, dataclass, field


@dataclass
class ProjectConfig:
  extensions: list[str] = field(default_factory=lambda: [".py"])
  exclude_dirs: list[str] = field(
    default_factory=lambda: [".venv", "venv", ".git", "__pycache__", "build"]
  )
  exclude_files: list[str] = field(default_factory=list)

  def __post_init__(self):
    if not isinstance(self.extensions, list):
      raise ValueError(f"extensions must be a list, got {type(self.extensions).__name__}")

    for ext in self.extensions:
      if not isinstance(ext, str) or not ext.startswith("."):
        raise ValueError(f"Extension '{ext}' must be a string starting with '.'")


@dataclass
class OutputConfig:
  language: str = "en"
  output_mode: str = "mirror"
  output_dir: str = ".fsc/specs"
  batch_size: int = 50

  def __post_init__(self):
    if self.output_mode not in ("mirror", "adjacent", "batch"):
      raise ValueError(
        f"output_mode must be one of: mirror, adjacent, batch, got '{self.output_mode}'"
      )

    if not isinstance(self.batch_size, int) or self.batch_size <= 0:
      raise ValueError(f"batch_size must be a positive integer, got {self.batch_size}")


@dataclass
class ApiConfig:
  provider: str = "openrouter"


@dataclass
class PromptConfig:
  file: str = ".fsc/PROMPT.md"


@dataclass
class RuntimeConfig:
  concurrency: int = 1
  force_per_file: bool = False

  def __post_init__(self):
    if not isinstance(self.concurrency, int) or self.concurrency < 1:
      raise ValueError(f"concurrency must be >= 1, got {self.concurrency}")


@dataclass
class FSCConfig:
  project: ProjectConfig = field(default_factory=ProjectConfig)
  output: OutputConfig = field(default_factory=OutputConfig)
  api: ApiConfig = field(default_factory=ApiConfig)
  prompt: PromptConfig = field(default_factory=PromptConfig)
  runtime: RuntimeConfig = field(default_factory=RuntimeConfig)

  @classmethod
  def from_dict(cls, data: dict) -> "FSCConfig":
    return cls(
      project=ProjectConfig(**data.get("project", {})),
      output=OutputConfig(**data.get("output", {})),
      api=ApiConfig(**data.get("api", {})),
      prompt=PromptConfig(**data.get("prompt", {})),
      runtime=RuntimeConfig(**data.get("runtime", {})),
    )

  def to_dict(self) -> dict:
    return asdict(self)

  def to_toml(self) -> str:
    d = self.to_dict()
    parts = []

    for section, fields in d.items():
      parts.append(f"[{section}]")

      for key, value in fields.items():
        if isinstance(value, list):
          items = ", ".join(f'"{v}"' for v in value)
          parts.append(f"{key} = [{items}]")

        elif isinstance(value, bool):
          parts.append(f"{key} = {'true' if value else 'false'}")

        elif isinstance(value, int):
          parts.append(f"{key} = {value}")

        else:
          parts.append(f'{key} = "{value}"')

      parts.append("")

    return "\n".join(parts)
