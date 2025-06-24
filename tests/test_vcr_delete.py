import pytest
import vcr
import pandas as pd
from teamworksams.delete_main import delete_event_data, delete_multiple_events
from teamworksams.delete_option import DeleteEventOption
from teamworksams.import_main import insert_event_data
from teamworksams.import_option import InsertEventOption
from teamworksams.export_main import get_event_data
from teamworksams.form_main import get_forms
from teamworksams.export_option import EventOption
from teamworksams.utils import AMSClient, AMSError
from tests.test_fixtures import credentials
from unittest.mock import patch
import time

@pytest.fixture
def valid_form(credentials):
    """Retrieve a valid event form name."""
    with vcr.use_cassette('tests/cassettes/get_forms.yaml', record_mode='new_episodes'):
        forms_df = get_forms(
            url=credentials["url"],
            username=credentials["username"],
            password=credentials["password"],
            option=None
        )
        event_forms = forms_df[forms_df["type"].str.lower() == "event"]["form_name"]
        if event_forms.empty:
            if not forms_df.empty:
                return forms_df["form_name"].iloc[0]
            pytest.fail("No forms available in AMS instance")
        return event_forms.iloc[0]


@pytest.fixture
def created_event_id(credentials, valid_form):
    """Create a test event and return its event_id."""
    df = pd.DataFrame({
        "username": [credentials["username"]],
        "start_date": ["01/01/2025"],
        "duration": [60]
    })
    with vcr.use_cassette('tests/cassettes/insert_test_event.yaml', record_mode='new_episodes'):
        insert_event_data(
            df=df,
            form=valid_form,
            url=credentials["url"],
            username=credentials["username"],
            password=credentials["password"],
            option=InsertEventOption(interactive_mode=False, id_col="username")
        )
    for _ in range(3):
        with vcr.use_cassette('tests/cassettes/get_event_data_for_id.yaml', record_mode='new_episodes'):
            df_events = get_event_data(
                form=valid_form,
                start_date="01/01/2024",
                end_date="01/02/2025",
                url=credentials["url"],
                username=credentials["username"],
                password=credentials["password"],
                option=EventOption(interactive_mode=False)
            )
            if not df_events.empty:
                return int(df_events["event_id"].iloc[0])
        time.sleep(1)
    pytest.fail(f"Failed to create or retrieve test event in form '{valid_form}'")


@pytest.fixture(autouse=True)
def cleanup_event(credentials, valid_form, created_event_id):
    """Clean up test event after test."""
    yield
    with vcr.use_cassette('tests/cassettes/cleanup_test_event.yaml', record_mode='new_episodes'):
        try:
            delete_event_data(
                event_id=created_event_id,
                url=credentials["url"],
                username=credentials["username"],
                password=credentials["password"],
                option=DeleteEventOption(interactive_mode=False)
            )
        except AMSError:
            pass


@vcr.use_cassette('tests/cassettes/delete_event_data_success.yaml', record_mode='new_episodes')
def test_delete_event_data_success(credentials, created_event_id):
    """Test successful deletion of a single event."""
    with patch.object(AMSClient, "_fetch", return_value={"state": "SUCCESS", "message": f"Deleted {created_event_id}"}):
        result = delete_event_data(
            event_id=created_event_id,
            url=credentials["url"],
            username=credentials["username"],
            password=credentials["password"],
            option=DeleteEventOption(interactive_mode=False)
        )
        assert "SUCCESS" in result
        assert isinstance(result, str)


@vcr.use_cassette('tests/cassettes/delete_event_data_invalid_id.yaml', record_mode='new_episodes')
def test_delete_event_data_invalid_id(credentials):
    """Test deletion with invalid event_id."""
    with pytest.raises(ValueError) as exc_info:
        delete_event_data(
            event_id=-1,
            url=credentials["url"],
            username=credentials["username"],
            password=credentials["password"],
            option=DeleteEventOption(interactive_mode=False)
        )
    assert "event_id must be a single positive integer" in str(exc_info.value)


@vcr.use_cassette('tests/cassettes/delete_event_data_invalid_response.yaml', record_mode='new_episodes')
def test_delete_event_data_invalid_response(credentials):
    """Test deletion with invalid API response."""
    with patch.object(AMSClient, "_fetch", return_value={"state": "ERROR", "message": "Invalid event ID"}):
        result = delete_event_data(
            event_id=999999,
            url=credentials["url"],
            username=credentials["username"],
            password=credentials["password"],
            option=DeleteEventOption(interactive_mode=False)
        )
        assert "ERROR" in result
        assert isinstance(result, str)


