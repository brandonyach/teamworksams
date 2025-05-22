from typing import Optional, List


class GetDatabaseOption:
    """Options for retrieving database entries from an AMS database form.

    Defines customization options for the `get_database` function, allowing control over
    caching of API responses and interactive feedback during execution. These options enable
    users to tailor the retrieval process to their needs, such as disabling status messages
    or reusing cached responses for performance.

    Args:
        interactive_mode (bool): Whether to print status messages during the operation, such
            as the number of entries retrieved or if none are found. Defaults to True.
        cache (bool): Whether to cache API responses to improve performance for repeated
            requests. Defaults to True.

    Attributes:
        interactive_mode (bool): Indicates whether interactive mode is enabled.
        cache (bool): Indicates whether caching is enabled.

    Examples:
        >>> from teamworksams import GetDatabaseOption
        >>> option = GetDatabaseOption(interactive_mode = True, cache = False)
    """
    def __init__(
        self,
        interactive_mode: bool = True,
        cache: bool = True,
    ):
        self.interactive_mode = interactive_mode,
        self.cache = cache



class InsertDatabaseOption:
    """Options for inserting database entries into an AMS database form.

    Defines customization options for the `insert_database_entry` function, allowing
    specification of table fields, caching of API responses, and interactive feedback.
    Table fields indicate which DataFrame columns are treated as table fields in the AMS
    database form, affecting how data is structured in the API payload.

    Args:
        table_fields (Optional[List[str]]): A list of field names that are table fields in
            the form. If None, no fields are treated as table fields. Defaults to None.
        interactive_mode (bool): Whether to print status messages during the operation, such
            as the number of entries being inserted and the result. Defaults to True.
        cache (bool): Whether to cache API responses to improve performance for repeated
            requests. Defaults to True.

    Attributes:
        table_fields (Optional[List[str]]): The list of table field names.
        interactive_mode (bool): Indicates whether interactive mode is enabled.
        cache (bool): Indicates whether caching is enabled.

    Examples:
        >>> from teamworksams import InsertDatabaseOption
        >>> option = InsertDatabaseOption(table_fields = ["Table"], interactive_mode = True, cache = True)
    """
    def __init__(
        self,
        table_fields: Optional[List[str]] = None,
        interactive_mode: bool = True,
        cache: bool = True,
    ):
        self.table_fields = table_fields,
        self.interactive_mode = interactive_mode,
        self.cache = cache



class UpdateDatabaseOption:
    """Options for updating database entries in an AMS database form.

    Defines customization options for the `update_database_entry` function, allowing
    specification of table fields, caching of API responses, and interactive feedback.
    Table fields indicate which DataFrame columns are treated as table fields in the AMS
    database form, affecting how data is structured in the API payload. Interactive mode
    enables confirmation prompts and status messages.

    Args:
        table_fields (Optional[List[str]]): A list of field names that are table fields in
            the form. If None, no fields are treated as table fields. Defaults to None.
        interactive_mode (bool): Whether to print status messages and prompt for confirmation
            during the update process. If True, users are prompted to confirm before updating.
            Defaults to True.
        cache (bool): Whether to cache API responses to improve performance for repeated
            requests. Defaults to True.

    Attributes:
        table_fields (Optional[List[str]]): The list of table field names.
        interactive_mode (bool): Indicates whether interactive mode is enabled.
        cache (bool): Indicates whether caching is enabled.

    Examples:
        >>> from teamworksams import UpdateDatabaseOption
        >>> option = UpdateDatabaseOption(table_fields = ["Table"], interactive_mode = True, cache = False)
    """
    def __init__(
        self,
        table_fields: Optional[List[str]] = None,
        interactive_mode: bool = True,
        cache: bool = True,
    ):
        self.table_fields = table_fields,
        self.interactive_mode = interactive_mode,
        self.cache = cache