import pandas as pd
from pathlib import Path
from glynn_cleaner.cleaner import clean_data


def test_duplicate_row_removal(tmp_path):
    # Create a temporary CSV with duplicates
    input_file = tmp_path / "dupe_test.csv"
    input_file.write_text(
        "name,email,date_of_birth,notes\n"
        "John,john@example.com,1990-01-01,ok\n"
        "John , john@example.com ,1990-01-01 ,ok\n"  # duplicate with whitespace
        "JOHN,JOHN@EXAMPLE.COM,1990-01-01,ok\n"      # duplicate with case differences
        "Lucy,lucy@example.com,1993-08-14,valid\n"   # unique row
    )

    output_file = tmp_path / "cleaned.csv"

    clean_data(
        input_path=str(input_file),
        output_path=str(output_file),
        mode="simple",
        strictness="lenient",
        dry_run=False,
        summary_only=False,
    )

    df = pd.read_csv(output_file)

    # Only 2 unique rows should remain
    assert len(df) == 2

    # Check the remaining rows are the correct ones
    names = sorted(df["name"].tolist())
    assert names == ["John", "Lucy"]

    # Check the email for John is normalised and correct
    john_row = df[df["name"] == "John"].iloc[0]
    assert john_row["email"] == "john@example.com"
    assert john_row["date_of_birth"] == "1990-01-01"
