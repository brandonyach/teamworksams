import pandas as pd
from pandas import DataFrame
from typing import Optional, Dict, List
from .utils import AMSError
from .user_filter import UserFilter
from .user_process import _map_user_updates


def _build_user_payload(filter: Optional[UserFilter] = None) -> Dict:
    """Build the payload for usersearch or groupmembers API endpoints.

    Constructs a payload for fetching users based on the provided filter (e.g., by username, email, or group).

    Args:
        filter (Optional[UserFilter]): A UserFilter object specifying the user key and value to filter by.

    Returns:
        Dict: The payload dictionary for the API request.
    """
    payload = {"identification": []}
    if filter and filter.user_key and filter.user_value:
        if filter.user_key == "group":
            return {"name": [filter.user_value] if isinstance(filter.user_value, str) else filter.user_value}
        elif isinstance(filter.user_value, list):
            payload["identification"] = [{filter.user_key: value} for value in filter.user_value]
        else:
            payload["identification"] = [{filter.user_key: filter.user_value}]
    return payload



def _build_all_user_data_payload(user_ids: List[str]) -> Dict:
    """Build the payload for the /api/v2/person/get endpoint.

    Constructs a payload for fetching complete user objects based on a list of user IDs.

    Args:
        user_ids (List[str]): List of user IDs to include in the filter.

    Returns:
        Dict: The payload dictionary for the API request.
    """
    return {
        "filter": {
            "comparisons": {
                "op": "0",
                "branches": [
                    {
                        "leaf": {
                            "negated": False,
                            "comp": "1",
                            "fieldName": "id",
                            "valueInteger": user_ids
                        }
                    }
                ]
            },
            "limit": "-1",
            "offset": "-1"
        }
    }
    
    
def _build_group_payload(username: Optional[str]) -> dict:
    """Build the payload for the listgroups API endpoint.

    Constructs a payload for fetching groups, optionally filtering by username.

    Args:
        username (Optional[str]): The username to filter groups by.

    Returns:
        dict: The payload dictionary for the API request.
    """
    return {"name": username}



def _build_user_save_payload(row: pd.Series, is_create: bool = True) -> Dict:
    """Build the payload for the /api/v2/person/save endpoint from a DataFrame row.

    Args:
        row (pd.Series): A row from the cleaned DataFrame containing user data.
        is_create (bool): Whether the payload is for creating a new user (id="-1") or updating (uses existing id).

    Returns:
        Dict: The payload dictionary for the API request.
    """
    user_data = {
        "id": "-1" if is_create else row.get("id", "-1"),
        "firstName": row["firstName"],
        "lastName": row["lastName"],
        "username": row["username"],
        "emailAddress": row["emailAddress"],
        "dateOfBirth": row["dateOfBirth"],
        "password": row["password"],
        "active": row["active"],
        "knownAs": row["knownAs"],
        "middleNames": row["middleNames"],
        "language": row["language"],
        "sidebarWidth": row["sidebarWidth"],
        "uuid": row["uuid"]
    }
    if "sex" in row and row["sex"]:
        user_data["sex"] = row["sex"]
    return user_data


def _build_user_edit_payload(row: pd.Series, user_df: DataFrame, column_mapping: Dict[str, str]) -> Dict:
    """Build the payload for updating a user via the /api/v2/person/save endpoint.

    Args:
        row (pd.Series): A row from the cleaned mapping DataFrame containing update values.
        user_df (DataFrame): DataFrame with complete user data from /api/v2/person/get.
        column_mapping (Dict[str, str]): Mapping of DataFrame columns to API field names.

    Returns:
        Dict: The updated user data dictionary with new values from the row.

    Raises:
        AMSError: If the user_id is not found in user_df.
    """
    user_id = row["user_id"]
    if pd.isna(user_id):
        raise AMSError(f"Invalid user_id for row: {row.to_dict()}")
    user_data = user_df[user_df["id"] == user_id].to_dict("records")
    if not user_data:
        raise AMSError(f"User ID {user_id} not found in user data")
    return _map_user_updates(row, user_data[0], column_mapping)