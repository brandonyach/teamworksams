import pandas as pd
from pandas import DataFrame
from typing import Optional, List, Dict
from tqdm import tqdm
from .utils import AMSClient, AMSError, get_client
from .user_build import _build_group_payload, _build_user_save_payload, _build_user_edit_payload
from .user_fetch import _fetch_user_data, _fetch_user_save, _fetch_all_user_data
from .user_clean import _clean_user_data, _transform_group_data, _clean_user_data_for_save, _get_update_columns
from .user_process import _filter_by_about, _flatten_user_response, _match_user_ids, _process_users
from .user_print import _print_user_status, _print_group_status, _report_user_results
from .user_filter import UserFilter
from .user_option import UserOption, GroupOption
from .user_validate import _validate_user_data_for_edit, _validate_user_data_for_save


def get_user(
    url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    filter: Optional[UserFilter] = None,
    option: Optional[UserOption] = None,
    client: Optional[AMSClient] = None
) -> DataFrame:
    """Retrieve user data from an AMS instance.

    Fetches user data for all accessible users or a filtered subset based on attributes like
    username, email, group, or about field. The function queries the AMS API, processes the
    response into a pandas DataFrame with columns such as user ID, name, email, and group
    affiliations, and provides interactive feedback on the number of users retrieved if
    enabled. Supports caching and column selection for customized output. See 
    :ref:`user_management` for user account workflows.

    Args:
        url (str): The AMS instance URL (e.g., 'https://example.smartabase.com/site'). Must include a valid site name.
        username (Optional[str]): Username for authentication. If None, uses :envvar:`AMS_USERNAME` or :class:`keyring` credentials. Defaults to None.
        password (Optional[str]): Password for authentication. If None, uses :envvar:`AMS_PASSWORD` or :class:`keyring` credentials. Defaults to None.
        filter (:class:`UserFilter`, optional): Filter users by attributes like 'username', 'email', 'group', or 'about'. For example, `UserFilter(user_key = "group", user_value = "TeamA")` retrieves users in "TeamA". Defaults to None (all users).
        option (:class:`UserOption`, optional): Configuration options, including `columns` (list of output columns, e.g., `["user_id", "email"]`) and `interactive_mode` (print status messages). Defaults to None (default :class:`UserOption`).
        client (:class:`AMSClient`, optional): Pre-authenticated client from :func:`get_client`. If None, a new client is created. Defaults to None.

    Returns:
        DataFrame: A pandas DataFrame containing user data with columns such as 'user_id',
            'first_name', 'last_name', 'email', 'groups', and others, depending on the API
            response and `option.columns`. Returns an empty DataFrame if no users are found
            or no users match the filter.

    Raises:
        AMSError: If authentication fails, the API request returns an invalid response,
            or no users are accessible.

    Examples:
        >>> import pandas as pd
        >>> from teamworksams import get_user, UserFilter, UserOption
        >>> df = get_user(
        ...     url = "https://example.smartabase.com/site",
        ...     username = "user",
        ...     password = "pass",
        ...     filter = UserFilter(user_key = "group", user_value = "TeamA"),
        ...     option = UserOption(columns = ["user_id", "first_name", "groups"], interactive_mode = True)
        ... )
        ℹ Fetching user data...
        ✔ Retrieved 2 users.
        >>> print(df)
           user_id first_name groups
        0    12345   John Doe  TeamA
        1    12346 Jane Smith  TeamA
    """
    option = option or UserOption()
    client = client or get_client(url, username, password, cache=option.cache, interactive_mode=option.interactive_mode)
    
    filter_type = filter.user_key if filter else None
    
    if option.interactive_mode:
        print("ℹ Fetching user data...")
    
    data = _fetch_user_data(client, filter, cache=option.cache)
    user_df = pd.DataFrame(_flatten_user_response(data))
    
    if filter and filter.user_key == "about" and filter.user_value:
        user_df = _filter_by_about(user_df, filter.user_value)
    
    user_df = _clean_user_data(user_df, option.columns, filter_type)
    _print_user_status(user_df, option)
    
    return user_df



