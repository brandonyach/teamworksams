from typing import Dict, List, Optional
from pandas import DataFrame
import pandas as pd
from .import_build import _build_table_rows
from .import_process import _categorize_fields, _extract_non_table_values, _build_pairs
from .utils import AMSError


def _build_database_payload(
    df: DataFrame,
    form_id: int,
    application_id: int,
    entered_by_user_id: int,
    overwrite_existing: bool,
    table_fields: Optional[List[str]]
) -> List[Dict]:
    """Build the payload for an AMS API database entry import request.

    Groups the DataFrame by user_id and entry_id (for updates), constructs entry metadata,
    and builds rows for table and non-table fields.

    Args:
        df (DataFrame): DataFrame containing the database entry data.
        form_id (int): The ID of the database form.
        application_id (int): The ID of the application.
        entered_by_user_id (int): The ID of the user performing the operation.
        overwrite_existing (bool): Whether this is an update operation.
        table_fields (Optional[List[str]]): List of field names that are table fields.

    Returns:
        List[Dict]: List of payload dictionaries for the API request.
    """
    non_table_fields = _categorize_fields(df, table_fields)
    
    if table_fields is not None:
        flattened_fields = []
        for item in table_fields:
            if isinstance(item, list):
                flattened_fields.extend(item)
            else:
                flattened_fields.append(item)
        table_fields = [str(col) for col in flattened_fields if isinstance(col, str)]
    
    # Ensure table_fields exist in DataFrame
    if table_fields:
        missing_fields = [col for col in table_fields if col not in df.columns]
        if missing_fields:
            raise AMSError(
                f"Table fields not found in DataFrame columns: {missing_fields}",
                function="_build_database_payload"
            )
    
    payloads = []
    
    if overwrite_existing:
        group_keys = ["entry_id"]
        grouped_df = df.groupby(group_keys)

        for (entry_id,), group in grouped_df:
            payload = _build_entry_metadata(
                group,
                form_id,
                application_id,
                entered_by_user_id,
                overwrite_existing
            )
            payload["rows"] = _build_table_rows(group, table_fields, non_table_fields)
            payloads.append({"event": payload})
    else:
        # For inserts, treat each row as a separate entry or group by table fields
        if table_fields and any(col in df.columns for col in table_fields):
            group_keys = [col for col in non_table_fields if col in df.columns]
            grouped_df = df.groupby(group_keys) if group_keys else [(None, df)]
        else:
            grouped_df = [(i, df.iloc[[i]]) for i in range(len(df))]
        
        for _, group in grouped_df:
            payload = _build_entry_metadata(
                group,
                form_id,
                application_id,
                entered_by_user_id,
                overwrite_existing
            )
            payload["rows"] = _build_table_rows(group, table_fields, non_table_fields)
            payloads.append({"event": payload})
    
    return payloads


def _build_entry_metadata(
    group: DataFrame,
    form_id: int,
    application_id: int,
    entered_by_user_id: int,
    overwrite_existing: bool
) -> Dict:
    """Build metadata for a database entry payload.

    Constructs the metadata portion of the payload, including form ID, application ID,
    entry mode, and optional entry ID for updates.

    Args:
        group (DataFrame): DataFrame group containing entry data.
        form_id (int): The ID of the database form.
        application_id (int): The ID of the application.
        entered_by_user_id (int): The ID of the user performing the operation.
        overwrite_existing (bool): Whether this is an update operation.

    Returns:
        Dict: Dictionary containing the entry metadata.
    """
    payload = {
        "entryMode": "1" if overwrite_existing else "0",
        "applicationId": int(application_id),
        "formId": int(form_id),
        "enteredByUserId": int(entered_by_user_id),
        "id": "-1"
    }
    if overwrite_existing and "entry_id" in group.columns:
        entry_id = group["entry_id"].iloc[0]
        if pd.notna(entry_id):
            payload["id"] = int(entry_id)
    return payload


def _build_table_rows(
    group: DataFrame,
    table_fields: Optional[List[str]],
    non_table_fields: List[str]
) -> Dict:
    """Build rows for table and non-table fields in a database entry payload.

    For table forms, non-table fields are included in row 0, and table fields are included
    in all rows. For non-table forms, all fields are included in row 0.

    Args:
        group (DataFrame): DataFrame group containing entry data.
        table_fields (Optional[List[str]]): List of field names that are table fields.
        non_table_fields (List[str]): List of field names that are non-table fields.

    Returns:
        Dict: Dictionary mapping row indices to key-value pairs.
    """
    rows = {}
    non_table_values = _extract_non_table_values(group, non_table_fields)
    
    if table_fields:
        for idx, (_, row) in enumerate(group.iterrows()):
            row_data = {}
            if idx == 0:
                for field, value in non_table_values.items():
                    row_data[field] = value
            table_pairs = _build_pairs(row, table_fields)
            for pair in table_pairs:
                row_data[pair["key"]] = pair["value"]
            if row_data:
                rows[str(idx)] = row_data
    else:
        rows["0"] = {field: value for field, value in non_table_values.items()}
    
    return rows if rows else {"0": {}}




