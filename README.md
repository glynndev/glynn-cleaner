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
- [Overview](#-overview)
- [Quick Start](#-quick-start)
- [CLI Preview](#️-cli-preview)
- [Features](#-features)
- [Installation](#-installation)
- [Usage](#-usage)
- [Output Files](#-output-files)
- [Project Structure](#-project-structure)
- [Testing](#-testing)
- [Changelog](#-changelog)
- [Versioning Strategy](#-versioning-strategy)
- [Roadmap](#-roadmap)
- [Why This Tool Exists](#-why-this-tool-exists)
- [Contributing](#-contributing)
- [License](#-license)

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
Audit Mode provides detailed reporting, issue detection, and a full audit trail.

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
9. **Remove duplicates** — Identifies and removes duplicate rows based on the full row content.  
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

### v1.0.0 (Planned)
- First stable release  
- Full support for simple and audit modes  
- Strict/lenient validation  
- Email cleaning  
- Date parsing  
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

## 🤝 Contributing
Contributions welcome. See `CONTRIBUTING.md`.

---

## 📜 License
MIT License — see `LICENSE`.

---

## 🙌 Acknowledgements
Built with a focus on clarity, reliability, and real‑world analyst workflows.






