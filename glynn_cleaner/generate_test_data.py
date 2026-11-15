import pandas as pd

rows = []

# --------------------------------------------------
# Group 1 - Perfect records (100)
# --------------------------------------------------

for i in range(1, 101):
    rows.append({
        "name": f"Person {i}",
        "email": f"person{i}@example.com",
        "date_of_birth": f"1980-01-{(i % 28) + 1:02d}",
        "notes": "Valid record"
    })

# --------------------------------------------------
# Group 2 - Exact duplicates (25 pairs = 50 rows)
# --------------------------------------------------

for i in range(1, 26):
    record = {
        "name": f"Duplicate {i}",
        "email": f"duplicate{i}@example.com",
        "date_of_birth": f"1975-02-{(i % 28) + 1:02d}",
        "notes": "Exact duplicate"
    }

    rows.append(record.copy())
    rows.append(record.copy())

# --------------------------------------------------
# Group 3 - Identity merge test (50 rows)
# Same email + DOB but different notes
# --------------------------------------------------

for i in range(1, 11):

    email = f"merge{i}@example.com"
    dob = f"1985-03-{i:02d}"

    for note_num in range(1, 6):
        rows.append({
            "name": f"Merge Person {i}",
            "email": email,
            "date_of_birth": dob,
            "notes": f"Interaction {note_num}"
        })

# --------------------------------------------------
# Group 4 - Invalid emails (50)
# --------------------------------------------------

for i in range(1, 51):

    bad_emails = [
        f"user{i}@",
        f"user{i}example.com",
        f"user{i}@test",
        f"user{i}@@example.com",
        ""
    ]

    rows.append({
        "name": f"Bad Email {i}",
        "email": bad_emails[i % len(bad_emails)],
        "date_of_birth": f"1990-04-{(i % 28) + 1:02d}",
        "notes": "Invalid email test"
    })

# --------------------------------------------------
# Group 5 - Invalid dates (50)
# --------------------------------------------------

bad_dates = [
    "99/99/9999",
    "32/01/2000",
    "2000/99/01",
    "not-a-date",
    ""
]

for i in range(1, 51):
    rows.append({
        "name": f"Bad Date {i}",
        "email": f"baddate{i}@example.com",
        "date_of_birth": bad_dates[i % len(bad_dates)],
        "notes": "Invalid date test"
    })

# --------------------------------------------------
# Group 6 - Whitespace and capitalisation (50)
# --------------------------------------------------

for i in range(1, 51):
    rows.append({
        "name": f"   jOhN sMiTh {i}   ",
        "email": f"   JOHN{i}@EXAMPLE.COM   ",
        "date_of_birth": "1988-05-01",
        "notes": "Whitespace test"
    })

# --------------------------------------------------
# Group 7 - Missing data (25)
# --------------------------------------------------

for i in range(1, 26):

    if i % 5 == 0:
        rows.append({
            "name": "",
            "email": "",
            "date_of_birth": "",
            "notes": ""
        })

    elif i % 2 == 0:
        rows.append({
            "name": f"Missing Email {i}",
            "email": "",
            "date_of_birth": "1980-01-01",
            "notes": "Missing email"
        })

    else:
        rows.append({
            "name": f"Missing DOB {i}",
            "email": f"missing{i}@example.com",
            "date_of_birth": "",
            "notes": "Missing DOB"
        })

# --------------------------------------------------
# Group 8 - Realistic email typos (20)
# --------------------------------------------------

typo_emails = [
    ("john@gmial.com", "Common Gmail typo"),
    ("jane@hotmial.com", "Common Hotmail typo"),
    ("fred@yahooo.com", "Extra character"),
    ("sarah@outlok.com", "Missing letter"),
    ("mark@gamil.com", "Letter transposition"),
    ("emma@gnail.com", "Common keyboard error"),
    ("tom@icloud.co", "Missing TLD character"),
    ("lucy@hotmai.com", "Missing letter"),
    ("paul@gmai.com", "Missing letter"),
    ("amy@yaho.com", "Missing letter"),
    ("dave@outloo.com", "Missing letter"),
    ("kate@gmali.com", "Transposed letters"),
    ("rob@iclod.com", "Missing letter"),
    ("anna@hotmial.co.uk", "Hotmail typo"),
    ("ben@gmaill.com", "Extra character"),
    ("chris@yahhoo.com", "Repeated character"),
    ("sam@outllook.com", "Repeated letters"),
    ("jo@gmaiil.com", "Repeated character"),
    ("claire@icloudcom", "Missing dot"),
    ("nick@gmial.co.uk", "Gmail typo UK")
]

for i, (email, note) in enumerate(typo_emails, start=1):
    rows.append({
        "name": f"Typo Email {i}",
        "email": email,
        "date_of_birth": f"1991-06-{(i % 28) + 1:02d}",
        "notes": note
    })

# --------------------------------------------------
# Group 9 - Duplicate edge cases
# --------------------------------------------------

# Should merge
rows.append({
    "name": "Valid Duplicate A",
    "email": "duplicate@example.com",
    "date_of_birth": "1980-01-01",
    "notes": "First record"
})

rows.append({
    "name": "Valid Duplicate B",
    "email": "duplicate@example.com",
    "date_of_birth": "1980-01-01",
    "notes": "Second record"
})

