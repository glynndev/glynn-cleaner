import pandas as pd
from pathlib import Path
from glynn_cleaner.cleaner import clean_data


def test_strict_mode_pipeline(tmp_path):
    input_file = Path("input/sample_dirty_data.csv")
    output_file = tmp_path / "strict_cleaned.csv"

    clean_data(
        input_path=str(input_file),
        output_path=str(output_file),
        mode="simple",
        strictness="strict",
        dry_run=False,
        summary_only=False,
    )

    df = pd.read_csv(output_file)

    # 1. Strict mode should only keep rows with:
    #    - valid email
    #    - valid date
    #    - non-disposable domain
    #    - non-role-based email
    #    - valid format
    assert len(df) > 0  # sanity check

    # 2. Every email must be valid under strict rules
    from glynn_cleaner.helpers.email_utils import is_valid_email_strict

    for email in df["email"]:
        assert is_valid_email_strict(email)

    # 3. Every date must be valid and normalised
    for dob in df["date_of_birth"]:
        if isinstance(dob, str) and dob.strip():
            assert len(dob) == 10
            assert dob.count("-") == 2

    # 4. No disposable domains should remain
    from glynn_cleaner.helpers.email_disposable_loader import load_disposable_domains

    disposable = load_disposable_domains()
    for email in df["email"]:
        if "@" in email:
            domain = email.split("@")[1].lower()
            assert domain not in disposable

    # 5. No role-based emails should remain
    from glynn_cleaner.helpers.email_utils import ROLE_BASED_PREFIXES

    for email in df["email"]:
        local = email.split("@")[0].lower()
        assert local not in ROLE_BASED_PREFIXES
