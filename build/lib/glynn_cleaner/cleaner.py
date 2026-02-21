"""
Data Cleaning Tool
Author: Glynn Holland

Version:
    The current version is defined in glynn_cleaner.__version__.

Description:
    A command-line CSV cleaning utility supporting simple and audit modes,
    with lenient or strict validation. Generates cleaned output, a machine-
    readable summary CSV, and a human-readable text report.

Features:
    - Email validation (lenient or strict)
    - Date parsing and normalisation
    - Junk row removal
    - Duplicate removal
    - Name capitalisation
    - Dry-run mode (no files written)
    - Summary-only mode
    - Structured progress messages
    - Startup and success banners
"""


import pandas as pd
from datetime import datetime
import re
from glynn_cleaner import __version__


from glynn_cleaner.utils.file_helpers import (
    load_csv,
    save_csv,
    save_summary,
    save_text_report
)

from glynn_cleaner.utils.logger import (
    log_info,
    log_debug,
    log_warning,
    log_error
)

# ------------------------------------------------------------
# Email validation helpers
# ------------------------------------------------------------
STRICT_EMAIL_REGEX = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)

def is_valid_email(email: str, strict: bool = False) -> bool:
    if not isinstance(email, str):
        return False

    email = email.strip()

    if strict:
        return bool(STRICT_EMAIL_REGEX.match(email))

    if "@" not in email:
        return False
    local, _, domain = email.partition("@")
    return bool(local.strip()) and bool(domain.strip())


def suggest_email_fix(email: str) -> str:
    if not isinstance(email, str):
        return email
    cleaned = email.replace(" ", "")
    return cleaned if cleaned != email else ""


# ------------------------------------------------------------
# Date parsing helpers
# ------------------------------------------------------------
def parse_date(date_str: str, strict: bool = False):
    if not isinstance(date_str, str) or not date_str.strip():
        return "", date_str, False

    original = date_str.strip()

    normalised = (
        original.replace(".", "-")
                .replace("/", "-")
                .replace(" ", "-")
    )

    if strict and not re.search(r"\b\d{4}\b", normalised):
        return "", original, False

    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%m-%d-%Y",
        "%d-%m-%y",
        "%m-%d-%y",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(normalised, fmt)

            if strict and "%y" in fmt:
                return "", original, False

            return dt.strftime("%Y-%m-%d"), original, True
        except ValueError:
            continue

    return "", original, False


