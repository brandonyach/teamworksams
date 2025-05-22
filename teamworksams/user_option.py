from typing import Optional, List

class UserOption:
    """Options for configuring user-related operations.

    Defines customization options for the `get_user`, `edit_user`, and `create_user`
    functions, controlling aspects such as selecting output columns, caching API responses,
    and enabling interactive feedback. These options allow users to tailor the user data
    retrieval or modification process, optimizing performance and user experience.

    Args:
        columns (Optional[List[str]]): A list of column names to include in the output
            DataFrame for `get_user` (e.g., ['user_id', 'first_name', 'email']). Ignored
            by `edit_user` and `create_user`. If None, includes all available columns.
            Defaults to None.
        cache (bool): Whether to cache API responses to improve performance for repeated
            requests. Defaults to True.
        interactive_mode (bool): Whether to print status messages during execution, such as
            the number of users retrieved or updated. Defaults to True.

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

    Defines customization options for the `get_group` function, controlling aspects such as
    inferring column data types, caching API responses, and enabling interactive feedback.
    These options allow users to tailor the group data retrieval process, optimizing
    performance and output formatting.

    Args:
        guess_col_type (bool): Whether to infer column data types (e.g., string for group
            names) in the resulting DataFrame. Defaults to True.
        interactive_mode (bool): Whether to print status messages during execution, such as
            the number of groups retrieved. Defaults to True.
        cache (bool): Whether to cache API responses to improve performance for repeated
            requests. Defaults to True.

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