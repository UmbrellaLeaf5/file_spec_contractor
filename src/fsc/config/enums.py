from enum import StrEnum


class GenerationMode(StrEnum):
  bulk = "bulk"
  per_file = "per-file"
  per_file_parallel = "per-file-parallel"


class OutputMode(StrEnum):
  mirror = "mirror"
  adjacent = "adjacent"
  batch = "batch"
