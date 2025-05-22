import pandas as pd
from pandas import DataFrame
from typing import Optional, List, Dict, Tuple
from .user_process import _flatten_groups_and_roles


def _clean_phone_numbers(phone_numbers: Optional[List[Dict]]) -> str:
    """Clean the phoneNumbers field from an AMS API response.

    Converts a list of phone number dictionaries into a semicolon-separated string of cleaned phone numbers.

    Args:
        phone_numbers (Optional[List[Dict]]): A list of phone number dictionaries, each containing 'countryCode', 'prefix', and 'number'.

    Returns:
        str: A semicolon-separated string of cleaned phone numbers, or an empty string if no valid numbers are found.
    """
    if not phone_numbers or not isinstance(phone_numbers, list):
        return ""
    cleaned = []
    for phone in phone_numbers:
        if isinstance(phone, dict):
            country_code = phone.get("countryCode", "")
            prefix = phone.get("prefix", "")
            number = phone.get("number", "")
            full_number = f"{country_code}{prefix}{number}".replace(" ", "")
            if full_number:
                cleaned.append(full_number)
    return "; ".join(cleaned) if cleaned else ""



def _clean_user_data(
    df: DataFrame,
    columns: Optional[List[str]] = None,
    filter_type: Optional[str] = None
) -> DataFrame:
    """Clean and format user data from an AMS API response.

    Processes raw user data by creating an 'about' column, cleaning phone numbers, flattening group/role data,
    renaming columns, and selecting/reordering columns based on the provided options.

    Args:
        df (DataFrame): The raw DataFrame containing user data from the API.
        columns (Optional[List[str]]): Specific columns to include in the output DataFrame (default: None).
        filter_type (Optional[str]): The type of filter used ('username', 'email', 'group', 'about') (default: None).

    Returns:
        DataFrame: A cleaned DataFrame with renamed and reordered columns.

    Raises:
        AMSError: If no users are found when filtering by 'about'.
    """

    if "about" not in df.columns:
        df["about"] = df["firstName"] + " " + df["lastName"]
    
    if "phoneNumbers" in df.columns:
        df["phoneNumbers"] = df["phoneNumbers"].apply(_clean_phone_numbers)
    else:
        df["phoneNumbers"] = ""
    
    if "groupsAndRoles" in df.columns:
        df = _flatten_groups_and_roles(df)
    
    rename_map = {
        "userId": "user_id",
        "about": "about",
        "firstName": "first_name",
        "lastName": "last_name",
        "dob": "dob",
        "username": "username",
        "emailAddress": "email",
        "uuid": "uuid",
        "middleName": "middle_name",
        "knownAs": "known_as",
        "sex": "sex",
        "phoneNumbers": "phone_number"
    }
    df = df.rename(columns=rename_map)
    
    desired_columns = [
        "user_id", "about", "first_name", "last_name", "dob", "username", "email",
        "uuid", "middle_name", "known_as", "sex", "role", "athlete_group", "coach_group", "phone_number"
    ]
    
    if columns:
        available_columns = set(df.columns)
        requested_columns = set(columns)
        missing_columns = requested_columns - available_columns
        
        if filter_type == "about" and missing_columns:
            groups_and_roles_columns = {'role', 'athlete_group', 'coach_group'}
            missing_groups_and_roles = missing_columns & groups_and_roles_columns
            if missing_groups_and_roles:
                print(f"ℹ Warning: When using 'about' as the user_key in UserFilter, columns {missing_groups_and_roles} are not returned. "
                      "To return these columns, use one of 'username' or 'email' as the user_key in this filter.")
            other_missing = missing_columns - groups_and_roles_columns
            if other_missing:
                print(f"ℹ Warning: Columns {other_missing} not available in user data.")
        elif missing_columns:
            print(f"ℹ Warning: Columns {missing_columns} not available in user data.")
        
        final_columns = [col for col in columns if col in df.columns]
    else:
        final_columns = [col for col in desired_columns if col in df.columns]
    
    return df[final_columns]



def _transform_group_data(
        df: DataFrame, 
        guess_col_type: bool = False
    ) -> DataFrame:
    """Transform a group DataFrame by optionally guessing column types.

    Args:
        df (DataFrame): The DataFrame containing group data.
        guess_col_type (bool): Whether to infer column data types (default: False).

    Returns:
        DataFrame: The transformed DataFrame.
    """
    if guess_col_type:
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass
    return df



def _clean_user_data_for_save(df: DataFrame, preserve_columns: Optional[List[str]] = None) -> DataFrame:
    """Clean user data DataFrame for creating or updating users via /api/v2/person/save.

    Args:
        df (DataFrame): The DataFrame containing user data.
        preserve_columns (Optional[List[str]]): Columns to preserve without renaming (e.g., 'user_id', 'about').

    Returns:
        DataFrame: Cleaned DataFrame with API-compatible column names and default values.
    """
    df = df.copy()
    preserve_columns = preserve_columns or []

    rename_dict = {
        'user_id': 'user_id',  # Preserve user_id
        'first_name': 'firstName',
        'last_name': 'lastName',
        'username': 'username',
        'email': 'emailAddress',
        'dob': 'dateOfBirth',
        'password': 'password',
        'active': 'active',
        'uuid': 'uuid',
        'known_as': 'knownAs',
        'middle_names': 'middleNames',
        'language': 'language',
        'sidebar_width': 'sidebarWidth',
        'sex': 'sex'
    }
    # Exclude preserve_columns from renaming
    rename_dict = {k: v for k, v in rename_dict.items() if k not in preserve_columns}
    df = df.rename(columns=rename_dict)

    # Ensure required fields are strings and handle NaN
    for col in ['firstName', 'lastName', 'username', 'emailAddress', 'dateOfBirth', 'password', 'knownAs', 'middleNames', 'language', 'sidebarWidth', 'uuid', 'sex']:
        if col in df.columns and col not in preserve_columns:
            df[col] = df[col].astype(str).replace('nan', '')

    # Handle active as boolean
    if 'active' in df.columns and 'active' not in preserve_columns:
        df['active'] = df['active'].fillna(False).astype(bool)

    # Preserve non-standard columns (e.g., about), but keep user_id as integer
    for col in preserve_columns:
        if col in df.columns and col != 'user_id':
            df[col] = df[col].astype(str).replace('nan', '')
        elif col == 'user_id' and col in df.columns:
            df[col] = df[col].astype(int)  # Ensure user_id remains integer

    return df



def _get_update_columns(df: DataFrame, user_key: str) -> Tuple[Dict[str, str], List[str]]:
    """Get the column mapping and updatable columns for edit_user.

    Args:
        df (DataFrame): The cleaned DataFrame containing user data.
        user_key (str): The user identifier column in df.

    Returns:
        Tuple[Dict[str, str], List[str]]: The column mapping and list of updatable columns.
    """
    column_mapping = {
        "firstName": "firstName",
        "lastName": "lastName",
        "username": "username",
        "emailAddress": "emailAddress",
        "dateOfBirth": "dateOfBirth",
        "password": "password",
        "active": "active",
        "knownAs": "knownAs",
        "middleNames": "middleNames",
        "language": "language",
        "sidebarWidth": "sidebarWidth",
        "uuid": "uuid",
        "sex": "sex"
    }
    update_columns = [col for col in df.columns if col in column_mapping and col != user_key]
    return column_mapping, update_columns