import pytest
import pandas as pd
from pandas import DataFrame
from teamworksams.form_main import get_forms, get_form_schema
from teamworksams.form_option import FormOption
from teamworksams.utils import AMSError
import os
from dotenv import load_dotenv

load_dotenv()

# Test get_forms
@pytest.mark.vcr
def test_get_forms_success():
    """Test successful retrieval of forms metadata."""
    results = get_forms(
        url=os.getenv("AMS_URL"),
        username=os.getenv("AMS_USERNAME"),
        password=os.getenv("AMS_PASSWORD"),
        option=FormOption(interactive_mode=False)
    )
    assert isinstance(results, DataFrame)
    assert set(["form_id", "form_name", "type"]).issubset(results.columns)
    assert len(results) >= 0  # Allow for varying number of forms
    if not results.empty:
        assert all(results["form_id"].notna())
        assert all(results["form_name"].notna())
        assert all(results["type"].isin(["event", "profile", "database", "linkedOnlyEvent", "linkedOnlyProfile"]))

# Test get_form_schema
@pytest.mark.vcr
def test_get_form_schema_success():
    """Test successful retrieval of form schema with formatted output."""
    results = get_form_schema(
        form="Training Log",
        url=os.getenv("AMS_URL"),
        username=os.getenv("AMS_USERNAME"),
        password=os.getenv("AMS_PASSWORD"),
        option=FormOption(interactive_mode=False, field_details=True, include_instructions=True)
    )
    assert isinstance(results, str)
    assert "Form Schema Summary" in results
    assert "Training Log" in results
    assert "Sections" in results
    assert "Form Item Types" in results

@pytest.mark.vcr
def test_get_form_schema_raw_success():
    """Test successful retrieval of form schema with raw output."""
    results = get_form_schema(
        form="Training Log",
        url=os.getenv("AMS_URL"),
        username=os.getenv("AMS_USERNAME"),
        password=os.getenv("AMS_PASSWORD"),
        option=FormOption(interactive_mode=False, raw_output=True)
    )
    assert isinstance(results, dict)
    assert "name" in results
    assert "id" in results
    assert results["name"] == "Training Log"
    assert isinstance(results.get("children", []), list)

def test_get_form_schema_invalid_name():
    """Test form schema retrieval with an invalid form name."""
    with pytest.raises(AMSError, match="Form 'Invalid Form' not found"):
        get_form_schema(
            form="Invalid Form",
            url=os.getenv("AMS_URL"),
            username=os.getenv("AMS_USERNAME"),
            password=os.getenv("AMS_PASSWORD"),
            option=FormOption(interactive_mode=False)
        )