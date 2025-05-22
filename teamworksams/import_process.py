from typing import Dict, List, Optional
from pandas import DataFrame
import pandas as pd
from .utils import AMSClient, AMSError
from .user_main import get_user
from .user_option import UserOption


def _extract_non_table_values(group: DataFrame, non_table_fields: List[str]) -> Dict:
    """Extract non-table field values from the group, taking the first non-NaN value.

    Args:
        group: DataFrame group containing event or profile data.
        non_table_fields: List of field names to extract.

    Returns:
        Dictionary mapping field names to their first non-NaN values.
    """
    non_table_values = {}
    for field in non_table_fields:
        non_nan_values = group[field].dropna()
        if not non_nan_values.empty:
            non_table_values[field] = str(non_nan_values.iloc[0])
    return non_table_values


def _count_unique_events(events: List[Dict]) -> int:
    """Count unique events based on user_id, start_date, and optionally existingEventId.

    Args:
        events: List of event dictionaries from the payload.

    Returns:
        Number of unique events based on grouping keys.
    """
    group_keys = ["startDate"]
    if any("existingEventId" in event for event in events):
        group_keys.append("existingEventId")
    return len(set(
        tuple(
            [event["userId"]["userId"]] + [event[key] for key in group_keys]
        )
        for event in events
    ))


def _handle_import_response(response: Dict) -> Dict:
    """Handle the response from the AMS eventsimport or profileimport endpoint.

    Args:
        response: Raw response dictionary from the API.

    Returns:
        Processed response dictionary with state, IDs, and message.
    """
    # Check if response has a 'result' key; otherwise, use the response directly
    result = response.get("result", response)
    state = result.get("state", response.get("state", "UNKNOWN"))
    ids = result.get("ids", response.get("ids", []))
    message = result.get("message", response.get("message", ""))
    
    processed_result = {
        "state": state,
        "ids": ids,
        "message": message
    }
    # print(f"Debug: API response received: {response}")
    # print(f"Debug: Processed result: {processed_result}")
    return processed_result



def _count_unique_profiles(profiles: List[Dict]) -> int:
    """Count unique profiles based on user_id.

    Args:
        profiles: List of profile dictionaries from the payload.

    Returns:
        Number of unique profiles based on user_id.
    """
    return len(set(profile["userId"]["userId"] for profile in profiles))


def _categorize_fields(df: DataFrame, table_fields: Optional[List[str]] = None) -> List[str]:
    """Categorize DataFrame columns into non-table fields, excluding metadata fields.

    Args:
        df: Input DataFrame containing event or profile data.
        table_fields: List of field names that are table fields, or None for non-table forms.

    Returns:
        List of field names that are non-table fields.
    """
    excluded_fields = [
        "user_id", "about", "username", "email", "form", "entered_by_user_id",
        "full_name", "sex", "dob", "start_date", "start_time", "end_date",
        "end_time", "event_id"
    ]
    return [col for col in df.columns if col not in excluded_fields and (not table_fields or col not in table_fields)]


def _get_existing_event_id(group: DataFrame, overwrite_existing: bool) -> Optional[int]:
    """Extract the existingEventId from the group if overwrite_existing is True.

    Args:
        group: DataFrame group containing event data.
        overwrite_existing: Boolean indicating if this is an update operation.

    Returns:
        Integer event ID if present and overwrite_existing is True, otherwise None.
    """
    if not overwrite_existing or "event_id" not in group.columns or group["event_id"].isna().all():
        return None
    event_id = group["event_id"].dropna().iloc[0]
    return int(event_id) if pd.notna(event_id) else None


def _build_pairs(data: Dict, fields: List[str]) -> List[Dict]:
    """Build key-value pairs for specified fields, excluding NaN values.

    Args:
        data: Dictionary containing field-value pairs (e.g., a DataFrame row).
        fields: List of field names to include in the pairs.

    Returns:
        List of dictionaries with 'key' and 'value' for each field, excluding NaN values.
    """
    if not fields:
        return []
    return [{"key": k, "value": str(data[k])} for k in fields if pd.notna(data[k])]



def _filter_user_df(
        user_df: DataFrame, 
        id_col: str, 
        unique_ids: List[str]
    ) -> DataFrame:
    """Filter a user DataFrame based on the specified id_col and unique_ids.

    Args:
        user_df: DataFrame containing user data with columns like 'user_id', 'username', etc.
        id_col: The column name to filter on (e.g., 'username', 'about').
        unique_ids: List of unique values to filter the id_col by.

    Returns:
        Filtered DataFrame containing only rows where id_col matches one of the unique_ids.
    """
    if id_col == "about":
        user_df[id_col] = (user_df["first_name"].astype(str) + " " + user_df["last_name"].astype(str)).str.strip()
        return user_df[user_df[id_col].isin(unique_ids)]
    return user_df[user_df[id_col].isin(unique_ids)]



def _map_id_col_to_user_id(df: DataFrame, id_col: str, client: AMSClient) -> DataFrame:
    """Map a user identifier column to AMS user IDs.

    This function fetches all users from AMS, filters them based on the specified
    id_col, and merges the resulting user IDs into the input DataFrame.

    Args:
        df: Input DataFrame containing a column with user identifiers (e.g., 'username').
        id_col: The column name in df to map to user IDs (e.g., 'username', 'about', 'user_id').
        client: An AMSClient instance for making API requests.

    Returns:
        DataFrame with an additional 'user_id' column mapped from the id_col.

    Raises:
        AMSError: If the id_col is not found, no valid values are present, or mapping fails.
    """
    df = df.copy()
    
    if id_col == "user_id":
        if "user_id" in df.columns:
            return df
        raise AMSError("user_id column required.")
    
    if id_col not in df.columns:
        raise AMSError(f"'{id_col}' column not found.")
    
    if "user_id" in df.columns:
        df = df.drop(columns=["user_id"])
    
    unique_ids = df[id_col].dropna().unique().tolist()
    if not unique_ids:
        raise AMSError(f"No valid '{id_col}' values.")
    
    user_df = get_user(
        url=client.url,
        filter=None,
        client=client,
        option=UserOption(interactive_mode=False)
    )
    
    user_df = _filter_user_df(user_df, id_col, unique_ids)
    
    df_mapped = df.merge(user_df[["user_id", id_col]], on=id_col, how="left")
    
    if "user_id" not in df_mapped.columns:
        raise AMSError("Merge failed to include 'user_id'.")
    if df_mapped["user_id"].isna().any():
        unmapped = df_mapped[df_mapped["user_id"].isna()][id_col].tolist()
        raise AMSError(f"Failed to map '{id_col}': {unmapped}")
    
    return df_mapped
