from typing import List, Dict


def _print_import_status(results: List[Dict], form: str, action: str, interactive_mode: bool) -> None:
    """Print the status of the import operation.

    Args:
        results: List of result dictionaries from the API responses.
        form: The name of the AMS form.
        action: The action performed ('inserted', 'updated', 'upserted').
        interactive_mode: Boolean indicating if the status should be printed.
    """
    if not interactive_mode:
        return
    total_success = sum(1 for r in results if r.get("state") in ["SUCCESSFULLY_IMPORTED", "SUCCESS"])
    print(f"ℹ Form: {form}")
    print(f"ℹ Result: {'Success' if total_success > 0 else 'Failed'}")
    print(f"ℹ Records {action}: {total_success}")
    print(f"ℹ Records attempted: {len(results)}")