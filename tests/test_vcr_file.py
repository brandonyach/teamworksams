import pytest
import pandas as pd
from pandas import DataFrame
from teamworksams.file_main import upload_and_attach_to_events, upload_and_attach_to_avatars
from teamworksams.file_option import FileUploadOption
from teamworksams.file_process import (
    _format_file_reference, _map_user_ids_to_file_df, _build_result_df,
    _download_attachment, _validate_and_prepare_files, _upload_single_file,
    _create_avatar_mapping_df
)
from teamworksams.utils import AMSClient, AMSError
from pathlib import Path
import os
from dotenv import load_dotenv
from unittest.mock import patch, MagicMock

load_dotenv()

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
    """Fixture for a sample avatar mapping DataFrame."""
    return DataFrame({
        "username": ["Riley.Jones", "Samantha.Fields", "Dean.Jones"],
        "file_name": ["Riley Jones.png", "Samantha Fields.png", "Dean Jones.svg"]
    })

@pytest.fixture
def file_dir(tmp_path):
    """Fixture for a temporary file directory with sample files."""
    dir_path = tmp_path / "files"
    dir_path.mkdir()
    (dir_path / "doc1.pdf").write_bytes(b"%PDF-1.4\n%Sample PDF content")
    (dir_path / "doc2.pdf").write_bytes(b"%PDF-1.4\n%Sample PDF content")
    (dir_path / "doc3.pdf").write_bytes(b"%PDF-1.4\n%Sample PDF content")
    (dir_path / "doc2.svg").write_bytes(b"<svg></svg>")
    (dir_path / "Riley Jones.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08")
    (dir_path / "Samantha Fields.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08")
    (dir_path / "Dean Jones.svg").write_bytes(b"<svg></svg>")
    return dir_path

@pytest.fixture
def invalid_dir():
    """Fixture for an invalid directory path."""
    return "/non/existent/path"

# Tests for file_main.py
@pytest.mark.vcr(record_mode='none')
def test_upload_events_success(event_mapping_df, file_dir):
    """Test event file upload with mixed outcomes."""
    with patch("teamworksams.file_process._fetch_user_ids", return_value=(
        ["78901", "78902", "78903"],
        DataFrame({
            "userId": ["78901", "78902", "78903"],
            "username": ["Riley.Jones", "Samantha.Fields", "Dean.Jones"]
        })
    )):
        with patch("teamworksams.file_main.get_event_data", side_effect=AMSError("No events found")):
            results = upload_and_attach_to_events(
                mapping_df=event_mapping_df,
                mapping_col='attachment_id',
                file_dir=str(file_dir),
                user_key="username",
                form="Test File Upload",
                file_field_name="attachment",
                url=os.getenv("AMS_URL"),
                username=os.getenv("AMS_USERNAME"),
                password=os.getenv("AMS_PASSWORD"),
                option=FileUploadOption(interactive_mode=False)
            )
            assert isinstance(results, DataFrame)
            assert set(results.columns) == {"username", "file_name", "event_id", "file_id", "server_file_name", "status", "reason"}
            assert len(results["file_name"].unique()) == 3
            assert results["status"].eq("FAILED").all()
            assert all("Failed to retrieve events: No events found. Please check inputs or contact your site administrator." in str(reason) for reason in results["reason"])

@pytest.mark.vcr(record_mode='none')
def test_upload_events_invalid_form(event_mapping_df, file_dir):
    """Test event upload with invalid form name."""
    with patch("teamworksams.file_process._fetch_user_ids", return_value=(
        ["78901", "78902", "78903"],
        DataFrame({
            "userId": ["78901", "78902", "78903"],
            "username": ["Riley.Jones", "Samantha.Fields", "Dean.Jones"]
        })
    )):
        with patch("teamworksams.file_main.get_event_data", side_effect=AMSError("Invalid form")):
            results = upload_and_attach_to_events(
                mapping_df=event_mapping_df,
                mapping_col='attachment_id',
                file_dir=str(file_dir),
                user_key="username",
                form="Invalid Form",
                file_field_name="attachment",
                url=os.getenv("AMS_URL"),
                username=os.getenv("AMS_USERNAME"),
                password=os.getenv("AMS_PASSWORD"),
                option=FileUploadOption(interactive_mode=False)
            )
            assert isinstance(results, DataFrame)
            assert set(results.columns) == {"username", "file_name", "event_id", "file_id", "server_file_name", "status", "reason"}
            assert all("Failed to retrieve events: Invalid form. Please check inputs or contact your site administrator." in str(reason) for reason in results["reason"])

