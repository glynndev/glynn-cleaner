import re

COMMON_DOMAINS = {
    "gmail": "gmail.com",
    "hotmail": "hotmail.com",
    "outlook": "outlook.com",
    "yahoo": "yahoo.com",
    "live": "live.com",
}

def suggest_email_fix(email: str) -> str | None:
    """
    Returns a suggested fix for an invalid email.
    Never modifies the original email.
    Only suggests safe, obvious corrections.
    """

    if not isinstance(email, str):
        return None

    e = email.strip().lower()

    # If it's already valid, no suggestion needed
    if re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", e):
        return None

    # 1. Missing TLD but domain is a known provider
    # e.g. sarah@gmail → sarah@gmail.com
    match = re.match(r"^([\w\.-]+)@([a-zA-Z]+)$", e)
    if match:
        user, domain = match.groups()
        if domain in COMMON_DOMAINS:
            return f"{user}@{COMMON_DOMAINS[domain]}"

    # 2. Common typos
    typo_fixes = {
        "gamil.com": "gmail.com",
        "gnail.com": "gmail.com",
        "hotnail.com": "hotmail.com",
        "hotmai.com": "hotmail.com",
        "yaho.com": "yahoo.com",
        "outlok.com": "outlook.com",
    }

    for wrong, correct in typo_fixes.items():
        if e.endswith(wrong):
            return e.replace(wrong, correct)

    # 3. Trailing punctuation
    if e.endswith((".", ",", ";", "!", "?")):
        return e.rstrip(".,;!?")

    # 4. Double dots in domain
    if ".." in e:
        return e.replace("..", ".")

    # 5. Missing @ but looks like an email
    if "@" not in e and "." in e:
        # e.g. sarah.gmail.com → sarah@gmail.com (only if domain is known)
        parts = e.split(".")
        if len(parts) >= 2 and parts[-2] in COMMON_DOMAINS:
            user = ".".join(parts[:-2])
            domain = parts[-2]
            suggestion = f"{user}@{COMMON_DOMAINS[domain]}"
            return suggestion.lower()

    # No safe suggestion
    return None