from typing import Dict, List


def _build_delete_event_payload(event_id: int) -> Dict:
    """Build the payload for the deleteevent API endpoint.

    Constructs a payload for deleting a single event by its ID.

    Args:
        event_id (int): The ID of the event to delete.

    Returns:
        Dict: The payload dictionary for the API request.
    """
    return {"eventId": event_id}


def _build_delete_multiple_events_payload(event_ids: List[int]) -> Dict:
    """Build the payload for the event/deleteAll API endpoint.

    Constructs a payload for deleting multiple events by their IDs.

    Args:
        event_ids (List[int]): The list of event IDs to delete.

    Returns:
        Dict: The payload dictionary for the API request.
    """
    return {"eventIds": [str(event_id) for event_id in event_ids]}