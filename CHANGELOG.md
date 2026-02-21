# Changelog
All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and the project adheres to [Semantic Versioning](https://semver.org/).

---

## [1.3] – 2026-02-08
### Added
- Centralised version number via `glynn_cleaner.__version__`.
- Structured progress messages across all cleaning stages.
- Startup banner and success banner for a polished CLI experience.
- `--no-colour` flag to disable ANSI colour output.
- Name capitalisation for the `name` column.
- Summary CSV and human‑readable report generation.
- Dry‑run mode (runs all steps without writing files).
- Summary‑only mode (skips cleaned CSV output).
- Strict email validation using RFC‑like regex.
- Strict date validation requiring 4‑digit year and valid calendar date.

### Improved
- Logging system upgraded with colour‑safe wrappers.
- Cleaner, more consistent console output.
- Column normalisation and whitespace trimming logic refined.
- Junk row detection made more robust.

### Fixed
- Duplicate progress message for email/date validation.
- Step counter initialisation order.
- Minor inconsistencies in logging output.

---

## [1.2] – 2026-01-XX
### Added
- Duplicate row removal.
- Improved junk row filtering.
- Initial audit mode structure.

---

## [1.1] – 2025-12-XX
### Added
- Email suggestion logic (removes spaces).
- Basic date parsing and normalisation.
- Initial summary reporting.

---

## [1.0] – 2025-12-XX
### Added
- First public release.
- Simple mode cleaning pipeline.
- Column normalisation and whitespace trimming.
- Basic logging and CSV output.
