import pandas as pd
from pandas import DataFrame
from typing import Optional, Dict, List, Tuple, Union
from .export_filter import EventFilter, ProfileFilter
from .utils import AMSClient, AMSError, get_client
from .user_filter import UserFilter
from .user_option import UserOption
from .user_build import _build_user_payload, _build_all_user_data_payload
from .user_process import _flatten_user_response, _filter_by_about


def _fetch_user_data(
    client: AMSClient,
    filter: Optional[UserFilter] = None,
    cache: bool = True
) -> Dict:
    """Fetch user data from the AMS API based on a filter.

    Retrieves user data using the appropriate endpoint ('usersearch' or 'groupmembers') based on the filter.

    Args:
        client (AMSClient): The authenticated AMSClient instance.
        filter (Optional[UserFilter]): A UserFilter object to narrow results (e.g., by username, email, group).
        cache (bool): Whether to cache the API response (default: True).

    Returns:
        Dict: The raw API response containing user data.

    Raises:
        AMSError: If the API request fails or no users are found.
    """
    if filter and filter.user_key == "group":
        endpoint = "groupmembers"
        payload = _build_user_payload(filter)
        data = client._fetch(endpoint, method="POST", payload=payload, cache=cache, api_version="v1")
        if not data.get("results") or not data["results"][0].get("results"):
            raise AMSError(f"No members found in group '{filter.user_value}' - Function: get_user - Endpoint: {endpoint}")
    else:
        endpoint = "usersearch"
        # Use empty payload for about to avoid duplicates
        if filter and filter.user_key == "about":
            payload = {"identification": []}
        else:
            payload = _build_user_payload(filter)
        data = client._fetch(endpoint, method="POST", payload=payload, cache=cache, api_version="v1")
        if not data or "results" not in data or not data["results"]:
            raise AMSError(f"No users returned from server - Function: get_user - Endpoint: {endpoint}")
    return data



def _fetch_user_save(
    user_data: Dict,
    client: AMSClient,
    interactive_mode: bool = False
) -> Tuple[Dict, Optional[str]]:
    """Make the API call to save a user via the /api/v2/person/save endpoint for creation or update.

    Args:
        user_data (Dict): The user data dictionary, containing 'id' (set to "-1" for creation) and fields to update or create.
        client (AMSClient): The AMSClient instance.
        interactive_mode (bool): Whether to print debug information (default: False).

    Returns:
        Tuple[Dict, Optional[str]]: The API response and the user_id (if available, None otherwise).

    Raises:
        AMSError: If the API request fails or the response indicates a failure.
    """
    # Ensure id is present (can be "-1" for creation)
    if "id" not in user_data:
        AMSError("Missing required field 'id' in user_data", function="fetch_user_save")

    # Ensure certain fields are strings as expected by the API
    for key in ["id", "avatarId", "organisationId", "ownerId", "plan", "state", "uuid", "emailAddress", "firstName", "lastName", "username", "password", "dateOfBirth", "knownAs", "middleNames", "language", "sidebarWidth", "sex"]:
        if key in user_data and user_data[key] is not None:
            user_data[key] = str(user_data[key])

    payload = {"person": user_data}
    response = client._fetch(
        "person/save",
        method="POST",
        payload=payload,
        cache=False,
        api_version="v2"
    )

    # Check for RPC exception in the response
    if response.get("__is_rpc_exception__", False):
        error_type = response.get("type", "UnknownError")
        error_message = response.get("value", {}).get("detailMessage", "No error message provided")
        cause = response.get("value", {}).get("cause", "Unknown cause")
        AMSError(f"API error ({error_type}): {error_message}. Cause: {cause}", function="fetch_user_save")

    # Validate the response
    if not response:
        AMSError("No response from server", function="fetch_user_save")

    # Extract user_id from response
    user_id = None
    if "id" in response:
        user_id = str(response["id"])  # Convert to string for consistency

    return response, user_id



def _fetch_user_ids(
    client: AMSClient,
    filter: Optional[Union[UserFilter, EventFilter, ProfileFilter]] = None,
    cache: bool = True
) -> Tuple[List[int], Optional[DataFrame]]:
    """Fetch user IDs and the raw user DataFrame for event or profile data export.

    Retrieves user IDs based on the provided filter, along with the raw user DataFrame for further processing.

    Args:
        client (AMSClient): The authenticated AMSClient instance.
        filter (Optional[Union[UserFilter, EventFilter, ProfileFilter]]): A filter object to narrow user selection.
        cache (bool): Whether to cache the API response (default: True).

    Returns:
        Tuple[List[int], Optional[DataFrame]]: A tuple containing the list of user IDs and the raw user DataFrame.

    Raises:
        AMSError: If no users are found.
    """
    data = _fetch_user_data(client, filter, cache)
    user_data = _flatten_user_response(data)
    if not user_data:
        return [], None
    
    user_df = pd.DataFrame(user_data)
    if user_df.empty:
        return [], None
    
    if filter and filter.user_key == "about" and filter.user_value:
        user_df = _filter_by_about(user_df, filter.user_value)
        if user_df.empty:
            return [], None
    
    user_ids = user_df["userId"].dropna().astype(int).tolist()
    return user_ids, user_df