def get_group(
    url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    option: Optional[GroupOption] = None,
    client: Optional[AMSClient] = None
) -> DataFrame:
    """Retrieve group data from an AMS instance.

    Fetches a list of groups accessible to the authenticated user, such as teams or
    departments, and processes the API response into a pandas DataFrame with group names.
    Provides interactive feedback on the number of groups retrieved if enabled. Supports
    caching and data type inference for the output DataFrame. See :ref:`user_management` 
    for user account workflows.

    Args:
        url (str): The AMS instance URL (e.g., 'https://example.smartabase.com/site'). Must include a valid site name (e.g., '/site').
        username (Optional[str]): Username for authentication. If None, uses :envvar:`AMS_USERNAME` or :class:`keyring` credentials. Defaults to None.
        password (Optional[str]): Password for authentication. If None, uses :envvar:`AMS_PASSWORD` or :class:`keyring` credentials. Defaults to None.
        option (:class:`GroupOption`, optional): Configuration options, including `guess_col_type` to infer column data types (e.g., string for group names) and `interactive_mode` to print status messages (e.g., "Retrieved 3 groups"). Defaults to None (uses default :class:`GroupOption`).
        client (:class:`AMSClient`, optional): Pre-authenticated client from :func:`get_client`. If None, a new client is created. Defaults to None.

    Returns:
        DataFrame: A pandas DataFrame containing group data with a 'name' column listing
            group names. Returns an empty DataFrame if no groups are accessible.

    Raises:
        AMSError: If authentication fails, the API request returns an invalid response,
            or no groups are accessible.

    Examples:
        >>> import pandas as pd
        >>> from teamworksams import get_group, GroupOption
        >>> df = get_group(
        ...     url = "https://example.smartabase.com/site",
        ...     username = "user",
        ...     password = "pass",
        ...     option = GroupOption(interactive_mode = True)
        ... )
        ℹ Fetching group data...
        ✔ Retrieved 3 groups.
        >>> print(df)
              name
        0    Example Group A
        1    Example Group B
        2    Example Group C
    """
    option = option or GroupOption()
    client = client or get_client(url, username, password, cache=option.cache, interactive_mode=option.interactive_mode)
    
    resolved_username = username or client.username
    if not resolved_username:
        raise AMSError("No valid username provided for group payload. Supply 'username', set AMS_USERNAME env var, or use keyring credentials.")
    
    payload = _build_group_payload(resolved_username)
    
    if option.interactive_mode:
        print("ℹ Fetching group data...")
    
    data = client._fetch("listgroups", method="POST", payload=payload, cache=option.cache, api_version="v1")
    
    if not data or "name" not in data or not data["name"]:
        AMSError("No groups returned from server", function="get_group", endpoint="listgroups")
    
    group_df = pd.DataFrame({"name": data["name"]})
    
    group_df = _transform_group_data(group_df, option.guess_col_type)
    
    _print_group_status(group_df, option)
    
    return group_df