def test_delete_event_data_interactive_cancel(capsys, monkeypatch):
    """Test interactive mode cancellation in delete_event_data."""
    prompts = []
    def mock_input(prompt):
        prompts.append(prompt)
        return "n"
    monkeypatch.setattr("builtins.input", mock_input)
    with pytest.raises(AMSError) as exc_info:
        delete_event_data(
            event_id=134273,
            url="https://example.smartabase.com/site",
            username="user",
            password="pass",
            option=DeleteEventOption(interactive_mode=True)
        )
    assert "Delete operation cancelled by user" in str(exc_info.value)
    print(f"Debug: Captured prompts: {prompts}")
    assert any("Are you sure" in p for p in prompts) 
    captured = capsys.readouterr()
    assert "Are you sure" in captured.out  


@vcr.use_cassette('tests/cassettes/delete_multiple_events_success.yaml', record_mode='new_episodes')
def test_delete_multiple_events_success(credentials, created_event_id):
    """Test successful deletion of multiple events."""
    with patch.object(AMSClient, "_fetch", return_value=None):
        result = delete_multiple_events(
            event_ids=[created_event_id],
            url=credentials["url"],
            username=credentials["username"],
            password=credentials["password"],
            option=DeleteEventOption(interactive_mode=False)
        )
        assert "SUCCESS" in result
        assert isinstance(result, str)


@vcr.use_cassette('tests/cassettes/delete_multiple_events_empty.yaml', record_mode='new_episodes')
def test_delete_multiple_events_empty(credentials):
    """Test deletion with empty event_ids."""
    with pytest.raises(ValueError) as exc_info:
        delete_multiple_events(
            event_ids=[],
            url=credentials["url"],
            username=credentials["username"],
            password=credentials["password"],
            option=DeleteEventOption(interactive_mode=False)
        )
    assert "event_ids must be a non-empty list of integers" in str(exc_info.value)


@vcr.use_cassette('tests/cassettes/delete_multiple_events_invalid_response.yaml', record_mode='new_episodes')
def test_delete_multiple_events_invalid_response(credentials):
    """Test deletion with invalid API response."""
    with patch.object(AMSClient, "_fetch", return_value=None):
        result = delete_multiple_events(
            event_ids=[134273, 134274],
            url=credentials["url"],
            username=credentials["username"],
            password=credentials["password"],
            option=DeleteEventOption(interactive_mode=False)
        )
        assert "SUCCESS" in result
        assert isinstance(result, str)


def test_delete_multiple_events_interactive_success(capsys, monkeypatch):
    """Test interactive mode success in delete_multiple_events."""
    prompts = []
    def mock_input(prompt):
        prompts.append(prompt)
        return "y"
    monkeypatch.setattr("builtins.input", mock_input)
    with patch.object(AMSClient, "_fetch", return_value=None):
        result = delete_multiple_events(
            event_ids=[134273, 134274],
            url="https://example.smartabase.com/site",
            username="user",
            password="pass",
            option=DeleteEventOption(interactive_mode=True)
        )
        assert "SUCCESS" in result
    print(f"Debug: Captured prompts: {prompts}")
    assert any("Are you sure" in p for p in prompts)  
    captured = capsys.readouterr()
    assert "Are you sure" in captured.out  


def test_build_delete_event_payload():
    """Test _build_delete_event_payload."""
    from teamworksams.delete_build import _build_delete_event_payload
    payload = _build_delete_event_payload(134273)
    assert payload == {"eventId": 134273}


def test_build_delete_multiple_events_payload():
    """Test _build_delete_multiple_events_payload."""
    from teamworksams.delete_build import _build_delete_multiple_events_payload
    payload = _build_delete_multiple_events_payload([134273, 134274])
    assert payload == {"eventIds": ["134273", "134274"]}
    

@vcr.use_cassette('tests/cassettes/delete_event_data_invalid_structure.yaml', record_mode='new_episodes')
def test_delete_event_data_invalid_structure(credentials):
    """Test deletion with invalid API response structure."""
    with patch.object(AMSClient, "_fetch", return_value={}):
        with pytest.raises(AMSError) as exc_info:
            delete_event_data(
                event_id=999999,
                url=credentials["url"],
                username=credentials["username"],
                password=credentials["password"],
                option=DeleteEventOption(interactive_mode=False)
            )
        assert "Invalid response" in str(exc_info.value)


@vcr.use_cassette('tests/cassettes/delete_multiple_events_api_failure.yaml', record_mode='new_episodes')
def test_delete_multiple_events_api_failure(credentials):
    """Test deletion with API failure."""
    with patch.object(AMSClient, "_fetch", side_effect=AMSError("API error")):
        with pytest.raises(AMSError) as exc_info:
            delete_multiple_events(
                event_ids=[134273, 134274],
                url=credentials["url"],
                username=credentials["username"],
                password=credentials["password"],
                option=DeleteEventOption(interactive_mode=False)
            )
        assert "API error" in str(exc_info.value)