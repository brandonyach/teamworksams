# tests/test_vcr_auth.py
import pytest
import vcr
from teamworksams.login_main import login
from teamworksams.utils import get_client
from teamworksams.login_option import LoginOption
from tests.test_fixtures import credentials


@vcr.use_cassette('tests/cassettes/login.yaml')
def test_login_vcr(credentials):
    """Test login with recorded API responses."""
    option = LoginOption(interactive_mode=False)
    result = login(
        url=credentials["url"],
        username=credentials["username"],
        password=credentials["password"],
        option=option
    )
    assert isinstance(result, dict)
    assert "session_header" in result
    assert "cookie" in result
    assert "login_data" in result
    assert result["cookie"].startswith("JSESSIONID=")


@vcr.use_cassette('tests/cassettes/get_client.yaml')
def test_get_client_vcr(credentials):
    """Test get_client with recorded API responses."""
    client = get_client(
        url=credentials["url"],
        username=credentials["username"],
        password=credentials["password"],
        cache=True,
        interactive_mode=False
    )
    assert client.authenticated
    assert client.session_header is not None