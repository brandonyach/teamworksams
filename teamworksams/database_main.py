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

    Fetches entries from a specified AMS database form, returning a
    :class:`pandas.DataFrame` with columns for entry IDs and field values. Supports
    pagination via `limit` and `offset`, and customization through
    :class:`GetDatabaseOption` for caching, interactive feedback, or raw output. Ideal
    for retrieving structured data like allergies or equipment lists. See
    :ref:`vignettes/database_operations` for database workflows.

    Args:
        form_name (str): Name of the AMS database form (e.g., 'Allergies'). Must be a
            non-empty string and correspond to a valid database form.
        url (str): AMS instance URL (e.g., 'https://example.smartabase.com/site'). Must
            include a valid site name.
        username (Optional[str]): Username for authentication. If None, uses
            :envvar:`AMS_USERNAME` or :class:`keyring`. Defaults to None.
        password (Optional[str]): Password for authentication. If None, uses
            :envvar:`AMS_PASSWORD` or :class:`keyring` credentials. Defaults to None.
        limit (int): Maximum number of entries to return per request. Must be positive
            (e.g., 10000). Use smaller values for large datasets to manage memory.
            Defaults to 10000.
        offset (int): Starting index for pagination. Must be non-negative. Use to skip
            entries in large datasets (e.g., 10000 for the next batch). Defaults to 0.
        option (:class:`GetDatabaseOption`, optional): Configuration options, including
            `interactive_mode` for status messages (e.g., "Retrieved 100 entries"),
            `cache` to reuse a client, and `raw_output` for unprocessed API responses.
            Defaults to None (uses default :class:`GetDatabaseOption`).
        client (:class:`AMSClient`, optional): Pre-authenticated client from
            :func:`get_client`. If None, a new client is created. Defaults to None.

    Returns:
        :class:`pandas.DataFrame`: Database entries with columns like 'id' and
            form-specific fields (e.g., 'Allergy'). Returns an empty DataFrame if no
            entries are found

    Raises:
        :class:`AMSError`: If `form_name` is empty, not a database form,
            authentication fails, or the API request fails.
        :class:`ValueError`: If `limit` is not positive or `offset` is negative.

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

    Sends a request to the AMS API to delete the database entry with the specified ID,
    returning True if successful. Requires valid credentials and a valid entry ID,
    typically obtained from :func:`get_database`. See
    :ref:`vignettes/database_operations` for database workflows.

    Args:
        database_entry_id (int): ID of the database entry to delete. Must be a
            non-negative integer (e.g., 386197).
        url (str): AMS instance URL (e.g., 'https://example.smartabase.com/site'). Must
            include a valid site name.
        username (Optional[str]): Username for authentication. If None, uses
            :envvar:`AMS_USERNAME` or :class:`keyring` credentials. Defaults to None.
        password (Optional[str]): Password for authentication. If None, uses
            :envvar:`AMS_PASSWORD` or :class:`keyring` credentials. Defaults to None.
        client (:class:`AMSClient`, optional): Pre-authenticated client from
            :func:`get_client`. If None, a new client is created. Defaults to None.

    Returns:
        bool: True if the entry is successfully deleted.

    Raises:
        :class:`AMSError`: If authentication fails, the API request fails, or the
            deletion fails.
        :class:`ValueError`: If `database_entry_id` is negative or not an integer.

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

    Processes a :class:`pandas.DataFrame` containing database entry data, validates it,
    and inserts new entries into the specified AMS database form via the API. Supports
    table fields and customizable options for caching and interactive feedback. See
    :ref:`vignettes/database_operations` for database workflows.

    Args:
        df (:class:`pandas.DataFrame`): DataFrame with database entry data. Columns
            represent form fields (e.g., 'Allergy'), and rows contain values. Must not
            be empty.
        form (str): Name of the AMS database form (e.g., 'Allergies'). Must be a
            non-empty string and correspond to a valid database form.
        url (str): AMS instance URL (e.g., 'https://example.smartabase.com/site'). Must
            include a valid site name.
        username (Optional[str]): Username for authentication. If None, uses
            :envvar:`AMS_USERNAME` or :class:`keyring` credentials. Defaults to None.
        password (Optional[str]): Password for authentication. If None, uses
            :envvar:`AMS_PASSWORD` or :class:`keyring` credentials. Defaults to None.
        option (:class:`InsertDatabaseOption`, optional): Configuration options,
            including `table_fields` for table field names, `interactive_mode` for status
            messages (e.g., "Inserted 3 entries"), and `cache` to reuse a client.
            Defaults to None (uses default :class:`InsertDatabaseOption`).
        client (:class:`AMSClient`, optional): Pre-authenticated client from
            :func:`get_client`. If None, a new client is created. Defaults to None.

    Returns:
        None: The function does not return a value but inserts entries into the AMS database
            and prints status messages if interactive_mode is enabled.

    Raises:
        :class:`AMSError`: If `form` is empty, not a database form, authentication
            fails, `df` is invalid (e.g., empty), or the API request fails.
        :class:`ValueError`: If `table_fields` contains invalid field names not in `df`.

    Examples:
        >>> import pandas as pd
        >>> from teamworksams import insert_database_entry, InsertDatabaseOption
        >>> df = pd.DataFrame({
        ...     "Allergy": ["Dairy", "Eggs", "Peanuts"]
        ... })
        >>> insert_database_entry(
        ...     df = df,
        ...     form = "Allergies",
        ...     url = "https://example.smartabase.com/site",
        ...     username = "user",
        ...     password = "pass"
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

    Processes a :class:`pandas.DataFrame` with an 'entry_id' column to update existing
    entries in the specified AMS database form via the API. Validates data, supports
    table fields, and offers interactive confirmation prompts. See
    :ref:`vignettes/database_operations` for database workflows.

    Args:
        df (:class:`pandas.DataFrame`): DataFrame with database entry data. Must include
            'entry_id' (valid integer IDs) and columns for fields to update (e.g.,
            'Allergy'). Must not be empty.
        form (str): Name of the AMS database form (e.g., 'Allergies'). Must be a
            non-empty string and correspond to a valid database form.
        url (str): AMS instance URL (e.g., 'https://example.smartabase.com/site'). Must
            include a valid site name.
        username (Optional[str]): Username for authentication. If None, uses
            :envvar:`AMS_USERNAME` or :class:`keyring` credentials. Defaults to None.
        password (Optional[str]): Password for authentication. If None, uses
            :envvar:`AMS_PASSWORD` or :class:`keyring` credentials. Defaults to None.
        option (:class:`UpdateDatabaseOption`, optional): Configuration options,
            including `table_fields` for table field names, `interactive_mode` for
            status messages and confirmation prompts, and `cache` to reuse a client.
            Defaults to None (uses default :class:`UpdateDatabaseOption`).
        client (:class:`AMSClient`, optional): Pre-authenticated client from
            :func:`get_client`. If None, a new client is created. Defaults to None.

    Returns:
        None: Updates entries in the AMS database and prints status messages if
            ``option.interactive_mode=True``.

    Raises:
        :class:`AMSError`: If `form` is empty, not a database form, authentication
            fails, `df` is invalid (e.g., empty, missing 'entry_id'), user cancels in
            interactive mode, or the API request fails.
        :class:`ValueError`: If `table_fields` contains invalid field names not in `df`.

    Examples:
        >>> import pandas as pd
        >>> from teamworksams import update_database_entry, UpdateDatabaseOption
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
        ...     option = UpdateDatabaseOption(interactive_mode = True)
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