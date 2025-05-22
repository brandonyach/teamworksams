import pandas as pd
from pandas import DataFrame
from typing import Optional, List, Dict
from tqdm import tqdm
from .utils import AMSClient, AMSError, get_client
from .user_build import _build_group_payload, _build_user_save_payload, _build_user_edit_payload
from .user_fetch import _fetch_user_data, _fetch_user_save, _fetch_all_user_data
from .user_clean import _clean_user_data, _transform_group_data, _clean_user_data_for_save, _get_update_columns
from .user_process import _filter_by_about, _flatten_user_response, _match_user_ids, _map_user_updates, _process_users
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
    enabled. Supports caching and column selection for customized output.

    Args:
        url (str): The AMS instance URL (e.g., 'https://example.smartabase.com/site').
        username (Optional[str]): The username for authentication. If None, uses the
            AMS_USERNAME environment variable. Defaults to None.
        password (Optional[str]): The password for authentication. If None, uses the
            AMS_PASSWORD environment variable. Defaults to None.
        filter (Optional[UserFilter]): A UserFilter object to narrow results by user
            attributes (e.g., 'username', 'email', 'group', 'about'). If None, retrieves
            all accessible users. Defaults to None.
        option (Optional[UserOption]): Configuration options for the retrieval, including
            columns (to select specific output columns), interactive_mode (for status
            messages), and cache (for API response caching). If None, uses default
            UserOption. Defaults to None.
        client (Optional[AMSClient]): A pre-authenticated AMSClient instance. If None,
            a new client is created using the provided url, username, and password.
            Defaults to None.

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
        >>> from teamworksams import get_user
        >>> from teamworksams import UserFilter
        >>> from teamworksams import UserOption
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
    caching and data type inference for the output DataFrame.

    Args:
        url (str): The AMS instance URL (e.g., 'https://example.smartabase.com/site').
        username (Optional[str]): The username for authentication. If None, uses the
            AMS_USERNAME environment variable. Defaults to None.
        password (Optional[str]): The password for authentication. If None, uses the
            AMS_PASSWORD environment variable. Defaults to None.
        option (Optional[GroupOption]): Configuration options for the retrieval, including
            guess_col_type (to infer column data types), interactive_mode (for status
            messages), and cache (for API response caching). If None, uses default
            GroupOption. Defaults to None.
        client (Optional[AMSClient]): A pre-authenticated AMSClient instance. If None,
            a new client is created using the provided url, username, and password.
            Defaults to None.

    Returns:
        DataFrame: A pandas DataFrame containing group data with a 'name' column listing
            group names. Returns an empty DataFrame if no groups are accessible.

    Raises:
        AMSError: If authentication fails, the API request returns an invalid response,
            or no groups are accessible.

    Examples:
        >>> import pandas as pd
        >>> from teamworksams import get_group
        >>> from teamworksams import GroupOption
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
    
    payload = _build_group_payload(username)
    
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
    """Update user fields in an AMS instance.

    Updates specified fields for existing users identified by a user key (e.g., username,
    email), using the AMS API’s `/api/v2/person/save` endpoint. The function retrieves
    complete user data to preserve unchanged fields, applies updates of only the fields provided
    from the DataFrame, and returns a DataFrame of failed updates with reasons. Supports interactive
    feedback, including status messages and confirmation prompts, and allows caching for
    performance.

    Args:
        mapping_df (DataFrame): A pandas DataFrame containing:
            - A column with user identifiers (named by `user_key`, e.g., 'username', 'email').
            - Updatable columns (e.g., 'first_name', 'last_name', 'email', 'dob', 'sex', 
              'username', 'known_as', 'active', 'uuid'). Empty values are uploaded as empty strings.
        user_key (str): The name of the user identifier column in `mapping_df`, one of
            'username', 'email', 'about', or 'uuid'.
        url (str): The AMS instance URL (e.g., 'https://example.smartabase.com/site').
        username (Optional[str]): The username for authentication. If None, uses the
            AMS_USERNAME environment variable. Defaults to None.
        password (Optional[str]): The password for authentication. If None, uses the
            AMS_PASSWORD environment variable. Defaults to None.
        option (Optional[UserOption]): Configuration options for the update, including
            interactive_mode (for status messages and confirmation), cache (for API response
            caching), and columns (ignored for this function). If None, uses default
            UserOption. Defaults to None.
        client (Optional[AMSClient]): A pre-authenticated AMSClient instance. If None,
            a new client is created using the provided url, username, and password.
            Defaults to None.

    Returns:
        DataFrame: A pandas DataFrame containing failed updates with columns:
            - 'user_id': The user ID (if matched) or None.
            - 'user_key': The user identifier value that failed to update.
            - 'reason': The reason for the failure (e.g., 'User not found', 'API request failed').
            Returns an empty DataFrame if all updates succeed.

    Raises:
        AMSError: If `mapping_df` is invalid (e.g., missing `user_key` column), `user_key` is
            invalid, no users are found, authentication fails, or the API request fails.
        ValueError: If `mapping_df` is empty or contains invalid data.

    Examples:
        >>> import pandas as pd
        >>> from teamworksams import edit_user
        >>> from teamworksams import UserOption
        >>> mapping_df = pd.DataFrame({
        ...     "username": ["john.doe", "jane.smith"],
        ...     "first_name": ["John", "Jane"],
        ...     "email": ["john.doe@new.com", "jane.smith@new.com"]
        ... })
        >>> failed_df = edit_user(
        ...     mapping_df = mapping_df,
        ...     user_key = "username",
        ...     url = "https://example.smartabase.com/site",
        ...     username = "user",
        ...     password = "pass",
        ...     option = UserOption(interactive_mode = True)
        ... )
        ℹ Retrieving user data for 2 users using username...
        ℹ Updating 2 users...
        ✔ Successfully updated 2 users.
        >>> print(failed_df)
        Empty DataFrame
        Columns: [user_id, user_key, reason]
    """
    option = option or UserOption(interactive_mode=True)
    client = client or get_client(url, username, password, cache=option.cache, interactive_mode=option.interactive_mode)

    _validate_user_data_for_edit(mapping_df, user_key)

    user_values = mapping_df[user_key].unique().tolist()
    if option.interactive_mode:
        print(f"ℹ Retrieving user data for {len(user_values)} users using {user_key}...")

    try:
        user_df = _fetch_all_user_data(
            url=url,
            username=username,
            password=password,
            user_ids=None,  # Fetch all users
            option=option,
            client=client
        )
    except AMSError as e:
        if option.interactive_mode:
            print(f"⚠️ Failed to retrieve user data: {str(e)}")
        return DataFrame({
            "user_id": [None] * len(mapping_df),
            "user_key": mapping_df[user_key],
            "reason": f"Failed to retrieve user data: {str(e)}"
        })

    if user_df.empty:
        if option.interactive_mode:
            print(f"⚠️ No users found")
        return DataFrame({
            "user_id": [None] * len(mapping_df),
            "user_key": mapping_df[user_key],
            "reason": "No users found"
        })

    mapping_df, failed_matches = _match_user_ids(
        mapping_df,
        user_df,
        user_key,
        interactive_mode=option.interactive_mode
    )
    failed_df = failed_matches.rename(columns={"user_key": "user_key"})

    if mapping_df.empty:
        if option.interactive_mode:
            print(f"⚠️ No users matched for update")
        return failed_df

    df = _clean_user_data_for_save(mapping_df, preserve_columns=[user_key, "user_id"])

    column_mapping, update_columns = _get_update_columns(df, user_key)

    if not update_columns:
        if option.interactive_mode:
            print(f"⚠️ No updatable columns provided in mapping_df")
        return failed_df

    if option.interactive_mode:
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

    failed_operations_with_user_key = []
    for op in failed_operations:
        user_key_val = op["user_key"]
        user_id_row = mapping_df[mapping_df[user_key] == user_key_val]
        user_id = user_id_row["user_id"].iloc[0] if not user_id_row.empty else None
        failed_operations_with_user_key.append({
            "user_id": user_id,
            "user_key": user_key_val,
            "reason": op["reason"]
        })

    failed_df = pd.concat([failed_df, DataFrame(failed_operations_with_user_key)], ignore_index=True)
    return _report_user_results(len(df), failed_operations_with_user_key, user_ids, "updated", interactive_mode=option.interactive_mode)



