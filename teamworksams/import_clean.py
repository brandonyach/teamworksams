from typing import Tuple
from pandas import DataFrame, notna
import pandas as pd
from datetime import datetime, timedelta


def _clean_import_df(df: DataFrame) -> DataFrame:
    """Clean a DataFrame for import into an AMS Event Form by applying standard transformations.

    This function performs several cleaning steps on the input DataFrame to prepare it for
    import into AMS:
    - Removes protected columns like 'first name' and 'last name'.
    - Inserts default date and time columns if missing.
    - Replaces NaN values with empty strings (except for 'event_id').
    - Converts ID column names to lowercase.

    Args:
        df: Input DataFrame containing event data to clean.

    Returns:
        Cleaned DataFrame ready for import into AMS.
    """
    df = _remove_protected_columns(df)
    df = _insert_date_time(df)
    df = _replace_na_with_empty_string(df)
    df = _convert_id_names_to_lower(df)
    return df


def _clean_profile_df(df: DataFrame) -> DataFrame:
    """Clean a DataFrame for import into an AMS Profile Form by applying standard transformations.

    This function performs cleaning steps on the input DataFrame to prepare it for
    import into an AMS Profile Form:
    - Removes protected columns like 'first name' and 'last name'.
    - Replaces NaN values with empty strings.
    - Converts ID column names to lowercase.
    - Does not insert date/time columns, as profile forms do not support them.

    Args:
        df: Input DataFrame containing profile data to clean.

    Returns:
        Cleaned DataFrame ready for import into AMS.
    """
    df = _remove_protected_columns(df)
    df = _replace_na_with_empty_string(df)
    df = _convert_id_names_to_lower(df)
    return df



def _remove_protected_columns(df: DataFrame) -> DataFrame:
    """Remove protected columns like 'first name' and 'last name' from the DataFrame.

    Protected columns are those that AMS does not allow to be imported, such as
    'first name' and 'last name'. This function identifies and removes them, printing
    a warning if any are found.

    Args:
        df: Input DataFrame to process.

    Returns:
        DataFrame with protected columns removed.
    """
    protected = [col for col in df.columns if col.lower() in ["first name", "last name"]]
    if protected:
        print(f"Warning: Protected columns {protected} removed from DataFrame.")
        df = df.drop(columns=protected)
    return df



def _insert_date_time(df: DataFrame) -> DataFrame:
    """Insert default date and time columns if missing, setting end_date to start_date.

    Ensures that 'start_date', 'start_time', 'end_date', and 'end_time' columns are present
    in the DataFrame, adding default values if they are missing. The default end_date is set
    to match the start_date, and the default end_time is one hour after the start_time.

    Args:
        df: Input DataFrame to process.

    Returns:
        DataFrame with date and time columns added or updated.
    """
    now = datetime.now()
    default_start_date = now.strftime("%d/%m/%Y")
    default_start_time = now.strftime("%I:%M %p")
    default_end_time = (now.replace(hour=(now.hour + 1) % 24)).strftime("%I:%M %p")
    
    if "start_date" not in df.columns:
        df["start_date"] = default_start_date
    if "start_time" not in df.columns:
        df["start_time"] = default_start_time
    if "end_date" not in df.columns:
        df["end_date"] = df["start_date"] 
    if "end_time" not in df.columns:
        df["end_time"] = default_end_time
    return df



def _replace_na_with_empty_string(df: DataFrame) -> DataFrame:
    """Replace NaN values with empty strings, except for the 'event_id' column.

    AMS requires non-null values for most fields, so this function replaces NaN values
    with empty strings for all columns except 'event_id', which may need to remain NaN for
    new records in upsert operations.

    Args:
        df: Input DataFrame to process.

    Returns:
        DataFrame with NaN values replaced by empty strings, except for 'event_id'.
    """
    exclude = ["event_id"] if "event_id" in df.columns else []
    for col in df.columns:
        if col not in exclude:
            df[col] = df[col].fillna("")
        else:
            df[col] = df[col].where(notna(df[col]), None)
    return df



def _convert_id_names_to_lower(df: DataFrame) -> DataFrame:
    """Convert ID-related column names to lowercase for consistency.

    This function converts specific ID-related column names ('about', 'user_id', 'username',
    'email', 'event_id') to lowercase to ensure consistent handling in downstream processes.

    Args:
        df: Input DataFrame to process.

    Returns:
        DataFrame with specified ID column names converted to lowercase.
    """
    id_cols = ["about", "user_id", "username", "email", "event_id"]
    rename_map = {col: col.lower() for col in df.columns if col in id_cols}
    return df.rename(columns=rename_map)


def _set_default_dates_and_times(row: pd.Series) -> Tuple[str, str, str, str]:
    """Set default values for start_time, end_time, start_date, and end_date if not provided.

    Args:
        row: A pandas Series (DataFrame row) containing date and time fields.

    Returns:
        Tuple of (start_date, start_time, end_date, end_time) with default values applied.
    """
    start_time = row.get("start_time", datetime.now().strftime("%-I:%M %p"))
    if isinstance(start_time, str) and start_time == "":
        start_time = datetime.now().strftime("%-I:%M %p")
    start_time = start_time.replace("PM", "PM").replace("AM", "AM")

    start_date = row.get("start_date", datetime.now().strftime("%d/%m/%Y"))
    default_date = start_date if pd.notna(start_date) else datetime.now().strftime("%d/%m/%Y")
    end_date = row.get("end_date", default_date)
    if isinstance(end_date, str) and end_date == "":
        end_date = default_date

    end_time = row.get("end_time", (datetime.now() + timedelta(hours=1)).strftime("%-I:%M %p"))
    if isinstance(end_time, str) and end_time == "":
        end_time = (datetime.now() + timedelta(hours=1)).strftime("%-I:%M %p")
    end_time = end_time.replace("PM", "PM").replace("AM", "AM")

    return start_date, start_time, end_date, end_time
