from pydantic import BaseModel, Field, field_validator

from fsc.config.enums import GenerationMode, OutputMode


class CLIConfigOverrides(BaseModel):
  """Typed container for CLI flag overrides applied to FSCConfig."""

  extensions: list[str] | None = None
  exclude_dirs: list[str] | None = None
  exclude_files: list[str] | None = None
  provider: str | None = None
  model: str | None = None
  output_mode: str | None = None
  output_dir: str | None = None
  batch_size: int | None = None
  prompt_file: str | None = None
  language: str | None = None
  concurrency: int | None = None
  generation_mode: str | None = None


class ProjectConfig(BaseModel):
  extensions: list[str] = Field(default_factory=lambda: [".py"])
  exclude_dirs: list[str] = Field(
    default_factory=lambda: [".venv", "venv", ".git", "__pycache__", "build"]
  )
  exclude_files: list[str] = Field(default_factory=list)

  @field_validator("extensions")
  @classmethod
  def _check_extensions(cls, v: list[str]) -> list[str]:
    for ext in v:
      if not ext.startswith("."):
        raise ValueError(f"Extension '{ext}' must start with '.'")

    return v


class OutputConfig(BaseModel):
  language: str = "en"
  output_mode: OutputMode = OutputMode.mirror
  output_dir: str = ".fsc/specs"
  batch_size: int = Field(default=50, gt=0)


class ApiConfig(BaseModel):
  provider: str = "openrouter"
  model: str | None = None


class PromptConfig(BaseModel):
  file: str = ".fsc/PROMPT.md"


class RuntimeConfig(BaseModel):
  concurrency: int = Field(default=3, ge=1)
  generation_mode: GenerationMode = GenerationMode.per_file


class FSCConfig(BaseModel):
  project: ProjectConfig = Field(default_factory=ProjectConfig)
  output: OutputConfig = Field(default_factory=OutputConfig)
  api: ApiConfig = Field(default_factory=ApiConfig)
  prompt: PromptConfig = Field(default_factory=PromptConfig)
  runtime: RuntimeConfig = Field(default_factory=RuntimeConfig)

  @classmethod
  def from_dict(cls, data: dict) -> "FSCConfig":
    return cls(**data)

  def to_dict(self) -> dict:
    return self.model_dump()

  def to_toml(self) -> str:
    d = self.model_dump(mode="json", exclude_none=True)
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
