import pytest
import vcr
from teamworksams.export_main import get_event_data, sync_event_data, get_profile_data
from teamworksams.export_option import EventOption, SyncEventOption, ProfileOption
from teamworksams.export_filter import EventFilter, SyncEventFilter, ProfileFilter
from pandas import DataFrame
from tests.test_fixtures import credentials
from datetime import datetime


@vcr.use_cassette('tests/cassettes/get_event_data.yaml')
def test_get_event_data_vcr(credentials):
    """Test get_event_data with recorded API responses."""
    option = EventOption(interactive_mode=False, clean_names=True)
    try:
        df = get_event_data(
            form="Training Log",
            start_date="01/01/2025",
            end_date="31/12/2025",
            url=credentials["url"],
            username=credentials["username"],
            password=credentials["password"],
            filter=None,
            option=option
        )
        assert isinstance(df, DataFrame)
        assert "event_id" in df.columns
        assert "user_id" in df.columns
        assert "form" in df.columns
        assert "start_date" in df.columns
    except Exception as e:
        pytest.fail(f"get_event_data failed: {str(e)}")


@vcr.use_cassette('tests/cassettes/sync_event_data.yaml')
def test_sync_event_data_vcr(credentials):
    """Test sync_event_data with recorded API responses."""
    option = SyncEventOption(interactive_mode=False, include_user_data=True)
    last_sync_time = int(datetime(2025, 1, 1).timestamp() * 1000)  
    try:
        df, new_sync_time = sync_event_data(
            form="Training Log",
            last_synchronisation_time=last_sync_time,
            url=credentials["url"],
            username=credentials["username"],
            password=credentials["password"],
            filter=None,
            option=option
        )
        assert isinstance(df, DataFrame)
        assert "event_id" in df.columns
        assert "user_id" in df.columns
        assert "form" in df.columns
        assert isinstance(new_sync_time, int)
    except Exception as e:
        pytest.fail(f"sync_event_data failed: {str(e)}")


@vcr.use_cassette('tests/cassettes/get_profile_data.yaml')
def test_get_profile_data_vcr(credentials):
    """Test get_profile_data with recorded API responses."""
    option = ProfileOption(interactive_mode=False, clean_names=True)
    try:
        df = get_profile_data(
            form="Athlete Profile", 
            url=credentials["url"],
            username=credentials["username"],
            password=credentials["password"],
            filter=None,
            option=option
        )
        assert isinstance(df, DataFrame)
        assert "profile_id" in df.columns
        assert "user_id" in df.columns
        assert "form" in df.columns
    except Exception as e:
        pytest.fail(f"get_profile_data failed: {str(e)}")