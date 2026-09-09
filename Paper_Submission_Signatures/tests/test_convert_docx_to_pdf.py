"""Tests for convert_docx_to_pdf.py.

The actual .docx → .pdf conversion is delegated to ``docx2pdf``, which
requires Microsoft Word or LibreOffice. We don't test that here; instead
we test the pure helpers: file discovery, lock-file filtering, and
post-conversion verification.
"""
from __future__ import annotations

from convert_docx_to_pdf import (
    discover_conversion_jobs,
    is_word_lock_file,
    verify_conversion_results,
)


def _touch(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()


# ---------------------------------------------------------------------------
# is_word_lock_file
# ---------------------------------------------------------------------------

class TestIsWordLockFile:
    def test_normal_docx_is_not_lock(self):
        assert is_word_lock_file("Папка 1.docx") is False

    def test_tilde_dollar_prefix_is_lock(self):
        assert is_word_lock_file("~$пка 1.docx") is True

    def test_tilde_without_dollar_is_not_lock(self):
        assert is_word_lock_file("~something.docx") is False

    def test_empty_string(self):
        assert is_word_lock_file("") is False


# ---------------------------------------------------------------------------
# discover_conversion_jobs
# ---------------------------------------------------------------------------

class TestDiscoverConversionJobs:
    def test_empty_input_folder(self, tmp_path):
        (tmp_path / "in").mkdir()
        (tmp_path / "out").mkdir()
        pending, done, locks = discover_conversion_jobs(
            str(tmp_path / "in"), str(tmp_path / "out")
        )
        assert pending == []
        assert done == []
        assert locks == []

    def test_all_pending_when_output_is_empty(self, tmp_path):
        in_dir = tmp_path / "in"
        out_dir = tmp_path / "out"
        _touch(in_dir / "a.docx")
        _touch(in_dir / "b.docx")
        _touch(in_dir / "c.docx")
        out_dir.mkdir()

        pending, done, locks = discover_conversion_jobs(str(in_dir), str(out_dir))
        assert pending == ["a.docx", "b.docx", "c.docx"]
        assert done == []
        assert locks == []

    def test_skips_files_with_existing_pdf(self, tmp_path):
        in_dir = tmp_path / "in"
        out_dir = tmp_path / "out"
        _touch(in_dir / "a.docx")
        _touch(in_dir / "b.docx")
        _touch(in_dir / "c.docx")
        _touch(out_dir / "b.pdf")

        pending, done, locks = discover_conversion_jobs(str(in_dir), str(out_dir))
        assert pending == ["a.docx", "c.docx"]
        assert done == ["b.docx"]
        assert locks == []

    def test_ignores_non_docx_files(self, tmp_path):
        in_dir = tmp_path / "in"
        out_dir = tmp_path / "out"
        _touch(in_dir / "real.docx")
        _touch(in_dir / "readme.txt")
        _touch(in_dir / "image.png")
        _touch(in_dir / ".hidden")
        out_dir.mkdir()

        pending, done, locks = discover_conversion_jobs(str(in_dir), str(out_dir))
        assert pending == ["real.docx"]
        assert done == []
        assert locks == []

    def test_handles_uppercase_docx_extension(self, tmp_path):
        in_dir = tmp_path / "in"
        out_dir = tmp_path / "out"
        _touch(in_dir / "MIXED.DOCX")
        out_dir.mkdir()

        pending, done, locks = discover_conversion_jobs(str(in_dir), str(out_dir))
        assert pending == ["MIXED.DOCX"]

    def test_results_are_sorted(self, tmp_path):
        in_dir = tmp_path / "in"
        out_dir = tmp_path / "out"
        for name in ["zebra.docx", "alpha.docx", "mango.docx"]:
            _touch(in_dir / name)
        out_dir.mkdir()

        pending, _, _ = discover_conversion_jobs(str(in_dir), str(out_dir))
        assert pending == ["alpha.docx", "mango.docx", "zebra.docx"]

    def test_handles_bulgarian_filenames(self, tmp_path):
        in_dir = tmp_path / "in"
        out_dir = tmp_path / "out"
        _touch(in_dir / "Папка 1 с подписи от 1 до 1000.docx")
        _touch(in_dir / "Папка 2 с подписи от 1001 до 2000.docx")
        _touch(out_dir / "Папка 1 с подписи от 1 до 1000.pdf")

        pending, done, locks = discover_conversion_jobs(str(in_dir), str(out_dir))
        assert pending == ["Папка 2 с подписи от 1001 до 2000.docx"]
        assert done == ["Папка 1 с подписи от 1 до 1000.docx"]
        assert locks == []

    def test_filters_out_word_lock_files(self, tmp_path):
        """Lock files like ``~$пка 11.docx`` must be excluded."""
        in_dir = tmp_path / "in"
        out_dir = tmp_path / "out"
        _touch(in_dir / "Папка 11.docx")
        _touch(in_dir / "~$пка 11.docx")          # Word lock file
        _touch(in_dir / "~$some_other_doc.docx")   # Another lock file
        out_dir.mkdir()

        pending, done, locks = discover_conversion_jobs(str(in_dir), str(out_dir))
        assert pending == ["Папка 11.docx"]
        assert done == []
        assert sorted(locks) == ["~$some_other_doc.docx", "~$пка 11.docx"]


# ---------------------------------------------------------------------------
# verify_conversion_results
# ---------------------------------------------------------------------------

class TestVerifyConversionResults:
    def test_all_successful(self, tmp_path):
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        _touch(out_dir / "a.pdf")
        _touch(out_dir / "b.pdf")

        successful, failed = verify_conversion_results(
            ["a.docx", "b.docx"], str(out_dir)
        )
        assert successful == ["a.docx", "b.docx"]
        assert failed == []

    def test_all_failed(self, tmp_path):
        out_dir = tmp_path / "out"
        out_dir.mkdir()

        successful, failed = verify_conversion_results(
            ["a.docx", "b.docx"], str(out_dir)
        )
        assert successful == []
        assert failed == ["a.docx", "b.docx"]

    def test_mixed(self, tmp_path):
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        _touch(out_dir / "a.pdf")
        _touch(out_dir / "c.pdf")

        successful, failed = verify_conversion_results(
            ["a.docx", "b.docx", "c.docx"], str(out_dir)
        )
        assert successful == ["a.docx", "c.docx"]
        assert failed == ["b.docx"]

    def test_handles_bulgarian_filenames(self, tmp_path):
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        _touch(out_dir / "Папка 1 с подписи от 1 до 1000.pdf")

        successful, failed = verify_conversion_results(
            [
                "Папка 1 с подписи от 1 до 1000.docx",
                "Папка 2 с подписи от 1001 до 2000.docx",
            ],
            str(out_dir),
        )
        assert successful == ["Папка 1 с подписи от 1 до 1000.docx"]
        assert failed == ["Папка 2 с подписи от 1001 до 2000.docx"]