# Should NOT merge (invalid DOB)
rows.append({
    "name": "Invalid DOB Duplicate A",
    "email": "invaliddob@example.com",
    "date_of_birth": "not-a-date",
    "notes": "First invalid DOB"
})

rows.append({
    "name": "Invalid DOB Duplicate B",
    "email": "invaliddob@example.com",
    "date_of_birth": "not-a-date",
    "notes": "Second invalid DOB"
})

# Should NOT merge (invalid email)
rows.append({
    "name": "Invalid Email Duplicate A",
    "email": "invalidemail",
    "date_of_birth": "1985-06-01",
    "notes": "First invalid email"
})

rows.append({
    "name": "Invalid Email Duplicate B",
    "email": "invalidemail",
    "date_of_birth": "1985-06-01",
    "notes": "Second invalid email"
})

# --------------------------------------------------
# Group 10 - Near duplicates (should NOT merge)
# --------------------------------------------------

# Same email, different DOB
rows.append({
    "name": "Near Duplicate Email A",
    "email": "neardupe@example.com",
    "date_of_birth": "1980-01-01",
    "notes": "Same email first DOB"
})

rows.append({
    "name": "Near Duplicate Email B",
    "email": "neardupe@example.com",
    "date_of_birth": "1981-01-01",
    "notes": "Same email second DOB"
})

# Same DOB, different email
rows.append({
    "name": "Near Duplicate DOB A",
    "email": "doba@example.com",
    "date_of_birth": "1990-06-15",
    "notes": "Same DOB first email"
})

rows.append({
    "name": "Near Duplicate DOB B",
    "email": "dobb@example.com",
    "date_of_birth": "1990-06-15",
    "notes": "Same DOB second email"
})

# --------------------------------------------------
# Group 11 - Notes preservation (should merge safely)
# --------------------------------------------------

# Duplicate notes should not be repeated
rows.append({
    "name": "Duplicate Notes A",
    "email": "duplicatenotes@example.com",
    "date_of_birth": "1979-04-01",
    "notes": "Training required"
})

rows.append({
    "name": "Duplicate Notes B",
    "email": "duplicatenotes@example.com",
    "date_of_birth": "1979-04-01",
    "notes": "Training required"
})

# Blank note should not overwrite populated note
rows.append({
    "name": "Blank Note A",
    "email": "blanknote@example.com",
    "date_of_birth": "1982-08-15",
    "notes": ""
})

rows.append({
    "name": "Blank Note B",
    "email": "blanknote@example.com",
    "date_of_birth": "1982-08-15",
    "notes": "DBS completed"
})

# Distinct notes should be merged
rows.append({
    "name": "Merged Notes A",
    "email": "mergednotes@example.com",
    "date_of_birth": "1988-11-20",
    "notes": "Training required"
})

rows.append({
    "name": "Merged Notes B",
    "email": "mergednotes@example.com",
    "date_of_birth": "1988-11-20",
    "notes": "DBS completed"
})

# --------------------------------------------------
# Group 13 - Email edge cases
# --------------------------------------------------

# Mixed case emails
rows.append({
    "name": "Mixed Case Email A",
    "email": "JOHN@GMAIL.COM",
    "date_of_birth": "1980-01-01",
    "notes": "Upper case email"
})

rows.append({
    "name": "Mixed Case Email B",
    "email": "John@Gmail.Com",
    "date_of_birth": "1980-01-01",
    "notes": "Mixed case email"
})

rows.append({
    "name": "Mixed Case Email C",
    "email": "john@gmail.com",
    "date_of_birth": "1980-01-01",
    "notes": "Lower case email"
})

# Plus addressing
rows.append({
    "name": "Plus Address Email",
    "email": "john+newsletter@gmail.com",
    "date_of_birth": "1985-05-05",
    "notes": "Plus address"
})

# Dots in local part
rows.append({
    "name": "Dotted Email",
    "email": "john.smith@gmail.com",
    "date_of_birth": "1986-06-06",
    "notes": "Dotted local part"
})

# Subdomain email
rows.append({
    "name": "Subdomain Email",
    "email": "john@hr.company.com",
    "date_of_birth": "1987-07-07",
    "notes": "Subdomain address"
})

# Long TLD
rows.append({
    "name": "Long TLD Email",
    "email": "john@example.technology",
    "date_of_birth": "1988-08-08",
    "notes": "Long TLD"
})

# --------------------------------------------------
# Group 15 - Strict mode behaviour
# --------------------------------------------------

# Invalid email - should survive lenient, be removed in strict
rows.append({
    "name": "Strict Invalid Email",
    "email": "not-an-email",
    "date_of_birth": "1980-01-01",
    "notes": "Strict email test"
})

# Ambiguous DOB - should survive lenient, be removed in strict
rows.append({
    "name": "Strict Ambiguous DOB",
    "email": "strictdob@example.com",
    "date_of_birth": "03/11/1985",
    "notes": "Strict DOB test"
})

# Valid control record - should survive both
rows.append({
    "name": "Strict Control Record",
    "email": "strictcontrol@example.com",
    "date_of_birth": "1985-11-03",
    "notes": "Control record"
})

# --------------------------------------------------
# Save CSV
# --------------------------------------------------

df = pd.DataFrame(rows)

output_file = "test_dataset.csv"

df.to_csv(output_file, index=False)

print(f"Created {output_file}")
print(f"Rows: {len(df)}")