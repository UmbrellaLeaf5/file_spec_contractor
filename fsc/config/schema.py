from dataclasses import dataclass, field


@dataclass
class ProjectConfig:
  extensions: list[str] = field(default_factory=lambda: [".py"])
  exclude_dirs: list[str] = field(
    default_factory=lambda: [".venv", "venv", ".git", "__pycache__", "tests"]
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
