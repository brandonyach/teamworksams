from typing import Optional, List


class InsertEventOption:
    """Options for configuring the insert_event_data function.

    Customizes the behavior of :func:`insert_event_data`,
    controlling user identifier mapping, caching, interactive feedback, and table fields.
    Optimizes performance and user experience for inserting new events into an AMS Event
    Form. See :ref:`importing_data` for import workflows.

    Args:
        interactive_mode (bool): Whether to print status messages during execution, such as
            the number of events being inserted and the result. Defaults to True.
        cache (bool): If True, reuses an existing :class:`AMSClient` via
            :func:`get_client`, reducing API calls for multi-function workflows (e.g.,
            inserting multiple batches). Set to False for independent sessions. Defaults
            to True.
        id_col (str): Column name in the input :class:`pandas.DataFrame` for user
            identifiers. Must be one of 'user_id', 'about', 'username', or 'email'.
            Used to map identifiers to AMS user IDs. Defaults to 'user_id'.
        table_fields (Optional[List[str]]): List of table field names in the AMS form
            (e.g., ['session_details']). Must match DataFrame columns if specified. If
            None, assumes no table fields. Defaults to None.

    Attributes:
        interactive_mode (bool): Indicates whether interactive mode is enabled.
        cache (bool): Indicates whether caching is enabled.
        id_col (str): The column name used for mapping user identifiers.
        table_fields (List[str]): The list of table field names, or an empty list if None.

    Raises:
        :class:`ValueError`: If `id_col` is not one of 'user_id', 'about', 'username', or
        'email'.

    Examples:
        >>> from teamworksams import InsertEventOption, insert_event_data
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     "username": ["john.doe"],
        ...     "start_date": ["01/01/2025"],
        ...     "duration": [60]
        ... })
        >>> option = InsertEventOption(id_col = "username", interactive_mode = True)
        >>> insert_event_data(
        ...     df = df,
        ...     form = "Training Log",
        ...     url = "https://example.smartabase.com/site",
        ...     option = option
        ... )
    """
    
    def __init__(
            self, 
            interactive_mode: bool = True, 
            cache: bool = True, 
            id_col: str = "user_id", 
            table_fields: Optional[List[str]] = None
        ):
        
        self.interactive_mode = interactive_mode
        
        self.cache = cache
        
        if id_col not in ["user_id", "about", "username", "email"]:
            raise ValueError("id_col must be 'user_id', 'about', 'username', or 'email'.")
        
        self.id_col = id_col
        
        self.table_fields = table_fields if table_fields is not None else None



class UpdateEventOption:
    """Options for configuring the update_event_data function.

    Customizes the behavior of :func:`update_event_data`,
    controlling user identifier mapping, confirmation prompts, caching, interactive
    feedback, and table fields. Ensures safe and efficient updates of existing events in
    an AMS Event Form. See :ref:`importing_data` for update workflows.

    Args:
        interactive_mode (bool): If True, prints status messages (e.g., "Updated 2
            events") and :mod:`tqdm` progress bars, and prompts for confirmation if
            `require_confirmation` is True. Set to False for silent execution. Defaults
            to True.
        cache (bool): If True, reuses an existing :class:`AMSClient` via
            :func:`get_client`, reducing API calls for multi-function workflows. Set to
            False for independent sessions. Defaults to True.
        id_col (str): Column name in the input :class:`pandas.DataFrame` for user
            identifiers. Must be one of 'user_id', 'about', 'username', or 'email'.
            Used to map identifiers to AMS user IDs. Defaults to 'user_id'.
        table_fields (Optional[List[str]]): List of table field names in the AMS form
            (e.g., ['session_details']). Must match DataFrame columns if specified. If
            None, assumes no table fields. Defaults to None.
        require_confirmation (bool): If True, prompts for user confirmation before
            updating events when `interactive_mode` is True, preventing accidental
            changes. Set to False to skip prompts. Defaults to True.

    Attributes:
        interactive_mode: Boolean indicating if interactive feedback is enabled.
        cache: Boolean indicating if caching is enabled.
        id_col: The column name used for mapping user identifiers.
        table_fields: List of table field names, or an empty list if None.

    Raises:
        :class:`ValueError`: If id_col is not one of the allowed values.
        
    Examples:
        >>> from teamworksams import UpdateEventOption, update_event_data
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     "event_id": [67890],
        ...     "username": ["john.doe"],
        ...     "duration": [65]
        ... })
        >>> option = UpdateEventOption(id_col = "username", interactive_mode = True)
        >>> update_event_data(
        ...     df = df,
        ...     form = "Training Log",
        ...     url = "https://example.smartabase.com/site",
        ...     option = option
        ... )
        ℹ Updating 1 events for 'Training Log'...
        Are you sure you want to update 1 existing events in 'Training Log'? (y/n): y
        ✔ Processed 1 events for 'Training Log'
    """
    def __init__(
            self, 
            interactive_mode: bool = True, 
            cache: bool = True, 
            id_col: str = "user_id", 
            table_fields: Optional[List[str]] = None,
            require_confirmation: bool = True
        ):
        
        self.interactive_mode = interactive_mode
        
        self.cache = cache
        
        if id_col not in ["user_id", "about", "username", "email"]:
            raise ValueError("id_col must be 'user_id', 'about', 'username', or 'email'.")
        
        self.id_col = id_col
        
        self.table_fields = table_fields if table_fields is not None else None
        
        self.require_confirmation = require_confirmation



