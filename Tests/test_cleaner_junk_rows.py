import pandas as pd
from pathlib import Path
from glynn_cleaner.cleaner import clean_data


def test_junk_row_removal(tmp_path):
    # Create a temporary CSV with junk rows
    input_file = tmp_path / "junk_test.csv"
    input_file.write_text(
        "name,email,date_of_birth,notes\n"
        ",,,\n"               # empty row
        "\"\",\"\",\"\",\"\"\n"  # quotes-only row
        "   ,   ,   ,   \n"   # whitespace row
        "John,john@example.com,1990-01-01,ok\n"  # valid row
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

    # Only the valid row should remain
    assert len(df) == 1

    # Check the remaining row is the correct one
    assert df.iloc[0]["name"] == "John"
    assert df.iloc[0]["email"] == "john@example.com"
    assert df.iloc[0]["date_of_birth"] == "1990-01-01"
