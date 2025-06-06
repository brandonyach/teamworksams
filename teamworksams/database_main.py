from pandas import DataFrame
from typing import Optional, Dict, Union
from .database_fetch import _fetch_database_data, _fetch_database_save
from .database_process import _process_database_entries
from .database_clean import _clean_database_df
from .database_validate import _validate_database_df
from .database_build import _build_database_payload
from .database_option import GetDatabaseOption, InsertDatabaseOption, UpdateDatabaseOption
from .form_main import _fetch_form_id_and_type
from .form_option import FormOption
from .utils import AMSClient, AMSError, get_client
from .import_print import _print_import_status


def get_database(
    form_name: str,
    url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    limit: int = 10000,
    offset: int = 0,
    option: Optional[GetDatabaseOption] = None,
    client: Optional[AMSClient] = None
) -> DataFrame:
    """Retrieve database entries from an AMS database form.

    Fetches entries from a specified AMS database form using the provided credentials and
    configuration options. The function queries the AMS API, processes the response into a
    pandas DataFrame, and returns the data. Supports pagination through limit and offset
    parameters, and allows customization via a GetDatabaseOption object (e.g., for caching
    or interactive feedback).

    Args:
        form_name (str): The name of the AMS database form to retrieve entries from.
        url (str): The AMS instance URL (e.g., 'https://example.smartabase.com/site').
        username (Optional[str]): The username for authentication. If None, uses the
            AMS_USERNAME environment variable. Defaults to None.
        password (Optional[str]): The password for authentication. If None, uses the
            AMS_PASSWORD environment variable. Defaults to None.
        limit (int): The maximum number of entries to return per request. Must be positive.
            Defaults to 10000.
        offset (int): The starting index for pagination. Must be non-negative. Defaults to 0.
        option (Optional[GetDatabaseOption]): Configuration options such as caching,
            interactive mode, or raw output. If None, uses default GetDatabaseOption.
            Defaults to None.
        client (Optional[AMSClient]): A pre-authenticated AMSClient instance. If None,
            a new client is created using the provided url, username, and password.
            Defaults to None.

    Returns:
        DataFrame: A pandas DataFrame containing the database entries, with
            columns for entry IDs and field values, or a dictionary with the raw API response
            if raw_output is True in the option. If no entries are found, returns an empty
            DataFrame.

    Raises:
        AMSError: If the form_name is empty, the form is not a database form, authentication
            fails, or the API request returns an error.
        ValueError: If limit is not positive or offset is negative.

    Examples:
        >>> from teamworksams import get_database
        >>> df = get_database(
        ...     form_name = "Allergies",
        ...     url = "https://example.smartabase.com/site",
        ...     username = "user",
        ...     password = "pass",
        ...     limit = 100,
        ...     offset = 0
        ... )
        >>> print(df)
           id  Allergy    
        0  386197   Dairy  
        1  386198    Eggs  
        2  386199  Peanuts  
    """
    option = option or GetDatabaseOption()
    client = client or get_client(url, username, password, cache=option.cache, interactive_mode=option.interactive_mode)
    
    if not form_name:
        raise AMSError("Form name is required", function="get_database")
    
    if limit < 1:
        raise ValueError("Limit must be a positive integer.")
    if offset < 0:
        raise ValueError("Offset must be a non-negative integer.")
    
    form_option = FormOption(
        interactive_mode=False,
        cache=option.cache,
        raw_output=False,
        field_details=False,
        include_instructions=False
    )
    
    form_id, form_type = _fetch_form_id_and_type(form_name, url, username, password, form_option, client)
    
    if form_type != "database":
        raise AMSError(
            f"Form '{form_name}' is not a database form (type: {form_type})",
            function="get_database"
        )
    
    if option.interactive_mode:
        print(f"ℹ Fetching database entries for form '{form_name}' (ID: {form_id})...")
    
    response = _fetch_database_data(form_id, limit, offset, client, cache=option.cache)
    
    df = _process_database_entries(response, form_name, option)
    
    if isinstance(df, DataFrame) and option.interactive_mode:
        if df.empty:
            print(f"ℹ No database entries found for form '{form_name}' with limit {limit} and offset {offset}.")
        else:
            print(f"✔ Retrieved {len(df)} database entries for form '{form_name}'.")
    
    return df