class UpsertEventOption:
    """Options for configuring the upsert_event_data function.

    Customizes the behavior of :func:`upsert_event_data`,
    controlling user identifier mapping, caching, interactive feedback, and table fields.
    Optimizes performance for inserting new events and updating existing ones in an AMS
    Event Form. See :ref:`importing_data` for upsert workflows.

    Args:
        interactive_mode (bool): If True, prints status messages (e.g., "Upserted 2
            events") and :mod:`tqdm` progress bars during execution, ideal for interactive
            environments like Jupyter notebooks. Set to False for silent execution.
            Defaults to True.
        cache (bool): If True, reuses an existing :class:`AMSClient` via
            :func:`get_client`, reducing API calls for multi-function workflows. Set to
            False for independent sessions. Defaults to True.
        id_col (str): Column name in the input :class:`pandas.DataFrame` for user
            identifiers. Must be one of 'user_id', 'about', 'username', or 'email'.
            Used to map identifiers to AMS user IDs. Defaults to 'user_id'.
        table_fields (Optional[List[str]]): List of table field names in the AMS form
            (e.g., ['session_details']). Must match DataFrame columns if specified. If
            None, assumes no table fields. Defaults to None.

    Attributes:
        interactive_mode: Boolean indicating if interactive feedback is enabled.
        cache: Boolean indicating if caching is enabled.
        id_col: The column name used for mapping user identifiers.
        table_fields: List of table field names, or an empty list if None.

    Raises:
        :class:`ValueError`: If id_col is not one of the allowed values.
        
    Examples:
        >>> from teamworksams import UpsertEventOption, upsert_event_data
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     "event_id": [67890, None],
        ...     "username": ["john.doe", "jane.smith"],
        ...     "start_date": ["01/01/2025", "02/01/2025"],
        ...     "duration": [65, 45]
        ... })
        >>> option = UpsertEventOption(id_col = "username", interactive_mode = True)
        >>> upsert_event_data(
        ...     df = df,
        ...     form = "Training Log",
        ...     url = "https://example.smartabase.com/site",
        ...     option = option
        ... )
        ℹ Updating 1 existing events for 'Training Log'
        ℹ Inserting 1 new events for 'Training Log'
        ✔ Processed 2 events for 'Training Log'
    """
    def __init__(
            self, 
            interactive_mode: bool = True, 
            cache: bool = True, 
            id_col: str = "user_id", 
            table_fields: Optional[List[str]] = None
        ):
        
        self.interactive_mode = interactive_mode
        
        self.cache = cache
        
        if id_col not in ["user_id", "about", "username", "email"]:
            raise ValueError("id_col must be 'user_id', 'about', 'username', or 'email'.")
        
        self.id_col = id_col
        
        self.table_fields = table_fields if table_fields is not None else None
        
        

class UpsertProfileOption:
    """Options for configuring the upsert_profile_data function.

    Customizes the behavior of :func:`upsert_profile_data`,
    controlling user identifier mapping, caching, and interactive feedback. Ensures
    efficient upserting of profile records in an AMS Profile Form, with one record per
    user. 

    Args:
        interactive_mode (bool): If True, prints status messages (e.g., "Upserted 2
            profiles") and :mod:`tqdm` progress bars during execution, ideal for
            interactive environments like Jupyter notebooks. Set to False for silent
            execution. Defaults to True.
        cache (bool): If True, reuses an existing :class:`AMSClient` via
            :func:`get_client`, reducing API calls for multi-function workflows. Set to
            False for independent sessions. Defaults to True.
        id_col (str): Column name in the input :class:`pandas.DataFrame` for user
            identifiers. Must be one of 'user_id', 'about', 'username', or 'email'.
            Used to map identifiers to AMS user IDs. Defaults to 'user_id'.

    Attributes:
        interactive_mode: Boolean indicating if interactive feedback is enabled.
        cache: Boolean indicating if caching is enabled.
        id_col: The column name used for mapping user identifiers.

    Raises:
        :class:`ValueError`: If id_col is not one of the allowed values.
        
    Examples:
        >>> from teamworksams import UpsertProfileOption, upsert_profile_data
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     "username": ["john.doe"],
        ...     "athlete_id": [8194028]
        ... })
        >>> option = UpsertProfileOption(id_col="username", interactive_mode=True)
        >>> upsert_profile_data(
        ...     df = df,
        ...     form = "Athlete Profile",
        ...     url = "https://example.smartabase.com/site",
        ...     option = option
        ... )
        ℹ Upserting 1 profile records for 'Athlete Profile'
        ✔ Processed 1 profile records for 'Athlete Profile'
    """
    def __init__(
            self, 
            interactive_mode: bool = True, 
            cache: bool = True, 
            id_col: str = "user_id"
        ):
        self.interactive_mode = interactive_mode
        self.cache = cache
        if id_col not in ["user_id", "about", "username", "email"]:
            raise ValueError("id_col must be 'user_id', 'about', 'username', or 'email'.")
        self.id_col = id_col