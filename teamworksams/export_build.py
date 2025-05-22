from typing import Optional, List, Tuple, Dict
from .utils import AMSError
from .export_filter import EventFilter


def _build_event_payload(
        form: str, 
        start_date: str, 
        end_date: str, 
        user_ids: List[int], 
        filter: Optional[EventFilter] = None, 
        events_per_user: Optional[int] = None
    ) -> Tuple[str, Dict]:
    """Build the payload for eventsearch or filteredeventsearch API endpoints.

    Constructs a payload for fetching events, optionally applying filters for data fields or limiting
    the number of events per user. Determines the appropriate endpoint based on the presence of filters.

    Args:
        form (str): The event form name.
        start_date (str): Start date in DD/MM/YYYY format.
        end_date (str): End date in DD/MM/YYYY format.
        user_ids (List[int]): List of user IDs to fetch events for.
        filter (Optional[EventFilter]): An EventFilter object to apply additional data filters.
        events_per_user (Optional[int]): Maximum number of events to retrieve per user.

    Returns:
        Tuple[str, Dict]: A tuple containing the endpoint ('eventsearch' or 'filteredeventsearch') and the payload dictionary.
    """

    condition_map = {
        "=": 1,
        "!=": 2,  
        "contains": 3, 
        "<": 4,  
        ">": 5,  
        "<=": 6, 
        ">=": 7  
    }
    
    if filter and filter.data_key and filter.data_value and filter.data_condition:
        filter_condition = condition_map.get(filter.data_condition)
        if filter_condition is None:
            raise AMSError(f"Invalid data_condition: '{filter.data_condition}'. Must be one of {list(condition_map.keys())}")
        
        payload = {
            "filter": [
                {
                    "formName": form,
                    "filterSet": [
                        {
                            "key": filter.data_key,
                            "value": filter.data_value,
                            "filterCondition": filter_condition
                        }
                    ]
                }
            ],
            "userIds": user_ids,
            "startDate": start_date,
            "finishDate": end_date,
            "startTime": "12:00 AM",
            "finishTime": "11:59 PM"
        }
        if events_per_user:
            payload["resultsPerUser"] = events_per_user
        endpoint = "filteredeventsearch"
    else:
        payload = {
            "formNames": [form],
            "userIds": user_ids,
            "startDate": start_date,
            "finishDate": end_date,
            "startTime": "12:00 AM",
            "finishTime": "11:59 PM"
        }
        if events_per_user:
            payload["resultsPerUser"] = events_per_user
        endpoint = "eventsearch"
    
    return endpoint, payload



def _build_sync_event_payload(
        form: str, 
        last_synchronisation_time: int, 
        user_ids: List[int]
    ) -> Dict:
    """Build the payload for the synchronise API endpoint.

    Constructs a payload for fetching event data that has been modified since the specified time.

    Args:
        form (str): The name of the form to fetch events from.
        last_synchronisation_time (int): The last synchronisation time in milliseconds since 1970-01-01.
        user_ids (List[int]): List of user IDs to fetch events for.

    Returns:
        Dict: The payload dictionary for the API request.
    """
    return {
        "formName": form,
        "lastSynchronisationTimeOnServer": last_synchronisation_time,
        "userIds": user_ids
    }



def _build_profile_payload(form: str, user_ids: List[int]) -> Dict:
    """Build the payload for the profilesearch API endpoint.

    Constructs a payload for fetching profile data for specified users and form.

    Args:
        form (str): The name of the form to fetch profiles from.
        user_ids (List[int]): List of user IDs to fetch profiles for.

    Returns:
        Dict: The payload dictionary for the API request.
    """
    return {
        "formNames": [form],
        "userIds": user_ids
    }



def _build_form_endpoint(form_type: str, form_id: int) -> str:
    """Build the endpoint for the forms API.

    Constructs the endpoint URL for fetching form details based on type and ID.

    Args:
        form_type (str): The type of form (e.g., 'event', 'profile').
        form_id (int): The ID of the form.

    Returns:
        str: The API endpoint (e.g., 'forms/event/123').
    """
    return f"forms/{form_type}/{form_id}"






