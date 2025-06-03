from typing import Optional, List


class InsertEventOption:
    """Options for configuring the insert_event_data function.

    Defines customization options for inserting new events into an AMS Event Form, controlling
    aspects such as user identifier mapping, caching API responses, enabling interactive
    feedback, and specifying table fields. These options allow users to tailor the insertion
    process, optimizing performance and user experience.

    Args:
        interactive_mode (bool): Whether to print status messages during execution, such as
            the number of events being inserted and the result. Defaults to False.
        cache (bool): Whether to cache API responses to improve performance for repeated
            requests. Defaults to True.
        id_col (str): The column name in the DataFrame used to map user identifiers to user
            IDs. Must be one of 'user_id', 'about', 'username', or 'email'. Defaults to
            'user_id'.
        table_fields (Optional[List[str]]): A list of field names that are table fields in
            the form. If None, the form is treated as non-table. Defaults to None.

    Attributes:
        interactive_mode (bool): Indicates whether interactive mode is enabled.
        cache (bool): Indicates whether caching is enabled.
        id_col (str): The column name used for mapping user identifiers.
        table_fields (List[str]): The list of table field names, or an empty list if None.

    Raises:
        ValueError: If `id_col` is not one of 'user_id', 'about', 'username', or 'email'.

    Examples:
        >>> from teamworksams import InsertEventOption
        >>> option = InsertEventOption(
        ...     interactive_mode = True,
        ...     cache = True,
        ...     id_col = "username",
        ...     table_fields = ["TableField"]
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

    Defines customization options for updating existing events in an AMS Event Form, controlling
    aspects such as user identifier mapping, caching API responses, enabling interactive
    feedback, and specifying table fields. These options allow users to tailor the update
    process, including confirmation prompts and status messages.

    Args:
        interactive_mode (bool): Whether to print status messages and prompt for confirmation
            during execution, such as the number of events being updated. Defaults to False.
        cache (bool): Whether to cache API responses to improve performance for repeated
            requests. Defaults to True.
        id_col (str): The column name in the DataFrame used to map user identifiers to user
            IDs. Must be one of 'user_id', 'about', 'username', or 'email'. Defaults to
            'user_id'.
        table_fields (Optional[List[str]]

    Attributes:
        interactive_mode: Boolean indicating if interactive feedback is enabled.
        cache: Boolean indicating if caching is enabled.
        id_col: The column name used for mapping user identifiers.
        table_fields: List of table field names, or an empty list if None.

    Raises:
        ValueError: If id_col is not one of the allowed values.
        
    Examples:
        >>> from teamworksams import UpdateEventOption
        >>> option = UpdateEventOption(
        ...     interactive_mode = True,
        ...     cache = True,
        ...     id_col = "username",
        ...     table_fields = ["TableField"]
        ... )
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

    Defines customization options for upserting events (importing new events and updating 
    existing events) in an AMS Event Form, controlling aspects such as user identifier mapping, 
    caching API responses, enabling interactive feedback, and specifying table fields. These 
    options allow users to tailor the upsert process, including confirmation prompts and status 
    messages.

    Args:
        interactive_mode (bool): Whether to print status messages and prompt for confirmation
            during execution, such as the number of events being updated. Defaults to False.
        cache (bool): Whether to cache API responses to improve performance for repeated
            requests. Defaults to True.
        id_col (str): The column name in the DataFrame used to map user identifiers to user
            IDs. Must be one of 'user_id', 'about', 'username', or 'email'. Defaults to
            'user_id'.
        table_fields (Optional[List[str]]

    Attributes:
        interactive_mode: Boolean indicating if interactive feedback is enabled.
        cache: Boolean indicating if caching is enabled.
        id_col: The column name used for mapping user identifiers.
        table_fields: List of table field names, or an empty list if None.

    Raises:
        ValueError: If id_col is not one of the allowed values.
        
    Examples:
        >>> from teamworksams import UpsertEventOption
        >>> option = UpsertEventOption(
        ...     interactive_mode = True,
        ...     cache = True,
        ...     id_col = "username",
        ...     table_fields = ["TableField"]
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
        
        

class UpsertProfileOption:
    """Options for configuring the upsert_profile_data function.

    This class defines configuration options for upserting profile data in an AMS Profile Form,
    including whether to display interactive feedback, cache API responses, and specify the user
    identifier column.

    Args:
        interactive_mode: If True, display progress bars and interactive prompts. Defaults to False.
        cache: If True, cache API responses and reuse the client session. Defaults to True.
        id_col: The column name to use for mapping user identifiers to user IDs.
            Must be one of 'user_id', 'about', 'username', or 'email'. Defaults to 'user_id'.

    Attributes:
        interactive_mode: Boolean indicating if interactive feedback is enabled.
        cache: Boolean indicating if caching is enabled.
        id_col: The column name used for mapping user identifiers.

    Raises:
        ValueError: If id_col is not one of the allowed values.
        
    Examples:
        >>> from teamworksams import UpsertProfileOption
        >>> option = UpsertProfileOption(
        ...     interactive_mode = True,
        ...     cache = True,
        ...     id_col = "username"
        ... )
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