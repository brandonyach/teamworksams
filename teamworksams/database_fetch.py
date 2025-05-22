from typing import Dict, List
from tqdm import tqdm
from .utils import AMSClient, AMSError
from .database_process import _handle_database_response  


def _fetch_database_data(
    form_id: int,
    limit: int,
    offset: int,
    client: AMSClient,
    cache: bool = True
) -> Dict:
    """Fetch database entries from the AMS API.

    Args:
        form_id (int): The ID of the database form.
        limit (int): The maximum number of entries to return.
        offset (int): The offset of the first item to return.
        client (AMSClient): The AMSClient instance.
        cache (bool): Whether to cache the API response (default: True).

    Returns:
        Dict: The raw API response containing database entries.

    Raises:
        AMSError: If the API request fails.
    """
    payload = {
        "databaseFormId": int(form_id),
        "limit": limit,
        "offset": offset
    }
    response = client._fetch(
        "userdefineddatabase/findTableByDatabaseFormId",
        method="POST",
        payload=payload,
        cache=cache,
        api_version="v2"
    )
    return response



def _fetch_database_save(
    client: AMSClient,
    payloads: List[Dict],
    action: str,
    interactive_mode: bool,
    cache: bool
) -> List[Dict]:
    """Send payloads to the AMS API for database entry processing.

    Processes each payload by sending it to the /api/v2/userdefineddatabase/save endpoint,
    displaying a progress bar if interactive_mode is True, and handles any errors that occur.

    Args:
        client: AMSClient instance for making API requests.
        payloads: List of payloads, each containing an 'event' key with database entry data.
        action: The action being performed ('insert' or 'update').
        interactive_mode: Boolean indicating if interactive feedback should be provided.
        cache: Boolean indicating if API responses should be cached.

    Returns:
        List of result dictionaries with state, IDs, and message.

    Raises:
        AMSError: If an API request fails, included in the results list with state 'ERROR'.
    """
    results = []
    
    payload_iterator = tqdm(payloads, desc=f"Processing {action} database entries", leave=False) if interactive_mode else payloads
    for i, payload in enumerate(payload_iterator):
        try:
            if not isinstance(payload, dict) or "event" not in payload:
                raise AMSError(f"Invalid payload at index {i}: {payload}", function="_fetch_database_payloads")

            response = client._fetch(
                "userdefineddatabase/save",
                method="POST",
                payload=payload,
                cache=cache,
                api_version="v2"
            )
 
            result = _handle_database_response(response, action)
            results.append(result)
            
        except AMSError as e:
            if interactive_mode:
                print(f"✖ ERROR - {str(e)}")
            results.append({"state": "ERROR", "message": str(e), "ids": []})
    
    return results