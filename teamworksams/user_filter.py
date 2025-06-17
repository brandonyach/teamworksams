from typing import Optional, Union, List
from .export_validate import _validate_user_filter_key


class UserFilter:
    """Filter for selecting users in user data export.

    Defines criteria for filtering users retrieved by :func:`get_user`,
    allowing selection based on attributes like username, email, group, or about field.
    Validates the filter key to ensure it is supported. See
    :ref:`user_management` for filtering workflows.

    Args:
        user_key (Optional[str]): Attribute to filter by. Must be one of 'username',
            'email', 'group', or 'about'. For example, 'group' filters by group
            membership. If None, no filtering is applied. Defaults to None.
        user_value (Optional[Union[str, List[str]]]): Value(s) to match for
            `user_key`. For example, 'TeamA' or ['TeamA', 'TeamB'] for
            `user_key="group"` matches users in those groups. Case-sensitive. If None,
            no filtering is applied. Defaults to None.

    Attributes:
        user_key (Optional[str]): The filter key.
        user_value (Optional[Union[str, List[str]]]): The filter value(s).

    Raises:
        :class:`ValueError`: If `user_key` is not 'username', 'email', 'group', or
            'about'.

    Examples:
        >>> from teamworksams import UserFilter, get_user
        >>> filter = UserFilter(user_key="group", user_value="TeamA")
        >>> df = get_user(
        ...     url="https://example.smartabase.com/site",
        ...     filter=filter
        ... )
        >>> print(df['groups'])
        0    [TeamA]
        1    [TeamA]
        Name: groups, dtype: object
        >>> filter = UserFilter(user_key="email", user_value=["john.doe@example.com"])
        >>> df = get_user(url="https://example.smartabase.com/site", filter=filter)
    """
    def __init__(
        self, 
        user_key: Optional[str] = None, 
        user_value: Optional[Union[str, List[str]]] = None
    ):
        self.user_key = user_key
        self.user_value = user_value
        self._validate()

    def _validate(self) -> None:
        """Validate the user filter parameters."""
        _validate_user_filter_key(self.user_key)