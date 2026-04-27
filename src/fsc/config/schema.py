from typing import Literal

from pydantic import BaseModel, Field, field_validator


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
  output_mode: Literal["mirror", "adjacent", "batch"] = "mirror"
  output_dir: str = ".fsc/specs"
  batch_size: int = Field(default=50, gt=0)


class ApiConfig(BaseModel):
  provider: str = "openrouter"


class PromptConfig(BaseModel):
  file: str = ".fsc/PROMPT.md"


class RuntimeConfig(BaseModel):
  concurrency: int = Field(default=1, ge=1)
  force_per_file: bool = False


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
