import pytest
import pandas as pd
from teamworksams.file_print import _print_failed_attachments
from teamworksams.import_print import _print_import_status
from teamworksams.export_print import _print_event_status
from teamworksams.export_option import EventOption

def test_print_failed_attachments_non_empty(capsys):
    """Test _print_failed_attachments with non-empty DataFrame and interactive_mode=True."""
    failed_df = pd.DataFrame({
        "file": ["file1.pdf", "file2.pdf"],
        "error": ["Invalid format", "Upload failed"]
    })
    _print_failed_attachments(failed_df, interactive_mode=True)
    captured = capsys.readouterr()
    assert "Failed attachments:" in captured.out
    assert "file1.pdf" in captured.out
    assert "Invalid format" in captured.out

def test_print_failed_attachments_empty(capsys):
    """Test _print_failed_attachments with empty DataFrame and interactive_mode=True."""
    failed_df = pd.DataFrame(columns=["file", "error"])
    _print_failed_attachments(failed_df, interactive_mode=True)
    captured = capsys.readouterr()
    assert captured.out == ""  # No output for empty DataFrame

def test_print_failed_attachments_non_interactive(capsys):
    """Test _print_failed_attachments with interactive_mode=False."""
    failed_df = pd.DataFrame({"file": ["file1.pdf"], "error": ["Invalid format"]})
    _print_failed_attachments(failed_df, interactive_mode=False)
    captured = capsys.readouterr()
    assert captured.out == ""  # No output when non-interactive

def test_print_import_status_all_success(capsys):
    """Test _print_import_status with all successful results and interactive_mode=True."""
    results = [
        {"state": "SUCCESS", "ids": [67890], "message": ""},
        {"state": "SUCCESSFULLY_IMPORTED", "ids": [67891], "message": ""}
    ]
    _print_import_status(results, "Training Log", "inserted", interactive_mode=True)
    captured = capsys.readouterr()
    assert "ℹ Form: Training Log" in captured.out
    assert "ℹ Result: Success" in captured.out
    assert "ℹ Records inserted: 2" in captured.out
    assert "ℹ Records attempted: 2" in captured.out
    assert "failed" not in captured.out

def test_print_import_status_some_failed(capsys):
    """Test _print_import_status with some failed results and interactive_mode=True."""
    results = [
        {"state": "SUCCESS", "ids": [67890], "message": ""},
        {"state": "ERROR", "ids": [], "message": "Invalid event_id"}
    ]
    _print_import_status(results, "Training Log", "inserted", interactive_mode=True)
    captured = capsys.readouterr()
    assert "ℹ Form: Training Log" in captured.out
    assert "ℹ Result: Success" in captured.out
    assert "ℹ Records inserted: 1" in captured.out
    assert "ℹ Records attempted: 2" in captured.out
    assert "⚠️ 1 events failed:" in captured.out
    assert "Error: Invalid event_id" in captured.out

def test_print_import_status_all_failed(capsys):
    """Test _print_import_status with all failed results and interactive_mode=True."""
    results = [
        {"state": "ERROR", "ids": [], "message": "Invalid event_id"},
        {"state": "ERROR", "ids": [], "message": "Missing data"}
    ]
    _print_import_status(results, "Training Log", "inserted", interactive_mode=True)
    captured = capsys.readouterr()
    assert "ℹ Form: Training Log" in captured.out
    assert "ℹ Result: Failed" in captured.out
    assert "ℹ Records inserted: 0" in captured.out
    assert "ℹ Records attempted: 2" in captured.out
    assert "⚠️ 2 events failed:" in captured.out
    assert "Error: Invalid event_id" in captured.out
    assert "Error: Missing data" in captured.out

def test_print_import_status_non_interactive(capsys):
    """Test _print_import_status with interactive_mode=False."""
    results = [{"state": "SUCCESS", "ids": [67890], "message": ""}]
    _print_import_status(results, "Training Log", "inserted", interactive_mode=False)
    captured = capsys.readouterr()
    assert captured.out == ""  # No output when non-interactive

def test_print_import_status_edge_case(capsys):
    """Test _print_import_status with missing state/message and interactive_mode=True."""
    results = [
        {"ids": [67890]},  # Missing state
        {"state": "ERROR", "ids": [], "message": ""}  # Empty message
    ]
    _print_import_status(results, "Training Log", "inserted", interactive_mode=True)
    captured = capsys.readouterr()
    assert "ℹ Form: Training Log" in captured.out
    assert "ℹ Result: Failed" in captured.out
    assert "ℹ Records inserted: 0" in captured.out
    assert "ℹ Records attempted: 2" in captured.out
    assert "⚠️ 2 events failed:" in captured.out
    assert "Error: Unknown error" in captured.out

def test_print_event_status_non_empty(capsys):
    """Test _print_event_status with non-empty DataFrame and interactive_mode=True."""
    df = pd.DataFrame({
        "event_id": [1, 2],
        "user_id": [123, 124],
        "form": ["Training Log", "Training Log"],
        "start_date": ["01/01/2024", "02/01/2024"]
    })
    option = EventOption(interactive_mode=True)
    _print_event_status(df, "Training Log", option)
    captured = capsys.readouterr()
    assert "✔ Retrieved 2 events for form 'Training Log'" in captured.out

def test_print_event_status_empty(capsys):
    """Test _print_event_status with empty DataFrame and interactive_mode=True."""
    df = pd.DataFrame(columns=["event_id", "user_id", "form", "start_date"])
    option = EventOption(interactive_mode=True)
    _print_event_status(df, "Training Log", option)
    captured = capsys.readouterr()
    assert "✔ Retrieved 0 events for form 'Training Log'" in captured.out

def test_print_event_status_non_interactive(capsys):
    """Test _print_event_status with interactive_mode=False."""
    df = pd.DataFrame({"event_id": [1], "user_id": [123], "form": ["Training Log"], "start_date": ["01/01/2024"]})
    option = EventOption(interactive_mode=False)
    _print_event_status(df, "Training Log", option)
    captured = capsys.readouterr()
    assert captured.out == ""  # No output when non-interactive