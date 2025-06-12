from typing import Optional, Union, List
from .export_validate import _validate_user_filter_key, _validate_event_filter


class EventFilter:
    """Filter for selecting events in event data export.

    Defines criteria for filtering events retrieved by
    :func:`teamworksams.export_main.get_event_data`, allowing selection based on user
    attributes (e.g., username, group) or event data fields (e.g., intensity). Validates
    filter parameters to ensure compatibility with the AMS API. 

    Args:
        user_key (Optional[str]): User attribute to filter by, one of 'username',
            'email', 'group', or 'about'. If None, no user filtering is applied.
            Defaults to None.
        user_value (Optional[Union[str, List[str]]]): Value(s) to match for
            `user_key` (e.g., 'TeamA' for `user_key="group"`). Case-sensitive. If None,
            no user filtering is applied. Defaults to None.
        data_key (Optional[str]): Event data field to filter by (e.g., 'intensity').
            Must match a valid form field. If None, no data filtering is applied.
            Defaults to None.
        data_value (Optional[str]): Value to match for `data_key` (e.g., 'High'). If
            None, no data filtering is applied. Defaults to None.
        data_condition (Optional[str]): Condition for `data_key` filtering, one of
            'equals', 'not_equals', 'contains'. If None, defaults to 'equals'. Defaults
            to None.
        events_per_user (Optional[int]): Maximum number of events per user. If None,
            retrieves all events. Defaults to None.

    Attributes:
        user_key (Optional[str]): The user filter key.
        user_value (Optional[Union[str, List[str]]]): The user filter value(s).
        data_key (Optional[str]): The data field key.
        data_value (Optional[Union[str, List[str]]]): The data field value(s).
        data_condition (Optional[str]): The data filter condition.
        events_per_user (Optional[int]): The maximum events per user.

    Raises:
        :class:`ValueError`: If any parameter is invalid, such as an unrecognized user_key, invalid
            data_condition, or negative events_per_user.

    Examples:
        >>> from teamworksams import get_event_data, EventFilter
        >>> filter = EventFilter(
        ...     user_key = "group",
        ...     user_value = "Example Group",
        ...     data_key = "Intensity",
        ...     data_value = "High",
        ...     data_condition = "=",
        ...     events_per_user = 10
        ... )
        >>> df = get_event_data(
        ...     form = "Training Log",
        ...     start_date = "01/01/2025",
        ...     end_date = "31/01/2025",
        ...     url = "https://example.smartabase.com/site",
        ...     filter = filter
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

    Defines criteria for filtering events retrieved by
    :func:`teamworksams.export_main.sync_event_data`, allowing selection based on user
    attributes (e.g., username, group). Validates filter parameters for compatibility
    with the AMS 'synchronise' endpoint.

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
        :class:`ValueError`: If user_key is not one of the valid options ('about', 'username', 'email',
            'group', 'current_group').

    Examples:
        >>> from teamworksams import SyncEventFilter, sync_event_data
        >>> filter = SyncEventFilter(user_key = "group", user_value = "Group A")
        >>> df, new_sync_time = sync_event_data(
        ...     form = "Training Log",
        ...     last_synchronisation_time = 1677654321000,
        ...     url = "https://example.smartabase.com/site",
        ...     filter = filter
        ... )
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

    Defines criteria for filtering profiles retrieved by
    :func:`teamworksams.export_main.get_profile_data`, allowing selection based on user
    attributes (e.g., username, group). Validates filter parameters for compatibility
    with the AMS API.

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
        :class:`ValueError`: If user_key is not one of the valid options ('group', 'username', 'email',
            'about').

    Examples:
        >>> from teamworksams import ProfileFilter, get_profile_data
        >>> filter = ProfileFilter(user_key = "group", user_value = "Group A")
        >>> df = get_profile_data(
        ...     form = "Athlete Profile",
        ...     url = "https://example.smartabase.com/site",
        ...     filter = filter
        ... )
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