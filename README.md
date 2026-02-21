# 🧼 glynn-cleaner
A fast, reliable, analyst‑friendly CSV cleaning tool with audit mode, strict/lenient validation, and Excel‑safe output formatting.

<!-- Badges -->
<p align="left">

  <!-- Python version -->
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg" alt="Python Version">

  <!-- License -->
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">

  <!-- Build status (placeholder until CI is added) -->
  <img src="https://img.shields.io/badge/Build-Passing-brightgreen.svg" alt="Build Status">

  <!-- Project status -->
  <img src="https://img.shields.io/badge/Status-Active-success.svg" alt="Project Status">

  <!-- Repo size -->
  <img src="https://img.shields.io/github/repo-size/glynndev/glynn-cleaner.svg" alt="Repo Size">

  <!-- Last commit -->
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

### ✨ Overview
`glynn-cleaner` is a command‑line data cleaning tool designed for analysts, small businesses, and anyone who needs clean, consistent CSV files without wrestling with spreadsheets. It handles common data‑quality issues automatically — blank rows, junk values, inconsistent dates, malformed emails, and more — while producing a clear summary of what was fixed.

The tool supports two modes:

- **Simple Mode** — quick cleaning with minimal intervention  
- **Audit Mode** — detailed reporting, suggested corrections, and Excel‑safe outputs  

Strict and lenient validation options allow you to control how aggressively the tool enforces data quality.

## ⚡ Quick Start

Follow these steps to clean your first CSV file using **glynn-cleaner**.

---

### 1. Prepare your input file
Place your CSV file somewhere easy to reference, for example:

```
data/input.csv
```

---

### 2. Run the cleaner in Simple Mode
Simple Mode performs fast, automatic cleaning with minimal reporting.

```
python -m glynn_cleaner data/input.csv data/output.csv --mode simple
```

This generates:

- `output.csv` — your cleaned dataset

---

### 3. Run the cleaner in Audit Mode
Audit Mode provides detailed reporting, suggestions, and Excel‑safe date outputs.

```
python -m glynn_cleaner data/input.csv data/output.csv --mode audit
```

This generates:

- `output.csv` — cleaned dataset  
- `summary.csv` — detailed log of changes, issues, and suggestions  

---

### 4. Enable strict validation (optional)
Strict mode enforces tighter rules and flags more issues.

```
python -m glynn_cleaner data/input.csv data/output.csv --strict
```

You can combine strict mode with audit mode:

```
python -m glynn_cleaner data/input.csv data/output.csv --mode audit --strict
```

---

### 5. View your results
Open the generated files in Excel, VS Code, or your preferred tool:

- `output.csv` — final cleaned data  
- `summary.csv` — audit log (audit mode only)

You now have a fully cleaned, analysis‑ready dataset.

## 🖥️ CLI Preview

A quick look at how **glynn-cleaner** runs from the command line. This helps new users understand the flow of the tool before trying it themselves.

> Replace the placeholder image link below with your own screenshot or GIF once you capture it.

<p align="center">
  <img src="https://via.placeholder.com/800x300.png?text=CLI+Preview+Goes+Here" alt="glynn-cleaner CLI preview" width="80%">
</p>

### How to add your own screenshot or GIF
1. Run the tool in your terminal.
2. Take a screenshot or record a short GIF (e.g., using ShareX, ScreenToGif, or macOS screenshot tools).
3. Upload the image to your GitHub repo:
   - Click **Add file → Upload files**.
   - Place it in a folder like `assets/` or `docs/`.
4. Copy the file’s GitHub URL.
5. Replace the placeholder link in the `<img>` tag with your real URL.

Example once you add your own image:

```
<p align="center">
  <img src="https://github.com/glynndev/glynn-cleaner/blob/main/assets/cli-preview.gif" alt="glynn-cleaner CLI preview" width="80%">
</p>
```


---

### 🚀 Features
- Removes blank rows and junk rows  
- Normalises column names  
- Cleans and validates email addresses  
- Detects and standardises date formats  
- Provides Excel‑safe date suggestions  
- Capitalises names for professional polish  
- Generates a summary CSV of all changes  
- Supports **simple** and **audit** modes  
- Supports **strict** and **lenient** validation  
- Fully CLI‑driven for repeatable workflows  

---

### 📦 Installation
Once published to PyPI/TestPyPI, installation will be:

```
pip install glynn-cleaner
```

For now, run locally via:

```
python -m glynn_cleaner --help
```

---

## 🧩 Requirements

To run **glynn-cleaner**, you’ll need the following:

- **Python 3.10 or higher** — the tool uses modern Python features and typing.
- **pip** — for installing dependencies and (eventually) the PyPI package.
- **pandas** — core dependency for CSV processing.
- **python-dateutil** — used for flexible date parsing.
- **A terminal or command prompt** — the tool is fully CLI‑driven.
- **CSV files encoded in UTF‑8** — recommended for best compatibility.

All required Python packages will be installed automatically once the project is published to PyPI. For local development, install dependencies with:

```
pip install -r requirements.txt
```

---

### 🛠 Usage

