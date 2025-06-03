from typing import Dict, List, Optional
from tqdm import tqdm
import sys
from .utils import AMSClient, AMSError
from .import_process import _handle_import_response, _count_unique_events


def _fetch_import_payloads(
    client: AMSClient,
    payloads: List[Dict],
    action: str,
    interactive_mode: bool,
    cache: bool,
    is_profile: bool = False,
    table_fields: Optional[List[str]] = None
) -> List[Dict]:
    """Send one API call per event payload with real-time progress."""
    results = []
    
    def send_payload(payload: Dict, item_count: int) -> List[Dict]:
        try:
            response = client._fetch(
                "profileimport" if is_profile else "eventsimport",
                method="POST",
                payload=payload,
                cache=cache,
                api_version="v1"
            )
            result = _handle_import_response(response)
            ids = result.get("ids", [])
            return [{"state": result["state"], "ids": [id], "message": result["message"]} for id in ids] or [result]
        except AMSError as e:
            if interactive_mode:
                print(f"✖ ERROR - {str(e)}")
            return [{"state": "ERROR", "message": str(e), "ids": []}] * item_count

    if is_profile:
        profile_iterator = tqdm(payloads, desc="Processing profiles", leave=False, total=len(payloads), position=0, dynamic_ncols=True, file=sys.stdout) if interactive_mode else payloads
        for profile in profile_iterator:
            results.extend(send_payload(profile, 1))
    else:
        payload_iterator = tqdm(payloads, desc="Processing events", leave=False, total=len(payloads), position=0, dynamic_ncols=True, file=sys.stdout) if interactive_mode else payloads
        for payload in payload_iterator:
            events = payload.get("events", [])
            if not events:
                continue
            item_count = _count_unique_events(events, table_fields)
            results.extend(send_payload(payload, item_count))
    
    return results