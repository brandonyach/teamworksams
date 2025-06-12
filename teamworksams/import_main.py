from typing import Optional
from pandas import DataFrame
from .utils import AMSClient, get_client, AMSError
from .import_option import InsertEventOption, UpdateEventOption, UpsertEventOption, UpsertProfileOption
from .import_build import _build_import_payload, _build_profile_payload
from .import_clean import _clean_import_df, _clean_profile_df
from .import_fetch import _fetch_import_payloads
from .import_print import _print_import_status
from .import_process import _map_id_col_to_user_id
from .import_validate import _validate_import_df


def insert_event_data(
    df: DataFrame,
    form: str,
    url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    option: Optional[InsertEventOption] = None,
    client: Optional[AMSClient] = None
) -> None:
    
    """Insert new event records into an AMS Event Form.

    Processes a :class:`pandas.DataFrame` containing event data, maps user identifiers to user IDs,
    validates the data, constructs an API payload, and sends it to the AMS API to insert
    new events into the specified Event Form. Supports table fields via the InsertEventOption,
    which allows configuration of user identifier mapping, caching, and interactive feedback.
    Provides status updates if interactive mode is enabled, reporting the number of events
    inserted. See :ref:`vignettes/importing_data` for import workflows.

    Args:
        df (:class:`pandas.DataFrame`): A pandas DataFrame containing the event data to insert. Columns
            represent field names (including 'start_date', 'user_id' or another identifier
            specified by `option.id_col`), and rows contain values. Must not be empty.
        form (str): The name of the AMS Event Form to insert data into. Must be a non-empty
            string and correspond to a valid event form.
        url (str): The AMS instance URL (e.g., 'https://example.smartabase.com/site').
        username (Optional[str]): The username for authentication. If None, uses the
            AMS_USERNAME environment variable. Defaults to None.
        password (Optional[str]): The password for authentication. If None, uses the
            AMS_PASSWORD environment variable. Defaults to None.
        option (:class:`InsertEventOption`, optional): Configuration options for the insertion,
            including id_col (column for user identifiers, e.g., 'user_id', 'username'),
            interactive_mode (for status messages), cache (for API response caching), and
            table_fields (list of table field names). If None, uses default
            InsertEventOption. Defaults to None.
        client (:class:`AMSClient`, optional): A pre-authenticated AMSClient instance. If None,
            a new client is created using the provided url, username, and password.
            Defaults to None.

    Returns:
        None: The function does not return a value but inserts events into the AMS database
            and prints status messages if interactive_mode is enabled.

    Raises:
        :class:`AMSError`: If the form is empty, not an event form, authentication fails, the DataFrame
            is invalid (e.g., empty, missing required fields like 'start_date'), the payload
            cannot be built, or the API request fails.
        :class:`ValueError`: If `option.id_col` is invalid or `table_fields` contains field names not
            present in the DataFrame.

    Examples:
        >>> import pandas as pd
        >>> from teamworksams import insert_event_data, InsertEventOption
        >>> df = pd.DataFrame({
        ...     "username": ["john.doe", "jane.smith"],
        ...     "start_date": ["01/01/2025", "01/01/2025"],
        ...     "duration": [60, 45],
        ...     "intensity": ["High", "Medium"]
        ... })
        >>> insert_event_data(
        ...     df = df,
        ...     form = "Training Log",
        ...     url = "https://example.smartabase.com/site",
        ...     username = "user",
        ...     password = "pass",
        ...     option = InsertEventOption(id_col = "username", interactive_mode = True)
        ... )
        ℹ Inserting 2 events for 'Training Log'
        ✔ Processed 2 events for 'Training Log'
        ℹ Form: TrainingLog
        ℹ Result: Success
        ℹ Records inserted: 2
        ℹ Records attempted: 2
    """
    option = option or InsertEventOption()
    client = client or get_client(url, username, password, cache=option.cache, interactive_mode=option.interactive_mode)
    
    df_clean = _clean_import_df(df)
    
    df_clean = _map_id_col_to_user_id(df_clean, option.id_col, client)
    
    _validate_import_df(df_clean, form, overwrite_existing=False, table_fields=option.table_fields)
    
    entered_by_user_id = client.login_data["user"]["id"]
    
    payloads = _build_import_payload(
        df_clean,
        form,
        option.table_fields,
        entered_by_user_id,
        overwrite_existing=False
    )
    
    # event_count = len(payloads[0]["events"])
    # event_count = sum(len(p["events"]) for p in payloads)
    event_count = len(payloads) 
    
    if option.interactive_mode:
        print(f"ℹ Inserting {event_count} events for '{form}'")
    
    results = _fetch_import_payloads(client, payloads, "insert", option.interactive_mode, option.cache)
    
    if option.interactive_mode:
        print(f"✔ Processed {event_count} events for '{form}'")
    
    _print_import_status(results, form, "inserted", option.interactive_mode)
    
    return df_clean



