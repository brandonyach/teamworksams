from pandas import DataFrame
from .form_option import FormOption


def _print_forms_status(df: DataFrame, option: FormOption) -> None:
    """Print the status of forms retrieval.

    Args:
        df (DataFrame): The DataFrame containing forms data.
        option (FormOption): The FormOption object specifying interactive mode.
    """
    if option.interactive_mode:
        print(f"✔ Retrieved {len(df)} forms.")
        