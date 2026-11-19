import pandas as pd
from pathlib import Path

from glynn_cleaner.cleaner import clean_data


def test_quarantine_file_created(tmp_path):
    """
    Strict mode should create a quarantine file
    containing rejected rows.
    """

    input_file = Path("input/test_dataset.csv")

    output_file = tmp_path / "cleaned.csv"

    clean_data(
        input_path=str(input_file),
        output_path=str(output_file),
        mode="simple",
        strictness="strict"
    )

    quarantine_file = tmp_path / "cleaned_quarantined.csv"

    assert quarantine_file.exists()


def test_quarantine_file_contains_reason_column(tmp_path):
    """
    Quarantined rows should include a reason column.
    """

    input_file = Path("input/test_dataset.csv")

    output_file = tmp_path / "cleaned.csv"

    clean_data(
        input_path=str(input_file),
        output_path=str(output_file),
        mode="simple",
        strictness="strict"
    )

    quarantine_file = tmp_path / "cleaned_quarantined.csv"

    quarantine_df = pd.read_csv(quarantine_file)

    assert "quarantine_reason" in quarantine_df.columns


def test_quarantine_file_contains_rows(tmp_path):
    """
    Strict mode test dataset should produce
    at least one quarantined row.
    """

    input_file = Path("input/test_dataset.csv")

    output_file = tmp_path / "cleaned.csv"

    clean_data(
        input_path=str(input_file),
        output_path=str(output_file),
        mode="simple",
        strictness="strict"
    )

    quarantine_file = tmp_path / "cleaned_quarantined.csv"

    quarantine_df = pd.read_csv(quarantine_file)

    assert len(quarantine_df) > 0


def test_quarantine_reasons_are_populated(tmp_path):
    """
    Every quarantined row should have a reason.
    """

    input_file = Path("input/test_dataset.csv")

    output_file = tmp_path / "cleaned.csv"

    clean_data(
        input_path=str(input_file),
        output_path=str(output_file),
        mode="simple",
        strictness="strict"
    )

    quarantine_file = tmp_path / "cleaned_quarantined.csv"

    quarantine_df = pd.read_csv(quarantine_file)

    assert quarantine_df["quarantine_reason"].notna().all()