def delete_database_entry(
    database_entry_id: int,
    url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    client: Optional[AMSClient] = None
) -> bool:
    """Delete a specific database entry from an AMS instance.

    Sends a request to the AMS API to delete the database entry with the specified ID.
    Requires valid authentication credentials and a valid entry ID. Returns True if the
    deletion is successful, or raises an exception if the operation fails.

    Args:
        database_entry_id (int): The ID of the database entry to delete. Must be a non-negative integer.
        url (str): The AMS instance URL (e.g., 'https://example.smartabase.com/site').
        username (Optional[str]): The username for authentication. If None, uses the
            AMS_USERNAME environment variable. Defaults to None.
        password (Optional[str]): The password for authentication. If None, uses the
            AMS_PASSWORD environment variable. Defaults to None.
        client (Optional[AMSClient]): A pre-authenticated AMSClient instance. If None,
            a new client is created using the provided url, username, and password.
            Defaults to None.

    Returns:
        bool: True if the database entry is successfully deleted.

    Raises:
        AMSError: If authentication fails, the API request returns an error, or the deletion fails.
        ValueError: If database_entry_id is negative or not an integer.

    Examples:
        >>> from teamworksams import delete_database_entry
        >>> result = delete_database_entry(
        ...     database_entry_id=386197,
        ...     url = "https://example.smartabase.com/site",
        ...     username = "user",
        ...     password = "pass"
        ... )
        >>> print(result)
        ✔ Successfully deleted database entry 386197.
    """
    client = client or get_client(url, username, password, cache=True, interactive_mode=False)
    
    if not isinstance(database_entry_id, int) or database_entry_id < 0:
        raise ValueError("database_entry_id must be a non-negative integer.")
    
    payload = {"id": database_entry_id}
    
    response = client._fetch(
        "userdefineddatabase/delete",
        method="POST",
        payload=payload,
        cache=False,
        api_version="v2"
    )
    
    if response is None:
        return f"✔ Successfully deleted database entry {database_entry_id}."
    
    raise AMSError(
        f"Failed to delete database entry with ID {database_entry_id}: {response}",
        function="delete_database_entry",
        endpoint="userdefineddatabase/delete"
    )


