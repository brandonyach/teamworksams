from pandas import DataFrame, isna
from typing import Optional, List
from .utils import AMSError
from .import_validate import _validate_ids

def _validate_database_df(
    df: DataFrame,
    form: str,
    overwrite_existing: bool,
    table_fields: Optional[List[str]]
) -> None:
    """Validate a DataFrame for import into an AMS database form.

    Performs validation checks for:
    - DataFrame type and non-emptiness.
    - Form name validity.
    - User ID and entry ID columns (for updates).

    Args:
        df (DataFrame): DataFrame containing the database entry data.
        form (str): The name of the AMS database form.
        overwrite_existing (bool): Whether this is an update operation.
        table_fields (Optional[List[str]]): List of field names that are table fields.

    Raises:
        AMSError: If any validation check fails.
    """
    if not isinstance(df, DataFrame):
        raise AMSError("DataFrame must be a pandas DataFrame", function="database_entry")
    if df.empty:
        raise AMSError("DataFrame must not be empty", function="database_entry")
    if not form or not isinstance(form, str):
        raise AMSError("Form must be a non-empty string", function="database_entry")
    
    if overwrite_existing:
        if "entry_id" not in df.columns:
            raise AMSError("entry_id column is required for updating database entries", function="database_entry")
        if not df["entry_id"].apply(lambda x: isinstance(x, (int, float)) and not isna(x)).all():
            raise AMSError("entry_id column must contain valid integer values", function="database_entry")