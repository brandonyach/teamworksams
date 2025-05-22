import pandas as pd
from pandas import DataFrame
from datetime import datetime
from typing import Optional, Tuple
from .utils import AMSClient, AMSError, get_client
from .export_filter import EventFilter, SyncEventFilter, ProfileFilter
from .export_option import EventOption, SyncEventOption, ProfileOption
from .export_clean import _reorder_columns, _transform_event_data, _transform_profile_data, _sort_event_data, _sort_profile_data
from .export_process import _process_events_to_rows, _process_profile_rows, _append_user_data
from .export_validate import _validate_event_filter, _validate_dates
from .export_build import _build_event_payload, _build_sync_event_payload, _build_profile_payload
from .export_print import _print_event_status, _print_profile_status
from .user_fetch import _fetch_user_ids


def get_event_data(
    form: str,
    start_date: str,
    end_date: str,
    url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    filter: Optional[EventFilter] = None,
    option: Optional[EventOption] = None,
    client: Optional[AMSClient] = None
) -> DataFrame:
    """Retrieve event data from an AMS Event Form within a date range.

    Fetches event data from the specified AMS Event Form for a given date range, optionally
    applying filters to narrow results by user attributes (e.g., username, group) or data fields
    (e.g., specific field values). The function processes the API response into a pandas DataFrame
    with columns such as event IDs, user IDs, and form fields. Supports downloading attachments
    if enabled in the EventOption, and provides interactive feedback on the number of events
    retrieved if interactive mode is active.

    Args:
        form (str): The name of the AMS Event Form to retrieve data from. Must be a non-empty
            string and correspond to a valid event form.
        start_date (str): The start date for the event range in 'DD/MM/YYYY' format.
        end_date (str): The end date for the event range in 'DD/MM/YYYY' format.
        url (str): The AMS instance URL (e.g., 'https://example.smartabase.com/site').
        username (Optional[str]): The username for authentication. If None, uses the
            AMS_USERNAME environment variable. Defaults to None.
        password (Optional[str]): The password for authentication. If None, uses the
            AMS_PASSWORD environment variable. Defaults to None.
        filter (Optional[EventFilter]): An EventFilter object to narrow results by user
            attributes (e.g., 'username', 'group') or data fields (e.g., specific field values).
            If None, no filtering is applied. Defaults to None.
        option (Optional[EventOption]): Configuration options for the retrieval, including
            interactive_mode (for status messages), download_attachment (to fetch attachments),
            clean_names (to standardize column names), guess_col_type (to infer data types),
            convert_dates (to parse dates), cache (for API response caching), and
            attachment_directory (for saving attachments). If None, uses default EventOption.
            Defaults to None.
        client (Optional[AMSClient]): A pre-authenticated AMSClient instance. If None,
            a new client is created using the provided url, username, and password.
            Defaults to None.

    Returns:
        DataFrame: A pandas DataFrame containing event data with columns such as 'event_id',
            'user_id', 'start_date', 'form', and form-specific fields. Returns an empty DataFrame
            with columns ['user_id', 'event_id', 'form', 'start_date'] if no events are found
            or no users match the filter.

    Raises:
        AMSError: If the form is empty, no events are found, no users match the filter,
            authentication fails, or the API request returns an error.
        ValueError: If start_date or end_date is not in 'DD/MM/YYYY' format, or if filter
            parameters are invalid (e.g., invalid user_key or data_condition).

    Examples:
        >>> import pandas as pd
        >>> from teamworksams import get_event_data
        >>> from teamworksams import EventFilter
        >>> from teamworksams import EventOption
        >>> df = get_event_data(
        ...     form = "Training Log",
        ...     start_date = "01/01/2025",
        ...     end_date = "31/01/2025",
        ...     url = "https://example.smartabase.com/site",
        ...     username = "user",
        ...     password = "pass",
        ...     filter = EventFilter(user_key = "group", user_value = "Example Group"),
        ...     option = EventOption(interactive_mode = True, clean_names = True)
        ... )
        ℹ Requesting event data for 'Training Log' between 01/01/2025 and 31/01/2025
        ℹ Processing 10 events...
        >>> print(df.head())
           about  user_id  event_id  form         start_date  duration  intensity
        0  John Doe    12345    67890  Training Log  01/01/2025        60       High
        1  Jane Smith  12346    67891  Training Log  02/01/2025        45     Medium
    """
    option = option or EventOption()
    client = client or get_client(url, username, password, cache=option.cache, interactive_mode=option.interactive_mode)
    
    if not form:
        AMSError("Form name is required", function="get_event_data")
    
    start, end = _validate_dates(start_date, end_date)
    start_date_api = start.strftime("%d/%m/%Y")
    end_date_api = end.strftime("%d/%m/%Y")
    
    if filter:
        _validate_event_filter(filter.user_key, filter.user_value, filter.data_key, filter.data_value, filter.data_condition, filter.events_per_user)
    
    user_ids, user_df = _fetch_user_ids(client, filter, option.cache)
    if not user_ids:
        if option.interactive_mode:
            print("⚠️ No users found to fetch events for - Function: get_event_data")
        return DataFrame(columns=["user_id", "event_id", "form", "start_date"])
    
    endpoint, payload = _build_event_payload(form, start_date_api, end_date_api, user_ids, filter, filter.events_per_user if filter else None)
    
    if option.interactive_mode:
        print(f"ℹ Requesting event data for '{form}' between {start_date} and {end_date}")
    
    data = client._fetch(endpoint, method="POST", payload=payload, cache=option.cache, api_version="v1")
    if not data or "events" not in data or not data["events"]:
        AMSError(f"No events found for form '{form}' in the date range {start_date} to {end_date}", 
                           function="get_event_data", endpoint=endpoint)
    
    if option.interactive_mode:
        print(f"ℹ Processing {len(data['events'])} events...")
    rows = _process_events_to_rows(
        data["events"], 
        start, 
        end, 
        filter, 
        download_attachment=option.download_attachment, 
        client=client, 
        option=option
    )
    if not rows:
        AMSError(f"No event data found for form '{form}' between {start_date} and {end_date}", 
                           function="get_event_data", endpoint=endpoint)
    event_df = pd.DataFrame(rows)
    
    event_df = _transform_event_data(event_df, option.clean_names, option.guess_col_type, option.convert_dates)
    event_df = _append_user_data(event_df, user_df, option.include_missing_users)
    event_df = _reorder_columns(['about', 'user_id'], event_df, ['end_date', 'start_time', 'end_time', 'entered_by_user_id'])
    event_df = _sort_event_data(event_df)
    
    _print_event_status(event_df, form, option)
    
    return event_df
    
    

