from pandas import DataFrame
from typing import List, Optional
from .import_clean import _remove_protected_columns, _convert_id_names_to_lower, _replace_na_with_empty_string


def _clean_database_df(df: DataFrame, table_fields: Optional[List[str]] = None) -> DataFrame:
    """Clean a DataFrame for import into an AMS database form.

    This function performs cleaning steps to prepare the DataFrame for database entry import:
    - Removes protected columns like 'first name' and 'last name'.
    - Replaces NaN values with empty strings, except for 'entry_id'.
    - Converts ID column names to lowercase.

    Args:
        df (DataFrame): Input DataFrame containing database entry data.
        table_fields (Optional[List[str]]): List of field names that are table fields.

    Returns:
        DataFrame: Cleaned DataFrame ready for import into AMS.
    """
    df = _remove_protected_columns(df)
    exclude_cols = ["entry_id"] if "entry_id" in df.columns else []
    if table_fields:
        exclude_cols.extend(table_fields)
    df = _replace_na_with_empty_string(df)
    df = _convert_id_names_to_lower(df)
    return df