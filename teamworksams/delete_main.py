from typing import Optional, Dict, List
from .utils import AMSClient, AMSError, get_client
from .delete_build import _build_delete_event_payload, _build_delete_multiple_events_payload
from .delete_option import DeleteEventOption


def delete_event_data(
    event_id: int,
    url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    option: Optional[DeleteEventOption] = None,
    client: Optional[AMSClient] = None
) -> str:
    """Delete a single event from an AMS instance.

    Sends a request to the AMS API's deleteevent endpoint to remove the event with the
    specified ID, returning a message indicating success or failure. Requires valid
    authentication and a positive integer `event_id`, obtainable via
    :func:`get_event_data`. In interactive mode, prompts for confirmation and provides
    feedback. See :ref:`vignettes/deleting_data` for deletion workflows.

    Args:
        event_id (int): ID of the event to delete. Must be a positive integer (e.g.,
            134273).
        url (str): AMS instance URL (e.g., 'https://example.smartabase.com/site'). Must
            include a valid site name.
        username (Optional[str]): Username for authentication. If None, uses
            :envvar:`AMS_USERNAME` or :class:`keyring` credentials. Defaults to None.
        password (Optional[str]): Password for authentication. If None, uses
            :envvar:`AMS_PASSWORD` or :class:`keyring` credentials. Defaults to
             None.
        option (:class:`DeleteEventOption`, optional): Configuration options, including
            `interactive_mode` for confirmation prompts and status messages (e.g.,
            "SUCCESS: Deleted 134273"). Defaults to None (uses default
            :class:`DeleteEventOption` with `interactive_mode=True`).
        client (:class:`AMSClient`, optional): Pre-authenticated client from
            :func:`get_client`. If None, a new client is created. Defaults to
            None.

    Returns:
        str: A message indicating the result of the deletion, e.g., "SUCCESS: Deleted 134273"
            or "FAILURE: [error message]".

    Raises:
        :class:`AMSError`: If authentication fails, the API request returns an error, the response is
            invalid, or the user cancels the operation in interactive mode.
        :class:`ValueError`: If event_id is not a positive integer.

    Examples:
        >>> from teamworksams import delete_event_data, DeleteEventOption
        >>> result = delete_event_data(
        ...     event_id = 134273,
        ...     url = "https://example.smartabase.com/site",
        ...     username = "user",
        ...     password = "pass",
        ...     option = DeleteEventOption(interactive_mode = True)
        ... )
        Are you sure you want to delete event '134273'? (y/n): y
        ℹ Deleting event with ID 134273...
        ✔ SUCCESS: Deleted 134273
    """
    option = option or DeleteEventOption()
    client = client or get_client(url, username, password, cache=True, interactive_mode=option.interactive_mode)
    
    if not isinstance(event_id, int) or event_id <= 0:
        raise ValueError("event_id must be a single positive integer.")
    
    payload = _build_delete_event_payload(event_id)
    
    if option.interactive_mode:
        confirm = input(f"Are you sure you want to delete event '{event_id}'? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            raise AMSError("Delete operation cancelled by user.")
        print(f"ℹ Deleting event with ID {event_id}...")
    
    try:
        response = client._fetch("deleteevent", method="POST", payload=payload, cache=False, api_version="v1")
    except AMSError as e:
        if option.interactive_mode:
            print(f"✖ Failed to delete event with ID {event_id}: {str(e)}")
        raise
    
    if not isinstance(response, dict) or "state" not in response or "message" not in response:
        raise AMSError(f"Invalid response from deleteevent endpoint: {response}")
    
    state = response["state"]
    message = response["message"]
    full_message = f"{state}: {message}"
    
    if option.interactive_mode:
        if state == "SUCCESS":
            print(f"✔ {full_message}")
        else:
            print(f"✖ {full_message}")
    
    return full_message



def delete_multiple_events(
    event_ids: List[int],
    url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    option: Optional[DeleteEventOption] = None,
    client: Optional[AMSClient] = None
) -> str:
    """Delete multiple events from an AMS instance.

    Sends a request to the AMS API's event/deleteAll endpoint to remove a list of events
    specified by their IDs, returning a message indicating success or failure. Requires
    valid authentication and a non-empty list of positive integer `event_ids`, obtainable
    via :func:`get_event_data`. In interactive mode, prompts for confirmation and provides
    feedback. See :ref:`vignettes/deleting_data` for deletion workflows.

    Args:
        event_ids (List[int]): List of event IDs to delete. Must be a non-empty list of
            positive integers (e.g., [134273, 134274]).
        url (str): AMS instance URL (e.g., 'https://example.smartabase.com/site'). Must
            include a valid site name.
        username (Optional[str]): Username for authentication. If None, uses
            :envvar:`AMS_USERNAME` or :class:`keyring` credentials. Defaults to None.
        password (Optional[str]): Password for authentication. If None, uses
            :envvar:`AMS_PASSWORD` or :class:`keyring` credentials. Defaults to
            None.
        option (:class:`DeleteEventOption`, optional): Configuration options, including
            `interactive_mode` for confirmation prompts and status messages (e.g.,
            "SUCCESS: Deleted 3 events"). Defaults to None (uses default
            :class:`DeleteEventOption` with `interactive_mode=True`).
        client (:class:`AMSClient`, optional): Pre-authenticated client from
            :func:`get_client`. If None, a new client is created. Defaults to
            None.

    Returns:
        str: A message indicating the result of the deletion, e.g., "SUCCESS: Deleted 3 events"
            or "FAILURE: Could not delete events with IDs [134273, 134274]".

    Raises:
        :class:`AMSError`: If authentication fails, the API request returns an error, or the user
            cancels the operation in interactive mode.
        :class:`ValueError`: If event_ids is empty or contains non-positive integers.

    Examples:
        >>> from teamworksams import delete_multiple_events
        >>> result = delete_multiple_events(
        ...     event_ids = [134273, 134274, 134275],
        ...     url = "https://example.smartabase.com/site",
        ...     username = "user",
        ...     password = "pass",
        ...     option = DeleteEventOption(interactive_mode = True)
        ... )
        Are you sure you want to delete 3 events with IDs [134273, 134274, 134275]? (y/n): y
        ℹ Deleting 3 events with IDs [134273, 134274, 134275]...
        ✔ SUCCESS: Deleted 3 events
    """
    option = option or DeleteEventOption()
    client = client or get_client(url, username, password, cache=True, interactive_mode=option.interactive_mode)
    
    if not isinstance(event_ids, list) or not event_ids:
        raise ValueError("event_ids must be a non-empty list of integers.")
    
    for event_id in event_ids:
        if not isinstance(event_id, int) or event_id <= 0:
            raise ValueError("All event_ids must be positive integers.")
    
    payload = _build_delete_multiple_events_payload(event_ids)
    
    if option.interactive_mode:
        confirm = input(f"Are you sure you want to delete {len(event_ids)} events with IDs {event_ids}? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            raise AMSError("Delete operation cancelled by user.")
        
        print(f"ℹ Deleting {len(event_ids)} events with IDs {event_ids}...")
        
    try:
        response = client._fetch("event/deleteAll", method="POST", payload=payload, cache=False, api_version="v2")
    except AMSError as e:
        if option.interactive_mode:
            print(f"✖ Failed to delete events with IDs {event_ids}: {str(e)}")
        raise
    
    if response is None:
        full_message = f"SUCCESS: Deleted {len(event_ids)} events"
    else:
        full_message = f"FAILURE: Could not delete events with IDs {event_ids}"
        if option.interactive_mode:
            print(f"✖ {full_message}")
        raise AMSError(full_message)
    
    if option.interactive_mode:
        print(f"✔ {full_message}")
    
    return full_message