@pytest.mark.vcr(record_mode='none')
def test_upload_events_invalid_field(event_mapping_df, file_dir):
    """Test event upload with invalid file_field_name."""
    with patch("teamworksams.file_process._fetch_user_ids", return_value=(
        ["78901", "78902", "78903"],
        DataFrame({
            "userId": ["78901", "78902", "78903"],
            "username": ["Riley.Jones", "Samantha.Fields", "Dean.Jones"]
        })
    )):
        with patch("teamworksams.file_main.get_event_data", return_value=DataFrame({"event_id": ["123"], "other_col": ["value"]})):
            results = upload_and_attach_to_events(
                mapping_df=event_mapping_df,
                mapping_col='attachment_id',
                file_dir=str(file_dir),
                user_key="username",
                form="Test File Upload",
                file_field_name="invalid_field",
                url=os.getenv("AMS_URL"),
                username=os.getenv("AMS_USERNAME"),
                password=os.getenv("AMS_PASSWORD"),
                option=FileUploadOption(interactive_mode=False)
            )
            assert isinstance(results, DataFrame)
            assert set(results.columns) == {"username", "file_name", "event_id", "file_id", "server_file_name", "status", "reason"}
            assert all("Event form 'Test File Upload' does not have a 'attachment_id' field" in str(reason) for reason in results["reason"])

def test_upload_events_empty_mapping_df(file_dir):
    """Test event upload with empty mapping_df."""
    empty_df = DataFrame(columns=["username", "file_name", "attachment_id"])
    results = upload_and_attach_to_events(
        mapping_df=empty_df,
        mapping_col='attachment_id',
        file_dir=str(file_dir),
        user_key="username",
        form="Test File Upload",
        file_field_name="attachment",
        url=os.getenv("AMS_URL"),
        username=os.getenv("AMS_USERNAME"),
        password=os.getenv("AMS_PASSWORD"),
        option=FileUploadOption(interactive_mode=False)
    )
    assert isinstance(results, DataFrame)
    assert results.empty
    assert set(results.columns) == {"username", "file_name", "event_id", "user_id", "file_id", "server_file_name", "status", "reason"}

@pytest.mark.vcr(record_mode='none')
def test_upload_avatars_success(avatar_mapping_df, file_dir):
    """Test avatar file upload with mixed outcomes."""
    with patch("teamworksams.file_process._fetch_user_ids", return_value=(
        ["78901", "78902", "78903"],
        DataFrame({
            "userId": ["78901", "78902", "78903"],
            "username": ["Riley.Jones", "Samantha.Fields", "Dean.Jones"]
        })
    )):
        with patch("teamworksams.file_process._validate_and_prepare_files", return_value=(
            None,
            DataFrame({
                "username": ["Riley.Jones", "Samantha.Fields", "Dean.Jones"],
                "file_name": ["Riley Jones.png", "Samantha Fields.png", "Dean Jones.svg"],
                "user_id": ["78901", "78902", None],
                "file_id": [None, None, None],
                "server_file_name": [None, None, None],
                "status": ["SUCCESS", "SUCCESS", "FAILED"],
                "reason": [None, None, "Invalid file type '.svg'. Allowed: .png, .jpeg, .jpg"]
            })
        )):
            results = upload_and_attach_to_avatars(
                mapping_df=avatar_mapping_df,
                file_dir=str(file_dir),
                user_key="username",
                url=os.getenv("AMS_URL"),
                username=os.getenv("AMS_USERNAME"),
                password=os.getenv("AMS_PASSWORD"),
                option=FileUploadOption(interactive_mode=False)
            )
            assert isinstance(results, DataFrame)
            assert set(results.columns) == {"username", "file_name", "user_id", "file_id", "server_file_name", "status", "reason"}
            assert len(results) == 3
            assert any(results["file_name"] == "Dean Jones.svg")
            assert any("Invalid file type '.svg'." in str(reason) for reason in results[results["file_name"] == "Dean Jones.svg"]["reason"])

# Tests for file_process.py
def test_format_file_reference():
    """Test _format_file_reference formats file_id|server_file_name."""
    df = DataFrame({
        "file_id": ["123", "456"],
        "server_file_name": ["doc1.pdf", "doc2.pdf"]
    })
    result = _format_file_reference(df, "attachment")
    assert result["attachment"].equals(pd.Series(["123|doc1.pdf", "456|doc2.pdf"]))

@pytest.mark.vcr
def test_map_user_ids_to_file_df_success(file_dir):
    """Test _map_user_ids_to_file_df with successful user mapping."""
    client = MagicMock(spec=AMSClient)
    client.session = MagicMock()
    with patch("teamworksams.file_process._fetch_user_ids", return_value=(
        ["78901", "78902"],
        DataFrame({"userId": ["78901", "78902"], "username": ["Riley.Jones", "Samantha.Fields"]})
    )):
        df = DataFrame({
            "username": ["Riley.Jones", "Samantha.Fields"],
            "file_name": ["doc1.pdf", "doc2.pdf"]
        })
        result_df, failed_df = _map_user_ids_to_file_df(df, "username", client, False, True)
        assert result_df["user_id"].equals(pd.Series(["78901", "78902"]))
        assert failed_df.empty

