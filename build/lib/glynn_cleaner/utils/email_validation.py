import re
import pandas as pd

def validate_emails(df):
    # If the column isn't present, skip
    if "email" not in df.columns:
        return df

    # Normalise formatting but DO NOT convert missing values to strings
    df["email"] = (
        df["email"]
        .astype("string") # preserves <NA> properly
        .str.strip()
        .str.replace(" ", "", regex=False)
        .str.lower()
    )

    # Validation pattern: must contain @ and a dot in the domain
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    df["email_valid"] = df["email"].apply(
        lambda x: bool(re.match(pattern, x)) if pd.notna(x) else False
    )

    return df