def create_user(
    user_df: DataFrame,
    url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    option: Optional[UserOption] = None,
    client: Optional[AMSClient] = None
) -> DataFrame:
    """Create new users in an AMS instance.

    Creates new user accounts using the AMS API’s `/api/v2/person/save` endpoint, setting
    the user ID to '-1' to indicate new users. The function processes a DataFrame with
    required fields (e.g., 'first_name', 'last_name', 'username', 'email', 'dob',
    'password', 'active') and optional fields (e.g., 'uuid', 'sex'), validates the data,
    and applies the creations. Returns a DataFrame of failed creations with reasons.
    Supports interactive feedback and caching.

    Args:
        user_df (DataFrame): A pandas DataFrame containing user data for creation. Required
            columns: 'first_name', 'last_name', 'username', 'email', 'dob', 'password',
            'active'. Optional columns: 'uuid', 'known_as', 'middle_names', 'language',
            'sidebar_width', 'sex'. Must not be empty.
        url (str): The AMS instance URL (e.g., 'https://example.smartabase.com/site').
        username (Optional[str]): The username for authentication. If None, uses the
            AMS_USERNAME environment variable. Defaults to None.
        password (Optional[str]): The password for authentication. If None, uses the
            AMS_PASSWORD environment variable. Defaults to None.
        option (Optional[UserOption]): Configuration options for the creation, including
            interactive_mode (for status messages), cache (for API response caching), and
            columns (ignored for this function). If None, uses default UserOption.
            Defaults to None.
        client (Optional[AMSClient]): A pre-authenticated AMSClient instance. If None,
            a new client is created using the provided url, username, and password.
            Defaults to None.

    Returns:
        DataFrame: A pandas DataFrame containing failed creations with columns:
            - 'user_key': The 'username' value that failed to create.
            - 'reason': The reason for the failure (e.g., 'Invalid data', 'API request failed').
            Returns an empty DataFrame if all creations succeed.

    Raises:
        AMSError: If `user_df` is invalid (e.g., missing required columns), authentication
            fails, or the API request fails.
        ValueError: If `user_df` is empty or contains invalid data.

    Examples:
        >>> import pandas as pd
        >>> from teamworksams import create_user
        >>> from teamworksams import UserOption
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
        >>> print(failed_df)
        Empty DataFrame
        Columns: [user_key, reason]
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