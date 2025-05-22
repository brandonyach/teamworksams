from typing import Dict, List
from tqdm import tqdm
from .utils import AMSClient, AMSError
from .import_process import _handle_import_response, _count_unique_events


def _fetch_import_payloads(
    client: AMSClient,
    payloads: List[Dict],
    action: str,
    interactive_mode: bool,
    cache: bool,
    is_profile: bool = False
) -> List[Dict]:
    """Send payloads to the AMS API for processing.

    Processes each payload by sending it to the API (eventsimport or profileimport endpoint),
    displaying a progress bar if interactive_mode is True, and handles any errors that occur.
    For profile imports, sends each profile payload individually to isolate potential issues.

    Args:
        client: AMSClient instance for making API requests.
        payloads: List of payloads to process; for events, a list of {'events': [...]}; for profiles, a list of profile dictionaries.
        action: The action being performed ('insert', 'update', 'upsert').
        interactive_mode: Boolean indicating if interactive feedback should be provided.
        cache: Boolean indicating if API responses should be cached.
        is_profile: Boolean indicating if this is a profile import (uses profileimport endpoint).

    Returns:
        List of result dictionaries from the API responses.

    Raises:
        AMSError: If an API request fails, included in the results list with state 'ERROR'.
    """
    results = []
    
    # For profiles, payloads is a list of profile dictionaries; for events, a list of {'events': [...]}
    if is_profile:
        # Process each profile dictionary individually
        profile_iterator = tqdm(payloads, desc="Processing profiles", leave=False) if interactive_mode else payloads
        for i, profile in enumerate(profile_iterator):
            try:
                if not isinstance(profile, dict):
                    raise AMSError(f"Invalid profile payload at index {i}: {profile}")
                # print(f"Debug: Sending profile {i+1}/{len(payloads)}: {profile}")
                response = client._fetch("profileimport", method="POST", payload=profile, cache=cache, api_version="v1")
                result = _handle_import_response(response)
                results.append(result)
            except AMSError as e:
                if interactive_mode:
                    print(f"✖ ERROR - {str(e)}")
                results.append({"state": "ERROR", "message": str(e), "ids": []})
    else:
        # Process event payloads
        payload_iterator = tqdm(payloads, desc="Processing payloads", leave=False) if interactive_mode else payloads
        for payload in payload_iterator:
            try:
                items = payload.get("events", [])
                item_count = _count_unique_events(items)
                # print(f"Debug: Sending event payload: {payload}")
                response = client._fetch("eventsimport", method="POST", payload=payload, cache=cache, api_version="v1")
                result = _handle_import_response(response)
                results.extend([result] * item_count)
            except AMSError as e:
                if interactive_mode:
                    print(f"✖ ERROR - {str(e)}")
                item_count = _count_unique_events(payload.get("events", []))
                results.extend([{"state": "ERROR", "message": str(e), "ids": []}] * item_count)
    
    return results

