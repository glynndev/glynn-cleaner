from pathlib import Path
from glynn_cleaner.cleaner import clean_data


def test_dry_run_mode(tmp_path):
    input_file = tmp_path / "dry_run_test.csv"
    input_file.write_text(
        "name,email,date_of_birth,notes\n"
        "John,john@example.com,1990-01-01,ok\n"
    )

    output_file = tmp_path / "cleaned.csv"

    clean_data(
        input_path=str(input_file),
        output_path=str(output_file),
        mode="simple",
        strictness="lenient",
        dry_run=True,
        summary_only=False,
    )

    # No files should be written in dry-run mode
    assert not output_file.exists()
    assert not (tmp_path / "cleaned_summary.csv").exists()
    assert not (tmp_path / "cleaned_report.txt").exists()
