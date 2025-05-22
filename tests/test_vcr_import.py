import pytest
import vcr
from teamworksams.import_main import insert_event_data, update_event_data, upsert_event_data, upsert_profile_data
from teamworksams.import_option import InsertEventOption, UpdateEventOption, UpsertEventOption, UpsertProfileOption
from pandas import DataFrame
from tests.test_fixtures import credentials


@pytest.fixture
def test_insert_df():
    """Provide a test DataFrame for inserting events."""
    return DataFrame({
        "user_id": [72827],  
        "start_date": ["01/01/2025"],
        "Duration": [60],
        "RPE": [6]
    })


@pytest.fixture
def test_update_df():
    """Provide a test DataFrame for updating events."""
    return DataFrame({
        "event_id": [2296234], 
        "user_id": [72827],
        "Duration": [60],
        "RPE": [6]
    })


@pytest.fixture
def test_upsert_df():
    """Provide a test DataFrame for upserting events."""
    return DataFrame({
        "event_id": [2296256, None],  
        "user_id": [72827, 72828],
        "start_date": ["01/03/2025", "01/03/2025"],
        "Duration": [65, 45],
        "RPE": [8, 9]
    })


@pytest.fixture
def test_profile_df():
    """Provide a test DataFrame for upserting profiles."""
    return DataFrame({
        "user_id": [72828],
        "Athlete Number": [18],
        "ID": ["b427232d-3001-44bb-b4b4-6b6a970647fd"]
    })


@vcr.use_cassette('tests/cassettes/insert_event.yaml')
def test_insert_event_vcr(credentials, test_insert_df):
    """Test insert_event_data with recorded API responses."""
    option = InsertEventOption(interactive_mode=False, id_col="user_id")
    try:
        insert_event_data(
            df=test_insert_df,
            form="Training Log",
            url=credentials["url"],
            username=credentials["username"],
            password=credentials["password"],
            option=option
        )
    except Exception as e:
        pytest.fail(f"insert_event_data failed: {str(e)}")


@vcr.use_cassette('tests/cassettes/update_event.yaml')
def test_update_event_vcr(credentials, test_update_df):
    """Test update_event_data with recorded API responses."""
    option = UpdateEventOption(interactive_mode=False, id_col="user_id")
    try:
        update_event_data(
            df=test_update_df,
            form="Training Log",
            url=credentials["url"],
            username=credentials["username"],
            password=credentials["password"],
            option=option
        )
    except Exception as e:
        pytest.fail(f"update_event_data failed: {str(e)}")


@vcr.use_cassette('tests/cassettes/upsert_event.yaml')
def test_upsert_event_vcr(credentials, test_upsert_df):
    """Test upsert_event_data with recorded API responses."""
    option = UpsertEventOption(interactive_mode=False, id_col="user_id")
    try:
        upsert_event_data(
            df=test_upsert_df,
            form="Training Log",
            url=credentials["url"],
            username=credentials["username"],
            password=credentials["password"],
            option=option
        )
    except Exception as e:
        pytest.fail(f"upsert_event_data failed: {str(e)}")


@vcr.use_cassette('tests/cassettes/upsert_profile.yaml')
def test_upsert_profile_vcr(credentials, test_profile_df):
    """Test upsert_profile_data with recorded API responses."""
    option = UpsertProfileOption(interactive_mode=False, id_col="user_id")
    try:
        upsert_profile_data(
            df=test_profile_df,
            form="Athlete Profile",
            url=credentials["url"],
            username=credentials["username"],
            password=credentials["password"],
            option=option
        )
    except Exception as e:
        pytest.fail(f"upsert_profile_data failed: {str(e)}")