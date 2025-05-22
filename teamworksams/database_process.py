from pandas import DataFrame
from typing import Dict, Union
from .database_option import GetDatabaseOption
from .utils import AMSError


def _process_database_entries(
    response: Dict,
    form_name: str,
    option: GetDatabaseOption,
) -> Union[DataFrame, Dict]:
    """Process the raw database entries response into a DataFrame.

    Args:
        response (Dict): The raw API response from the findTableByDatabaseFormId endpoint.
        form_name (str): The name of the database form.
        option (FormOption): The FormOption object for configuration.

    Returns:
        Union[DataFrame, Dict]: A DataFrame containing the processed database entries, or the raw response if raw_output is True.

    Raises:
        AMSError: If the response format is invalid or contains an error.
    """
    if not response:
        raise AMSError(f"No database entries found for form '{form_name}'")

    # Check for error in the response
    if response.get("error", False):
        error_message = response.get("message", "Unknown error")
        raise AMSError(f"Failed to fetch database entries for form '{form_name}': {error_message}")

    # Extract the value section of the response
    value = response.get("value", {})
    
    # Extract entries, IDs, and field mappings
    entries = value.get("rows", [])
    entry_ids = value.get("ids", [])
    index_to_name = value.get("indexToName", {})
    
    if not isinstance(entries, list):
        if option.interactive_mode:
            print(f"ℹ Expected a list of entries, got: {type(entries)}. Full response: {response}")
        entries = []

    if not entries:
        if option.interactive_mode:
            print(f"ℹ No entries found in response for form '{form_name}'. Full response: {response}")
        return DataFrame()

    # Ensure the number of IDs matches the number of entries
    if len(entry_ids) != len(entries):
        if option.interactive_mode:
            print(f"ℹ Mismatch between number of IDs ({len(entry_ids)}) and entries ({len(entries)}). Full response: {response}")
        entry_ids = [None] * len(entries)  # Fallback to None if IDs don't match

    # Process each entry into a row
    rows = []
    for entry_idx, entry in enumerate(entries):
        if not isinstance(entry, list):
            if option.interactive_mode:
                print(f"ℹ Skipping invalid entry format at index {entry_idx}: {entry}")
            continue
        
        row = {
            "id": entry_ids[entry_idx] if entry_idx < len(entry_ids) else None,
            "form_name": form_name
        }
        # Map values to field names using indexToName
        for col_idx, value in enumerate(entry):
            field_name = index_to_name.get(str(col_idx), f"field_{col_idx}")
            row[field_name] = value
        rows.append(row)

    df = DataFrame(rows)
    if df.empty and option.interactive_mode:
        print(f"ℹ Processed DataFrame is empty for form '{form_name}'. Full response: {response}")
    
    return df


def _handle_database_response(response: Union[None, int, Dict], action: str) -> Dict:
    """Handle the response from the AMS userdefineddatabase/save endpoint.

    Args:
        response: Raw response from the API (null or positive integer for success, negative/zero or dict for errors).
        action: The action being performed ('insert' or 'update').

    Returns:
        Dict: Processed response dictionary with state, IDs, and message.

    Raises:
        AMSError: If the response is an invalid type.
    """
    if response is None or (isinstance(response, int) and response > 0):
        return {
            "state": "SUCCESS",
            "ids": [response] if isinstance(response, int) else [],  # Include entry ID if available
            "message": f"Database entry {action} successful"
        }
    
    if isinstance(response, int):
        return {
            "state": "ERROR",
            "ids": [],
            "message": f"Failed to {action} database entry: API returned status code {response}"
        }
    
    if isinstance(response, dict):
        if response.get("error", False):
            error_message = response.get("message", "Unknown error")
            return {
                "state": "ERROR",
                "ids": [],
                "message": f"Failed to {action} database entry: {error_message}"
            }
        return {
            "state": "ERROR",
            "ids": [],
            "message": f"Failed to {action} database entry: Unexpected response format {response}"
        }
    
    raise AMSError(
        f"Invalid response type from database endpoint: {type(response)}",
        function="_handle_database_response"
    )