def update_event_data(
    df: DataFrame,
    form: str,
    url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    option: Optional[UpdateEventOption] = None,
    client: Optional[AMSClient] = None
) -> None:
    
    """Update existing event records in an AMS Event Form.

    Processes a :class:`pandas.DataFrame` containing data with an 'event_id' column, maps user
    identifiers to user IDs, validates the data, constructs an API payload, and sends it to
    the AMS API to update existing events in the specified Event Form. Supports table fields
    via the UpdateEventOption, which allows configuration of user identifier mapping, caching,
    and interactive feedback. In interactive mode, prompts for confirmation before updating
    and provides status updates. See :ref:`vignettes/importing_data` for update workflows.

    Args:
        df (:class:`pandas.DataFrame`): A pandas DataFrame containing the event data to update. Must include
            an 'event_id' column with valid integer IDs of existing events, and other columns
            for field names with values to update. Must not be empty.
        form (str): The name of the AMS Event Form to update data in. Must be a non-empty
            string and correspond to a valid event form.
        url (str): The AMS instance URL (e.g., 'https://example.smartabase.com/site').
        username (Optional[str]): The username for authentication. If None, uses the
            AMS_USERNAME environment variable. Defaults to None.
        password (Optional[str]): The password for authentication. If None, uses the
            AMS_PASSWORD environment variable. Defaults to None.
        option (:class:`UpdateEventOption`, optional): Configuration options for the update,
            including id_col (column for user identifiers, e.g., 'user_id', 'username'),
            interactive_mode (for status messages and confirmation), cache (for API response
            caching), and table_fields (list of table field names). If None, uses default
            UpdateEventOption. Defaults to None.
        client (:class:`AMSClient`, optional): A pre-authenticated AMSClient instance. If None,
            a new client is created using the provided url, username, and password.
            Defaults to None.

    Returns:
        None: The function does not return a value but updates events in the AMS database
            and prints status messages if interactive_mode is enabled.

    Raises:
        :class:`AMSError`: If the form is empty, not an event form, authentication fails, the 
            DataFrame is invalid (e.g., empty, missing 'event_id', or invalid IDs), the payload 
            cannot be built, the API request fails, or the user cancels the operation in 
            interactive mode.
        :class:`ValueError`: If `option.id_col` is invalid or `table_fields` contains field names 
            not present in the DataFrame.

    Examples:
        >>> import pandas as pd
        >>> from teamworksams import update_event_data, UpdateEventOption
        >>> df = pd.DataFrame({
        ...     "event_id": [67890, 67891],
        ...     "username": ["john.doe", "jane.smith"],
        ...     "duration": [65, 50],
        ...     "intensity": ["High Updated", "Medium Updated"]
        ... })
        >>> update_event_data(
        ...     df = df,
        ...     form = "Training Log",
        ...     url = "https://example.smartabase.com/site",
        ...     username = "user",
        ...     password = "pass",
        ...     option = UpdateEventOption(id_col = "username", interactive_mode = True)
        ... )
        ℹ Updating 2 events for 'Training Log'
        Are you sure you want to update 2 existing events in 'Training Log'? (y/n): y
        ✔ Processed 2 events for 'Trainin gLog'
        ℹ Form: Training Log
        ℹ Result: Success
        ℹ Records updated: 2
        ℹ Records attempted: 2
    """
    
    option = option or UpdateEventOption()
    
    client = client or get_client(url, username, password, cache=option.cache, interactive_mode=option.interactive_mode)
    
    df_clean = _clean_import_df(df)
    
    df_clean = _map_id_col_to_user_id(df_clean, option.id_col, client)
    
    _validate_import_df(df_clean, form, overwrite_existing=True, table_fields=option.table_fields)
    
    entered_by_user_id = client.login_data["user"]["id"]
    
    payloads = _build_import_payload(
        df_clean,
        form,
        option.table_fields,
        entered_by_user_id,
        overwrite_existing=True
    )
    
    # event_count = sum(len(p["events"]) for p in payloads)
    event_count = len(payloads) 
    
    if option.interactive_mode:
        print(f"ℹ Updating {event_count} events for '{form}'")
        if option.require_confirmation:
            confirm = input(f"Are you sure you want to update {event_count} existing events in '{form}'? (y/n): ").strip().lower()
            if confirm not in ['y', 'yes']:
                raise AMSError("Update operation cancelled by user.")
    
    results = _fetch_import_payloads(client, payloads, "update", option.interactive_mode, option.cache)
    
    if option.interactive_mode:
        print(f"✔ Processed {event_count} events for '{form}'")
    
    _print_import_status(results, form, "updated", option.interactive_mode)
    
    return df_clean



