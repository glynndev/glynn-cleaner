import builtins
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from glynn_cleaner.helpers.email_disposable_loader import (
    load_disposable_domains,
    _write_cache,
    _load_cached_list,
    start_background_refresh,
    CACHE_PATH,
)


@pytest.fixture(autouse=True)
def clear_cache():
    # Reset LRU cache before each test
    load_disposable_domains.cache_clear()
    if CACHE_PATH.exists():
        CACHE_PATH.unlink()
    yield
    load_disposable_domains.cache_clear()
    if CACHE_PATH.exists():
        CACHE_PATH.unlink()


def test_load_remote_success(tmp_path):
    fake_data = "temp-mail.org\nmailinator.com\n"

    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = fake_data

        domains = load_disposable_domains()

    assert "temp-mail.org" in domains
    assert "mailinator.com" in domains
    assert CACHE_PATH.exists()


def test_load_remote_failure_falls_back_to_cache(tmp_path):
    # Write a fake cache file
    CACHE_PATH.write_text("cached.com\n", encoding="utf-8")

    with patch("requests.get", side_effect=Exception("Network down")):
        domains = load_disposable_domains()

    assert "cached.com" in domains
    assert len(domains) == 1


def test_load_remote_failure_no_cache_returns_empty(tmp_path):
    with patch("requests.get", side_effect=Exception("Network down")):
        domains = load_disposable_domains()

    assert domains == set()


def test_write_cache_creates_sorted_file(tmp_path):
    domains = {"z.com", "a.com", "m.com"}
    _write_cache(domains)

    text = CACHE_PATH.read_text(encoding="utf-8").splitlines()
    assert text == ["a.com", "m.com", "z.com"]


def test_background_refresh_thread_starts():
    with patch("threading.Thread") as mock_thread:
        start_background_refresh()
        mock_thread.assert_called_once()
        args, kwargs = mock_thread.call_args
        assert kwargs["daemon"] is True