#### Simple Mode
```
python -m glynn_cleaner input.csv output.csv --mode simple
```

#### Audit Mode
```
python -m glynn_cleaner input.csv output.csv --mode audit
```

#### Strict Validation
```
python -m glynn_cleaner input.csv output.csv --strict
```

#### Combined Example
```
python -m glynn_cleaner input.csv output.csv --mode audit --strict
```

---

### 📄 Output Files
Depending on mode and flags, the tool may generate:

- **Cleaned CSV** — your final cleaned dataset  
- **Summary CSV** — a log of all changes, suggestions, and flagged issues  
- **Audit report** (audit mode) — detailed breakdown of detected problems  

---

### 📁 Project Structure
```
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
```

---

### 🧪 Testing
Run the test suite:

```
pytest
```

---

## 🗺️ Roadmap

A clear view of what’s coming next for **glynn-cleaner**. This helps users understand the project’s direction and gives contributors a sense of where they can help.

### Near‑term improvements
- Add support for additional date formats and locale-aware parsing  
- Improve email validation with more robust pattern matching  
- Add optional logging to a dedicated `logs/` directory  
- Expand summary reporting with clearer issue categories  
- Add more unit tests for edge cases and helper functions  

### Medium‑term goals
- Introduce a configuration file (`glynn-cleaner.toml`) for reusable settings  
- Add support for cleaning Excel files (`.xlsx`) directly  
- Provide a plugin system for custom cleaning rules  
- Add a progress indicator for large files  
- Publish to TestPyPI and then PyPI for easy installation  

### Long‑term vision
- Build a simple GUI for non-technical users  
- Offer a web-based version for quick uploads and downloads  
- Create integrations for Power BI and Tableau workflows  
- Develop a library API so developers can import and use the cleaner programmatically  

---

## 💡 Why This Tool Exists

Most analysts and small businesses spend far too much time fixing messy CSV files — blank rows, inconsistent dates, malformed emails, strange characters, and formatting issues that break Excel or downstream tools. These problems slow down real work and create frustration.

**glynn-cleaner** was built to solve that problem with a tool that is:

- fast  
- predictable  
- repeatable  
- easy to run  
- safe for Excel users  
- transparent about what it changes  

The goal is to give people a reliable way to clean data without needing to write Python scripts, build complex formulas, or manually fix the same issues over and over again. It’s designed for real-world workflows, where data is rarely perfect and time is always limited.

This project exists to make data cleaning simple, consistent, and accessible — whether you’re an analyst, a small business owner, or someone who just wants their CSV files to behave.

---

## 📝 Changelog

A version-by-version record of improvements, fixes, and new features added to **glynn-cleaner**. This helps users understand what has changed over time and provides transparency for contributors.

### Unreleased
- Initial public release preparation  
- README polish and documentation improvements  
- Added Quick Start, CLI Preview, Roadmap, and project purpose sections  
- Repository structure cleaned and standardised  
- GitHub publishing and remote setup completed  

### v1.0.0 (Planned)
- First stable release  
- Full support for simple and audit modes  
- Strict and lenient validation options  
- Email cleaning and validation  
- Date parsing with Excel‑safe suggestions  
- Name capitalisation  
- Summary CSV generation  
- Junk row and blank row removal  
- Column normalisation  
- CLI interface with argparse  
- Comprehensive logging and reporting  

### Future versions
- Config file support (`glynn-cleaner.toml`)  
- Excel (`.xlsx`) input support  
- Plugin system for custom cleaning rules  
- Progress indicator for large files  
- GUI prototype  
- Web-based upload/clean/download interface  

---

## 🧩 Versioning Strategy

This project follows **Semantic Versioning (SemVer)** to ensure predictable, transparent releases. Each version number has the form:

```
MAJOR.MINOR.PATCH
```

### What each part means
- **MAJOR** — increased when breaking changes are introduced that may require users to update their workflows or code.
- **MINOR** — increased when new features are added in a backwards‑compatible way.
- **PATCH** — increased when bugs are fixed or small improvements are made that do not change behaviour.

### How this applies to glynn-cleaner
- **1.0.0** will represent the first stable release with all core features complete.
- **1.x.x** versions will add enhancements such as new cleaning rules, improved validation, or expanded reporting, without breaking existing usage.
- **2.0.0** will only be used if a major redesign or breaking change is introduced (e.g., a new CLI structure or incompatible configuration system).

### Release workflow
- Development changes are tracked in the **Unreleased** section of the Changelog.
- When a release is ready, a new version number is assigned and the Changelog is updated.
- Tags will be created in GitHub for each release to make version history clear and accessible.
- TestPyPI will be used for pre‑release validation before publishing to PyPI.

This approach keeps the project stable for users while allowing steady, well‑documented improvements.

---

### 🤝 Contributing
Contributions are welcome!  
Please read the `CONTRIBUTING.md` file for guidelines on:

- branching  
- code style  
- pull request workflow  
- testing requirements  

---

### 📜 License
MIT License — see `LICENSE` for details.

---

### 🙌 Acknowledgements
Built with a focus on clarity, reliability, and real‑world analyst workflows.




