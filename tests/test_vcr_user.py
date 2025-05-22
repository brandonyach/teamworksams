import pytest
import vcr
from teamworksams.user_main import get_user, edit_user, create_user, get_group
from teamworksams.user_option import UserOption, GroupOption
from teamworksams.user_filter import UserFilter
from pandas import DataFrame
from tests.test_fixtures import credentials


@pytest.fixture
def test_user_df():
    """Provide a test DataFrame for creating users."""
    return DataFrame({
        "first_name": ["Test"],
        "last_name": ["User"],
        "username": ["test.user.2025@example.com"],  
        "email": ["test.user.2025@example.com"],
        "dob": ["2000-01-01"],
        "password": ["Test123!"],
        "active": [True],
        "sex": ["Male"],
        "uuid": ["test-uuid-123"],
        "known_as": [""],
        "middle_names": [""],
        "language": [""],
        "sidebar_width": [""]
    })


@pytest.fixture
def test_edit_df():
    """Provide a test DataFrame for editing users."""
    return DataFrame({
        "username": ["test.user.2025@example.com"],
        "first_name": ["UpdatedTest"]
    })


@vcr.use_cassette('tests/cassettes/get_user.yaml')
def test_get_user_vcr(credentials):
    """Test get_user with recorded API responses."""
    option = UserOption(interactive_mode=False)
    df = get_user(
        url=credentials["url"],
        username=credentials["username"],
        password=credentials["password"],
        filter=None,  
        option=option
    )
    assert isinstance(df, DataFrame)
    assert "user_id" in df.columns
    assert "username" in df.columns


@vcr.use_cassette('tests/cassettes/edit_user.yaml')
def test_edit_user_vcr(credentials, test_edit_df):
    """Test edit_user with recorded API responses."""
    option = UserOption(interactive_mode=False)
    failed_df = edit_user(
        mapping_df=test_edit_df,
        user_key="username",
        url=credentials["url"],
        username=credentials["username"],
        password=credentials["password"],
        option=option
    )
    assert isinstance(failed_df, DataFrame)
    assert "user_key" in failed_df.columns
    assert "reason" in failed_df.columns


@vcr.use_cassette('tests/cassettes/create_user.yaml')
def test_create_user_vcr(credentials, test_user_df):
    """Test create_user with recorded API responses."""
    option = UserOption(interactive_mode=False)
    failed_df = create_user(
        user_df=test_user_df,
        url=credentials["url"],
        username=credentials["username"],
        password=credentials["password"],
        option=option
    )
    assert isinstance(failed_df, DataFrame)
    assert "user_key" in failed_df.columns
    assert "reason" in failed_df.columns


@vcr.use_cassette('tests/cassettes/get_group.yaml')
def test_get_group_vcr(credentials):
    """Test get_group with recorded API responses."""
    option = GroupOption(interactive_mode=False)
    df = get_group(
        url=credentials["url"],
        username=credentials["username"],
        password=credentials["password"],
        option=option
    )
    assert isinstance(df, DataFrame)
    assert "name" in df.columns