def edit_user(
    mapping_df: DataFrame,
    user_key: str,
    url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    option: Optional[UserOption] = None,
    client: Optional[AMSClient] = None
) -> DataFrame:
    """
    Update user fields in an AMS instance.

    Updates specified fields for existing users identified by a user key (e.g., username,
    email), using the AMS API’s `/api/v2/person/save` endpoint. The function retrieves
    complete user data to preserve unchanged fields, applies updates from the mapping_df
    DataFrame, and returns a DataFrame of failed updates with reasons. Supports interactive
    feedback, including status messages and confirmation prompts, and allows caching for
    performance. See :ref:`user_management` for user account workflows.

    Args:
        mapping_df (pandas.DataFrame): DataFrame containing a user_key column (e.g., 'username') and updatable columns (e.g., 'first_name', 'email', 'dob', 'sex', 'username', 'known_as', 'active', 'uuid'). Empty values are sent as empty strings. Must not be empty.
        user_key (str): Identifier column in mapping_df. Must be one of 'username', 'email', 'about', or 'uuid'. For example, 'username' matches users by their AMS username.
        url (str): AMS instance URL (e.g., 'https://example.smartabase.com/site'). Must include a valid site name.
        username (Optional[str]): Username for authentication. If None, uses AMS_USERNAME environment variable or keyring credentials. Defaults to None.
        password (Optional[str]): Password for authentication. If None, uses AMS_PASSWORD environment variable or keyring credentials. Defaults to None.
        option (UserOption, optional): Configuration options, including interactive_mode for status messages and cache to reuse a client. The columns option is ignored. Defaults to None (uses default UserOption with interactive_mode=True).
        client (AMSClient, optional): Pre-authenticated client from teamworksams.utils.get_client. If None, a new client is created. Defaults to None.

    Returns:
        pandas.DataFrame: DataFrame of failed updates with columns 'user_id' (ID if matched or None), 'user_key' (identifier value), and 'reason' (failure reason). Empty if all updates succeed.

    Raises:
        AMSError: If mapping_df is invalid, user_key is unsupported, no users are found, authentication fails, or the API request fails.
        ValueError: If mapping_df is empty or lacks valid columns.

    Examples:
        >>> import pandas as pd
        >>> from teamworksams import edit_user, UserOption
        >>> mapping_df = pd.DataFrame({
        ...     "username": ["john.doe", "jane.smith"],
        ...     "first_name": ["John", "Jane"],
        ...     "email": ["john.doe@new.com", "jane.smith@new.com"]
        ... })
        >>> results = edit_user(
        ...     mapping_df = mapping_df,
        ...     user_key = "username",
        ...     url = "https://example.smartabase.com/site",
        ...     username = "user",
        ...     password = "pass",
        ...     option = UserOption(interactive_mode = True)
        ... )
        ℹ Fetching all user data...
        ℹ Retrieved 30 users.
        ℹ Attempting to map 2 users using about from provided dataframe...
        ℹ Successfully mapped 2 users.
        ℹ Updating 2 users...
        Processing users: 100%|██████████| 2/2 [00:4<00:00, 3.46it/s]
        ✔ Successfully updated 2 users.
        ✔ No failed operations.

    """
    option = option or UserOption(interactive_mode=True)
    client = client or get_client(url, username, password, cache=option.cache, interactive_mode=option.interactive_mode)

    _validate_user_data_for_edit(mapping_df, user_key)

    user_values = mapping_df[user_key].unique().tolist()

    try:
        user_df = _fetch_all_user_data(
            url=url,
            username=username,
            password=password,
            user_ids=None,  
            option=option,
            client=client
        )
    except AMSError as e:
        if option.interactive_mode:
            print(f"⚠️ Failed to retrieve user data: {str(e)}")
        return DataFrame({
            "user_id": [None] * len(mapping_df),
            "user_key": mapping_df[user_key],
            "status": ["FAILED"] * len(mapping_df),
            "reason": f"Failed to retrieve user data: {str(e)}"
        })

    if user_df.empty:
        if option.interactive_mode:
            print(f"⚠️ No users found")
        return DataFrame({
            "user_id": [None] * len(mapping_df),
            "user_key": mapping_df[user_key],
            "status": ["FAILED"] * len(mapping_df),
            "reason": "No users found"
        })

    if option.interactive_mode:
        print(f"ℹ Attempting to map {len(user_values)} users using {user_key} from provided dataframe...")

    mapping_df, failed_matches = _match_user_ids(
        mapping_df,
        user_df,
        user_key,
        interactive_mode=option.interactive_mode
    )

    success_results = []
    failed_results = []

    if not failed_matches.empty:
        failed_results.append(failed_matches.rename(columns={"user_key": "user_key"}).assign(status="FAILED"))

    if mapping_df.empty:
        if option.interactive_mode:
            print(f"ℹ Successfully mapped 0 users.")
            print(f"⚠️ Failed to map {len(failed_matches)} users.")
        results_df = pd.concat(failed_results, ignore_index=True)[["user_id", "user_key", "status", "reason"]]
        return results_df

    df = _clean_user_data_for_save(mapping_df, preserve_columns=[user_key, "user_id"])

    column_mapping, update_columns = _get_update_columns(df, user_key)

    if not update_columns:
        if option.interactive_mode:
            print(f"ℹ Successfully mapped {len(df)} users.")
            print(f"⚠️ No updatable columns provided in mapping_df")
        failed_results.append(DataFrame({
            "user_id": df["user_id"],
            "user_key": df[user_key],
            "status": ["FAILED"] * len(df),
            "reason": ["No updatable columns provided"] * len(df)
        }))
        results_df = pd.concat(failed_results, ignore_index=True)[["user_id", "user_key", "status", "reason"]]
        
        return results_df

    if option.interactive_mode:
        print(f"ℹ Successfully mapped {len(df)} users.")
        print(f"ℹ Updating {len(df)} users...")

    def payload_builder(row: pd.Series) -> Dict:
        return _build_user_edit_payload(row, user_df, {k: v for k, v in column_mapping.items() if k in update_columns})

    failed_operations, user_ids = _process_users(
        df,
        client,
        payload_builder,
        _fetch_user_save,
        user_key,
        interactive_mode=option.interactive_mode
    )

    # Track successful updates
    for user_id in user_ids:
        user_row = df[df["user_id"] == int(user_id)]
        if not user_row.empty:
            success_results.append(DataFrame({
                "user_id": [user_id],
                "user_key": [user_row[user_key].iloc[0]],
                "status": ["SUCCESS"],
                "reason": [None]
            }))

    # Track failed operations
    if failed_operations:
        failed_results.append(DataFrame([
            {
                "user_id": df[df[user_key] == op["user_key"]]["user_id"].iloc[0] if op["user_key"] in df[user_key].values else None,
                "user_key": op["user_key"],
                "status": "FAILED",
                "reason": op["reason"]
            }
            for op in failed_operations
        ]))

    # Concatenate results
    success_df = pd.concat(success_results, ignore_index=True) if success_results else DataFrame(
        columns=["user_id", "user_key", "status", "reason"]
    )
    failed_df = pd.concat(failed_results, ignore_index=True) if failed_results else DataFrame(
        columns=["user_id", "user_key", "status", "reason"]
    )
    results_df = pd.concat([success_df, failed_df], ignore_index=True)

    if option.interactive_mode:
        successes = results_df[results_df["status"] == "SUCCESS"]

        failures = results_df[results_df["status"] == "FAILED"]
        
        unmapped = len(failed_df[failed_df["reason"].str.contains("User not found", na=False)])
        
        other_failures = len(failed_df[~failed_df["reason"].str.contains("User not found", na=False)])
        
        print(f"✔ Successfully updated {len(successes)} users with user id's {', '.join(map(str, successes['user_id'].dropna().astype(int).tolist()))}.")
        
        if not failures.empty:
            failure_msg = f"⚠️ Failed to update {len(failures)} users: "
            failure_details = []
            if unmapped > 0:
                failure_details.append(f"{unmapped} due to unmapped {user_key}")
            if other_failures > 0:
                failure_details.append(f"{other_failures} due to other errors")
            print(failure_msg + "; ".join(failure_details) + ".")
            
        if len(failed_operations) == 0 and len(failed_matches) == 0:
            print("No failed operations.")

    return results_df[["user_id", "user_key", "status", "reason"]]



