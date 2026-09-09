# Book of Initials

A single Python script that turns a CSV of signatory names into a
printable A5 Word document listing just their initials (e.g. `И. И.`),
in the **Bebas Neue Cyrillic** font.

This workflow is independent of the paper-submission one — you only
need what's listed below.

---

## About this code

This toolkit was written with help from an AI assistant (Claude by
Anthropic) and reviewed by a human. The code is intentionally written
to be readable by people who aren't programmers.

If anything here is unclear, if you want to verify how a script works,
or if you have a question this README doesn't answer — paste the
relevant code or text into an AI assistant (Claude, ChatGPT, etc.) and
ask. The AI can explain how each part works or help you adapt it.

---

## Quick start

1. Install Python 3.9+ from <https://www.python.org/downloads/>
   (on Windows, tick *"Add Python to PATH"* during installation).
2. Install the bundled **Bebas Neue Cyrillic** font
   (`bebasneuecyrillic.ttf`) — see [Installing the font](#installing-the-font).
3. Open PowerShell (Windows) or Terminal (macOS/Linux) **in this
   folder** and install the dependencies. Using a virtual environment
   is recommended on every OS, and is **required on most current Linux
   distributions** (Debian/Ubuntu/Mint 24+), which block installing
   into the system Python:

   **Linux / macOS:**
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

   **Windows (PowerShell):**
   ```
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

   The virtual environment lives in a `.venv/` folder next to the
   script. Activate it once per terminal session (run the `activate`
   line again in a new terminal) — you'll see `(.venv)` at the start
   of your prompt when it's active.

   > If you prefer not to use a virtual environment on Linux and
   > understand the risk, you can instead run
   > `pip install -r requirements.txt --break-system-packages`, but the
   > virtual environment above is the clean, recommended approach.

4. Put your CSV file `book_signatures_only_names.csv` next to the
   script and run (with the virtual environment active):

   ```
   python generate_initials_book.py
   ```
On average it takes around 7 minutes for full execution.

The output `book_signatures_initials.docx` appears in the same folder.

---

## Installing the font

The font file `bebasneuecyrillic.ttf` is bundled in this folder. After
installing, it registers itself on your system as **`Bebas Neue
Cyrillic`** — that is the exact name the script looks for.

### Windows

The simplest way is to double-click `bebasneuecyrillic.ttf` and press
**Install**. Or, from PowerShell in this folder:

```
Start-Process .\bebasneuecyrillic.ttf
```

…then press **Install** in the window that opens.

### macOS

Double-click the file and press **Install Font**, or from Terminal in
this folder:

```
cp bebasneuecyrillic.ttf ~/Library/Fonts/
```

### Linux

From Terminal in this folder:

```
mkdir -p ~/.local/share/fonts && cp bebasneuecyrillic.ttf ~/.local/share/fonts/ && fc-cache -f
```

After installing, confirm the exact family name your system reports —
on Linux it should match the `FONT_NAME` in the script
(`Bebas Neue Cyrillic`):

```
fc-list | grep -i bebas
```

If the name shown differs, set `FONT_NAME` in
`generate_initials_book.py` to exactly what `fc-list` reports.

---

## What the input should look like

A CSV with **two columns**: first name and last name, one signatory
per row. Any common separator works (comma, semicolon, tab, pipe).
Example:

```
Иван,Иванов
Петър,Петров
Мария,Маринова
```

Headers are *not* expected — the script reads from the very first row.

## What the output looks like

A single-column A5 document, one set of initials per line:

```
И. И.
П. П.
М. М.
```

Font: **Bebas Neue Cyrillic** at 10pt. Margins: 1.5 cm on all sides.

---

## Customising the script

Open `generate_initials_book.py` in any text editor. The first thing
in the file is a `# Configuration` block of `UPPER_CASE` variables:

- `INPUT_CSV`, `OUTPUT_DOCX` — file names
- `FONT_NAME`, `FONT_SIZE_PT` — font settings (must match the font
  installed on your system)
- `PAGE_WIDTH_CM`, `PAGE_HEIGHT_CM`, `PAGE_MARGIN_CM` — page layout

Save the file and re-run the script.

---

## Running the tests (for developers)

The project ships with a small `pytest` test suite covering the pure
helpers in `generate_initials_book.py`. To run it (with the virtual
environment from [Quick start](#quick-start) active):

```
pip install -r test_requirements.txt
python -m pytest
```

A successful run looks like:

```
======================== test session starts ========================
collected 19 items

tests/test_generate_initials_book.py ...................          [100%]

======================== 19 passed in 0.4s ==========================
```

If you change the configuration or the logic and the tests still pass,
you can be confident you haven't broken any of the behaviour the tests
cover (initial extraction, CSV parsing, document construction).

---

## Troubleshooting

- **`file '…' not found in this folder`** — make sure the CSV is in
  the same folder as the script and the name matches exactly,
  including capitalisation.
- **`Could not parse '…' into at least two columns`** — open the file
  in a text editor and check that columns are separated by commas,
  semicolons, tabs, or `|`. If possible, re-save as UTF-8.
- **The initials look like rectangles or the font looks wrong** — the
  Bebas Neue Cyrillic font isn't installed on your system. Install it
  using one of the commands above and re-run. If you're on Windows,
  close Word completely before re-running so it picks up the newly
  installed font.
- **`pip` is not recognised** — Python wasn't added to PATH. Re-install
  Python and tick *"Add Python to PATH"*, or use `py -m pip …`
  instead.
- **`error: externally-managed-environment`** (Linux) — your
  distribution blocks installing packages into the system Python. Use
  the virtual environment shown in [Quick start](#quick-start)
  (`python3 -m venv .venv && source .venv/bin/activate`) and run `pip`
  inside it. This is the recommended fix.
- **The initials look wrong only on Linux** — the installed font may
  register under a slightly different family name. Run
  `fc-list | grep -i bebas` and set `FONT_NAME` in the script to match
  exactly what it reports.

If your problem isn't here, paste the error and the relevant script
into an AI assistant (Claude, ChatGPT, etc.) — it can usually
diagnose it from the script and the message alone.

---

## Folder layout

```
book_of_initials/
├── README.md
├── .gitignore
├── requirements.txt
├── test_requirements.txt                   (extras for running tests)
├── bebasneuecyrillic.ttf                   (bundled font, install once)
├── generate_initials_book.py
├── tests/
│   ├── conftest.py
│   └── test_generate_initials_book.py
├── book_signatures_only_names.csv          (your input)
└── book_signatures_initials.docx           (the generated output)
```

> The `.venv/` folder (created by the Quick start) and the generated
> `book_signatures_initials.docx` are intentionally excluded from
> version control via `.gitignore`.

The older `ForBookInitials2.py` is not used by this workflow but can
be kept in a `legacy/` subfolder for reference.
