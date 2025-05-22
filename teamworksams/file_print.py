from pandas import DataFrame

def _print_failed_attachments(failed_df: DataFrame, interactive_mode: bool) -> None:
    """Print the failed attachments if interactive_mode is True.

    Args:
        failed_df (DataFrame): The DataFrame containing failed attachments.
        interactive_mode (bool): Whether to print interactive messages.
    """
    if interactive_mode and not failed_df.empty:
        print("Failed attachments:")
        print(failed_df)