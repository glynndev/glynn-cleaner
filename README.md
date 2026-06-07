# 🧼 glynn-cleaner
A fast, reliable, analyst‑friendly CSV cleaning tool with audit mode, strict/lenient validation, and Excel‑safe output formatting.

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Build-Passing-brightgreen.svg" alt="Build Status">
  <img src="https://img.shields.io/badge/Status-Active-success.svg" alt="Project Status">
  <img src="https://img.shields.io/github/repo-size/glynndev/glynn-cleaner.svg" alt="Repo Size">
  <img src="https://img.shields.io/github/last-commit/glynndev/glynn-cleaner.svg" alt="Last Commit">
</p>

---

## 📚 Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [How It Works](#how-it-works)
- [Supported Fields and Cleaning Logic](#supported-fields-and-cleaning-logic)
- [How Identity and Deduplication Work](#-how-identity-and-deduplication-work)
- [Audit Mode Explained](#-audit-mode-explained)
- [CLI Preview](#cli-preview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Output Files](#output-files)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Roadmap](#️-roadmap)
- [Changelog](#changelog)
- [Versioning Strategy](#versioning-strategy)
- [Frequently Asked Questions](#-frequently-asked-questions)
- [Why This Tool Exists](#-why-this-tool-exists)
- [Contributing](#contributing)
- [License](#license)


---

## ✨ Overview
`glynn-cleaner` is a command‑line data cleaning tool designed for analysts, small businesses, and anyone who needs clean, consistent CSV files without wrestling with spreadsheets. It handles common data‑quality issues automatically — blank rows, junk values, inconsistent dates, malformed emails, and more — while producing a clear summary of what was fixed.

The tool supports two modes:
- **Simple Mode** — quick cleaning with minimal intervention  
- **Audit Mode** — detailed reporting, suggested corrections, and Excel‑safe outputs  

Strict and lenient validation options allow you to control how aggressively the tool enforces data quality.

---

## ⚡ Quick Start

Follow these steps to clean your first CSV file using **glynn-cleaner**.

---

### 1. Prepare your input file
Place your CSV file somewhere easy to reference, for example:

    input/sample.csv

You can use any folder structure you prefer. The cleaner will preserve all columns and apply logic only to recognised fields.

---

### 2. Run the cleaner in Simple Mode
Simple Mode performs fast, automatic cleaning with minimal reporting.

    glynn-cleaner --input input/sample.csv --output output/cleaned.csv --mode simple

This generates:
- `cleaned.csv` — your cleaned dataset

---

### 3. Run the cleaner in Audit Mode
Audit mode provides detailed reporting, validation flags, suggested corrections, and Excel‑safe outputs

    glynn-cleaner --input input/sample.csv --output output/cleaned.csv --mode audit

This generates:
- `cleaned.csv` — cleaned dataset  
- `cleaned_summary.csv` — summary of issues, changes, and validation results  
- `cleaned_report.txt` — human‑readable audit report

---

### 4. Enable strict validation (optional)
Strict mode enforces tighter rules and removes rows with invalid emails, dates, or junk content.

    glynn-cleaner --input input/sample.csv --output output/cleaned.csv --strictness strict

You can combine strict mode with audit mode:

    glynn-cleaner --input input/sample.csv --output output/cleaned.csv --mode audit --strictness strict

> **Recommended default:**
> For most use cases, `--mode simple --strictness strict` provides the cleanest,
> HR‑ready output. Audit modes are intended for investigation and validation.

---

### 5. View your results
Open the generated files in Excel, VS Code, or your preferred tool:

- `cleaned.csv` — final cleaned data  
- `cleaned_summary.csv` — audit log (audit mode only)  
- `cleaned_report.txt` — detailed text report (audit mode only)

You now have a fully cleaned, analysis‑ready dataset.

---

## How It Works

The cleaner processes your CSV through a structured, multi‑stage pipeline designed to improve data quality while preserving the integrity of fields it does not explicitly modify. Each stage is logged when using `--verbose` and contributes to a final audit summary.

### Processing Pipeline

1. **Load the CSV** — Reads the file into memory, counts rows, and checks for basic structural issues.  
2. **Normalise column names** — Converts column headers to a consistent format (lowercase, underscores).  
3. **Trim whitespace** — Removes leading/trailing spaces from all string fields.  
4. **Apply name formatting** — Capitalises names and removes junk entries such as placeholder text.  
5. **Remove junk rows** — Filters out rows that contain no meaningful data.  
6. **Validate emails** — Checks email format and flags invalid entries (strict mode removes them).  
7. **Parse dates of birth** — Converts valid dates into a consistent format and flags invalid ones.  
8. **Apply strict filtering rules** — Removes rows with invalid or missing critical fields when strict mode is enabled.  
9. **Resolve duplicate identities** — Collapses records that refer to the same person using an identity
   key (email + date of birth). When multiple records match, they are merged into a single row and
   notes are combined deterministically.  
10. **Save outputs** — Writes the cleaned CSV, a summary CSV, and a text report to the output directory.

---

## Supported Fields and Cleaning Logic

The cleaner applies targeted transformations only to the fields it recognises. All other fields are preserved exactly as provided, ensuring compatibility with HR, CRM, finance, and operational datasets.

| Column name       | Cleaning applied                                                                 |
|-------------------|----------------------------------------------------------------------------------|
| `name`            | Whitespace trimming, normalisation, capitalisation, junk‑row detection           |
| `email`           | Format validation, strict filtering, junk‑row detection                          |
| `date_of_birth`   | Date parsing, invalid‑date detection, strict filtering                           |
| Other columns     | Preserved as‑is; no cleaning or validation applied                               |

---

## 🧠 How Identity and Deduplication Work

`glynn-cleaner` is designed primarily for HR‑style datasets, where identity cannot safely be inferred
from a single field.

### Identity Resolution Rules

For deduplication purposes, a *person* is defined using the following identity key:

- **Email address**
- **Date of birth**

Records are merged **only when both fields match and are valid**.

### Why not email‑only deduplication?

In real‑world HR data:
- email addresses may be shared, reused, or reassigned,
- historical records may contain corrected or conflicting personal details.

To avoid silent data loss, the cleaner **does not assume that one email equals one person**.
If identity cannot be proven, records are kept separate and fully explained.

### Notes and Information Preservation

When multiple records are merged:
- all non‑blank notes are combined,
- duplicate note content is removed,
- the final notes field remains human‑readable.

No contextual information is discarded.

---

## 🔎 Audit Mode Explained

Audit mode prioritises **transparency over minimal output**.

As a result, audit outputs may still contain:
- multiple records sharing the same email address,
- multiple names associated with one email,
- records that look similar but cannot be confidently merged.

This is intentional.

Audit mode is designed to:
- surface ambiguity,
- explain why rows were kept or removed,
- provide evidence for every decision.

If two records cannot be proven to represent the same individual, both are retained.

---

### ⚠️ Ambiguous Dates in Strict Mode

Strict mode removes dates that cannot be interpreted unambiguously. Formats such as `12/05/1990` or `03/11/1985` may be valid, but they can represent different dates depending on whether the source uses **DD/MM/YYYY** or **MM/DD/YYYY**. Because the cleaner cannot reliably determine the intended format, these dates are treated as invalid in strict mode and the entire row is removed.

Examples of ambiguous formats:
- `12/05/1990`  
- `03/11/1985`  

Examples of unambiguous formats (always accepted):
- `1992.07.14`  
- `14 08 1993`  
- `1990-05-12`  

If you want to keep ambiguous dates, use **lenient mode**, which preserves all rows and leaves date interpretation to the user or downstream tools.

---

## Behaviour With Unknown or Alternative Column Names

The cleaner does not attempt to guess or infer the meaning of columns. This prevents accidental mis‑cleaning of fields that share similar names but contain unrelated data.

Examples:
- Columns such as `dob`, `D.O.B`, `birthdate`, or `dateOfBirth` will **not** be treated as `date_of_birth` unless they use the exact name.  
- A column named `email_address` will not receive email validation unless it is named `email`.  
- Additional fields such as `address`, `postcode`, `department`, or `employee_id` will be included in the output unchanged.

This ensures predictable behaviour and avoids corrupting data.

### Advisory for Best Results
To ensure the cleaner applies all available logic, use the exact column names listed in the table above.

If your dataset uses alternative names, you may:
- rename the columns before running the cleaner, or  
- allow them to pass through unchanged.

All unrecognised fields are preserved, so no data is lost unless strict mode removes the entire row due to validation failures in recognised fields.

---

## 🖥️ CLI Preview

<p align="center">
  <img src="https://via.placeholder.com/800x300.png?text=CLI+Preview+Goes+Here" alt="glynn-cleaner CLI preview" width="80%">
</p>

---

## 🚀 Features
- Removes blank rows and junk rows  
- Normalises column names  
- Cleans and validates email addresses  
- Detects and standardises date formats  
- Provides Excel‑safe date suggestions  
- Capitalises names for professional polish  
- Generates a summary CSV of all changes  
- Supports simple and audit modes  
- Supports strict and lenient validation  
- Fully CLI‑driven for repeatable workflows  

---

## 📦 Installation

Once published to PyPI/TestPyPI:

    pip install glynn-cleaner

For local development:

    python -m glynn_cleaner --help

---

## 🧩 Requirements
- Python 3.10+  
- pip  
- pandas  
- python-dateutil  
- UTF‑8 CSV files  

Install dependencies locally:

    pip install -r requirements.txt

---

## 🛠 Usage

Simple Mode:

    python -m glynn_cleaner input.csv output.csv --mode simple

Audit Mode:

    python -m glynn_cleaner input.csv output.csv --mode audit

Strict Validation:

    python -m glynn_cleaner input.csv output.csv --strict

Combined:

    python -m glynn_cleaner input.csv output.csv --mode audit --strict

---

## 📄 Output Files
- Cleaned CSV  
- Summary CSV  
- Audit report (audit mode)

---

## 📁 Project Structure

    glynn-cleaner/
    │
    ├── glynn_cleaner/
    │   ├── cleaner.py
    │   ├── helpers/
    │   ├── __init__.py
    │   └── ...
    │
    ├── tests/
    ├── README.md
    ├── pyproject.toml
    └── setup.cfg

---

## 🧪 Testing

    pytest

---

## 🗺️ Roadmap
- Additional date formats  
- Improved email validation  
- Config file support  
- Excel input support  
- Plugin system  
- GUI prototype  
- Web-based version  

---

## 💡 Why This Tool Exists
Most analysts and small businesses spend too much time fixing messy CSV files. This tool provides a fast, predictable, repeatable way to clean data without writing code or manually fixing the same issues repeatedly.

---

## 📝 Changelog

### Unreleased
- Initial public release preparation  
- README improvements  
- Added Quick Start, CLI Preview, Roadmap  
- Repository structure standardised  

### v1.3.0
- First stable public release
- Full support for simple and audit modes
- Strict and lenient validation
- Identity‑based deduplication (email + date of birth)
- Notes preservation and merging
- Email validation
- Date parsing with ambiguity handling
- Name capitalisation
- Summary CSV generation
- Junk row removal
- Column normalisation
- CLI interface
- Logging and reporting 

---

## 🧩 Versioning Strategy
Semantic Versioning (SemVer):

    MAJOR.MINOR.PATCH

- MAJOR for breaking changes  
- MINOR for new features  
- PATCH for fixes 

---

## ❓ Frequently Asked Questions

### Why do I see the same email address multiple times in the output?

This is expected behaviour.

`glynn-cleaner` does **not** assume that one email address uniquely identifies a person.
In real‑world HR and operational datasets, email addresses can be:

- shared between people,
- reused historically,
- reassigned,
- incorrectly entered,
- or associated with corrected personal details over time.

For this reason, records are only merged when **both email and date of birth match and are valid**.
If identity cannot be proven, records remain separate to avoid silent data loss.

---

### Why doesn’t the cleaner deduplicate on email alone?

Email‑only deduplication looks attractive, but it is unsafe for HR‑style data.

Using email alone can incorrectly merge:
- different people sharing an inbox,
- historical records with corrected dates of birth,
- reused or reassigned email addresses.

To remain **auditable and predictable**, `glynn-cleaner` uses a conservative identity key:
**email + date of birth**.

This ensures records are only merged when there is strong evidence they represent the same individual.

---

### Audit mode output looks repetitive or messy. Is something wrong?

No — this is intentional.

Audit mode prioritises **transparency over minimal output**. It is designed to:
- surface ambiguity,
- show why records were kept or removed,
- explain why some records could not be merged.

If two records cannot be confidently proven to represent the same person, both are retained and fully visible.
Simple mode exists for users who prefer a cleaner operational view.

---

### Which mode should I use most of the time?

For most users, the recommended default is:

`--mode simple --strictness strict`

This produces the cleanest, HR‑ready dataset.

Use **audit mode** when you need to:
- understand why rows were removed,
- investigate data quality issues,
- validate upstream data sources,
- provide compliance or troubleshooting evidence.

---

### Why were some rows removed in strict mode but kept in lenient mode?

Lenient mode preserves all rows and flags issues.

Strict mode removes rows that fail essential validation rules, such as:
- invalid email addresses,
- invalid or ambiguous dates of birth,
- rows with insufficient identity information.

This allows you to choose between **maximum retention** (lenient) and **maximum correctness** (strict).

---

### Why are some dates treated as invalid even though they look reasonable?

See Ambiguous Dates in Strict Mode above for the full explanation.

Some date formats are ambiguous.

For example, `12/05/1990` could mean:
- 12 May 1990 (DD/MM), or
- 5 December 1990 (MM/DD).

Because the cleaner cannot reliably infer the intended format, such dates are treated as **ambiguous** and removed in strict mode.

Unambiguous formats such as `1992.07.14`, `1990-05-12`, or `14 08 1993` are always accepted.

---

### Does the cleaner modify columns it doesn’t recognise?

No.

Only recognised fields (`name`, `email`, `date_of_birth`) are validated or transformed.
All other columns are preserved **exactly as provided**.

This ensures compatibility with HR, finance, CRM, and operational datasets.

---

### Can deduplication rules be made more aggressive?

Not by default.

The current behaviour is deliberately conservative to avoid data loss.
More aggressive strategies (such as email‑only deduplication) may be considered in the future,
but would always be explicit, documented, and opt‑in.

---

## 🤝 Contributing
Contributions welcome. See `CONTRIBUTING.md`.

---

## 📜 License
MIT License — see `LICENSE`.

---

## 🙌 Acknowledgements
Built with a focus on clarity, reliability, and real‑world analyst workflows.






