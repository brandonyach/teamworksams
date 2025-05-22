from pandas import DataFrame
import pandas as pd
from .utils import AMSError


def _validate_user_key(user_key: str) -> None:
    """Validate the user_key for file operations.

    Args:
        user_key (str): The user key to validate (e.g., 'username', 'email').

    Raises:
        AMSError: If the user_key is invalid.
    """
    valid_user_keys = ["username", "email", "about", "uuid"]
    if user_key not in valid_user_keys:
        AMSError(f"Invalid user_key: '{user_key}'. Must be one of {valid_user_keys}", function="validate_user_key")
    
    
    
def _validate_user_data_for_save(df: DataFrame) -> None:
    """Validate user data DataFrame for creating or updating users via /api/v2/person/save.

    Ensures the DataFrame contains required columns with appropriate data types for user creation or update.

    Args:
        df (DataFrame): The DataFrame containing user data.

    Raises:
        AMSError: If required columns are missing or data types are incorrect.
    """
    required_columns = ['first_name', 'last_name', 'username', 'email', 'dob', 'password', 'active']

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise AMSError(f"Missing required columns: {', '.join(missing_columns)}")

    # Validate data types
    for col in ['first_name', 'last_name', 'username', 'email', 'dob', 'password']:
        if not all(isinstance(val, str) or pd.isna(val) for val in df[col]):
            raise AMSError(f"Column '{col}' must contain strings")

    if not all(isinstance(val, bool) or pd.isna(val) for val in df['active']):
        raise AMSError("Column 'active' must contain booleans")

    # Validate optional columns
    optional_columns = ['uuid', 'known_as', 'middle_names', 'language', 'sidebar_width', 'sex']
    for col in optional_columns:
        if col in df.columns and not all(isinstance(val, str) or pd.isna(val) for val in df[col]):
            raise AMSError(f"Column '{col}' must contain strings")
        
        
        
def _validate_user_data_for_edit(mapping_df: DataFrame, user_key: str) -> None:
    """Validate the input DataFrame and user_key for edit_user.

    Args:
        mapping_df (DataFrame): The DataFrame containing user data and identifiers.
        user_key (str): The user identifier column in mapping_df.

    Raises:
        AMSError: If validation fails.
    """
    _validate_user_key(user_key)
    if user_key not in mapping_df.columns:
        raise AMSError(f"Column '{user_key}' not found in mapping_df")