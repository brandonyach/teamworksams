import os
from typing import Optional, List, Tuple, Union
from datetime import datetime
from .utils import AMSError


def _validate_user_filter_key(user_key: Optional[str]) -> None:
    """Validate the user_key for UserFilter.

    Args:
        user_key (Optional[str]): The user key to validate (e.g., 'username', 'email').

    Raises:
        ValueError: If the user_key is invalid.
    """
    valid_user_keys = {"username", "email", "group", "about"}
    if user_key and user_key not in valid_user_keys:
        raise ValueError(f"Invalid user_key: '{user_key}'. Must be one of {valid_user_keys}")



def _validate_event_filter(
    user_key: Optional[str],
    user_value: Optional[Union[str, List[str]]],
    data_key: Optional[str],
    data_value: Optional[Union[str, List[str]]],
    data_condition: Optional[str],
    events_per_user: Optional[int]
) -> None:
    """Validate the parameters of an EventFilter.

    Args:
        user_key (Optional[str]): The user key to filter by (e.g., 'username', 'email').
        user_value (Optional[Union[str, List[str]]]): The value(s) to filter users by.
        data_key (Optional[str]): The data field key to filter events by.
        data_value (Optional[Union[str, List[str]]]): The value(s) to filter events by.
        data_condition (Optional[str]): The condition for data filtering (e.g., '=', '!=').
        events_per_user (Optional[int]): The maximum number of events per user.

    Raises:
        ValueError: If any filter parameters are invalid.
    """
    # Validate user_key
    if user_key and user_value:
        valid_user_keys = {"about", "username", "email", "uuid", "group"}
        if user_key not in valid_user_keys:
            raise ValueError(f"Invalid user_key: '{user_key}'. Must be one of {valid_user_keys}")
    
    # Validate data_key, data_value, data_condition
    if data_key or data_value or data_condition:
        if not (data_key and data_value and data_condition):
            raise ValueError("data_key, data_value, and data_condition must all be provided if any are specified.")
        valid_conditions = {">", ">=", "<", "<=", "=", "!=", "contains"}
        if data_condition not in valid_conditions:
            raise ValueError(f"Invalid data_condition: '{data_condition}'. Must be one of {valid_conditions}")
    
    # Validate events_per_user
    if events_per_user is not None:
        if not isinstance(events_per_user, int) or events_per_user <= 0:
            raise ValueError("events_per_user must be a positive integer.")



def _validate_dates(
        start_date: str, 
        end_date: str, 
        date_format: str = "%d/%m/%Y"
    ) -> Tuple[datetime, datetime]:
    """Validate and parse start and end dates into datetime objects.

    Args:
        start_date (str): The start date string (format: DD/MM/YYYY).
        end_date (str): The end date string (format: DD/MM/YYYY).
        date_format (str): The expected date format (default: '%d/%m/%Y').

    Returns:
        Tuple[datetime, datetime]: The parsed start and end dates.

    Raises:
        ValueError: If the dates are invalid or start_date is after end_date.
    """
    try:
        start = datetime.strptime(start_date, date_format)
        end = datetime.strptime(end_date, date_format)
    except ValueError:
        raise ValueError(f"start_date '{start_date}' and end_date '{end_date}' must be in DD/MM/YYYY format")
    if start > end:
        raise ValueError(f"start_date '{start_date}' cannot be after end_date '{end_date}'.")
    return start, end