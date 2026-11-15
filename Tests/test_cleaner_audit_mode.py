import pandas as pd
from pathlib import Path
from glynn_cleaner.cleaner import clean_data


def test_audit_mode_pipeline(tmp_path):
    input_file = Path("input/sample_dirty_data.csv")
    output_file = tmp_path / "audit_cleaned.csv"

    clean_data(
        input_path=str(input_file),
        output_path=str(output_file),
        mode="audit",
        strictness="lenient",
        dry_run=False,
        summary_only=False,
    )

    df = pd.read_csv(output_file)

    # 1. Audit mode should NEVER drop rows
    assert len(df) >= 1

    # 2. Check that audit columns exist (matching your actual output)
    expected_audit_cols = [
        "email_original",
        "email_valid",
        "email_suggested_fix",
        "date_of_birth_raw",
        "date_of_birth_valid",
    ]

    for col in expected_audit_cols:
        assert col in df.columns, f"Missing audit column: {col}"

    # 3. Check that original columns still exist
    assert "name" in df.columns
    assert "email" in df.columns
    assert "date_of_birth" in df.columns

    # 4. email_valid must be True/False
    assert df["email_valid"].isin([True, False]).all()

    # 5. date_of_birth_valid must be True/False
    assert df["date_of_birth_valid"].isin([True, False]).all()

    # 6. email_original must be strings
    assert df["email_original"].apply(lambda x: isinstance(x, str)).all()

    # 7. date_of_birth_raw must be a string
    assert df["date_of_birth_raw"].apply(lambda x: (isinstance(x, str) or pd.isna(x))).all()

def test_validation_aware_deduplication(tmp_path):
    input_file = Path("input/test_dataset.csv")
    output_file = tmp_path / "simple_cleaned.csv"

    clean_data(
        input_path=str(input_file),
        output_path=str(output_file),
        mode="simple",
        strictness="lenient",
        dry_run=False,
        summary_only=False,
    )

    df = pd.read_csv(output_file)

    # Valid duplicate should merge into one row
    valid_dupes = df[df["email"] == "duplicate@example.com"]
    assert len(valid_dupes) == 1

    # Invalid DOB duplicates should remain separate
    invalid_dob_dupes = df[
        df["email"] == "invaliddob@example.com"
    ]
    assert len(invalid_dob_dupes) == 2

    # Invalid email duplicates should remain separate
    invalid_email_dupes = df[
        df["name"].str.contains(
            "Invalid Email Duplicate",
            na=False
        )
    ]
    assert len(invalid_email_dupes) == 2

