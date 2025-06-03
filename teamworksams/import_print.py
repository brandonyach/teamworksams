from typing import List, Dict


# def _print_import_status(results: List[Dict], form: str, action: str, interactive_mode: bool) -> None:
#     """Print the status of the import operation.

#     Args:
#         results: List of result dictionaries from the API responses.
#         form: The name of the AMS form.
#         action: The action performed ('inserted', 'updated', 'upserted').
#         interactive_mode: Boolean indicating if the status should be printed.
#     """
#     if not interactive_mode:
#         return
#     total_success = sum(1 for r in results if r.get("state") in ["SUCCESSFULLY_IMPORTED", "SUCCESS"])
#     print(f"ℹ Form: {form}")
#     print(f"ℹ Result: {'Success' if total_success > 0 else 'Failed'}")
#     print(f"ℹ Records {action}: {total_success}")
#     print(f"ℹ Records attempted: {len(results)}")


# def _print_import_status(results: List[Dict], form: str, action: str, interactive_mode: bool) -> None:
#     """Print the status of the import operation.

#     Args:
#         results: List of result dictionaries from API responses.
#         form: The name of the AMS form.
#         action: The action ('inserted', 'updated', 'upserted').
#         interactive_mode: Boolean for printing status.
#     """
#     if not interactive_mode:
#         return
#     # Handle various success states from AMS API
#     success_states = ["SUCCESSFULLY_IMPORTED", "SUCCESS", "OK"]
#     total_success = sum(1 for r in results if r.get("state") in success_states and (r.get("ids") or r.get("message", "").lower().startswith("updated")))
#     total_attempted = len(results)
#     print(f"ℹ Form: {form}")
#     print(f"ℹ Result: {'Success' if total_success > 0 else 'Failed'}")
#     print(f"ℹ Records {action}: {total_success}")
#     print(f"ℹ Records attempted: {total_attempted}")
#     if interactive_mode and total_success < total_attempted:
#         failed_results = [r for r in results if r.get("state") not in success_states or not (r.get("ids") or r.get("message", "").lower().startswith("updated"))]
#         print(f"⚠️ {len(failed_results)} events failed:")
#         for r in failed_results[:5]:  # Limit to 5 for brevity
#             print(f"  - Error: {r.get('message', 'Unknown error')}")



def _print_import_status(results: List[Dict], form: str, action: str, interactive_mode: bool) -> None:
    """Print the status of the import operation."""
    if not interactive_mode:
        return
    success_states = ["SUCCESSFULLY_IMPORTED", "SUCCESS"]
    total_success = sum(1 for r in results if r.get("state") in success_states)
    total_attempted = len(results)
    print(f"ℹ Form: {form}")
    print(f"ℹ Result: {'Success' if total_success > 0 else 'Failed'}")
    print(f"ℹ Records {action}: {total_success}")
    print(f"ℹ Records attempted: {total_attempted}")
    if interactive_mode and total_success < total_attempted:
        failed_results = [r for r in results if r.get("state") not in success_states]
        print(f"⚠️ {len(failed_results)} events failed:")
        for r in failed_results[:5]:
            print(f"  - Error: {r.get('message', 'Unknown error')}")