def create_user(
    user_df: DataFrame,
    url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    option: Optional[UserOption] = None,
    client: Optional[AMSClient] = None
) -> DataFrame:
    """
    Create new users in an AMS instance.

    Creates new user accounts using the AMS API’s `/api/v2/person/save` endpoint. The function processes a DataFrame with
    required fields (e.g., 'first_name', 'last_name', 'username', 'email', 'dob',
    'password', 'active') and optional fields (e.g., 'uuid', 'sex'), validates the data,
    and applies the creations. Returns a DataFrame of failed creations with reasons.
    Supports interactive feedback and caching. See :ref:`user_management` for user account workflows.

    Args:
        user_df (pandas.DataFrame): DataFrame with user data. Required columns are 'first_name', 'last_name', 'username', 'email', 'dob', 'password', 'active'. Optional columns include 'uuid', 'known_as', 'middle_names', 'language', 'sidebar_width', 'sex'. Must not be empty.
        url (str): AMS instance URL (e.g., 'https://example.smartabase.com/site'). Must include a valid site name.
        username (Optional[str]): Username for authentication. If None, uses AMS_USERNAME environment variable or keyring credentials. Defaults to None.
        password (Optional[str]): Password for authentication. If None, uses AMS_PASSWORD environment variable or keyring credentials. Defaults to None.
        option (UserOption, optional): Configuration options, including interactive_mode to print status messages and cache to reuse a client. Defaults to None (uses default UserOption).
        client (AMSClient, optional): Pre-authenticated client from teamworksams.utils.get_client. If None, a new client is created. Defaults to None.

    Returns:
        pandas.DataFrame: DataFrame of failed creations with columns 'user_key' (username that failed) and 'reason' (failure reason). Empty if all creations succeed.

    Raises:
        AMSError: If user_df is invalid, authentication fails, or the API request fails.
        ValueError: If user_df is empty or contains invalid data.

    Examples:
        >>> import pandas as pd
        >>> from teamworksams import create_user, UserOption
        >>> user_df = pd.DataFrame({
        ...     "first_name": ["John", "Jane"],
        ...     "last_name": ["Doe", "Smith"],
        ...     "username": ["john.doe", "jane.smith"],
        ...     "email": ["john.doe@example.com", "jane.smith@example.com"],
        ...     "dob": ["1980-01-01", "12/02/1985"],
        ...     "password": ["secure123", "secure456"],
        ...     "sex": ["Male", "Female"],
        ...     "uuid": ["025380", "024854"],
        ...     "active": [True, False]
        ... })
        >>> failed_df = create_user(
        ...     user_df = user_df,
        ...     url = "https://example.smartabase.com/site",
        ...     username = "user",
        ...     password = "pass",
        ...     option = UserOption(interactive_mode = True)
        ... )
        ℹ Creating 2 users...
        ✔ Successfully created 2 users.

    """
    option = option or UserOption(interactive_mode=True)
    client = client or get_client(url, username, password, cache=option.cache, interactive_mode=option.interactive_mode)

    _validate_user_data_for_save(user_df)

    df = _clean_user_data_for_save(user_df)

    failed_operations, user_ids = _process_users(
        df,
        client,
        _build_user_save_payload,
        _fetch_user_save,
        "username",
        interactive_mode=option.interactive_mode
    )

    return _report_user_results(len(df), failed_operations, user_ids, "created", interactive_mode=option.interactive_mode)