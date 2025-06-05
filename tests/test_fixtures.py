import os
import pytest
from dotenv import load_dotenv
import keyring


@pytest.fixture(scope="session")
def credentials():
    """Provide test credentials with keyring and env fallback."""
    load_dotenv()
    try:
        import keyring
        username = keyring.get_password("smartabasepy", "username") or os.getenv("AMS_USERNAME", "")
        password = keyring.get_password("smartabasepy", "password") or os.getenv("AMS_PASSWORD", "")
    except (ImportError, keyring.errors.NoKeyringError):
        username = os.getenv("AMS_USERNAME", "")
        password = os.getenv("AMS_PASSWORD", "")
    url = os.getenv("AMS_URL", "")
    return {"url": url, "username": username, "password": password}