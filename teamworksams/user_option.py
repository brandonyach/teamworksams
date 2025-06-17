from typing import Optional, List

class UserOption:
    """Options for configuring user-related operations.

    Customizes the behavior of :func:`get_user`,
    :func:`edit_user`, and
    :func:`create_user`, controlling output columns, caching,
    and interactive feedback. Optimizes performance and user experience for user data
    operations. See :ref:`user_management` for usage examples.

    Args:
        columns (Optional[List[str]]): List of column names to include in the output
            :class:`pandas.DataFrame` for :func:`get_user` (e.g., ['user_id',
            'first_name']). Ignored by :func:`edit_user` and :func:`create_user`. If
            None, includes all available columns (e.g., 'user_id', 'email', 'groups').
            Defaults to None.
        cache (bool): If True, reuses an existing :class:`AMSClient` via
            :func:`get_client`, reducing API calls for multi-function workflows (e.g.,
            fetching then updating users). Set to False for independent sessions.
            Defaults to True.
        interactive_mode (bool): If True, prints status messages (e.g., "Retrieved 5
            users") and :mod:`tqdm` progress bars for operations like
            :func:`edit_user`. Set to False for silent execution in automated scripts.
            Defaults to True.

    Attributes:
        columns (Optional[List[str]]): The list of columns to include in the output.
        cache (bool): Indicates whether caching is enabled.
        interactive_mode (bool): Indicates whether interactive mode is enabled.

    Examples:
        >>> from teamworksams import UserOption
        >>> option = UserOption(
        ...     columns = ["user_id", "first_name", "email"],
        ...     cache = True,
        ...     interactive_mode = True
        ... )
    """
    def __init__(
        self, 
        columns: Optional[List[str]] = None, 
        cache: bool = True, 
        interactive_mode: bool = True
    ):
        self.columns = columns
        self.cache = cache
        self.interactive_mode = interactive_mode



class GroupOption:
    """Options for configuring group data export.

    Customizes the behavior of :func:`get_group`, controlling
    data type inference, caching, and interactive feedback. Optimizes the group data
    retrieval process for performance and output formatting. See
    :ref:`user_management` for combining group and user data.

    Args:
        guess_col_type (bool): If True, infers column data types in the output
            :class:`pandas.DataFrame` (e.g., string for group names), ensuring
            compatibility with operations like merging with :func:`get_user` results.
            Set to False to use default pandas types. Defaults to True.
        interactive_mode (bool): If True, prints status messages (e.g., "Retrieved 3
            groups") during execution, useful for interactive environments. Set to False for silent execution. Defaults to True.
        cache (bool): If True, reuses an existing :class:`AMSClient` via
            :func:`get_client`, reducing API calls for multi-function workflows. Set to
            False for independent sessions. Defaults to True.

    Attributes:
        guess_col_type (bool): Indicates whether column type inference is enabled.
        interactive_mode (bool): Indicates whether interactive mode is enabled.
        cache (bool): Indicates whether caching is enabled.

    Examples:
        >>> from teamworksams import GroupOption
        >>> option = GroupOption(
        ...     guess_col_type = True,
        ...     interactive_mode = True,
        ...     cache = False
        ... )
    """
    def __init__(
        self, 
        guess_col_type: bool = True, 
        interactive_mode: bool = True, 
        cache: bool = True
    ):
        self.guess_col_type = guess_col_type
        self.interactive_mode = interactive_mode
        self.cache = cache