import pandas as pd
from pathlib import Path
from glynn_cleaner.cleaner import clean_data


def test_summary_only_mode(tmp_path):
    input_file = tmp_path / "summary_test.csv"
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
        dry_run=False,
        summary_only=True,
    )

    # Cleaned CSV should NOT exist
    assert not output_file.exists()

    # Summary CSV should exist
    summary_file = tmp_path / "cleaned_summary.csv"
    assert summary_file.exists()

    # Report file should exist
    report_file = tmp_path / "cleaned_report.txt"
    assert report_file.exists()
