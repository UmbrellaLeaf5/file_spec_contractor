from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from fsc.config.schemas import FSCConfig
from fsc.providers.base import BaseProvider
from fsc.utils.console import console
from fsc.utils.fs import resolve_output_path, write_spec_atomic
from fsc.utils.progress import make_file_progress


def _build_user_prompt(file_path: str, language: str, code: str) -> str:
  return (
    f"Generate specification for the following file.\n\n"
    f"FILE: {file_path}\n"
    f"LANG: {language}\n\n"
    f"```\n{code}\n```"
  )


def _process_one_file(
  src_path: Path,
  rel_path: str,
  code: str,
  language: str,
  system_prompt: str,
  provider: BaseProvider,
  cfg: FSCConfig,
  project_root: Path,
  dry_run: bool,
  file_index: int = 0,
) -> Path | None:
  user_prompt = _build_user_prompt(rel_path, language, code)

  if dry_run:
    console.log(f"Would generate spec for {rel_path}")
    return resolve_output_path(src_path, project_root, cfg, file_index=file_index)

  console.log(f"Generating spec for {rel_path} ...")
  spec_text = provider.generate(system_prompt, user_prompt)
  out_path = resolve_output_path(src_path, project_root, cfg, file_index=file_index)

  if not dry_run:
    write_spec_atomic(out_path, spec_text)

  return out_path


def _try_process(
  rel_path: str,
  code: str,
  src_paths: dict[str, Path],
  cfg: FSCConfig,
  prompt_template: str,
  provider: BaseProvider,
  project_root: Path,
  dry_run: bool,
  index_map: dict[str, int],
  results: list[Path],
) -> None:
  try:
    out = _process_one_file(
      src_paths[rel_path],
      rel_path,
      code,
      cfg.output.language,
      prompt_template,
      provider,
      cfg,
      project_root,
      dry_run,
      index_map.get(rel_path, 0),
    )

    if out is not None:
      results.append(out)

  except Exception as e:
    console.print(f"[red]Error processing {rel_path}: {e}[/red]")


def _run_sequential(
  data: dict[str, str],
  src_paths: dict[str, Path],
  cfg: FSCConfig,
  prompt_template: str,
  provider: BaseProvider,
  project_root: Path,
  dry_run: bool,
  index_map: dict[str, int],
  show_progress: bool,
  description: str = "Generating specs",
) -> list[Path]:
  results: list[Path] = []

  if show_progress:
    with make_file_progress(len(data), description) as progress:
      task = progress.add_task("", total=len(data))

      try:
        for rel_path, code in data.items():
          progress.update(task, description=f"Processing {rel_path}")
          _try_process(
            rel_path,
            code,
            src_paths,
            cfg,
            prompt_template,
            provider,
            project_root,
            dry_run,
            index_map,
            results,
          )
          progress.update(task, advance=1)

      except KeyboardInterrupt:
        return results

  else:
    console.log(f"Processing {len(data)} files ...")

    try:
      for rel_path, code in data.items():
        _try_process(
          rel_path,
          code,
          src_paths,
          cfg,
          prompt_template,
          provider,
          project_root,
          dry_run,
          index_map,
          results,
        )

    except KeyboardInterrupt:
      return results

  return results


def _submit_futures(
  executor: ThreadPoolExecutor,
  data: dict[str, str],
  src_paths: dict[str, Path],
  cfg: FSCConfig,
  prompt_template: str,
  provider: BaseProvider,
  project_root: Path,
  dry_run: bool,
  index_map: dict[str, int],
) -> dict:
  futures = {}

  for rel_path, code in data.items():
    future = executor.submit(
      _process_one_file,
      src_paths[rel_path],
      rel_path,
      code,
      cfg.output.language,
      prompt_template,
      provider,
      cfg,
      project_root,
      dry_run,
      index_map[rel_path],
    )

    futures[future] = rel_path

  return futures


def _collect_future_result(future, rel_path, results) -> None:
  try:
    out = future.result()

    if out is not None:
      results.append(out)

  except Exception as e:
    console.print(f"[red]Error processing {rel_path}: {e}[/red]")


def _run_parallel(
  data: dict[str, str],
  src_paths: dict[str, Path],
  cfg: FSCConfig,
  prompt_template: str,
  provider: BaseProvider,
  project_root: Path,
  dry_run: bool,
  index_map: dict[str, int],
  concurrency: int,
  show_progress: bool,
) -> list[Path]:
  results: list[Path] = []

  if show_progress:
    with make_file_progress(len(data), "Generating specs") as progress:
      task = progress.add_task("", total=len(data))

      with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = _submit_futures(
          executor,
          data,
          src_paths,
          cfg,
          prompt_template,
          provider,
          project_root,
          dry_run,
          index_map,
        )

        try:
          for future in as_completed(futures):
            rel_path = futures[future]
            _collect_future_result(future, rel_path, results)
            progress.update(task, advance=1)

        except KeyboardInterrupt:
          for f in futures:
            f.cancel()
          return results

  else:
    console.log(f"Processing {len(data)} files ...")

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
      futures = _submit_futures(
        executor,
        data,
        src_paths,
        cfg,
        prompt_template,
        provider,
        project_root,
        dry_run,
        index_map,
      )

      try:
        for future in as_completed(futures):
          rel_path = futures[future]
          _collect_future_result(future, rel_path, results)

      except KeyboardInterrupt:
        for f in futures:
          f.cancel()
        return results

  console.print(f"[green]Done. Processed {len(results)} files.[/green]")

  return results
