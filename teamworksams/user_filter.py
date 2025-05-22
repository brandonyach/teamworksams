from typing import Optional, Union, List
from .export_validate import _validate_user_filter_key


class UserFilter:
    """Filter for selecting users in user data export.

    Defines criteria for filtering users retrieved by the `get_user` function, allowing
    users to narrow results based on a user attribute (e.g., username, email, group) and
    corresponding value(s). Validates the filter key to ensure it is one of the supported
    options.

    Args:
        user_key (Optional[str]): The user attribute to filter by, one of 'username',
            'email', 'group', or 'about'. If None, no filtering is applied. Defaults to None.
        user_value (Optional[Union[str, List[str]]]): The value(s) to filter by, such as a
            username, email, or group name. Can be a single string or a list of strings.
            If None, no filtering is applied. Defaults to None.

    Attributes:
        user_key (Optional[str]): The filter key.
        user_value (Optional[Union[str, List[str]]]): The filter value(s).

    Raises:
        ValueError: If `user_key` is not one of 'username', 'email', 'group', or 'about'.

    Examples:
        >>> from teamworksams import UserFilter
        >>> filter = UserFilter(user_key = "group", user_value = "Example Group A")
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