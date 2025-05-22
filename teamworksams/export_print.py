from pandas import DataFrame
from .export_option import EventOption, ProfileOption

def _print_event_status(df: DataFrame, form: str, option: EventOption) -> None:
    """Print the status of event data retrieval.

    Args:
        df (DataFrame): The DataFrame containing event data.
        form (str): The name of the form.
        option (EventOption): The EventOption object specifying interactive mode and attachment options.
    """
    if option.interactive_mode:
        if option.download_attachment:
            attachment_count = getattr(option, "attachment_count", 0)
            print(f"✔ Retrieved {len(df)} event records for form '{form}' with {attachment_count} attachments downloaded.")
        else:
            print(f"✔ Retrieved {len(df)} event records for form '{form}'.")



def _print_profile_status(df: DataFrame, form: str, option: ProfileOption) -> None:
    """Print the status of profile data retrieval.

    Args:
        df (DataFrame): The DataFrame containing profile data.
        form (str): The name of the form.
        option (ProfileOption): The ProfileOption object specifying interactive mode.
    """
    if option.interactive_mode:
        print(f"✔ Retrieved {len(df)} profile records for form '{form}'.")