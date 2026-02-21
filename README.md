# Glynn Cleaner — Data Cleaning Tool

A polished, user‑friendly command‑line CSV cleaning utility designed for analysts, developers, and small businesses.  
Glynn Cleaner provides strict or lenient validation, structured progress messages, detailed summaries, and clean output files — all wrapped in a professional CLI experience.

---

## Features

- **Simple and Audit Modes** — choose between minimal cleaning or full audit‑style validation.
- **Strict or Lenient Validation** — strict mode enforces RFC‑like email rules and 4‑digit‑year date formats; lenient mode accepts a wider range of inputs.
- **Email Validation & Suggestions** — detect invalid emails and generate suggested fixes.
- **Date Parsing & Normalisation** — convert multiple date formats into `YYYY-MM-DD`.
- **Whitespace Trimming & Name Capitalisation** — clean and standardise text fields automatically.
- **Junk Row Removal** — remove empty or placeholder rows.
- **Duplicate Removal** — ensure clean, unique records.
- **Dry‑Run Mode** — run the full cleaning process without writing any files.
- **Summary‑Only Mode** — generate summary + report without producing a cleaned CSV.
- **Structured Progress Messages** — clear step‑by‑step progress indicators.
- **Startup & Success Banners** — a polished CLI experience from start to finish.

---

## Installation

### Install via pip

```bash
pip install glynn-cleaner
```

### Or install the latest TestPyPI build

```bash
pip install -i https://test.pypi.org/simple/ glynn-cleaner
```

Requires **Python 3.9+**.

---

## Usage

### Basic cleaning (simple mode, lenient)

```bash
glynn-cleaner --input input.csv --output cleaned.csv
```

### Strict validation

```bash
glynn-cleaner -i input.csv -o cleaned_strict.csv --strictness strict
```

### Audit mode (keeps helper columns)

```bash
glynn-cleaner -i input.csv -o cleaned_audit.csv --mode audit
```

### Dry‑run (no files written)

```bash
glynn-cleaner -i input.csv --dry-run
```

### Summary‑only (no cleaned CSV)

```bash
glynn-cleaner -i input.csv --summary-only
```

---

## Modes

### Simple Mode

Produces a clean, user‑facing CSV with four columns:

- name  
- email  
- date_of_birth (ISO‑formatted)  
- notes  

### Audit Mode

Keeps all helper columns for inspection:

- email_valid  
- email_suggested_fix  
- date_of_birth (cleaned ISO)  
- date_of_birth_raw  
- date_of_birth_valid  

---

## Strict vs Lenient Validation

### Strict Mode

- RFC‑like email validation  
- Requires 4‑digit years  
- Rejects ambiguous formats  
- Removes invalid rows  

### Lenient Mode

- Accepts a wider range of emails  
- Accepts more date formats  
- Keeps all rows except junk  

---

## Output Files

Each run produces:

- Cleaned CSV — unless `--summary-only` is used  
- Summary CSV — machine‑readable metrics  
- Text Report — human‑readable summary  

Example summary:

```
Rows loaded: 6
Junk rows removed: 2
Invalid emails removed: 2
Invalid dates removed: 0
Duplicates removed: 0
Final row count: 2
```

---

## Example

### Input

```
name,email,date_of_birth,notes
John Smith,john.smith @gmail.com,12/05/1990,likes football
Sarah Jones,sarah.jones@gmail,03/11/1985,works in sales
```

### Strict simple output

```
name,email,date_of_birth,notes
Mike Brown,mike.brown@yahoo.com,1992-07-14,
Lucy Adams,lucy.adams@hotmail.com,1993-08-14,new starter
```

Audit output includes helper columns for full transparency.

---

## License

MIT License — see `LICENSE` for details.

---

## Roadmap

- Config file support  
- Additional date formats  
- Improved email suggestions  
- Optional warnings file  
- GUI and web interface  

---

## Contributing

Pull requests are welcome. See `CONTRIBUTING.md` for guidelines.



