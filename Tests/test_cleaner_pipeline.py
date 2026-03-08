import pandas as pd
from pathlib import Path
from glynn_cleaner.cleaner import clean_data

def test_full_cleaning_pipeline(tmp_path):
    # Use your existing sample_dirty_data.csv
    input_file = Path("input/sample_dirty_data.csv")
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

    # Basic sanity checks — these will pass regardless of your exact data
    assert len(df) > 0
    assert "name" in df.columns
    assert "email" in df.columns
    assert "date_of_birth" in df.columns

    # Check that names are capitalised
    assert all(
        isinstance(name, str) and name == name.title()
        for name in df["name"]
        if isinstance(name, str)
    )

    # Check that emails are cleaned (no leading/trailing spaces)
    assert all(
        isinstance(email, str) and email == email.strip()
        for email in df["email"]
        if isinstance(email, str)
    )

    # Check that date_of_birth is normalised or blank
    for dob in df["date_of_birth"]:
        if isinstance(dob, str) and dob.strip():
            assert len(dob) == 10  # YYYY-MM-DD
            assert dob.count("-") == 2
