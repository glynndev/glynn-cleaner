import pandas as pd
import numpy as np

rows = 100_000  # bump to 200_000 or more if you like

df = pd.DataFrame({
    "name": np.random.choice(
        ["John Smith", "Sarah Jones", "Mike Brown", "Lucy Adams", "Anna Lee", "Tom Harris"],
        size=rows
    ),
    "email": np.random.choice(
        [
            "john.smith@gmail.com",
            "sarah.jones@gmail",
            "mike.brown@yahoo.com",
            "lucy.adams@hotmail.com",
            "invalid@@gmail.com",
            "   spaced @ email.com   ",
            "noatsymbol.com"
        ],
        size=rows
    ),
    "date_of_birth": np.random.choice(
        [
            "12/05/1990",
            "03-11-85",
            "1992.07.14",
            "14 08 1993",
            "",
            "32/13/2000"
        ],
        size=rows
    ),
    "notes": np.random.choice(
        ["likes football", "new starter", "", "works in sales", "   messy   spacing   "],
        size=rows
    )
})

output_path = "large_test_file.csv"
df.to_csv(output_path, index=False)
print(f"Generated {output_path} with {rows} rows")
