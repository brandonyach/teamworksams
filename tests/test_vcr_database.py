import pytest
import vcr
from teamworksams.database_main import get_database, delete_database_entry, insert_database_entry, update_database_entry
from teamworksams.database_option import GetDatabaseOption, InsertDatabaseOption, UpdateDatabaseOption
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
def test_delete_database_vcr(credentials):
    """Test delete_database_entry with recorded API responses."""
    entry_id = 386301 
    try:
        success = delete_database_entry(
            database_entry_id=entry_id,
            url=credentials["url"],
            username=credentials["username"],
            password=credentials["password"]
        )
        assert "Success" in success
    except Exception as e:
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
    option = UpdateDatabaseOption(interactive_mode=False)
    try:
        update_database_entry(
            df=test_update_df,
            form="Allergies",
            url=credentials["url"],
            username=credentials["username"],
            password=credentials["password"],
            option=option
        )
    except Exception as e:
        pytest.fail(f"update_database_entry failed: {str(e)}")