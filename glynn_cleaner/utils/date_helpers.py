from datetime import datetime
import pandas as pd
import re

def standardise_dates(df):
    accepted_formats = [
        "%d/%m/%Y",
        "%d/%m/%y",
        "%d-%m-%Y",
        "%d-%m-%y",
        "%d.%m.%Y",
        "%d.%m.%y",
        "%d %m %Y",
        "%d %m %y",
    ]

    parsed_dates = []
    validity_flags = []

    for raw in df["date_of_birth"].astype(str):

        # Clean hidden characters
        raw = raw.replace("\ufeff", "")
        raw = raw.replace("\u200b", "")
        raw = raw.replace("\u00a0", " ")
        raw = re.sub(r"[^0-9/\-.\s]", "", raw)
        raw = re.sub(r"\s+", " ", raw).strip()

        parsed = None

        for fmt in accepted_formats:
            try:
                parsed = datetime.strptime(raw, fmt)

                # Fix 2-digit years
                if parsed.year < 100:
                    parsed = parsed.replace(year=parsed.year + 1900)

                break
            except:
                continue

        if parsed:
            validity_flags.append(True)
            parsed_dates.append(parsed.strftime("%d/%m/%Y"))
        else:
            validity_flags.append(False)
            parsed_dates.append(pd.NA)

    df["date_of_birth"] = parsed_dates
    df["date_of_birth_valid"] = validity_flags

    return df


def suggest_date_fix(date_str):

    # Convert to string safely
    if date_str is None or pd.isna(date_str):
        return ""

    s = str(date_str).strip()

    # Ignore junk values
    if s.lower() in ["nan", "nat", "none", "null", ""]:
        return ""

    # Match formats like dd/mm/yyyy, dd-mm-yy, dd mm yyyy, dd.mm.yyyy
    m = re.match(
        r"^(\d{1,2})[./\-\s](\d{1,2})[./\-\s](\d{2}|\d{4})$",
        s
    )

    if m:
        day, month, year = m.groups()

        # Expand 2-digit years
        if len(year) == 2:
            year = "19" + year

        # Validate and format
        try:
            parsed = pd.to_datetime(f"{day}-{month}-{year}", dayfirst=True)
            formatted = parsed.strftime("%d:%m:%Y")

            # Excel-safe text literal
            return f'="{formatted}"'

        except:
            return "Invalid day/month combination"

    return "Expected Format Dd:Mm:Yyyy"