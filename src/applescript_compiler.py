from __future__ import annotations
import subprocess
from pathlib import Path


def compile_applescript(source_path: Path) -> str:
    compiled_path: Path = source_path.with_suffix(".scpt")
    compiled_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "osacompile",
        "-o",
        str(compiled_path),
        str(source_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(
            f"osacompile failed\n"
            f"cmd: {' '.join(cmd)}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
    return result.stdout.strip()


def run_compiled_script(compiled_path: Path, args: list[str]) -> str:
    cmd = ["osascript", str(compiled_path), *args]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(
            f"osascript failed\n"
            f"cmd: {' '.join(cmd)}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    return result.stdout.strip()
