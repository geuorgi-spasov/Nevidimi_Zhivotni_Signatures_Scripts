"""Tests for generate_initials_book.py."""
from __future__ import annotations

import pandas as pd
import pytest

from generate_initials_book import (
    build_initials_document,
    names_to_initials,
    read_two_column_csv,
)


# ---------------------------------------------------------------------------
# names_to_initials
# ---------------------------------------------------------------------------

class TestNamesToInitials:
    def test_single_full_name(self):
        df = pd.DataFrame([["Иван", "Иванов"]])
        assert names_to_initials(df) == ["И. И."]

    def test_multiple_rows(self):
        df = pd.DataFrame(
            [["Иван", "Иванов"], ["Петър", "Петров"], ["Мария", "Маринова"]]
        )
        assert names_to_initials(df) == ["И. И.", "П. П.", "М. М."]

    def test_latin_names(self):
        df = pd.DataFrame([["John", "Smith"], ["Jane", "Doe"]])
        assert names_to_initials(df) == ["J. S.", "J. D."]

    def test_lowercase_input_uppercased_in_output(self):
        df = pd.DataFrame([["иван", "иванов"]])
        assert names_to_initials(df) == ["И. И."]

    def test_surrounding_whitespace_stripped(self):
        df = pd.DataFrame([["  Иван  ", "  Иванов  "]])
        assert names_to_initials(df) == ["И. И."]

    def test_missing_last_name_uses_only_first(self):
        df = pd.DataFrame([["Иван", None]])
        assert names_to_initials(df) == ["И."]

    def test_missing_first_name_uses_only_last(self):
        df = pd.DataFrame([[None, "Иванов"]])
        assert names_to_initials(df) == ["И."]

    def test_both_names_missing_row_skipped(self):
        df = pd.DataFrame([[None, None]])
        assert names_to_initials(df) == []

    def test_empty_string_names_row_skipped(self):
        df = pd.DataFrame([["", ""]])
        assert names_to_initials(df) == []

    def test_empty_dataframe(self):
        df = pd.DataFrame(columns=[0, 1])
        assert names_to_initials(df) == []

    def test_mixed_complete_and_partial_rows(self):
        df = pd.DataFrame(
            [
                ["Иван", "Иванов"],
                [None, "Петров"],
                ["Мария", None],
                [None, None],
                ["Георги", "Георгиев"],
            ]
        )
        assert names_to_initials(df) == ["И. И.", "П.", "М.", "Г. Г."]


# ---------------------------------------------------------------------------
# read_two_column_csv
# ---------------------------------------------------------------------------

class TestReadTwoColumnCsv:
    def test_reads_comma_separated(self, tmp_path):
        csv = tmp_path / "names.csv"
        csv.write_text("Иван,Иванов\nПетър,Петров\n", encoding="utf-8")
        df = read_two_column_csv(str(csv))
        assert len(df) == 2
        assert df.iloc[0, 0] == "Иван"
        assert df.iloc[0, 1] == "Иванов"

    def test_reads_semicolon_separated(self, tmp_path):
        csv = tmp_path / "names.csv"
        csv.write_text("Иван;Иванов\nПетър;Петров\n", encoding="utf-8")
        df = read_two_column_csv(str(csv))
        assert len(df) == 2
        assert df.iloc[1, 1] == "Петров"

    def test_reads_tab_separated(self, tmp_path):
        csv = tmp_path / "names.tsv"
        csv.write_text("Иван\tИванов\nПетър\tПетров\n", encoding="utf-8")
        df = read_two_column_csv(str(csv))
        assert len(df) == 2

    def test_raises_on_single_column_file(self, tmp_path):
        csv = tmp_path / "broken.csv"
        csv.write_text("just_one_column\nstill_one\n", encoding="utf-8")
        with pytest.raises(ValueError):
            read_two_column_csv(str(csv))

    def test_raises_on_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            read_two_column_csv(str(tmp_path / "does_not_exist.csv"))


# ---------------------------------------------------------------------------
# build_initials_document
# ---------------------------------------------------------------------------

class TestBuildInitialsDocument:
    def test_one_paragraph_per_initial(self):
        doc = build_initials_document(["И. И.", "П. П.", "М. М."])
        non_empty = [p.text for p in doc.paragraphs if p.text]
        assert non_empty == ["И. И.", "П. П.", "М. М."]

    def test_empty_input_produces_empty_document(self):
        doc = build_initials_document([])
        assert [p.text for p in doc.paragraphs if p.text] == []

    def test_uses_configured_font(self):
        from generate_initials_book import FONT_NAME

        doc = build_initials_document(["И. И."])
        assert doc.styles["Normal"].font.name == FONT_NAME