def upsert_event_data(
    df: DataFrame,
    form: str,
    url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    option: Optional[UpsertEventOption] = None,
    client: Optional[AMSClient] = None
) -> None:
    
    """Insert and update event records in an AMS Event Form.

    Performs an upsert operation on a :class:`pandas.DataFrame`, splitting it into records 
    with an 'event_id' (for updates) and without (for inserts). Processes each group separately,
    mapping user identifiers to user IDs, validating the data, constructing API payloads,
    and sending them to the AMS API to update existing events or insert new ones in the
    specified Event Form. Supports table fields via the UpsertEventOption, which allows
    configuration of user identifier mapping, caching, and interactive feedback. In
    interactive mode, prompts for confirmation before updating and provides status updates.
    See :ref:`vignettes/importing_data` for upsert workflows.

    Args:
        df (:class:`pandas.DataFrame`): A pandas DataFrame containing the event data to upsert. 
            Records with an 'event_id' column are updated; those without are inserted. Columns 
            represent field names (including 'start_date', 'user_id' or another identifier 
            specified by `option.id_col`), and rows contain values. Must not be empty.
        form (str): The name of the AMS Event Form to upsert data into. Must be a non-empty
            string and correspond to a valid event form.
        url (str): The AMS instance URL (e.g., 'https://example.smartabase.com/site').
        username (Optional[str]): The username for authentication. If None, uses the
            AMS_USERNAME environment variable. Defaults to None.
        password (Optional[str]): The password for authentication. If None, uses the
            AMS_PASSWORD environment variable. Defaults to None.
        option (:class:`UpsertEventOption`, optional): Configuration options for the upsert,
            including id_col (column for user identifiers, e.g., 'user_id', 'username'),
            interactive_mode (for status messages and confirmation), cache (for API response
            caching), and table_fields (list of table field names). If None, uses default
            UpsertEventOption. Defaults to None.
        client (:class:`AMSClient`, optional): A pre-authenticated AMSClient instance. If None,
            a new client is created using the provided url, username, and password.
            Defaults to None.

    Returns:
        None: The function does not return a value but updates and inserts events in the AMS
            database and prints status messages if interactive_mode is enabled.

    Raises:
        AMSError: If the form is empty, not an event form, authentication fails, the DataFrame
            is invalid (e.g., empty, missing required fields for inserts or 'event_id' for
            updates), the payload cannot be built, the API request fails, or the user cancels
            the update operation in interactive mode.
        ValueError: If `option.id_col` is invalid or `table_fields` contains field names not
            present in the DataFrame.

    Examples:
        >>> import pandas as pd
        >>> from teamworksams import upsert_event_data, UpsertEventOption
        >>> df = pd.DataFrame({
        ...     "event_id": [67890, None],
        ...     "username": ["john.doe", "jane.smith"],
        ...     "start_date": ["01/01/2025", "02/01/2025"],
        ...     "duration": [65, 45],
        ...     "intensity": ["High Updated", "Medium"]
        ... })
        >>> upsert_event_data(
        ...     df = df,
        ...     form = "Training Log",
        ...     url = "https://example.smartabase.com/site",
        ...     username = "user",
        ...     password = "pass",
        ...     option = UpsertEventOption(id_col = "username", interactive_mode = True)
        ... )
        ℹ Updating 1 existing events for 'Training Log'
        Are you sure you want to update 1 existing events in 'Training Log'? (y/n): y
        ℹ Inserting 1 new events for 'Training Log'
        ✔ Processed 2 events for 'Training Log'
        ℹ Form: Training Log
        ℹ Result: Success
        ℹ Records upserted: 2
        ℹ Records attempted: 2
    """
    
    option = option or UpsertEventOption()
    
    client = client or get_client(url, username, password, cache=option.cache, interactive_mode=option.interactive_mode)
    
    df_clean = _clean_import_df(df)
    
    df_clean = _map_id_col_to_user_id(df_clean, option.id_col, client)
    
    _validate_import_df(df_clean, form, overwrite_existing=True, table_fields=option.table_fields)
    
    entered_by_user_id = client.login_data["user"]["id"]
    
    # Split DataFrame into updates (with event_id) and inserts (without event_id)
    updates_df = df_clean[df_clean["event_id"].notna()]
    
    inserts_df = df_clean[df_clean["event_id"].isna()]
    
    all_results = []
    
    if not updates_df.empty:
        update_payloads = _build_import_payload(
            updates_df,
            form,
            option.table_fields,
            entered_by_user_id,
            overwrite_existing=True
        )
        
        # update_count = len(update_payloads[0]["events"])
        # update_count = sum(len(p["events"]) for p in update_payloads)
        update_count = len(update_payloads) 
        
        if option.interactive_mode:
            print(f"ℹ Updating {update_count} existing events for '{form}'")
            if option.require_confirmation:
                confirm = input(f"Are you sure you want to update {update_count} existing events in '{form}'? (y/n): ").strip().lower()
                if confirm not in ['y', 'yes']:
                    raise AMSError("Update operation cancelled by user.")
            
        update_results = _fetch_import_payloads(client, update_payloads, "update", option.interactive_mode, option.cache)
        
        all_results.extend(update_results)
    
    # Process inserts
    if not inserts_df.empty:
        insert_payloads = _build_import_payload(
            inserts_df,
            form,
            option.table_fields,
            entered_by_user_id,
            overwrite_existing=False
        )
        
        # insert_count = len(insert_payloads[0]["events"])
        # insert_count = sum(len(p["events"]) for p in insert_payloads)
        insert_count = len(insert_payloads) 
        
        if option.interactive_mode:
            print(f"ℹ Inserting {insert_count} new events for '{form}'")
            
        insert_results = _fetch_import_payloads(client, insert_payloads, "insert", option.interactive_mode, option.cache)
        
        all_results.extend(insert_results)
    
    if option.interactive_mode:
        total_events = len(df_clean)
        print(f"✔ Processed {total_events} events for '{form}'")
    
    _print_import_status(all_results, form, "upserted", option.interactive_mode)
    
    return df_clean
    
    
    
