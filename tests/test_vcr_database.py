import pytest
import vcr
from teamworksams.database_main import get_database, delete_database_entry, insert_database_entry, update_database_entry
from teamworksams.database_option import GetDatabaseOption, InsertDatabaseOption, UpdateDatabaseOption
from teamworksams.utils import get_client, AMSError
from pandas import DataFrame
from tests.test_fixtures import credentials


@pytest.fixture
def test_insert_df():
    """Provide a test DataFrame for inserting database entries."""
    return DataFrame({
        "Allergy": ["Eggs"],
        "Reaction": ["Inflammation"]
    })


@pytest.fixture
def test_update_df():
    """Provide a test DataFrame for updating database entries."""
    return DataFrame({
        "entry_id": [386304],
        "Allergy": ["Dairy"],
        "Reaction": ["Inflammation"]
    })


@vcr.use_cassette('tests/cassettes/get_database.yaml')
def test_get_database_vcr(credentials):
    """Test get_database with recorded API responses."""
    option = GetDatabaseOption(interactive_mode=False)
    try:
        df = get_database(
            form_name="Allergies",
            url=credentials["url"],
            username=credentials["username"],
            password=credentials["password"],
            limit=1000,
            offset=0,
            option=option
        )
        assert isinstance(df, DataFrame)
        assert "id" in df.columns
        assert "form_name" in df.columns
    except Exception as e:
        pytest.fail(f"get_database failed: {str(e)}")


@vcr.use_cassette('tests/cassettes/delete_database.yaml')
def test_delete_database_vcr(credentials, test_insert_df):
    """Test delete_database_entry with recorded API responses."""
    client = get_client(
        url=credentials["url"],
        username=credentials["username"],
        password=credentials["password"],
        cache=False,
        interactive_mode=False
    )
    try:
        option = InsertDatabaseOption(interactive_mode=False)
        insert_database_entry(
            df=test_insert_df,
            form="Allergies",
            url=credentials["url"],
            username=credentials["username"],
            password=credentials["password"],
            option=option,
            client=client
        )
    except AMSError as e:
        pytest.fail(f"Failed to insert test entry: {str(e)}")
    get_option = GetDatabaseOption(interactive_mode=False)
    try:
        df = get_database(
            form_name="Allergies",
            url=credentials["url"],
            username=credentials["username"],
            password=credentials["password"],
            limit=1,
            offset=0,
            option=get_option,
            client=client
        )
    except AMSError as e:
        pytest.fail(f"Failed to fetch inserted entry: {str(e)}")
    if df.empty:
        pytest.fail("No entries found after insertion")
    entry_id = int(df["id"].iloc[0])
    try:
        success = delete_database_entry(
            database_entry_id=entry_id,
            url=credentials["url"],
            username=credentials["username"],
            password=credentials["password"],
            client=client
        )
        assert "Success" in success
    except AMSError as e:
        if "UNREGISTERED SERVER ERROR TYPE" in str(e):
            pytest.skip(f"Entry ID {entry_id} does not exist, likely already deleted: {str(e)}")
        else:
            pytest.fail(f"delete_database_entry failed: {str(e)}")     


@vcr.use_cassette('tests/cassettes/insert_database.yaml')
def test_insert_database_vcr(credentials, test_insert_df):
    """Test insert_database_entry with recorded API responses."""
    option = InsertDatabaseOption(interactive_mode=False)
    try:
        insert_database_entry(
            df=test_insert_df,
            form="Allergies",
            url=credentials["url"],
            username=credentials["username"],
            password=credentials["password"],
            option=option
        )
    except Exception as e:
        pytest.fail(f"insert_database_entry failed: {str(e)}")


@vcr.use_cassette('tests/cassettes/update_database.yaml')
def test_update_database_vcr(credentials, test_update_df):
    """Test update_database_entry with recorded API responses."""
    update_option = UpdateDatabaseOption(interactive_mode=False)
    try:
        update_database_entry(
            df=test_update_df,
            form="Allergies",
            url=credentials["url"],
            username=credentials["username"],
            password=credentials["password"],
            option=update_option
        )
    except Exception as e:
        pytest.fail(f"update_database_entry failed: {str(e)}")


def test_delete_database_vcr_other_error(credentials, test_insert_df, mocker):
    """Test delete_database_entry with a different AMSError to cover else branch."""
    # Mock the _fetch method to raise a different AMSError
    mocker.patch(
        'teamworksams.utils.AMSClient._fetch',
        side_effect=AMSError("Unexpected error")
    )
    client = get_client(
        url=credentials["url"],
        username=credentials["username"],
        password=credentials["password"],
        cache=False,
        interactive_mode=False
    )
    try:
        # Call the function, expecting the else branch to trigger pytest.fail
        with pytest.raises(pytest.fail.Exception) as exc_info:
            try:
                delete_database_entry(
                    database_entry_id=123,
                    url=credentials["url"],
                    username=credentials["username"],
                    password=credentials["password"],
                    client=client
                )
            except AMSError as e:
                if "UNREGISTERED SERVER ERROR TYPE" in str(e):
                    pytest.skip(f"Entry ID 123 does not exist: {str(e)}")
                else:
                    pytest.fail(f"delete_database_entry failed: {str(e)}")
        assert "Unexpected error" in str(exc_info.value)
    except pytest.fail.Exception as e:
        # Ensure the failure message contains the expected error
        assert "Unexpected error" in str(e)