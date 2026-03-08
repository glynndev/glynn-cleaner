from __future__ import annotations

import logging
import threading
import time
from functools import lru_cache
from pathlib import Path
from typing import Set

import requests

LOGGER = logging.getLogger(__name__)

# ------------------------------------------------------------
# Correct, stable upstream disposable-domain list
# ------------------------------------------------------------
BLACKLIST_URL = (
    "https://raw.githubusercontent.com/disposable/"
    "disposable-email-domains/master/domains.txt"
)

# Cache file lives alongside this module
CACHE_PATH = Path(__file__).with_name("disposable_email_blacklist.conf")


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def _parse_lines(text: str) -> Set[str]:
    return {
        line.strip().lower()
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    }


def _fetch_remote_list() -> Set[str]:
    response = requests.get(BLACKLIST_URL, timeout=10)
    response.raise_for_status()
    return _parse_lines(response.text)


def _load_cached_list() -> Set[str]:
    if not CACHE_PATH.exists():
        LOGGER.warning("Disposable email cache file not found: %s", CACHE_PATH)
        return set()

    text = CACHE_PATH.read_text(encoding="utf-8")
    return _parse_lines(text)


def _write_cache(domains: Set[str]) -> None:
    try:
        CACHE_PATH.write_text("\n".join(sorted(domains)), encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        LOGGER.warning("Failed to write disposable email cache: %s", exc)


# ------------------------------------------------------------
# Main loader (cached)
# ------------------------------------------------------------
@lru_cache(maxsize=1)
def load_disposable_domains() -> Set[str]:
    """
    Load the disposable domain set.

    Strategy:
    - Try remote GitHub list.
    - On success, update local cache and return.
    - On failure, fall back to cached file (if present).
    - If both fail, return an empty set.
    """
    try:
        domains = _fetch_remote_list()
        _write_cache(domains)
        LOGGER.info("Loaded %d disposable domains from remote source", len(domains))
        return domains

    except Exception as exc:  # noqa: BLE001
        LOGGER.warning("Failed to load disposable domains from remote source: %s", exc)

        cached = _load_cached_list()
        if cached:
            LOGGER.info("Loaded %d disposable domains from cache", len(cached))
        else:
            LOGGER.warning("No disposable domain cache available; using empty set")

        return cached


# ------------------------------------------------------------
# Background refresh loop (24 hours)
# ------------------------------------------------------------
REFRESH_INTERVAL_SECONDS = 24 * 60 * 60  # 24 hours


def _refresh_loop():
    while True:
        time.sleep(REFRESH_INTERVAL_SECONDS)
        try:
            domains = _fetch_remote_list()
            _write_cache(domains)
            load_disposable_domains.cache_clear()
            load_disposable_domains()
            LOGGER.info(
                "Refreshed disposable domain list (%d entries)", len(domains)
            )
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("Failed to refresh disposable domain list: %s", exc)


def start_background_refresh():
    """
    Start the background refresh thread.

    Safe to call multiple times — only one daemon thread will run
    because Python won't keep the process alive for daemon threads.
    """
    thread = threading.Thread(target=_refresh_loop, daemon=True)
    thread.start()


