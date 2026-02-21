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
        raw = re.sub(r"[^\dA-Za-z/.\- ]", "", raw).strip()

        parsed = None

        for fmt in accepted_formats:
            try:
                parsed = datetime.strptime(raw, fmt)

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


df = pd.DataFrame({
    "date_of_birth": [
        "12/5/1990",
        "03-11-85",
        "1992.07.14",
        "14 08 1993"
    ]
})

print("INPUT:")
print(df)

df = standardise_dates(df)

print("\nOUTPUT:")
print(df)

df.to_csv("test_output.csv", index=False)
print("Saved test_output.csv")