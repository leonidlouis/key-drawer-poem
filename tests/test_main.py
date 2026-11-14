import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import main  # noqa: E402


def run_entry(script_dir: Path, out_dir: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ, MAKEFUN_OUTPUT_DIR=str(out_dir))
    return subprocess.run(
        [sys.executable, "-I", str(script_dir / "main.py")],
        env=env, capture_output=True, text=True, timeout=30,
    )


class DeterminismTest(unittest.TestCase):
    def test_two_runs_write_identical_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp, "a"), Path(tmp, "b", "nested")  # b does not exist yet
            for out in (a, b):
                proc = run_entry(ROOT, out)
                self.assertEqual(proc.returncode, 0, proc.stderr)
            data = (a / "entry.txt").read_bytes()
            self.assertEqual(data, (b / "entry.txt").read_bytes())

    def test_shipped_poem_passes_gate(self):
        text = main.prepare(main.POEM_PATH.read_bytes())
        self.assertTrue(1 <= len(text) <= 1000)
        self.assertTrue(text.strip())
        self.assertTrue(text.endswith("\n") and not text.endswith("\n\n"))
        self.assertNotIn("\r", text)
        self.assertTrue(text.startswith("Kerak\n"))
        self.assertTrue(text.endswith("if someone stays at the stove.\n"))


class PrepareTest(unittest.TestCase):
    def test_length_limits(self):
        self.assertEqual(main.prepare(b"x"), "x\n")  # 2 chars, lower bound fine
        self.assertEqual(len(main.prepare(b"x" * 999)), 1000)
        with self.assertRaises(main.PoemError):
            main.prepare(b"x" * 1000)  # 1001 with the newline

    def test_counts_code_points_not_bytes(self):
        poem = ("é" * 999).encode("utf-8")  # 1998 bytes, 999 code points
        self.assertEqual(len(main.prepare(poem)), 1000)

    def test_refuses_empty_and_whitespace(self):
        for raw in (b"", b"   ", b"\n\n", b"\t \r\n", "﻿　".encode()):
            with self.subTest(raw=raw), self.assertRaises(main.PoemError):
                main.prepare(raw)

    def test_refuses_invalid_utf8(self):
        with self.assertRaises(main.PoemError):
            main.prepare(b"caf\xe9\n")

    def test_normalises_line_ends_and_trailing_newlines(self):
        self.assertEqual(main.prepare(b"a\r\nb\rc\n\n\n"), "a\nb\nc\n")
        self.assertEqual(main.prepare("﻿a".encode()), "a\n")


class BadInputExitTest(unittest.TestCase):
    def check_refused(self, poem: bytes | None):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            shutil.copy(ROOT / "main.py", tmp / "main.py")
            if poem is not None:
                (tmp / "poem.txt").write_bytes(poem)
            proc = run_entry(tmp, tmp / "out")
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("error:", proc.stderr)
            self.assertFalse((tmp / "out" / "entry.txt").exists())

    def test_too_long(self):
        self.check_refused(b"word " * 300)

    def test_whitespace_only(self):
        self.check_refused(b" \n \n")

    def test_bad_encoding(self):
        self.check_refused(b"\xff\xfe\x00poem")

    def test_missing_poem(self):
        self.check_refused(None)


if __name__ == "__main__":
    unittest.main()
