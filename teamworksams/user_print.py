from pandas import DataFrame
from typing import Dict, List
from .user_option import UserOption, GroupOption


def _report_user_results(
    total_users: int,
    failed_operations: List[Dict],
    user_ids: List[str],
    operation: str,
    interactive_mode: bool = False
) -> DataFrame:
    """Report the results of user operations, printing success and failure messages.

    Args:
        total_users (int): Total number of users processed.
        failed_operations (List[Dict]): List of failed operations with user_key and reason.
        user_ids (List[str]): List of successful user IDs.
        operation (str): The operation performed (e.g., 'created', 'updated').
        interactive_mode (bool): Whether to print status messages.

    Returns:
        DataFrame: A DataFrame containing failed operations with columns ['user_key', 'reason'].
    """
    failed_df = DataFrame(failed_operations, columns=["user_key", "reason"])
    successful_count = total_users - len(failed_df)

    if interactive_mode:
        if user_ids:
            user_id_str = ", ".join(user_ids[:3])
            if len(user_ids) > 3:
                user_id_str += ", ..."
            print(f"\n✔ Successfully {operation} {successful_count} users with user id's {user_id_str}.")
        else:
            print(f"\n✔ Successfully {operation} {successful_count} users.")
        if failed_df.empty:
            print("No failed operations.")
        else:
            print(f"⚠️ Failed to {operation[:-1]} {len(failed_df)} users:")
            print(failed_df.to_string(index=False))

    return failed_df




def _print_user_status(df: DataFrame, option: UserOption) -> None:
    """Print the status of user data retrieval.

    Args:
        df (DataFrame): The DataFrame containing user data.
        option (UserOption): The UserOption object specifying interactive mode.
    """
    if option.interactive_mode:
        print(f"ℹ Retrieved {len(df)} users.")



def _print_group_status(df: DataFrame, option: GroupOption) -> None:
    """Print the status of group data retrieval.

    Args:
        df (DataFrame): The DataFrame containing group data.
        option (GroupOption): The GroupOption object specifying interactive mode.
    """
    if option.interactive_mode:
        print(f"ℹ Retrieved {len(df)} groups.")