import pandas as pd
from pathlib import Path
from glynn_cleaner.cleaner import clean_data


def test_date_parsing(tmp_path):
    # Create a temporary CSV with mixed date formats
    input_file = tmp_path / "date_test.csv"
    input_file.write_text(
        "name,email,date_of_birth,notes\n"
        "John,john@example.com,1990-01-01,ok\n"      # already normalised
        "Lucy,lucy@example.com,14/08/1993,ok\n"      # slashes
        "Mike,mike@example.com,03.12.1985,ok\n"      # dots
        "Anna,anna@example.com,12 11 1980,ok\n"      # spaces
        "Bad,bad@example.com,not-a-date,fail\n"      # invalid
    )

    output_file = tmp_path / "cleaned.csv"

    clean_data(
        input_path=str(input_file),
        output_path=str(output_file),
        mode="audit",
        strictness="lenient",
        dry_run=False,
        summary_only=False,
    )

    df = pd.read_csv(output_file)

    # 1. All rows should remain in lenient mode
    assert len(df) == 5

    # 2. Check normalised date output
    assert df.loc[0, "date_of_birth"] == "1990-01-01"
    assert df.loc[1, "date_of_birth"] == "1993-08-14"
    assert df.loc[2, "date_of_birth"] == "1985-12-03"
    assert df.loc[3, "date_of_birth"] == "1980-11-12"

    # 3. Invalid date should be blank but preserved in raw column
    assert pd.isna(df.loc[4, "date_of_birth"])
    assert df.loc[4, "date_of_birth_raw"] == "not-a-date"
    assert bool(df.loc[4, "date_of_birth_valid"]) is False

