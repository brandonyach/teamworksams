from typing import Dict, List, Optional
from pandas import DataFrame
from .import_clean import _set_default_dates_and_times
from .import_process import _categorize_fields, _get_existing_event_id, _extract_non_table_values, _build_pairs


def _build_import_payload(
    df: DataFrame,
    form: str,
    table_fields: Optional[List[str]],
    entered_by_user_id: int,
    overwrite_existing: bool
) -> List[Dict]:
    """Build the payload for an AMS API event import request.

    Groups the DataFrame by user_id, start_date, and event_id (for updates), constructs
    event metadata, and builds rows for table and non-table fields.

    Args:
        df: DataFrame containing the event data to import.
        form: The name of the AMS Event Form.
        table_fields: List of field names that are table fields, or None for non-table forms.
        entered_by_user_id: The ID of the user performing the operation.
        overwrite_existing: Boolean indicating if this is an update operation.

    Returns:
        List containing a single dictionary with an 'events' key mapping to a list of event payloads.
    """
    non_table_fields = _categorize_fields(df, table_fields)
    
    group_keys = ["user_id", "start_date"]
    if overwrite_existing and "event_id" in df.columns:
        group_keys.append("event_id")
    grouped_df = df.groupby(group_keys)
    
    events = []
    for _, group in grouped_df:
        
        payload = _build_event_metadata(group, form, entered_by_user_id, overwrite_existing)
        
        payload["rows"] = _build_table_rows(group, table_fields, non_table_fields)
        
        events.append(payload)
    
    # Wrap in events list for eventsimport
    wrapped_payload = {"events": events}
    # print(f"Debug: Event payload being sent: {wrapped_payload}")  # Debugging statement
    return [wrapped_payload]



def _build_profile_payload(
    df: DataFrame,
    form: str,
    entered_by_user_id: int
) -> List[Dict]:
    """Build the payload for an AMS API profile import request.

    Groups the DataFrame by user_id, constructs profile metadata, and builds rows for
    non-table fields. Profile forms do not support table fields, so all fields are included
    in row 0.

    Args:
        df: DataFrame containing the profile data to import.
        form: The name of the AMS Profile form.
        entered_by_user_id: The ID of the user performing the operation.

    Returns:
        List containing profile payloads as dictionaries.
    """
    non_table_fields = _categorize_fields(df)
    
    grouped_df = df.groupby("user_id")
    
    profiles = []
    for user_id, group in grouped_df:
        
        payload = _build_profile_metadata(form, user_id, entered_by_user_id)
        
        payload["rows"] = _build_profile_rows(group, non_table_fields)
        
        profiles.append(payload)
    
    # print(f"Debug: Profile payload being sent: {profiles}")  # Debugging statement
    return profiles


def _build_event_metadata(
    group: DataFrame,
    form: str,
    entered_by_user_id: int,
    overwrite_existing: bool
) -> Dict:
    """Build event metadata for an AMS API payload.

    Constructs the metadata portion of the payload, including form name, dates, times,
    user ID, and optionally an existing event ID for updates.

    Args:
        group: DataFrame group containing event data for a single user and start_date.
        form: The name of the AMS Event Form.
        entered_by_user_id: The ID of the user performing the operation.
        overwrite_existing: Boolean indicating if this is an update operation.

    Returns:
        Dictionary containing the event metadata.
    """
    row = group.iloc[0]
    start_date, start_time, end_date, end_time = _set_default_dates_and_times(row)

    payload = {
        "formName": form,
        "startDate": start_date,
        "startTime": start_time,
        "finishDate": end_date,
        "finishTime": end_time,
        "userId": {"userId": int(row["user_id"])},
        "enteredByUserId": int(entered_by_user_id)
    }

    existing_event_id = _get_existing_event_id(group, overwrite_existing)
    if existing_event_id is not None:
        payload["existingEventId"] = existing_event_id

    return payload



def _build_profile_metadata(
    form: str,
    user_id: int,
    entered_by_user_id: int
) -> Dict:
    """Build profile metadata for an AMS API payload.

    Constructs the metadata portion of the payload for a profile form, including form name
    and user ID. Profile forms do not require date/time fields.

    Args:
        form: The name of the AMS Profile form.
        user_id: The ID of the user the profile data belongs to.
        entered_by_user_id: The ID of the user performing the operation.

    Returns:
        Dictionary containing the profile metadata.
    """
    payload = {
        "formName": form,
        "userId": {"userId": int(user_id)},
        "enteredByUserId": int(entered_by_user_id)
    }
    return payload


def _build_table_rows(
    group: DataFrame,
    table_fields: Optional[List[str]],
    non_table_fields: List[str]
) -> List[Dict]:
    """Build rows for table and non-table fields in an AMS API payload.

    For table forms, non-table fields are included in row 0, and table fields are included
    in all rows. For non-table forms, all fields are included in a single row (row 0).

    Args:
        group: DataFrame group containing event or profile data for a single user.
        table_fields: List of field names that are table fields, or None for non-table forms.
        non_table_fields: List of field names that are non-table fields.

    Returns:
        List of row dictionaries, each containing a 'row' index and 'pairs' of key-value data.
    """
    rows = []
    non_table_values = _extract_non_table_values(group, non_table_fields)

    if table_fields:
        # For table forms, include non-table fields in row 0 and table fields in all rows
        for idx, (_, row) in enumerate(group.iterrows()):
            pairs = []
            # Include non-table fields only in the first row (row 0)
            if idx == 0:
                for field, value in non_table_values.items():
                    pairs.append({"key": field, "value": value})
            
            # Include table fields in all rows
            table_pairs = _build_pairs(row, table_fields)
            pairs.extend(table_pairs)

            if pairs:  # Only add rows with non-empty pairs
                rows.append({"row": idx, "pairs": pairs})
    else:
        pairs = []
        for field, value in non_table_values.items():
            pairs.append({"key": field, "value": value})
        rows.append({"row": 0, "pairs": pairs})

    return rows if rows else [{"row": 0, "pairs": []}]



def _build_profile_rows(group: DataFrame, non_table_fields: List[str]) -> List[Dict]:
    """Build rows for a profile form in an AMS API payload.

    Profile forms do not support table fields, so all fields are treated as non-table fields
    and included in a single row (row 0).

    Args:
        group: DataFrame group containing profile data for a single user.
        non_table_fields: List of field names to include in the row.

    Returns:
        List containing a single row dictionary with a 'row' index of 0 and 'pairs' of key-value data.
    """
    rows = []
    non_table_values = _extract_non_table_values(group, non_table_fields)

    pairs = []
    for field, value in non_table_values.items():
        pairs.append({"key": field, "value": value})
    rows.append({"row": 0, "pairs": pairs})

    return rows if rows else [{"row": 0, "pairs": []}]