def insert_database_entry(
    df: DataFrame,
    form: str,
    url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    option: Optional[InsertDatabaseOption] = None,
    client: Optional[AMSClient] = None
) -> None:
    """Insert new database entries into an AMS database form.

    Processes a pandas DataFrame containing database entry data, validates the data, constructs
    an API payload, and sends it to the AMS API to insert new entries into the specified
    database form. Supports table fields via the InsertDatabaseOption, which allows
    configuration of table fields, caching, and interactive feedback. The function provides
    status updates if interactive mode is enabled, reporting the number of entries processed.

    Args:
        df (DataFrame): A pandas DataFrame containing the database entry data. Columns
            represent field names, and rows contain values to insert. Must not be empty.
        form (str): The name of the AMS database form to insert data into. Must be a non-empty
            string and correspond to a valid database form.
        url (str): The AMS instance URL (e.g., 'https://example.smartabase.com/site').
        username (Optional[str]): The username for authentication. If None, uses the
            AMS_USERNAME environment variable. Defaults to None.
        password (Optional[str]): The password for authentication. If None, uses the
            AMS_PASSWORD environment variable. Defaults to None.
        option (Optional[InsertDatabaseOption]): Configuration options for the insertion,
            including table_fields (list of table field names), interactive_mode (for status
            messages), and cache (for API response caching). If None, uses default
            InsertDatabaseOption. Defaults to None.
        client (Optional[AMSClient]): A pre-authenticated AMSClient instance. If None,
            a new client is created using the provided url, username, and password.
            Defaults to None.

    Returns:
        None: The function does not return a value but inserts entries into the AMS database
            and prints status messages if interactive_mode is enabled.

    Raises:
        AMSError: If the form is empty, not a database form, authentication fails, the DataFrame
            is invalid (e.g., empty or missing required fields), the payload cannot be built,
            or the API request fails.
        ValueError: If table_fields in the option contains invalid field names not present in
            the DataFrame.

    Examples:
        >>> import pandas as pd
        >>> from teamworksams import insert_database_entry
        >>> from teamworksams import InsertDatabaseOption
        >>> df = pd.DataFrame({
        ...     "Allergy": ["Dairy", "Eggs", "Peanuts"]
        ... })
        >>> insert_database_entry(
        ...     df = df,
        ...     form = "Allergies",
        ...     url = "https://example.smartabase.com/site",
        ...     username = "user",
        ...     password = "pass",
        ...     option = InsertDatabaseOption(table_fields = ["Table"])
        ... )
        ℹ Inserting 3 database entries for form 'Allergies'
        ✔ Processed 3 database entries for form 'Allergies'
        ℹ Form: Allergies
        ℹ Result: Success
        ℹ Records inserted: 3
        ℹ Records attempted: 3
    """
    option = option or InsertDatabaseOption()
    client = client or get_client(url, username, password, cache=option.cache, interactive_mode=option.interactive_mode)
    
    df_clean = _clean_database_df(df, table_fields=option.table_fields)
    
    _validate_database_df(df_clean, form, overwrite_existing=False, table_fields=option.table_fields)
    
    form_option = FormOption(
        interactive_mode=False,
        cache=option.cache,
        raw_output=False,
        field_details=False,
        include_instructions=False
    )
    
    form_id, form_type = _fetch_form_id_and_type(form, url, username, password, form_option, client)
    if form_type != "database":
        raise AMSError(
            f"Form '{form}' is not a database form (type: {form_type})",
            function="insert_database_entry"
        )
    
    application_id = client.login_data.get("applicationId")
    if not application_id:
        raise AMSError(
            "Application ID not found in login response",
            function="insert_database_entry"
        )
    
    entered_by_user_id = client.login_data.get("user", {}).get("id")
    if not entered_by_user_id:
        raise AMSError(
            "User ID not found in login response",
            function="insert_database_entry"
        )
    
    payloads = _build_database_payload(
        df_clean,
        form_id,
        application_id,
        entered_by_user_id,
        overwrite_existing=False,
        table_fields=option.table_fields
    )
    
    entry_count = len(payloads)
    if option.interactive_mode:
        print(f"ℹ Inserting {entry_count} database entries for form '{form}'")
    
    results = _fetch_database_save(
        client,
        payloads,
        "insert",
        option.interactive_mode,
        option.cache
    )
    
    if option.interactive_mode:
        print(f"✔ Processed {entry_count} database entries for form '{form}'")
    
    _print_import_status(results, form, "inserted", option.interactive_mode)


