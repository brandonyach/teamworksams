from typing import Optional, List
from pandas import DataFrame, notna, isna
from .utils import AMSError
from datetime import datetime


def _validate_ids(
        df: DataFrame, 
        overwrite_existing: bool
    ) -> None:
    
    """Validate the presence and format of user_id and event_id columns in the DataFrame.

    Ensures that the 'user_id' column is present and contains valid values. For update or upsert
    operations (when overwrite_existing is True), also validates the 'event_id' column, allowing
    NaN values for new records in upsert scenarios.

    Args:
        df: DataFrame to validate.
        overwrite_existing: Boolean indicating if this is an update or upsert operation.

    Raises:
        AMSError: If 'user_id' is missing or contains invalid values, or if 'event_id' contains
            invalid values when overwrite_existing is True.
    """
    
    if "user_id" not in df.columns:
        AMSError("user_id column is required", function="import_event_data")
    if not df["user_id"].apply(lambda x: isinstance(x, (int, float, str)) and notna(x)).all():
        AMSError("user_id column must contain valid values", function="import_event_data")
    
    # For updates/upserts, event_id must be present but can be NaN for new records (upserts)
    if overwrite_existing and "event_id" in df.columns:
        if not df["event_id"].apply(lambda x: notna(x) and isinstance(x, (int, float, str)) or isna(x)).all():
            AMSError("event_id must contain valid values or NaN when overwrite_existing=True", function="import_event_data")



def _validate_dates(df: DataFrame) -> None:
    
    """Validate the format of date columns in the DataFrame, allowing empty strings.

    Ensures that 'start_date' and 'end_date' columns, if present, contain valid date strings
    in the format 'DD/MM/YYYY'. Empty strings and NaN values are allowed.

    Args:
        df: DataFrame to validate.

    Raises:
        AMSError: If date columns contain invalid formats or non-string values (excluding empty strings and NaN).
    """
    
    for col in ["start_date", "end_date"]:
        if col not in df.columns:
            continue
        if not df[col].apply(lambda x: (notna(x) and isinstance(x, str)) or isna(x)).all():
            AMSError(f"{col} column must contain valid strings", function="import_event_data")
        non_empty_dates = df[col].dropna()
        
        non_empty_dates = non_empty_dates[non_empty_dates != ""]
        
        if not non_empty_dates.empty:
            try:
                non_empty_dates.apply(lambda x: bool(datetime.strptime(x, "%d/%m/%Y")))
            except ValueError:
                AMSError(f"{col} column must be in format DD/MM/YYYY", function="import_event_data")



def _validate_times(df: DataFrame) -> None:
    
    """Validate the format of time columns in the DataFrame, allowing empty strings.

    Ensures that 'start_time' and 'end_time' columns, if present, contain valid string values.
    Empty strings and NaN values are allowed. Note that time format validation is lenient,
    as Smartabase accepts various time formats.

    Args:
        df: DataFrame to validate.

    Raises:
        AMSError: If time columns contain non-string values (excluding empty strings and NaN).
    """
    
    for col in ["start_time", "end_time"]:
        if col not in df.columns:
            continue
        if not df[col].apply(lambda x: (notna(x) and isinstance(x, str)) or isna(x)).all():
            AMSError(f"{col} column must contain valid strings", function="import_event_data")



def _validate_import_df(
        df: DataFrame, 
        form: str, 
        overwrite_existing: bool, 
        table_fields: Optional[List[str]]
    ) -> None:
    
    """Validate an import DataFrame for import into an AMS event form.

    Performs comprehensive validation on the input DataFrame, including checks for:
    - DataFrame type and non-emptiness.
    - Form name validity.
    - User ID and event ID columns.
    - Date and time columns.

    Args:
        df: DataFrame containing the event data to validate.
        form: The name of the AMS form.
        overwrite_existing: Boolean indicating if this is an update or upsert operation.
        table_fields: List of field names that are table fields, or None for non-table forms.

    Raises:
        AMSError: If any validation check fails.
    """
    
    if not isinstance(df, DataFrame):
        AMSError("DataFrame must be a pandas DataFrame", function="import_event_data")
    if df.empty:
        AMSError("DataFrame must not be empty", function="import_event_data")
    if not form or not isinstance(form, str):
        AMSError("Form must be a non-empty string", function="import_event_data")
    
    _validate_ids(df, overwrite_existing)
    
    _validate_dates(df)
    
    _validate_times(df)