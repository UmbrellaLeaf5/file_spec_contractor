from dataclasses import asdict, dataclass, field


@dataclass
class ProjectConfig:
  extensions: list[str] = field(default_factory=lambda: [".py"])
  exclude_dirs: list[str] = field(
    default_factory=lambda: [".venv", "venv", ".git", "__pycache__"]
  )
  exclude_files: list[str] = field(default_factory=list)


@dataclass
class OutputConfig:
  language: str = "en"
  output_mode: str = "mirror"
  output_dir: str = ".fsc/specs"


@dataclass
class ApiConfig:
  provider: str = "deepseek"
  deepseek_api_key: str = ""


@dataclass
class PromptConfig:
  file: str = ".fsc/PROMPT.md"


@dataclass
class FscConfig:
  project: ProjectConfig = field(default_factory=ProjectConfig)
  output: OutputConfig = field(default_factory=OutputConfig)
  api: ApiConfig = field(default_factory=ApiConfig)
  prompt: PromptConfig = field(default_factory=PromptConfig)

  @classmethod
  def from_dict(cls, data: dict) -> "FscConfig":
    return cls(
      project=ProjectConfig(**data.get("project", {})),
      output=OutputConfig(**data.get("output", {})),
      api=ApiConfig(**data.get("api", {})),
      prompt=PromptConfig(**data.get("prompt", {})),
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

        else:
          parts.append(f'{key} = "{value}"')

      parts.append("")

    return "\n".join(parts)
