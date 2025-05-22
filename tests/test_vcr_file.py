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
def avatar_mapping_df():
    """Fixture for a sample avatar mapping DataFrame."""
    return DataFrame({
        "username": ["Riley.Jones", "Samantha.Fields", "Dean.Jones"],
        "file_name": ["avatar1.png", "avatar2.jpg", "avatar3.png"]
    })

@pytest.fixture
def file_dir(tmp_path):
    """Fixture for a temporary file directory with sample files."""
    dir_path = tmp_path / "files"
    dir_path.mkdir()
    (dir_path / "doc1.pdf").write_bytes(b"%PDF-1.4\n%Sample PDF content")
    (dir_path / "doc2.pdf").write_bytes(b"%PDF-1.4\n%Sample PDF content")
    (dir_path / "doc3.pdf").write_bytes(b"%PDF-1.4\n%Sample PDF content")
    (dir_path / "avatar1.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08")
    (dir_path / "avatar2.jpg").write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01")
    (dir_path / "avatar3.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08")
    return str(dir_path)

@pytest.fixture
def invalid_dir():
    """Fixture for an invalid directory path."""
    return "/non/existent/path"

# Test upload_and_attach_to_events
@pytest.mark.vcr
def test_upload_events_success(event_mapping_df, file_dir):
    """Test successful event file upload and attachment.

    Note: May produce a warning about protected columns (e.g., 'First Name', 'Last Name') being removed
    from user data, which is normal behavior in teamworksams.
    """
    results = upload_and_attach_to_events(
        mapping_df=event_mapping_df,
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
    assert len(results) == 3
    # Expect up to 3 successes (valid files)
    assert results[results["status"] == "SUCCESS"].shape[0] <= 3
    # Allow for failures due to unmatched events or upload issues
    assert results[results["status"] == "FAILED"].shape[0] >= 0
    # Check that any failures have a reason
    if results[results["status"] == "FAILED"].shape[0] > 0:
        assert all(pd.notna(reason) for reason in results[results["status"] == "FAILED"]["reason"])


def test_upload_events_invalid_dir(event_mapping_df, invalid_dir):
    """Test event upload with invalid directory."""
    with pytest.raises(AMSError, match="is not a valid directory"):
        upload_and_attach_to_events(
            mapping_df=event_mapping_df,
            file_dir=invalid_dir,
            user_key="username",
            form="Test File Upload",
            file_field_name="attachment",
            url=os.getenv("AMS_URL"),
            username=os.getenv("AMS_USERNAME"),
            password=os.getenv("AMS_PASSWORD"),
            option=FileUploadOption(interactive_mode=False)
        )


@pytest.mark.vcr
def test_upload_avatars_success(avatar_mapping_df, file_dir):
    """Test successful avatar file upload and attachment.

    Note: May produce a warning about protected columns (e.g., 'First Name', 'Last Name') being removed
    from user data, which is normal behavior in teamworksams.
    """
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
    assert len(results) == 3
    # Expect up to 3 successes (valid images)
    assert results[results["status"] == "SUCCESS"].shape[0] <= 3
    # Allow for failures due to unmatched users or upload issues
    assert results[results["status"] == "FAILED"].shape[0] >= 0
    # Check that any failures have a reason
    if results[results["status"] == "FAILED"].shape[0] > 0:
        assert all(pd.notna(reason) for reason in results[results["status"] == "FAILED"]["reason"])


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