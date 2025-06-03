import pytest
import pandas as pd
from pandas import DataFrame
from teamworksams.file_main import upload_and_attach_to_events, upload_and_attach_to_avatars
from teamworksams.file_option import FileUploadOption
from teamworksams.utils import AMSError
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Sample mapping DataFrames for testing
@pytest.fixture
def event_mapping_df():
    """Fixture for a sample event mapping DataFrame."""
    return DataFrame({
        "username": ["Riley.Jones", "Samantha.Fields", "Dean.Jones"],
        "file_name": ["doc1.pdf", "doc2.pdf", "doc3.pdf"],
        "attachment_id": ["att_001", "att_002", "att_003"]
    })

@pytest.fixture
def event_mapping_df_invalid():
    """Fixture for an event mapping DataFrame with an invalid file."""
    return DataFrame({
        "username": ["Riley.Jones", "Samantha.Fields", "Dean.Jones"],
        "file_name": ["doc1.pdf", "doc2.svg", "doc3.pdf"],
        "attachment_id": ["att_001", "att_002", "att_003"]
    })

@pytest.fixture
def avatar_mapping_df():
    """Fixture for a sample avatar mapping DataFrame matching user test conditions."""
    return DataFrame({
        "username": ["Riley.Jones", "Samantha.Fields", "Mary.Phillips", "Aiden.Thomas", "Dean.Jones", "Hunter.Carlson", "Annie.Wilkins"],
        "file_name": ["Riley Jones.png", "Samantha Fields.png", "Mary Phillips.png", "Aidan Thomass.png", "Dean Jones.svg", "Hunter Carlson.jpg", "Annie Wilkins.svg"]
    })

@pytest.fixture
def file_dir(tmp_path):
    """Fixture for a temporary file directory with sample files matching test conditions."""
    dir_path = tmp_path / "files"
    dir_path.mkdir()
    # Event files
    (dir_path / "doc1.pdf").write_bytes(b"%PDF-1.4\n%Sample PDF content")
    (dir_path / "doc2.pdf").write_bytes(b"%PDF-1.4\n%Sample PDF content")
    (dir_path / "doc3.pdf").write_bytes(b"%PDF-1.4\n%Sample PDF content")
    # Invalid event file
    (dir_path / "doc2.svg").write_bytes(b"<svg></svg>")
    # Avatar files
    (dir_path / "Riley Jones.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08")
    (dir_path / "Samantha Fields.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08")
    (dir_path / "Mary Phillips.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08")
    (dir_path / "Hunter Carlson.jpg").write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01")
    (dir_path / "Dean Jones.svg").write_bytes(b"<svg></svg>")
    (dir_path / "Annie Wilkins.svg").write_bytes(b"<svg></svg>")
    return str(dir_path)

@pytest.fixture
def invalid_dir():
    """Fixture for an invalid directory path."""
    return "/non/existent/path"

# Test upload_and_attach_to_events
@pytest.mark.vcr
def test_upload_events_success(event_mapping_df, file_dir):
    """Test event file upload with mixed outcomes, allowing for no successes due to missing site data."""
    try:
        results = upload_and_attach_to_events(
            mapping_df=event_mapping_df,
            mapping_col='attachment_id',
            file_dir=file_dir,
            user_key="username",
            form="Test File Upload",
            file_field_name="attachment",
            url=os.getenv("AMS_URL"),
            username=os.getenv("AMS_USERNAME"),
            password=os.getenv("AMS_PASSWORD"),
            option=FileUploadOption(interactive_mode=False, save_to_file=None)
        )
        assert isinstance(results, DataFrame)
        assert set(results.columns) == {"username", "file_name", "event_id", "file_id", "server_file_name", "status", "reason"}
        assert len(results["file_name"].unique()) == 3
        assert results[results["status"] == "FAILED"].shape[0] >= 1
        failed = results[results["file_name"] == "doc3.pdf"]
        assert any("User not found" in str(reason) or "No matching event" in str(reason) for reason in failed["reason"])
        if results[results["status"] == "FAILED"].shape[0] > 0:
            assert all(pd.notnull(reason) for reason in results[results["status"] == "FAILED"]["reason"])
    except AMSError as e:
        assert "No events found" in str(e) or "User not found" in str(e)

@pytest.mark.vcr
def test_upload_events_invalid_file(event_mapping_df_invalid, file_dir):
    """Test event file upload with an invalid file type."""
    results = upload_and_attach_to_events(
        mapping_df=event_mapping_df_invalid,
        mapping_col='attachment_id',
        file_dir=file_dir,
        user_key="username",
        form="Test File Upload",
        file_field_name="attachment",
        url=os.getenv("AMS_URL"),
        username=os.getenv("AMS_USERNAME"),
        password=os.getenv("AMS_PASSWORD"),
        option=FileUploadOption(interactive_mode=False, save_to_file=None)
    )
    assert isinstance(results, DataFrame)
    assert set(results.columns) == {"username", "file_name", "event_id", "file_id", "server_file_name", "status", "reason"}
    assert len(results["file_name"].unique()) == 3
    assert any(results["file_name"] == "doc2.svg")
    assert any("Invalid file type" in str(reason) for reason in results[results["file_name"] == "doc2.svg"]["reason"])

