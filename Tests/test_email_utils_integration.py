from unittest.mock import patch

from glynn_cleaner.helpers.email_utils import is_valid_email
from glynn_cleaner.helpers.email_disposable_loader import load_disposable_domains


def test_email_validation_with_disposable_domain():
    # Pretend the loader returns a known disposable domain
    with patch(
        "glynn_cleaner.helpers.email_disposable_loader.load_disposable_domains",
        return_value={"mailinator.com"},
    ):
        assert not is_valid_email("test@mailinator.com")
        assert is_valid_email("good@example.com")

