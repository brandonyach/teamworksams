from typing import Optional, List


class GetDatabaseOption:
    """Options for retrieving database entries from an AMS database form.

    Customizes the behavior of :func:`get_database`,
    controlling caching and interactive feedback. These options optimize performance
    and user experience for fetching database entries, such as allergies or equipment
    lists, typically used in one-off operations. See
    :ref:`database_operations` for database workflows.

    Args:
        interactive_mode (bool): If True, prints status messages during execution,
            such as "Retrieved 100 entries" or "No entries found," useful for
            interactive environments like Jupyter notebooks. Set to False for silent
            execution. Defaults to True.
        cache (bool): If True, reuses cached API responses via the :class:`AMSClient`,
            reducing API calls for repeated queries (e.g., fetching multiple pages).
            Set to False for fresh data. Defaults to True.

    Attributes:
        interactive_mode (bool): Whether interactive mode is enabled.
        cache (bool): Whether caching is enabled.

    Examples:
        >>> from teamworksams import GetDatabaseOption, get_database
        >>> option = GetDatabaseOption(interactive_mode = True, cache = False)
        >>> df = get_database(
        ...     form_name = "Allergies",
        ...     url = "https://example.smartabase.com/site",
        ...     option = option
        ... )
        ℹ Fetching database entries for form 'Allergies'...
        ✔ Retrieved 100 database entries for form 'Allergies'.
    """
    def __init__(
        self,
        interactive_mode: bool = True,
        cache: bool = True,
    ):
        self.interactive_mode = interactive_mode
        self.cache = cache



class InsertDatabaseOption:
    """Options for inserting database entries into an AMS database form.

    Customizes the behavior of :func:`insert_database_entry`,
    controlling table fields, caching, and interactive feedback. These options tailor
    the insertion process for one-off operations, ensuring data aligns with the AMS
    form’s structure. See :ref:`database_operations` for database workflows.

    Args:
        table_fields (Optional[List[str]]): List of field names in the AMS form that
            are table fields (e.g., ['Table']). Must match :class:`pandas.DataFrame`
            columns if specified. If None, no fields are treated as table fields.
            Defaults to None.
        interactive_mode (bool): If True, prints status messages during execution,
            such as "Inserted 3 entries," ideal for interactive environments. Set to
            False for silent execution. Defaults to True.
        cache (bool): If True, reuses cached API responses via the :class:`AMSClient`,
            reducing API calls for repeated operations. Set to False for independent
            requests. Defaults to True.

    Attributes:
        table_fields (Optional[List[str]]): List of table field names, or None if
            unspecified.
        interactive_mode (bool): Whether interactive mode is enabled.
        cache (bool): Whether caching is enabled.

    Examples:
        >>> from teamworksams import InsertDatabaseOption, insert_database_entry
        >>> import pandas as pd
        >>> df = pd.DataFrame({"Allergy": ["Dairy"]})
        >>> option = InsertDatabaseOption(interactive_mode = True)
        >>> insert_database_entry(
        ...     df = df,
        ...     form = "Allergies",
        ...     url = "https://example.smartabase.com/site",
        ...     option = option
        ... )
        ℹ Inserting 1 database entries for form 'Allergies'
        ✔ Processed 1 database entries for form 'Allergies'
    """
    def __init__(
        self,
        table_fields: Optional[List[str]] = None,
        interactive_mode: bool = True,
        cache: bool = True,
    ):
        self.table_fields = table_fields
        self.interactive_mode = interactive_mode
        self.cache = cache



class UpdateDatabaseOption:
    """Options for updating database entries in an AMS database form.

    Customizes the behavior of :py:func:`update_database_entry`,
    controlling table fields, caching, and interactive feedback with confirmation
    prompts. These options ensure safe and efficient updates for one-off operations.
    See :ref:`database_operations` for database workflows.

    Args:
        table_fields (Optional[List[str]]): List of field names in the AMS form that
            are table fields (e.g., ['Table']). Must match :class:`pandas.DataFrame`
            columns if specified. If None, no fields are treated as table fields.
            Defaults to None.
        interactive_mode (bool): If True, prints status messages (e.g., "Updated 2
            entries") and prompts for confirmation before updating, preventing
            accidental changes. Set to False for silent execution. Defaults to True.
        cache (bool): If True, reuses cached API responses via the AMSClient,
            reducing API calls for repeated operations. Set to False for independent
            requests. Defaults to True.

    Attributes:
        table_fields (Optional[List[str]]): List of table field names, or None if
            unspecified.
        interactive_mode (bool): Whether interactive mode is enabled.
        cache (bool): Whether caching is enabled.

    Examples:
        >>> from teamworksams import UpdateDatabaseOption, update_database_entry
        >>> import pandas as pd
        >>> df = pd.DataFrame({"entry_id": [386197], "Allergy": ["Dairy Updated"]})
        >>> option = UpdateDatabaseOption(interactive_mode = True)
        >>> update_database_entry(
        ...     df = df,
        ...     form = "Allergies",
        ...     url = "https://example.smartabase.com/site",
        ...     option = option
        ... )
        ℹ Updating 1 database entries for form 'Allergies'
        Are you sure you want to update 1 existing database entries in 'Allergies'? (y/n): y
        ✔ Processed 1 database entries for form 'Allergies'
    """
    def __init__(
        self,
        table_fields: Optional[List[str]] = None,
        interactive_mode: bool = True,
        cache: bool = True,
    ):
        self.table_fields = table_fields
        self.interactive_mode = interactive_mode
        self.cache = cache