def test_upload_events_invalid_dir(event_mapping_df, invalid_dir):
    """Test event upload with invalid directory."""
    with pytest.raises(AMSError, match="is not a valid directory"):
        upload_and_attach_to_events(
            mapping_df=event_mapping_df,
            mapping_col='attachment_id',
            file_dir=invalid_dir,
            user_key="username",
            form="Test File Upload",
            file_field_name="attachment",
            url=os.getenv("AMS_URL"),
            username=os.getenv("AMS_USERNAME"),
            password=os.getenv("AMS_PASSWORD"),
            option=FileUploadOption(interactive_mode=False)
        )

# Test upload_and_attach_to_avatars
@pytest.mark.vcr
def test_upload_avatars_success(avatar_mapping_df, file_dir):
    """Test avatar file upload with mixed valid, invalid, and missing files."""
    results = upload_and_attach_to_avatars(
        mapping_df=avatar_mapping_df,
        file_dir=file_dir,
        user_key="username",
        url=os.getenv("AMS_URL"),
        username=os.getenv("AMS_USERNAME"),
        password=os.getenv("AMS_PASSWORD"),
        option=FileUploadOption(interactive_mode=False, save_to_file=None)
    )
    assert isinstance(results, DataFrame)
    assert set(results.columns) == {"username", "file_name", "user_id", "file_id", "server_file_name", "status", "reason"}
    assert len(results) == 7
    assert any(results["file_name"] == "Dean Jones.svg")
    assert any("Invalid file type" in str(reason) or "User not found" in str(reason) for reason in results[results["file_name"] == "Dean Jones.svg"]["reason"])
    assert any(results["file_name"] == "Annie Wilkins.svg")
    assert any("Invalid file type" in str(reason) or "User not found" in str(reason) for reason in results[results["file_name"] == "Annie Wilkins.svg"]["reason"])
    assert any(results["file_name"] == "Aidan Thomass.png")
    assert any("not found" in str(reason) for reason in results[results["file_name"] == "Aidan Thomass.png"]["reason"])
    if results[results["status"] == "FAILED"].shape[0] > 0:
        assert all(pd.notnull(reason) for reason in results[results["status"] == "FAILED"]["reason"])

def test_upload_avatars_invalid_dir(avatar_mapping_df, invalid_dir):
    """Test avatar upload with invalid directory."""
    with pytest.raises(AMSError, match="is not a valid directory"):
        upload_and_attach_to_avatars(
            mapping_df=avatar_mapping_df,
            file_dir=invalid_dir,
            user_key="username",
            url=os.getenv("AMS_URL"),
            username=os.getenv("AMS_USERNAME"),
            password=os.getenv("AMS_PASSWORD"),
            option=FileUploadOption(interactive_mode=False)
        )

@pytest.mark.vcr
def test_upload_avatars_no_mapping_df(file_dir):
    """Test avatar upload without mapping_df, generating it from file_dir."""
    results = upload_and_attach_to_avatars(
        mapping_df=None,
        file_dir=file_dir,
        user_key="username",
        url=os.getenv("AMS_URL"),
        username=os.getenv("AMS_USERNAME"),
        password=os.getenv("AMS_PASSWORD"),
        option=FileUploadOption(interactive_mode=False, save_to_file=None)
    )
    assert isinstance(results, DataFrame)
    assert set(results.columns) == {"username", "file_name", "user_id", "file_id", "server_file_name", "status", "reason"}
    assert any(results["file_name"] == "Dean Jones.svg")
    assert any("Invalid file type" in str(reason) or "User not found" in str(reason) for reason in results[results["file_name"] == "Dean Jones.svg"]["reason"])
    assert any(results["file_name"] == "Annie Wilkins.svg")
    assert any("Invalid file type" in str(reason) or "User not found" in str(reason) for reason in results[results["file_name"] == "Annie Wilkins.svg"]["reason"])
    if results[results["status"] == "FAILED"].shape[0] > 0:
        assert all(pd.notnull(reason) for reason in results[results["status"] == "FAILED"]["reason"])

@pytest.mark.vcr
def test_upload_avatars_duplicate_files(avatar_mapping_df, file_dir):
    """Test avatar upload with duplicate file names."""
    mapping_df = pd.concat([avatar_mapping_df, avatar_mapping_df.iloc[[0]]], ignore_index=True)
    with pytest.raises(AMSError, match="Duplicate file names found in file_df"):
        upload_and_attach_to_avatars(
            mapping_df=mapping_df,
            file_dir=file_dir,
            user_key="username",
            url=os.getenv("AMS_URL"),
            username=os.getenv("AMS_USERNAME"),
            password=os.getenv("AMS_PASSWORD"),
            option=FileUploadOption(interactive_mode=False)
        )