def test_map_user_ids_to_file_df_no_users(file_dir):
    """Test _map_user_ids_to_file_df with no users found."""
    client = MagicMock(spec=AMSClient)
    client.session = MagicMock()
    with patch("teamworksams.file_process._fetch_user_ids", return_value=([], None)):
        df = DataFrame({
            "username": ["Riley.Jones"],
            "file_name": ["doc1.pdf"]
        })
        result_df, failed_df = _map_user_ids_to_file_df(df, "username", client, False, True)
        assert result_df.equals(df)
        assert not failed_df.empty
        assert "No users found" in failed_df["reason"].iloc[0]

def test_build_result_df_scalar():
    """Test _build_result_df with scalar inputs."""
    data = {
        "username": "Riley.Jones",
        "file_name": "doc1.pdf",
        "event_id": "123456",
        "file_id": "94196",
        "server_file_name": "doc1_1747654002120.pdf",
        "status": "SUCCESS",
        "reason": None
    }
    result = _build_result_df(data, "username", is_event=True)
    assert result.shape == (1, 7)
    assert result.iloc[0]["username"] == "Riley.Jones"
    assert result.iloc[0]["status"] == "SUCCESS"

def test_build_result_df_list():
    """Test _build_result_df with list inputs."""
    data = {
        "username": ["Riley.Jones", "Samantha.Fields"],
        "file_name": ["doc1.pdf", "doc2.pdf"],
        "event_id": ["123456", "123457"],
        "file_id": ["94196", "94197"],
        "server_file_name": ["doc1.pdf", "doc2.pdf"],
        "status": ["SUCCESS", "FAILED"],
        "reason": [None, "Upload failed"]
    }
    result = _build_result_df(data, "username", is_event=True)
    assert result.shape == (2, 7)
    assert result.iloc[1]["status"] == "FAILED"
    assert result.iloc[1]["reason"] == "Upload failed"

def test_download_attachment_success(tmp_path):
    """Test _download_attachment with successful download."""
    client = MagicMock(spec=AMSClient)
    client.session = MagicMock()
    client.session.get.return_value = MagicMock(status_code=200, content=b"file content")
    output_dir = str(tmp_path)
    result = _download_attachment(client, "https://example.com/file.pdf", "file.pdf", output_dir)
    assert os.path.exists(result)
    with open(result, "rb") as f:
        assert f.read() == b"file content"

def test_download_attachment_failure():
    """Test _download_attachment with failed download."""
    client = MagicMock(spec=AMSClient)
    client.session = MagicMock()
    client.session.get.return_value = MagicMock(status_code=404)
    with pytest.raises(AMSError, match="Failed to download attachment"):
        _download_attachment(client, "https://example.com/file.pdf", "file.pdf")

def test_validate_and_prepare_files_all_invalid(file_dir):
    """Test _validate_and_prepare_files with all invalid files."""
    mapping_df = DataFrame({
        "username": ["Riley.Jones"],
        "file_name": ["missing.pdf"],
        "user_id": ["123456"]
    })
    option = FileUploadOption(interactive_mode=False)
    files_to_upload, results_df = _validate_and_prepare_files(mapping_df, "username", file_dir, set(), [], option, is_event=False)
    assert files_to_upload is None
    assert not results_df.empty
    assert "not found in" in results_df["reason"].iloc[0]

@pytest.mark.vcr
def test_upload_single_file_failure(file_dir):
    """Test _upload_single_file with API failure."""
    client = MagicMock(spec=AMSClient)
    client.authenticated = True
    client.login_data = {"user": {"skypeName": "test_skype"}}
    client.url = "https://example.smartabase.com/site"
    client.headers = {}
    client.session = MagicMock()
    client.session.post.return_value = MagicMock(status_code=500)
    file_path = file_dir / "doc1.pdf"
    with pytest.raises(AMSError, match="Failed to upload file"):
        _upload_single_file(file_path, "doc1.pdf", client, "document-key")

def test_create_avatar_mapping_df_success(tmp_path):
    """Test _create_avatar_mapping_df with valid images."""
    dir_path = tmp_path / "avatars"
    dir_path.mkdir()
    (dir_path / "user1.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (dir_path / "user2.jpg").write_bytes(rb"\xff\xd8\xff\xe0")
    result = _create_avatar_mapping_df(str(dir_path), "username")
    assert result.shape == (2, 2)
    assert set(result["file_name"]) == {"user1.png", "user2.jpg"}
    assert set(result["username"]) == {"user1", "user2"}

def test_create_avatar_mapping_df_no_images(tmp_path):
    """Test _create_avatar_mapping_df with no valid images."""
    dir_path = tmp_path / "avatars"
    dir_path.mkdir()
    (dir_path / "doc1.pdf").write_bytes(b"%PDF-1.4\n")
    with pytest.raises(AMSError, match="No valid image files found"):
        _create_avatar_mapping_df(str(dir_path), "username")
    
    
