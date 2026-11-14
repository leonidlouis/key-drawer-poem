# Kerak — make.fun agency-poem-01 entry

A poem about agency, "Kerak" (Indonesian for the rice crust at the bottom of the pot), written to `entry.txt` by a small Python 3.13 program
(standard library only, no network).

## Layout

- `poem.txt` — the poem, the single source of truth.
- `main.py` — reads `poem.txt`, validates it against the contest gate, and
  writes it to `<output>/entry.txt`.
- `tests/test_main.py` — unittest suite.

## What `main.py` does

1. Reads `poem.txt` (next to `main.py`) as bytes and decodes it as strict UTF-8
   (a leading BOM is dropped).
2. Normalises `\r\n` and `\r` to `\n` and ends the text with exactly one `\n`.
3. Refuses the poem, exiting with status 1 and an `error:` message on stderr,
   if it is not UTF-8, is empty or only white space, or exceeds 1,000
   characters (Unicode code points, line ends included).
4. Writes the bytes to `$MAKEFUN_OUTPUT_DIR/entry.txt`, or `/output/entry.txt`
   when the variable is unset, creating the directory if needed.

The output depends only on `poem.txt`, so every run writes identical bytes.

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Test

```sh
python3 -m unittest discover -s tests -v
```

## License

MIT — see `LICENSE`.