def sync_event_data(
    form: str,
    last_synchronisation_time: int,
    url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    filter: Optional[SyncEventFilter] = None,
    option: Optional[SyncEventOption] = None,
    client: Optional[AMSClient] = None
) -> Tuple[DataFrame, int]:
    """Retrieve event data from an AMS event form modified since the last synchronization time.

    Fetches event data from the specified AMS Event Form using the `synchronise` API endpoint,
    returning only events inserted or updated since the provided `last_synchronisation_time`
    (in milliseconds since 1970-01-01). The function processes the API response into a pandas
    DataFrame and returns a tuple containing the DataFrame and the new synchronization time
    for subsequent calls. Supports filtering by user attributes and customization via
    SyncEventOption, such as including user metadata or UUIDs. Provides interactive feedback
    if enabled.

    Args:
        form (str): The name of the AMS Event Form to retrieve data from. Must be a non-empty
            string and correspond to a valid event form.
        last_synchronisation_time (int): The last synchronization time in milliseconds since
            1970-01-01. Must be non-negative.
        url (str): The AMS instance URL (e.g., 'https://example.smartabase.com/site').
        username (Optional[str]): The username for authentication. If None, uses the
            AMS_USERNAME environment variable. Defaults to None.
        password (Optional[str]): The password for authentication. If None, uses the
            AMS_PASSWORD environment variable. Defaults to None.
        filter (Optional[SyncEventFilter]): A SyncEventFilter object to narrow results by
            user attributes (e.g., 'username', 'group'). If None, no filtering is applied.
            Defaults to None.
        option (Optional[SyncEventOption]): Configuration options for the retrieval,
            including interactive_mode (for status messages), include_user_data (to add user
            metadata), include_uuid (to add UUIDs), guess_col_type (to infer data types),
            cache (for API response caching), and include_missing_users (to include users
            without events). If None, uses default SyncEventOption. Defaults to None.
        client (Optional[AMSClient]): A pre-authenticated AMSClient instance. If None,
            a new client is created using the provided url, username, and password.
            Defaults to None.

    Returns:
        Tuple[DataFrame, int]: A tuple containing:
            - A pandas DataFrame with event data (columns: 'event_id', 'user_id', 'start_date',
              'form', etc.). Returns an empty DataFrame with columns ['user_id', 'event_id',
              'form', 'start_date'] if no new events are found or no users match the filter.
            - An integer representing the new `lastSynchronisationTimeOnServer` in milliseconds,
              for use in subsequent synchronization calls.

    Raises:
        AMSError: If the form is empty, no users match the filter, authentication fails,
            or the API request returns an error.
        ValueError: If last_synchronisation_time is negative or not an integer.

    Examples:
        >>> from teamworksams import sync_event_data
        >>> from teamworksams import SyncEventFilter
        >>> from teamworksams import SyncEventOption
        >>> df, new_sync_time = sync_event_data(
        ...     form = "Training Log",
        ...     last_synchronisation_time = 1677654321000,
        ...     url = "https://example.smartabase.com/site",
        ...     username = "user",
        ...     password = "pass",
        ...     filter = SyncEventFilter(user_key = "group", user_value = "Example Group"),
        ...     option = SyncEventOption(interactive_mode = True, include_user_data = True)
        ... )
        ℹ Requesting event data for form 'Training Log' since last synchronisation time 2023-03-01 12:25:21
        ✔ Retrieved 5 event records for form 'Training Log' since last synchronisation time 2023-03-01 12:25:21
        >>> print(df.head())
           about  user_id  event_id  form         start_date  duration  intensity
        0  John Doe    12345    67890  Training Log  01/03/2025        60       High
        >>> print(new_sync_time)
        1677654400000
    """
    option = option or SyncEventOption()
    client = client or get_client(url, username, password, cache=option.cache, interactive_mode=option.interactive_mode)
    
    if not form:
        AMSError("Form name is required", function="sync_event")
    
    if not isinstance(last_synchronisation_time, int) or last_synchronisation_time < 0:
        raise ValueError("last_synchronisation_time must be a non-negative integer (milliseconds since 1970-01-01).")
    
    user_ids, user_df = _fetch_user_ids(client, filter, option.cache)
    if not user_ids:
        if option.interactive_mode:
            print("⚠️ No users found to fetch events for - Function: symc_event_data")
        return DataFrame(columns=["user_id", "event_id", "form", "start_date"])
    
    payload = _build_sync_event_payload(form, last_synchronisation_time, user_ids)
    
    if option.interactive_mode:
        print(f"ℹ Requesting event data for form '{form}' since last synchronisation time {datetime.fromtimestamp((last_synchronisation_time / 1000)).strftime('%Y-%m-%d %H:%M:%S')}")
    
    data = client._fetch("synchronise", method="POST", payload=payload, cache=option.cache, api_version="v1")
    
    export_data = data.get("export", {}) if data else {}
    events = export_data.get("events", [])
    new_sync_time = data.get("lastSynchronisationTimeOnServer", last_synchronisation_time) if data else last_synchronisation_time
    deleted_event_ids = data.get("idsOfDeletedEvents", []) if data else []
    
    rows = _process_events_to_rows(
        events,
        start=datetime(1970, 1, 1),  
        end=datetime.now(),          
        filter=None,                 
        download_attachment=False,  
        client=client,
        option=option
    )
    
    event_df = pd.DataFrame(rows) if rows else pd.DataFrame()
    
    if not event_df.empty:
        event_df = _transform_event_data(event_df, clean_names=False, guess_col_type=option.guess_col_type, convert_dates=False)
        
        if option.include_user_data:
            event_df = _append_user_data(event_df, user_df, option.include_missing_users)
        
        if option.include_uuid and user_df is not None:
            user_df = user_df.rename(columns={"userId": "user_id", "uuid": "uuid"})
            event_df = event_df.merge(user_df[["user_id", "uuid"]], on="user_id", how="left")
        
        front_cols = ['about', 'user_id'] if option.include_user_data else ['user_id']
        if option.include_uuid:
            front_cols.append('uuid')
        event_df = _reorder_columns(front_cols, event_df, ['end_date', 'start_time', 'end_time', 'entered_by_user_id'])
        
        event_df = _sort_event_data(event_df)
    
    event_df.attrs['deleted_event_ids'] = deleted_event_ids
    
    if option.interactive_mode:
        if len(events) == 0:
            print(f"ℹ No new data found for form '{form}' since last synchronization time {datetime.fromtimestamp((last_synchronisation_time / 1000)).strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"✔ Retrieved {len(event_df)} event records for form '{form}' since last synchronisation time {datetime.fromtimestamp((last_synchronisation_time / 1000)).strftime('%Y-%m-%d %H:%M:%S')}")
    
    return event_df, new_sync_time



def get_profile_data(
    form: str,
    url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    filter: Optional[ProfileFilter] = None,
    option: Optional[ProfileOption] = None,
    client: Optional[AMSClient] = None
) -> DataFrame:
    """Retrieve profile data from an AMS Profile Form.

    Fetches profile data from the specified AMS Profile Form, optionally applying filters to
    narrow results by user attributes (e.g., username, group). The function processes the API
    response into a pandas DataFrame with columns such as profile IDs, user IDs, and form-specific
    fields. Provides interactive feedback on the number of profiles retrieved if interactive
    mode is enabled.

    Args:
        form (str): The name of the AMS Profile Form to retrieve data from. Must be a non-empty
            string and correspond to a valid profile form.
        url (str): The AMS instance URL (e.g., 'https://example.smartabase.com/site').
        username (Optional[str]): The username for authentication. If None, uses the
            AMS_USERNAME environment variable. Defaults to None.
        password (Optional[str]): The password for authentication. If None, uses the
            AMS_PASSWORD environment variable. Defaults to None.
        filter (Optional[ProfileFilter]): A ProfileFilter object to narrow results by user
            attributes (e.g., 'username', 'group'). If None, no filtering is applied.
            Defaults to None.
        option (Optional[ProfileOption]): Configuration options for the retrieval,
            including interactive_mode (for status messages), clean_names (to standardize
            column names), guess_col_type (to infer data types), cache (for API response
            caching), and include_missing_users (to include users without profiles). If None,
            uses default ProfileOption. Defaults to None.
        client (Optional[AMSClient]): A pre-authenticated AMSClient instance. If None,
            a new client is created using the provided url, username, and password.
            Defaults to None.

    Returns:
        DataFrame: A pandas DataFrame containing profile data with columns such as 'profile_id',
            'user_id', 'form', and form-specific fields. Returns an empty DataFrame with columns
            ['user_id', 'profile_id', 'form'] if no profiles are found or no users match the filter.

    Raises:
        AMSError: If the form is empty, no profiles are found, no users match the filter,
            authentication fails, or the API request returns an error.
        ValueError: If filter parameters are invalid (e.g., invalid user_key).

    Examples:
        >>> import pandas as pd
        >>> from teamworksams import get_profile_data
        >>> from teamworksams import ProfileFilter
        >>> from teamworksams import ProfileOption
        >>> df = get_profile_data(
        ...     form = "Athlete Profile",
        ...     url = "https://example.smartabase.com/site",
        ...     username = "user",
        ...     password = "pass",
        ...     filter = ProfileFilter(user_key = "group", user_value = "Example Group"),
        ...     option = ProfileOption(interactive_mode = True, clean_names = True)
        ... )
        ℹ Requesting profile data for form 'Athlete Profile'
        ℹ Processing 5 profiles...
        >>> print(df.head())
           about  user_id  profile_id  form              ID
        0  John Doe    12345      54321  Athlete Profile    2435t4yrgfddeqwret12
        1  Jane Smith  12346      54322  Athlete Profile    2435t4yrgfddeqwret6
    """
    option = option or ProfileOption()
    client = client or get_client(url, username, password, cache=option.cache, interactive_mode=option.interactive_mode)
    
    if not form:
        AMSError("Form name is required", function="get_profile_data")
    
    user_ids, user_df = _fetch_user_ids(client, filter, option.cache)
    if not user_ids:
        if option.interactive_mode:
            print("⚠️ No users found to fetch profiles for - Function: get_profile_data")
        return DataFrame(columns=["user_id", "profile_id", "form"])
    
    payload = _build_profile_payload(form, user_ids)
    if option.interactive_mode:
        print(f"ℹ Requesting profile data for form '{form}'")
    
    data = client._fetch("profilesearch", method="POST", payload=payload, cache=option.cache, api_version="v1")
    if not data or "profiles" not in data or not data["profiles"]:
        AMSError(f"No profiles found for form '{form}'", function="get_profile_data", endpoint="profilesearch")
    
    if option.interactive_mode:
        print(f"ℹ Processing {len(data['profiles'])} profiles...")
    rows = _process_profile_rows(data["profiles"], filter, option)
    if not rows:
       AMSError(f"No profile data found for form '{form}'", function="get_profile_data", endpoint="profilesearch")
    profile_df = pd.DataFrame(rows)
    
    profile_df = _transform_profile_data(profile_df, option.clean_names, option.guess_col_type)
    profile_df = _append_user_data(profile_df, user_df, option.include_missing_users)
    profile_df = _reorder_columns(['about', 'user_id'], profile_df, ['entered_by_user_id'])
    profile_df = _sort_profile_data(profile_df)
    
    _print_profile_status(profile_df, form, option)
    
    return profile_df