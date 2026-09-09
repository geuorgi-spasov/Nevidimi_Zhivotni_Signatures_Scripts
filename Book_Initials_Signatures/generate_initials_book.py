"""
Generates a printable book of signatory initials from a CSV of names.

Reads a CSV with two columns (first name, last name), turns each row into
initials like ``И. И.`` (first letter of each name) and writes them, one per
line, into a single-column A5 Word document using the Bebas Neue Cyrillic
font.

Usage:
    python generate_initials_book.py

See README.md for the full workflow.
"""

from __future__ import annotations

import time

import numpy as np
import pandas as pd
from docx import Document
from docx.document import Document as DocumentType
from docx.shared import Cm, Pt

# ---------------------------------------------------------------------------
# Configuration — change these if your file names or layout differ
# ---------------------------------------------------------------------------

INPUT_CSV = "book_signatures_only_names.csv"
OUTPUT_DOCX = "book_signatures_initials.docx"

# The font must be installed on your system. The exact name has to match
# what your OS reports for the installed font. The bundled file
# `bebasneuecyrillic.ttf` registers itself as "Bebas Neue Cyrillic".
FONT_NAME = "Bebas Neue Cyrillic"
FONT_SIZE_PT = 10

# A5 page size and uniform margins (in centimeters)
PAGE_WIDTH_CM = 14.8
PAGE_HEIGHT_CM = 21.0
PAGE_MARGIN_CM = 1.5

# Separators tried when auto-detecting the CSV format
CSV_SEPARATORS = [",", ";", "\t", "|"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _format_duration(seconds: float) -> str:
    """Format seconds as ``'Xs'`` or ``'Xm Ys'``."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    return f"{int(seconds) // 60}m {int(seconds) % 60}s"


def read_two_column_csv(path: str) -> pd.DataFrame:
    """Read a CSV, trying common separators until one yields >1 column."""
    for sep in CSV_SEPARATORS:
        try:
            df = pd.read_csv(path, header=None, sep=sep)
        except FileNotFoundError:
            raise
        except Exception:
            continue
        if len(df.columns) > 1:
            print(f"  Read '{path}' using separator {sep!r}.")
            return df
    raise ValueError(
        f"Could not parse '{path}' into at least two columns. "
        f"Tried separators: {CSV_SEPARATORS}"
    )


def names_to_initials(df: pd.DataFrame) -> list[str]:
    """Extract initials from each (first_name, last_name) row.

    Uses vectorized pandas operations (~20× faster than row-by-row
    iteration on large datasets).
    """
    first_raw = df.iloc[:, 0].fillna("").astype(str).str.strip()
    last_raw = df.iloc[:, 1].fillna("").astype(str).str.strip()

    fi = first_raw.str[:1].str.upper().where(first_raw != "", "")
    li = last_raw.str[:1].str.upper().where(last_raw != "", "")

    has_f = fi != ""
    has_l = li != ""

    result = np.select(
        [has_f & has_l, has_f & ~has_l, ~has_f & has_l],
        [fi + ". " + li + ".", fi + ".", li + "."],
        default="",
    )
    return [r for r in result if r]


def build_initials_document(initials: list[str]) -> DocumentType:
    """Build an A5 Word document with one set of initials per line.

    Prints inline progress with ETA during the build.
    """
    doc = Document()

    # Page size and margins
    section = doc.sections[0]
    section.page_width = Cm(PAGE_WIDTH_CM)
    section.page_height = Cm(PAGE_HEIGHT_CM)
    section.left_margin = Cm(PAGE_MARGIN_CM)
    section.right_margin = Cm(PAGE_MARGIN_CM)
    section.top_margin = Cm(PAGE_MARGIN_CM)
    section.bottom_margin = Cm(PAGE_MARGIN_CM)

    # Make every paragraph use the chosen font, size, and tight spacing
    style = doc.styles["Normal"]
    style.font.name = FONT_NAME
    style.font.size = Pt(FONT_SIZE_PT)
    pf = style.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = 1.0

    total = len(initials)
    report_every = max(1, total // 20)  # ~20 progress updates
    start = time.perf_counter()

    for i, text in enumerate(initials, 1):
        doc.add_paragraph(text)
        if i % report_every == 0 or i == total:
            elapsed = time.perf_counter() - start
            eta = elapsed / i * (total - i)
            print(
                f"\r  Building: {i:,}/{total:,} ({i * 100 // total}%)"
                f" — ~{_format_duration(eta)} remaining   ",
                end="",
                flush=True,
            )

    if total > 0:
        elapsed = time.perf_counter() - start
        print(f"\r  Building: {total:,}/{total:,} (100%)"
              f" — done in {_format_duration(elapsed)}        ")

    return doc


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    overall_start = time.perf_counter()

    print(f"Reading '{INPUT_CSV}'...")
    try:
        df = read_two_column_csv(INPUT_CSV)
    except FileNotFoundError:
        print(f"ERROR: file '{INPUT_CSV}' not found in this folder.")
        return
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return

    print(f"  {len(df):,} rows. Extracting initials...")
    initials = names_to_initials(df)
    print(f"  {len(initials):,} initials extracted.\n")

    print(f"Building document ({FONT_NAME}, {FONT_SIZE_PT}pt)...")
    doc = build_initials_document(initials)

    print(f"\nSaving '{OUTPUT_DOCX}'...")
    doc.save(OUTPUT_DOCX)

    total = time.perf_counter() - overall_start
    print(f"\nDone in {_format_duration(total)}. Saved as '{OUTPUT_DOCX}'.")


if __name__ == "__main__":
    main()
