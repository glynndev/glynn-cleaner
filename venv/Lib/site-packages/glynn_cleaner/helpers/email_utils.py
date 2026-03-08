import re
import unicodedata
from glynn_cleaner.helpers.email_disposable_loader import load_disposable_domains


def _normalise_email(email: str) -> str:
    if not isinstance(email, str):
        return ""
    return email.strip()


def _is_idn(email: str) -> bool:
    try:
        _, domain = email.split("@", 1)
    except ValueError:
        return True
    if any(ord(c) > 127 for c in domain):
        return True
    if domain.lower().startswith("xn--"):
        return True
    return False


def _has_plus_alias(email: str) -> bool:
    try:
        local, _ = email.split("@", 1)
    except ValueError:
        return True
    return "+" in local


def _has_invalid_format(email: str) -> bool:
    if email.count("@") != 1:
        return True
    local, domain = email.split("@", 1)
    if not local or not domain:
        return True
    if local.startswith(".") or local.endswith("."):
        return True
    if ".." in local:
        return True
    if domain.startswith(".") or domain.endswith("."):
        return True
    if ".." in domain:
        return True
    if "_" in domain:
        return True
    if domain.count(".") < 1:
        return True
    if any(c.isupper() for c in domain):
        return True
    return False


def _has_valid_tld(email: str) -> bool:
    try:
        _, domain = email.split("@", 1)
    except ValueError:
        return False
    parts = domain.lower().split(".")
    if len(parts) < 2:
        return False
    for i in range(1, len(parts)):
        candidate = ".".join(parts[i:])
        if candidate in VALID_TLDS:
            return True
    return False


def is_disposable_domain(domain: str) -> bool:
    return domain.lower() in load_disposable_domains()


def _is_disposable_domain(email: str) -> bool:
    try:
        _, domain = email.split("@", 1)
    except ValueError:
        return True
    return is_disposable_domain(domain)


def _is_role_based(email: str) -> bool:
    try:
        local, _ = email.split("@", 1)
    except ValueError:
        return True
    return local.lower() in ROLE_BASED_PREFIXES


def _has_invalid_domain(email: str) -> bool:
    try:
        _, domain = email.split("@", 1)
    except ValueError:
        return True
    if domain.startswith("-") or domain.endswith("-"):
        return True
    if not re.match(r"^[a-z0-9.-]+$", domain):
        return True
    return False


def _passes_format_rules(email: str) -> bool:
    if _is_idn(email):
        return False
    if _has_plus_alias(email):
        return False
    if _has_invalid_format(email):
        return False
    return True


def _passes_security_rules(email: str) -> bool:
    if _is_disposable_domain(email):
        return False
    if _is_role_based(email):
        return False
    return True


def _passes_domain_rules(email: str) -> bool:
    if _has_invalid_domain(email):
        return False
    if not _has_valid_tld(email):
        return False
    return True


def is_valid_email_strict(email: str) -> bool:
    email = _normalise_email(email)
    return (
        _passes_format_rules(email)
        and _passes_security_rules(email)
        and _passes_domain_rules(email)
    )


def is_valid_email(email: str, strict: bool = False) -> bool:
    email = _normalise_email(email)

    # Always reject disposable domains
    try:
        _, domain = email.split("@", 1)
    except ValueError:
        return False
    if domain.lower() in load_disposable_domains():
        return False

    if strict:
        return is_valid_email_strict(email)

    # Lenient mode: basic sanity checks
    if email.count("@") != 1:
        return False
    local, domain = email.split("@", 1)
    if not local or not domain:
        return False
    if "." not in domain:
        return False
    return True


def suggest_email_fix(email: str) -> str:
    email = _normalise_email(email)
    if _is_idn(email):
        return ""
    if email.count("@") != 1:
        return ""
    local, domain = email.split("@", 1)
    if not local or not domain:
        return ""
    if domain.lower() in load_disposable_domains():
        return ""
    if local.lower() in ROLE_BASED_PREFIXES:
        return ""
    if "." not in domain:
        if domain.lower() in COMMON_PROVIDER_DOMAINS:
            return f"{local}@{COMMON_PROVIDER_DOMAINS[domain.lower()]}"
    if domain.lower() in COMMON_PROVIDER_DOMAINS:
        return f"{local}@{COMMON_PROVIDER_DOMAINS[domain.lower()]}"
    return ""


VALID_TLDS = {
    "com", "co.uk", "org", "org.uk", "net", "io", "ai", "co", "co.nz", "co.au",
    "uk", "gov.uk", "edu", "info", "biz", "dev", "app", "me", "us", "ca", "de",
    "fr", "es", "it", "nl", "se", "no", "fi", "dk", "ch", "be", "pl", "cz",
    "sk", "hu", "at", "ie", "pt", "gr", "ro", "bg", "lt", "lv", "ee", "jp",
    "kr", "cn", "in", "br", "mx", "ar", "za",
}

ROLE_BASED_PREFIXES = {
    "admin", "administrator", "support", "help", "info", "contact", "sales",
    "enquiries", "enquiry", "office", "team", "customerservice", "service",
}

COMMON_PROVIDER_DOMAINS = {
    "gamil.com": "gmail.com",
    "gmial.com": "gmail.com",
    "hotnail.com": "hotmail.com",
    "hotmial.com": "hotmail.com",
    "outlok.com": "outlook.com",
    "yaho.com": "yahoo.com",
    "icloud.co": "icloud.com",
}





