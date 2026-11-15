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

def test_note_merging_behaviour(tmp_path):
    input_file = Path("input/test_dataset.csv")
    output_file = tmp_path / "notes_test.csv"

    clean_data(
        input_path=str(input_file),
        output_path=str(output_file),
        mode="simple",
        strictness="lenient",
        dry_run=False,
        summary_only=False,
    )

    df = pd.read_csv(output_file)

    duplicate_notes = df[
        df["email"] == "duplicatenotes@example.com"
    ].iloc[0]

    assert duplicate_notes["notes"] == "Training required"

    blank_note = df[
        df["email"] == "blanknote@example.com"
    ].iloc[0]

    assert blank_note["notes"] == "DBS completed"

    merged_notes = df[
        df["email"] == "mergednotes@example.com"
    ].iloc[0]

    assert merged_notes["notes"] == "DBS completed; Training required"

def test_email_edge_cases(tmp_path):
    input_file = Path("input/test_dataset.csv")
    output_file = tmp_path / "email_test.csv"

    clean_data(
        input_path=str(input_file),
        output_path=str(output_file),
        mode="simple",
        strictness="lenient",
        dry_run=False,
        summary_only=False,
    )

    df = pd.read_csv(output_file)

    # Mixed-case emails should merge
    mixed_case = df[
        df["notes"].str.contains(
            "Upper case email",
            na=False
        )
    ]

    assert len(mixed_case) == 1

    notes = mixed_case.iloc[0]["notes"]

    assert "Upper case email" in notes
    assert "Mixed case email" in notes
    assert "Lower case email" in notes

    notes = mixed_case.iloc[0]["notes"]

    assert "Upper case email" in notes
    assert "Mixed case email" in notes
    assert "Lower case email" in notes

    # Plus addressing should be preserved
    assert (
        df["email"] == "john+newsletter@gmail.com"
    ).any()

    # Dotted local part should be preserved
    assert (
        df["email"] == "john.smith@gmail.com"
    ).any()

    # Subdomains should be valid
    assert (
        df["email"] == "john@hr.company.com"
    ).any()

    # Long TLDs should be valid
    assert (
        df["email"] == "john@example.technology"
    ).any()

def test_strict_mode_filtering(tmp_path):
    input_file = Path("input/test_dataset.csv")

    lenient_output = tmp_path / "lenient.csv"
    strict_output = tmp_path / "strict.csv"

    clean_data(
        input_path=str(input_file),
        output_path=str(lenient_output),
        mode="simple",
        strictness="lenient",
        dry_run=False,
        summary_only=False,
    )

    clean_data(
        input_path=str(input_file),
        output_path=str(strict_output),
        mode="simple",
        strictness="strict",
        dry_run=False,
        summary_only=False,
    )

    lenient_df = pd.read_csv(lenient_output)
    strict_df = pd.read_csv(strict_output)

    # Control record survives both modes
    assert (
        lenient_df["name"] == "Strict Control Record"
    ).any()

    assert (
        strict_df["name"] == "Strict Control Record"
    ).any()

    # Invalid email survives lenient mode
    assert (
        lenient_df["name"] == "Strict Invalid Email"
    ).any()

    # Invalid email removed in strict mode
    assert not (
        strict_df["name"] == "Strict Invalid Email"
    ).any()

    # UK-format date survives lenient mode
    assert (
        lenient_df["name"] == "Strict Ambiguous Dob"
    ).any()

    # UK-format date also survives strict mode
    assert (
        strict_df["name"] == "Strict Ambiguous Dob"
    ).any()
