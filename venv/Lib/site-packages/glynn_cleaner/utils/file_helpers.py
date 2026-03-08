import os
import pandas as pd
from glynn_cleaner.utils.logger import log_info, log_error, log_debug


def _ensure_directory(path: str):
    """Create the directory for a file path if it doesn't already exist."""
    dir_path = os.path.dirname(path)
    if dir_path:  # Avoid creating '' when saving to current directory
        os.makedirs(dir_path, exist_ok=True)


def load_csv(path):
    log_info(f"Loading CSV: {path}")
    try:
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        log_info(f"Loaded CSV successfully with {len(df)} rows")
        log_debug(f"Columns detected: {df.columns.tolist()}")
        return df
    except Exception as e:
        log_error(f"Failed to load CSV '{path}': {e}")
        raise


def save_csv(df, path):
    _ensure_directory(path)

    log_info(f"Saving cleaned CSV to: {path}")
    try:
        df.to_csv(path, index=False)
        log_info("Cleaned CSV saved successfully")
    except Exception as e:
        log_error(f"Failed to save cleaned CSV '{path}': {e}")
        raise


def save_summary(summary_dict, path):
    _ensure_directory(path)

    log_info(f"Saving summary CSV to: {path}")
    try:
        df = pd.DataFrame([summary_dict])
        df.to_csv(path, index=False)
        log_info("Summary CSV saved successfully")
        log_debug(f"Summary contents: {summary_dict}")
    except Exception as e:
        log_error(f"Failed to save summary CSV '{path}': {e}")
        raise


def save_text_report(text, path):
    _ensure_directory(path)

    log_info(f"Saving text report to: {path}")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        log_info("Text report saved successfully")
    except Exception as e:
        log_error(f"Failed to save text report '{path}': {e}")
        raise



