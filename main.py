"""agency-poem-01 entry: write poem.txt to <output>/entry.txt.

The output directory is $MAKEFUN_OUTPUT_DIR if set, else /output (as in the kit).
The poem is validated against the gate: UTF-8, 1 to 1,000 characters (Unicode
code points, line ends included), not only white space. Output is deterministic:
the same poem.txt always yields the same bytes.

    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import sys
from pathlib import Path

POEM_PATH = Path(__file__).resolve().parent / "poem.txt"
MAX_CHARS = 1000


class PoemError(ValueError):
    """The poem cannot be submitted as it is."""


def prepare(raw: bytes) -> str:
    """Decode, normalise and validate the poem; return the exact text to write."""
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PoemError(f"poem is not valid UTF-8 ({exc})") from None
    text = text.removeprefix("﻿")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if not text.strip():
        raise PoemError("poem is empty or only white space")
    text = text.rstrip("\n") + "\n"
    if len(text) > MAX_CHARS:
        raise PoemError(f"poem is {len(text)} characters; the limit is {MAX_CHARS}")
    return text


def output_dir() -> Path:
    return Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")


def run(poem_path: Path = POEM_PATH, out_dir: Path | None = None) -> tuple[Path, int]:
    out_dir = output_dir() if out_dir is None else out_dir
    try:
        raw = poem_path.read_bytes()
    except OSError as exc:
        raise PoemError(f"cannot read {poem_path}: {exc.strerror}") from None
    text = prepare(raw)
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.txt"
    target.write_bytes(text.encode("utf-8"))
    return target, len(text)


def main() -> int:
    try:
        target, chars = run()
    except PoemError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"error: cannot write output: {exc}", file=sys.stderr)
        return 1
    print(f"wrote {target} ({chars} characters)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
