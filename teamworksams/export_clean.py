import pandas as pd
from pandas import DataFrame
from typing import Optional, List
from .utils import AMSError


def _clean_column_names(df: DataFrame) -> DataFrame:
    """Clean column names by converting to lowercase and replacing special characters.

    Standardizes column names by removing or replacing special characters and ensuring uniqueness.

    Args:
        df (DataFrame): The DataFrame to clean column names for.

    Returns:
        DataFrame: The DataFrame with cleaned column names.
    """
    cleaned_names = []
    seen = {}
    for col in df.columns:
        name = (col.lower()
                .replace(" ", "_")
                .replace("(", "")
                .replace(")", "")
                .replace("%", "_percent")
                .replace(".", "_")
                .replace("#", "_num")
                .replace(",", "_")
                .replace("?", "_query")
                .replace("/", "_slash")
                .replace("[", "_")
                .replace("]", "_")
                .replace("-", "_")
                .replace("*", "_star")
                .replace("@", "_at")
                .strip("_"))
        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        else:
            seen[name] = 0
        cleaned_names.append(name)
    df.columns = cleaned_names
    return df



def _reorder_columns(
        front_cols: List[str], 
        df: DataFrame, 
        back_cols: List[str]
    ) -> DataFrame:
    """Reorder DataFrame columns, placing specified columns at the front and back.

    Args:
        front_cols (List[str]): Columns to place at the beginning of the DataFrame.
        df (DataFrame): The DataFrame to reorder columns for.
        back_cols (List[str]): Columns to place at the end of the DataFrame.

    Returns:
        DataFrame: The DataFrame with reordered columns.
    """
    front_cols = [col for col in front_cols if col in df.columns]
    back_cols = [col for col in back_cols if col in df.columns]
    other_cols = [col for col in df.columns if col not in front_cols and col not in back_cols]
    return df[front_cols + other_cols + back_cols]



def _guess_column_types(
        df: DataFrame, 
        exclude_cols: Optional[List[str]] = None
    ) -> DataFrame:
    """Guess and convert column types in a DataFrame, excluding specified columns.

    Attempts to convert columns to numeric types (int or float) where appropriate, while preserving
    excluded columns as strings.

    Args:
        df (DataFrame): The DataFrame to guess column types for.
        exclude_cols (Optional[List[str]]): Columns to exclude from type conversion (default: predefined list).

    Returns:
        DataFrame: The DataFrame with updated column types.
    """
    exclude_cols = exclude_cols or [
        "start_date", "end_date", "start_time", "end_time",
        "form", "event_id", "profile_id", "user_id", "entered_by_user_id",
        "entered_by", "last_modified", "last_modified_by",
        "last_modified_by_user_id", "about"
    ]
    for col in df.columns:
        if col not in exclude_cols and df[col].dtype == "object":
            sample = df[col].dropna().head(50)
            if not sample.empty:
                is_numeric = sample.apply(lambda x: isinstance(x, str) and x.replace(".", "").strip().lstrip("-").isdigit())
                if is_numeric.all():
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                    if df[col].notna().all() and (df[col] % 1 == 0).all():
                        df[col] = df[col].astype("int64")
    return df



def _convert_date_columns(
        df: DataFrame, 
        date_cols: List[str] = ["start_date", "end_date"], 
        date_format: str = "%d/%m/%Y"
    ) -> DataFrame:
    """Convert specified columns to datetime objects.

    Args:
        df (DataFrame): The DataFrame to convert date columns for.
        date_cols (List[str]): The columns to convert (default: ['start_date', 'end_date']).
        date_format (str): The expected date format (default: '%d/%m/%Y').

    Returns:
        DataFrame: The DataFrame with converted date columns.
    """
    for col in date_cols:
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col], format=date_format, errors="coerce")
            except (ValueError, TypeError):
                pass
    return df



def _convert_time_columns(
        df: DataFrame, 
        time_cols: List[str] = ["start_time", "end_time"], 
        time_format: str = "%H:%M:%S"
    ) -> DataFrame:
    """Convert specified columns to time objects.

    Args:
        df (DataFrame): The DataFrame to convert time columns for.
        time_cols (List[str]): The columns to convert (default: ['start_time', 'end_time']).
        time_format (str): The expected time format (default: '%H:%M:%S').

    Returns:
        DataFrame: The DataFrame with converted time columns.
    """
    for col in time_cols:
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col], format=time_format, errors="coerce").dt.time
            except (ValueError, TypeError):
                pass
    return df



def _transform_event_data(
        df: DataFrame, 
        clean_names: bool = False, 
        guess_col_type: bool = False, 
        convert_dates: bool = False
    ) -> DataFrame:
    """Apply transformations to an event DataFrame.

    Applies optional transformations such as cleaning column names, guessing column types, and converting date columns.

    Args:
        df (DataFrame): The event DataFrame to transform.
        clean_names (bool): Whether to clean column names (default: False).
        guess_col_type (bool): Whether to infer column data types (default: False).
        convert_dates (bool): Whether to convert date columns to datetime objects (default: False).

    Returns:
        DataFrame: The transformed event DataFrame.
    """
    if clean_names:
        df = _clean_column_names(df)
    if guess_col_type:
        df = _guess_column_types(df)
    if convert_dates:
        df = _convert_date_columns(df)
    return df



def _transform_profile_data(
        df: DataFrame, 
        clean_names: bool = False, 
        guess_col_type: bool = False
    ) -> DataFrame:
    """Apply transformations to a profile DataFrame.

    Applies optional transformations such as cleaning column names and guessing column types.

    Args:
        df (DataFrame): The profile DataFrame to transform.
        clean_names (bool): Whether to clean column names (default: False).
        guess_col_type (bool): Whether to infer column data types (default: False).

    Returns:
        DataFrame: The transformed profile DataFrame.
    """
    if clean_names:
        df = _clean_column_names(df)
    if guess_col_type:
        df = _guess_column_types(df)
    return df



def _sort_event_data(df: DataFrame) -> DataFrame:
    """Sort an event DataFrame by start_date, user_id, and event_id.

    Args:
        df (DataFrame): The event DataFrame to sort.

    Returns:
        DataFrame: The sorted event DataFrame.
    """
    return df.sort_values(
        by=["start_date", "user_id", "event_id"],
        ascending=[True, True, True],
        na_position="last"
    ).reset_index(drop=True)



def _sort_profile_data(df: DataFrame) -> DataFrame:
    """Sort a profile DataFrame by user_id and profile_id.

    Args:
        df (DataFrame): The profile DataFrame to sort.

    Returns:
        DataFrame: The sorted profile DataFrame.
    """
    return df.sort_values(
        by=["user_id", "profile_id"],
        ascending=[True, True],
        na_position="last"
    ).reset_index(drop=True)