def upsert_profile_data(
    df: DataFrame,
    form: str,
    url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    option: Optional[UpsertProfileOption] = None,
    client: Optional[AMSClient] = None
) -> None:
    """Upsert profile data in an AMS Profile Form.

    Processes a :class:`pandas.DataFrame` containing profile data, maps user identifiers to user IDs,
    validates the data, constructs an API payload, and sends it to the AMS API to update
    existing profile records or insert new ones in the specified Profile Form. Profile forms
    allow only one record per user. In interactive mode, prompts for confirmation before upserting 
    and provides status updates.

    Args:
        df (:class:`pandas.DataFrame`): A pandas DataFrame containing the profile data to upsert. 
            Columns represent field names, and rows contain values. Must include a user identifier
            column (specified by `option.id_col`, e.g., 'user_id', 'username'). Must not
            be empty.
        form (str): The name of the AMS Profile Form to upsert data into. Must be a non-empty
            string and correspond to a valid profile form.
        url (str): The AMS instance URL (e.g., 'https://example.smartabase.com/site').
        username (Optional[str]): The username for authentication. If None, uses the
            AMS_USERNAME environment variable. Defaults to None.
        password (Optional[str]): The password for authentication. If None, uses the
            AMS_PASSWORD environment variable. Defaults to None.
        option (:class:`UpsertEventOption`, optional): Configuration options for the upsert,
            including id_col (column for user identifiers, e.g., 'user_id', 'username'),
            interactive_mode (for status messages and confirmation), and cache (for API
            response caching). If None, uses default UpsertProfileOption. Defaults to None.
        client (:class:`AMSClient`, optional): A pre-authenticated AMSClient instance. If None,
            a new client is created using the provided url, username, and password.
            Defaults to None.

    Returns:
        None: The function does not return a value but updates and inserts profile records
            in the AMS database and prints status messages if interactive_mode is enabled.

    Raises:
        :class:`AMSError`: If the form is empty, not a profile form, authentication fails, the DataFrame
            is invalid (e.g., empty, missing required fields), the payload cannot be built,
            the API request fails, or the user cancels the operation in interactive mode.
        :class:`ValueError`: If `option.id_col` is invalid.

    Examples:
        >>> import pandas as pd
        >>> from teamworksams import upsert_profile_data, UpsertProfileOption
        >>> df = pd.DataFrame({
        ...     "username": ["john.doe", "jane.smith"],
        ...     "height_cm": [180, 165],
        ...     "weight_kg": [75, 60]
        ... })
        >>> upsert_profile_data(
        ...     df = df,
        ...     form = "Athlete Profile",
        ...     url = "https://example.smartabase.com/site",
        ...     username = "user",
        ...     password = "pass",
        ...     option = UpsertProfileOption(id_col = "username", interactive_mode = True)
        ... )
        ℹ Upserting 2 profile records for 'Athlete Profile'
        Are you sure you want to upsert 2 profile records in 'Athlete Profile'? (y/n): y
        ✔ Processed 2 profile records for 'Athlete Profile'
        ℹ Form: Athlete Profile
        ℹ Result: Success
        ℹ Records upserted: 2
        ℹ Records attempted: 2
    """
    option = option or UpsertProfileOption()
    client = client or get_client(url, username, password, cache=option.cache, interactive_mode=option.interactive_mode)
    
    df_clean = _clean_profile_df(df)
    
    df_clean = _map_id_col_to_user_id(df_clean, option.id_col, client)
    
    _validate_import_df(df_clean, form, overwrite_existing=False, table_fields=None)
    
    entered_by_user_id = client.login_data["user"]["id"]
    
    payload = _build_profile_payload(
        df_clean,
        form,
        entered_by_user_id
    )
    
    profile_count = len(payload)
    
    if option.interactive_mode:
        print(f"ℹ Upserting {profile_count} profile records for '{form}'")
        if option.require_confirmation:
            confirm = input(f"Are you sure you want to upsert {profile_count} profile records in '{form}'? (y/n): ").strip().lower()
            if confirm not in ['y', 'yes']:
                raise AMSError("Upsert operation cancelled by user.")
    
    results = _fetch_import_payloads(client, payload, "upsert", option.interactive_mode, option.cache, is_profile=True)
    
    if option.interactive_mode:
        print(f"✔ Processed {profile_count} profile records for '{form}'")
    
    _print_import_status(results, form, "upserted", option.interactive_mode)