def update_database_entry(
    df: DataFrame,
    form: str,
    url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    option: Optional[UpdateDatabaseOption] = None,
    client: Optional[AMSClient] = None
) -> None:
    """Update existing database entries in an AMS database form.

    Processes a pandas DataFrame containing database entry data with an 'entry_id' column,
    validates the data, constructs an API payload, and sends it to the AMS API to update
    existing entries in the specified database form. Supports table fields via the
    UpdateDatabaseOption, which allows configuration of table fields, caching, and interactive
    feedback. In interactive mode, prompts for confirmation before updating and provides
    status updates.

    Args:
        df (DataFrame): A pandas DataFrame containing the database entry data. Must include
            an 'entry_id' column with valid integer IDs of existing entries, and other columns
            for field names with values to update. Must not be empty.
        form (str): The name of the AMS database form to update data in. Must be a non-empty
            string and correspond to a valid database form.
        url (str): The AMS instance URL (e.g., 'https://example.smartabase.com/site').
        username (Optional[str]): The username for authentication. If None, uses the
            AMS_USERNAME environment variable. Defaults to None.
        password (Optional[str]): The password for authentication. If None, uses the
            AMS_PASSWORD environment variable. Defaults to None.
        option (Optional[UpdateDatabaseOption]): Configuration options for the update,
            including table_fields (list of table field names), interactive_mode (for status
            messages and confirmation), and cache (for API response caching). If None, uses
            default UpdateDatabaseOption. Defaults to None.
        client (Optional[AMSClient]): A pre-authenticated AMSClient instance. If None,
            a new client is created using the provided url, username, and password.
            Defaults to None.

    Returns:
        None: The function does not return a value but updates entries in the AMS database
            and prints status messages if interactive_mode is enabled.

    Raises:
        AMSError: If the form is empty, not a database form, authentication fails, the DataFrame
            is invalid (e.g., empty, missing 'entry_id', or invalid IDs), the payload cannot be
            built, the API request fails, or the user cancels the operation in interactive mode.
        ValueError: If table_fields in the option contains invalid field names not present in
            the DataFrame.

    Examples:
        >>> import pandas as pd
        >>> from teamworksams import update_database_entry
        >>> from teamworksams import UpdateDatabaseOption
        >>> df = pd.DataFrame({
        ...     "entry_id": [386197, 386198, 386199],
        ...     "Allergy": ["Dairy Updated", "Eggs Updated", "Peanuts Updated"]
        ... })
        >>> update_database_entry(
        ...     df = df,
        ...     form = "Allergies",
        ...     url = "https://example.smartabase.com/site",
        ...     username = "user",
        ...     password = "pass",
        ...     option = UpdateDatabaseOption(table_fields = ["Table"])
        ... )
        ℹ Updating 3 database entries for form 'Allergies'
        Are you sure you want to update 3 existing database entries in 'Allergies'? (y/n): y
        ✔ Processed 3 database entries for form 'Allergies'
        ℹ Form: Allergies
        ℹ Result: Success
        ℹ Records updated: 3
        ℹ Records attempted: 3
    """
    option = option or UpdateDatabaseOption()
    client = client or get_client(url, username, password, cache=option.cache, interactive_mode=option.interactive_mode)
    
    df_clean = _clean_database_df(df, table_fields=option.table_fields)
    
    _validate_database_df(df_clean, form, overwrite_existing=True, table_fields=option.table_fields)
    
    form_option = FormOption(
        interactive_mode=False, 
        cache=option.cache,
        raw_output=False,
        field_details=False,
        include_instructions=False
    )
    
    form_id, form_type = _fetch_form_id_and_type(form, url, username, password, form_option, client)
    if form_type != "database":
        raise AMSError(
            f"Form '{form}' is not a database form (type: {form_type})",
            function="update_database_entry"
        )
    
    application_id = client.login_data.get("applicationId")
    if not application_id:
        raise AMSError(
            "Application ID not found in login response",
            function="update_database_entry"
        )
    
    entered_by_user_id = client.login_data.get("user", {}).get("id")
    if not entered_by_user_id:
        raise AMSError(
            "User ID not found in login response",
            function="update_database_entry"
        )
    
    payloads = _build_database_payload(
        df_clean,
        form_id,
        application_id,
        entered_by_user_id,
        overwrite_existing=True,
        table_fields=option.table_fields
    )
    
    entry_count = len(payloads)
    
    if option.interactive_mode:
        print(f"ℹ Updating {entry_count} database entries for form '{form}'")
        confirm = input(f"Are you sure you want to update {entry_count} existing database entries in '{form}'? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            raise AMSError("Update operation cancelled by user", function="update_database_entry")
    
    results = _fetch_database_save(
        client,
        payloads,
        "update",
        option.interactive_mode,
        option.cache
    )
    
    if option.interactive_mode:
        print(f"✔ Processed {entry_count} database entries for form '{form}'")
    
    _print_import_status(results, form, "updated", option.interactive_mode)