def _fetch_all_user_ids(
    client: AMSClient,
    cache: bool = True
) -> List[str]:
    """Fetch all user IDs from the AMS instance using the /api/v1/usersearch endpoint.

    Args:
        client (AMSClient): The authenticated AMSClient instance.
        cache (bool): Whether to cache the API response (default: True).

    Returns:
        List[str]: A list of user IDs as strings.

    Raises:
        AMSError: If the API request fails or no users are found.
    """
    # Use an empty filter to fetch all users
    data = _fetch_user_data(client, filter=None, cache=cache)
    
    # Extract user IDs
    users = _flatten_user_response(data)
    user_ids = [str(user["userId"]) for user in users if "userId" in user]
    
    if not user_ids:
        AMSError("No user IDs returned from server", function="_get_all_user_ids", endpoint="usersearch")
    
    return user_ids



def _fetch_all_user_data(
    url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    user_ids: Optional[List[str]] = None,
    option: Optional[UserOption] = None,
    client: Optional[AMSClient] = None
) -> DataFrame:
    """Retrieve all user data from an AMS instance using the /api/v2/person/get endpoint.

    Internal helper function for edit_user and other operations. Fetches complete user objects for all users
    or a specified subset based on user IDs.

    Args:
        url (str): The AMS instance URL (e.g., 'https://example.smartabase.com/site').
        username (Optional[str]): The username for authentication. If None, uses AMS_USERNAME env var.
        password (Optional[str]): The password for authentication. If None, uses AMS_PASSWORD env var.
        user_ids (Optional[List[str]]): List of user IDs to filter the results (default: None, fetches all users).
        option (Optional[UserOption]): A UserOption object for customization (e.g., cache, interactive mode).
        client (Optional[AMSClient]): A pre-initialized AMSClient instance. If None, a new client is created.

    Returns:
        DataFrame: A DataFrame containing complete user data with all fields returned by the API.

    Raises:
        AMSError: If the API request fails or no users are found.
    """
    option = option or UserOption()
    client = client or get_client(url, username, password, cache=option.cache, interactive_mode=option.interactive_mode)
    
    if option.interactive_mode:
        print("ℹ Fetching all user data...")
    
    if user_ids is None:
        user_ids = _fetch_all_user_ids(client, cache=option.cache)
    
    payload = _build_all_user_data_payload(user_ids)
    
    try:
        data = client._fetch(
            "person/get",
            method="POST",
            payload=payload,
            cache=option.cache,
            api_version="v2"
        )
    except AMSError as e:
        raise AMSError(f"Failed to fetch user data: {str(e)} - Function: _get_all_user_data - Endpoint: person/get")
    
    if not data or "objects" not in data or not data["objects"]:
        raise AMSError("No users returned from server - Function: _get_all_user_data - Endpoint: person/get")
    
    user_df = pd.DataFrame(data["objects"])
    user_df["id"] = user_df["id"].astype(int)
    
    if option.interactive_mode:
        print(f"ℹ Retrieved {len(user_df)} users.")
    
    return user_df



def _update_single_user(
    user_data: Dict,
    client: AMSClient,
    user_id: str,
    identifier: str,
    interactive_mode: bool = False
) -> Optional[str]:
    """Update a single user via the /api/v2/person/save endpoint.

    Args:
        user_data (Dict): The user data dictionary with updated fields.
        client (AMSClient): The AMSClient instance.
        user_id (str): The user ID for error reporting.
        identifier (str): The identifier (e.g., file_name or user_key) for error reporting.
        interactive_mode (bool): Whether to print status messages.

    Returns:
        Optional[str]: Error message if update fails, None if successful.
    """
    try:
        _fetch_user_save(user_data, client, interactive_mode=interactive_mode)
        return None
    except AMSError as e:
        error_msg = str(e)
        if interactive_mode:
            print(f"⚠️ Failed to update user ID {user_id}: {error_msg}")
        return error_msg