# ------------------------------------------------------------
# Main cleaning function
# ------------------------------------------------------------
def clean_data(input_path: str, output_path: str, mode: str = "simple",
               strictness: str = "lenient", dry_run: bool = False,
               summary_only: bool = False):

    """Clean a CSV file according to the selected mode and strictness."""

    # ------------------------------------------------------------
    # Startup banner
    # ------------------------------------------------------------
    log_info("==============================================")
    log_info("        Glynn Cleaner — Data Cleaning Tool")
    log_info(f"                    Version {__version__}")
    log_info("==============================================")
    log_info(f"Mode: {mode} | Strictness: {strictness}")
    log_info("----------------------------------------------")

    # Progress counters
    step = 1
    total_steps = 10

    # ------------------------------------------------------------
    # Step 1 — Load CSV
    # ------------------------------------------------------------
    log_info(f"[{step}/{total_steps}] Loading CSV: {input_path}")
    step += 1

    df = load_csv(input_path)
    original_count = len(df)
    log_info(f"Rows loaded: {original_count}")

    # ------------------------------------------------------------
    # Step 2 — Column normalisation
    # ------------------------------------------------------------
    log_info(f"[{step}/{total_steps}] Normalising column names")
    step += 1

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    log_debug(f"Normalised columns: {df.columns.tolist()}")

    column_map = {
        "email_address": "email",
        "dob": "date_of_birth",
        "dateofbirth": "date_of_birth",
    }
    df = df.rename(columns={k: v for k, v in column_map.items() if k in df.columns})

    # ------------------------------------------------------------
    # Step 3 — Trim whitespace
    # ------------------------------------------------------------
    log_info(f"[{step}/{total_steps}] Trimming whitespace")
    step += 1

    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    # ------------------------------------------------------------
    # Step 4 — Capitalise names
    # ------------------------------------------------------------
    log_info(f"[{step}/{total_steps}] Applying name capitalisation")
    step += 1

    df["name"] = df["name"].str.title()

    # ------------------------------------------------------------
    # Step 5 — Remove junk rows
    # ------------------------------------------------------------
    log_info(f"[{step}/{total_steps}] Removing junk rows")
    step += 1

    def is_junk_row(row):
        vals = row.astype(str).str.strip()
        return all(v == "" or v == "'''" for v in vals)

    df = df.dropna(how="all")
    df = df[~df.apply(is_junk_row, axis=1)]
    removed_junk = original_count - len(df)
    log_info(f"Junk rows removed: {removed_junk}")

    # ------------------------------------------------------------
    # Step 6 — Email validation
    # ------------------------------------------------------------
    strict_flag = (strictness == "strict")
    log_info(f"[{step}/{total_steps}] Validating emails (strict={strict_flag})")
    step += 1

    df["email_valid"] = df["email"].apply(lambda e: is_valid_email(e, strict=strict_flag))
    df["email_suggested_fix"] = df["email"].apply(suggest_email_fix)

    invalid_email_count = (~df["email_valid"]).sum()
    log_info(f"Invalid emails detected: {invalid_email_count}")

    # ------------------------------------------------------------
    # Step 7 — Date parsing
    # ------------------------------------------------------------
    log_info(f"[{step}/{total_steps}] Parsing dates of birth")
    step += 1

    parsed = df["date_of_birth"].apply(lambda d: parse_date(d, strict=strict_flag))
    df["date_of_birth_cleaned"] = parsed.apply(lambda x: x[0])
    df["date_of_birth_original"] = parsed.apply(lambda x: x[1])
    df["date_of_birth_valid"] = parsed.apply(lambda x: x[2])

    invalid_date_count = (~df["date_of_birth_valid"]).sum()
    log_info(f"Invalid dates detected: {invalid_date_count}")

    # ------------------------------------------------------------
    # Step 8 — Strict mode filtering
    # ------------------------------------------------------------
    removed_invalid_emails = 0
    removed_invalid_dates = 0

    if strict_flag:
        log_info(f"[{step}/{total_steps}] Applying strict filtering rules")
        step += 1

        before = len(df)
        df = df[df["email_valid"]]
        removed_invalid_emails = before - len(df)
        log_info(f"Rows removed due to invalid emails: {removed_invalid_emails}")

        before = len(df)
        df = df[df["date_of_birth_valid"]]
        removed_invalid_dates = before - len(df)
        log_info(f"Rows removed due to invalid dates: {removed_invalid_dates}")
    else:
        # Still increment step even if strict mode is off
        log_info(f"[{step}/{total_steps}] Skipping strict filtering (lenient mode)")
        step += 1

    # ------------------------------------------------------------
    # Step 9 — Duplicate removal
    # ------------------------------------------------------------
    log_info(f"[{step}/{total_steps}] Removing duplicate rows")
    step += 1

    before = len(df)
    df = df.drop_duplicates()
    removed_dupes = before - len(df)
    log_info(f"Duplicates removed: {removed_dupes}")

    final_count = len(df)
    log_info(f"Final row count: {final_count}")

    # ------------------------------------------------------------
    # Simple mode: drop helper columns
    # ------------------------------------------------------------
    if mode == "simple":
        log_info("Simple mode selected — dropping helper columns")
        df = df[["name", "email", "date_of_birth", "notes"]]

    # ------------------------------------------------------------
    # Dry-run mode
    # ------------------------------------------------------------
    if dry_run:
        log_warning("Dry-run mode enabled — no output files will be written.")
        log_info("Cleaning process completed (dry-run).")

        log_info("Summary (dry-run):")
        log_info(f"  Rows loaded: {original_count}")
        log_info(f"  Junk rows removed: {removed_junk}")
        log_info(f"  Invalid emails removed: {removed_invalid_emails}")
        log_info(f"  Invalid dates removed: {removed_invalid_dates}")
        log_info(f"  Duplicates removed: {removed_dupes}")
        log_info(f"  Final row count: {final_count}")

        return

    # ------------------------------------------------------------
    # Step 10 — Save cleaned CSV (unless summary-only)
    # ------------------------------------------------------------
    log_info(f"[{step}/{total_steps}] Saving cleaned CSV")
    step += 1

    if not summary_only:
        save_csv(df, output_path)
    else:
        log_info("Skipping cleaned CSV (summary-only mode).")

    # ------------------------------------------------------------
    # Build summary
    # ------------------------------------------------------------
    summary = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input_file": input_path,
        "output_file": output_path,
        "mode": mode,
        "strictness": strictness,
        "rows_loaded": original_count,
        "junk_rows_removed": removed_junk,
        "invalid_emails_removed": removed_invalid_emails,
        "invalid_dates_removed": removed_invalid_dates,
        "duplicates_removed": removed_dupes,
        "final_row_count": final_count,
    }

    summary_path = output_path.replace(".csv", "_summary.csv")
    save_summary(summary, summary_path)

    # ------------------------------------------------------------
    # Human-readable report
    # ------------------------------------------------------------
    report_text = f"""
CLEANING REPORT — {summary['timestamp']}
----------------------------------------
Input file: {input_path}
Output file: {output_path}

Mode: {mode}
Strictness: {strictness}

Rows loaded: {original_count}
Junk rows removed: {removed_junk}
Invalid emails removed: {removed_invalid_emails}
Invalid dates removed: {removed_invalid_dates}
Duplicates removed: {removed_dupes}

Final row count: {final_count}
"""
    report_path = output_path.replace(".csv", "_report.txt")
    save_text_report(report_text.strip(), report_path)

    # ------------------------------------------------------------
    # Success banner
    # ------------------------------------------------------------
    log_info("==============================================")
    log_info(f"        Cleaning Completed Successfully (v{__version__})")
    log_info("==============================================")


# ------------------------------------------------------------
# CLI entry point
# ------------------------------------------------------------
def clean_data_cli():
    import argparse
    import logging

    parser = argparse.ArgumentParser(
        description="Clean CSV data with optional audit and strictness modes.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("--input", "-i", default="input/sample_dirty_data.csv")
    parser.add_argument("--output", "-o", default="output/cleaned_output.csv")
    parser.add_argument("--mode", "-m", choices=["simple", "audit"], default="simple")
    parser.add_argument("--strictness", "-s", choices=["lenient", "strict"], default="lenient")
    parser.add_argument(
        "--version",
        action="version",
        version=f"Data Cleaning Tool v{__version__}"
    )

    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--summary-only", action="store_true")

    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--quiet", action="store_true")

    args = parser.parse_args()

    # Adjust console logging level
    logger = logging.getLogger("cleaner_logger")
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    elif args.quiet:
        logger.setLevel(logging.WARNING)
    else:
        logger.setLevel(logging.INFO)

    clean_data(
        input_path=args.input,
        output_path=args.output,
        mode=args.mode,
        strictness=args.strictness,
        dry_run=args.dry_run,
        summary_only=args.summary_only
    )


if __name__ == "__main__":
    clean_data_cli()









