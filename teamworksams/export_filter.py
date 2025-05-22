from typing import Optional, Union, List
from .export_validate import _validate_user_filter_key, _validate_event_filter


class EventFilter:
    """Filter for selecting events in event data export.

    Defines criteria for filtering events retrieved by the `get_event_data` function, allowing
    users to narrow results based on user attributes (e.g., username, group), data fields
    (e.g., specific form field values), and the maximum number of events per user. The filter
    supports various conditions for data fields (e.g., equality, inequality) and validates
    parameters to ensure correctness.

    Args:
        user_key (Optional[str]): The user attribute to filter by, one of 'about', 'username',
            'email', 'uuid', or 'group'. If None, no user filtering is applied. Defaults to None.
        user_value (Optional[Union[str, List[str]]]): The value(s) to filter users by, such as a
            username, email, or group name. Can be a single string or a list of strings. If None,
            no user filtering is applied. Defaults to None.
        data_key (Optional[str]): The form field key to filter events by (e.g., 'Intensity').
            If None, no data field filtering is applied. Defaults to None.
        data_value (Optional[Union[str, List[str]]]): The value(s) to filter events by for the
            specified data_key. Can be a single string or a list of strings. If None, no data
            field filtering is applied. Defaults to None.
        data_condition (Optional[str]): The condition for data filtering, one of '=', '!=', '>',
            '<', '>=', '<=', 'contains', 'not contains', 'is empty', 'is not empty'. If None,
            defaults to '=' for data filtering. Defaults to None.
        events_per_user (Optional[int]): The maximum number of events to retrieve per user.
            Must be positive if specified. If None, all events are retrieved. Defaults to None.

    Attributes:
        user_key (Optional[str]): The user filter key.
        user_value (Optional[Union[str, List[str]]]): The user filter value(s).
        data_key (Optional[str]): The data field key.
        data_value (Optional[Union[str, List[str]]]): The data field value(s).
        data_condition (Optional[str]): The data filter condition.
        events_per_user (Optional[int]): The maximum events per user.

    Raises:
        ValueError: If any parameter is invalid, such as an unrecognized user_key, invalid
            data_condition, or negative events_per_user.

    Examples:
        >>> from teamworksams import EventFilter
        >>> filter = EventFilter(
        ...     user_key = "group",
        ...     user_value = "Example Group",
        ...     data_key = "Intensity",
        ...     data_value = "High",
        ...     data_condition = "=",
        ...     events_per_user = 10
        ... )
    """
    def __init__(
        self,
        user_key: Optional[str] = None,
        user_value: Optional[Union[str, List[str]]] = None,
        data_key: Optional[str] = None,
        data_value: Optional[Union[str, List[str]]] = None,
        data_condition: Optional[str] = None,
        events_per_user: Optional[int] = None
    ):
        self.user_key = user_key
        self.user_value = user_value
        self.data_key = data_key
        self.data_value = data_value
        self.data_condition = data_condition
        self.events_per_user = events_per_user
        self._validate()

    def _validate(self) -> None:
        """Validate the event filter parameters."""
        _validate_event_filter(self.user_key, self.user_value, self.data_key, self.data_value, self.data_condition, self.events_per_user)
        


class SyncEventFilter:
    """Filter for selecting users in sync event data export.

    Defines criteria for filtering users in the `sync_event_data` function, allowing users to
    narrow results based on a user attribute (e.g., username, group) and corresponding value(s).
    Validates the filter key to ensure it is one of the supported options.

    Args:
        user_key (Optional[str]): The user attribute to filter by, one of 'about', 'username',
            'email', 'group', or 'current_group'. If None, no filtering is applied.
            Defaults to None.
        user_value (Optional[Union[str, List[str]]]): The value(s) to filter by, such as a
            username, email, or group name. Can be a single string or a list of strings.
            If None, no filtering is applied. Defaults to None.

    Attributes:
        user_key (Optional[str]): The filter key.
        user_value (Optional[Union[str, List[str]]]): The filter value(s).

    Raises:
        ValueError: If user_key is not one of the valid options ('about', 'username', 'email',
            'group', 'current_group').

    Examples:
        >>> from teamworksams import SyncEventFilter
        >>> filter = SyncEventFilter(user_key = "group", user_value = "Example Group")
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
        """Validate the sync event filter parameters."""
        valid_user_keys = {"about", "username", "email", "group", "current_group"}
        if self.user_key and self.user_key not in valid_user_keys:
            raise ValueError(f"Invalid user_key: '{self.user_key}'. Must be one of {valid_user_keys}")



class ProfileFilter:
    """Filter for selecting users in profile data export.

    Defines criteria for filtering users in the `get_profile_data` function, allowing users to
    narrow results based on a user attribute (e.g., username, group) and corresponding value(s).
    Validates the filter key to ensure it is one of the supported options.

    Args:
        user_key (Optional[str]): The user attribute to filter by, one of 'group', 'username',
            'email', or 'about'. If None, no filtering is applied. Defaults to None.
        user_value (Optional[Union[str, List[str]]]): The value(s) to filter by, such as a
            username, email, or group name. Can be a single string or a list of strings.
            If None, no filtering is applied. Defaults to None.

    Attributes:
        user_key (Optional[str]): The filter key.
        user_value (Optional[Union[str, List[str]]]): The filter value(s).

    Raises:
        ValueError: If user_key is not one of the valid options ('group', 'username', 'email',
            'about').

    Examples:
        >>> from teamworksams import ProfileFilter
        >>> filter = ProfileFilter(user_key = "group", user_value = "TeamA")
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
        """Validate the profile filter parameters."""
        _validate_user_filter_key(self.user_key)