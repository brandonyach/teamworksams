import os
import pandas as pd
from pandas import DataFrame
from pathlib import Path
from typing import Optional, List, Tuple
from .file_option import FileUploadOption
from .utils import AMSError


def _validate_file_df(df: DataFrame, user_key: str, mapping_col: str = "attachment_id", require_mapping_col: bool = True) -> DataFrame:
    """Validate the file DataFrame for required columns, duplicates, and data types.

#     Args:
#         df (DataFrame): The DataFrame to validate.
#         user_key (str): The user identifier column name (e.g., 'username').
#         mapping_col (str): The column name for matching events (default: 'attachment_id').
#         require_mapping_col (bool): Whether to require the mapping_col column (default: True).

#     Returns:
#         DataFrame: Validated DataFrame with string-converted columns.

#     Raises:
#         AMSError: If required columns are missing, duplicates are found, or data types are invalid.
#     """
    if df.empty:
        return DataFrame(columns=[user_key, "file_name", mapping_col] if require_mapping_col else [user_key, "file_name"])
    
    required_columns = [user_key, "file_name"]
    if require_mapping_col:
        required_columns.append(mapping_col)
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise AMSError(f"Missing required columns in file_df: {missing_columns}", function="validate_file_df")

    df = df.copy()
    dtype_changes = {}
    for col in required_columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            if col == mapping_col and require_mapping_col:
                print(f"⚠️ Warning: Column '{col}' contains numeric values; converting to strings to prevent float conversion.")
            dtype_changes[col] = 'string'

    if dtype_changes:
        df = df.astype(dtype_changes)

    if df["file_name"].duplicated().any():
        duplicates = df[df["file_name"].duplicated(keep=False)]["file_name"].tolist()
        raise AMSError(f"Duplicate file names found in file_df: {duplicates}", function="validate_file_df")
    if require_mapping_col and df[mapping_col].duplicated().any():
        duplicates = df[df[mapping_col].duplicated(keep=False)][mapping_col].tolist()
        raise AMSError(f"Duplicate values found in file_df for '{mapping_col}': {duplicates}", function="validate_file_df")

    return df
    

def _validate_output_directory(output_dir: Optional[str], function: str) -> str:
    """Validate and prepare the output directory for file operations.

    Args:
        output_dir (Optional[str]): The directory to validate. If None, uses the current working directory.
        function (str): The name of the calling function for error reporting.

    Returns:
        str: The validated directory path.

    Raises:
        AMSError: If the directory is not writable or cannot be created.
    """
    if output_dir is None:
        output_dir = os.getcwd()
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        elif not os.access(output_dir, os.W_OK):
            raise AMSError(
                f"Directory '{output_dir}' is not writable. Please specify a writable directory.",
                function=function
            )
    except OSError as e:
        raise AMSError(
            f"Failed to create or access directory '{output_dir}': {str(e)}. Ensure the path is valid and writable.",
            function=function
        )
    return output_dir


def _validate_file_path(file_dir: str, file_names: List[str], function: str, is_avatar: bool = False, option: Optional[FileUploadOption] = None) -> Tuple[List[Tuple[Path, str]], List[Tuple[str, str]]]:
    """Validate a list of file names for existence and type, returning valid and invalid files.

    Args:
        file_dir (str): Directory containing the files.
        file_names (List[str]): List of file names to validate.
        function (str): Name of the calling function for error reporting.
        is_avatar (bool): If True, validates only avatar-compatible image types. Defaults to False.
        option (Optional[FileUploadOption]): Configuration for interactive mode. Defaults to None.

    Returns:
        Tuple[List[Tuple[Path, str]], List[Tuple[str, str]]]: A tuple containing:
            - List of (file_path, file_name) tuples for valid files.
            - List of (file_name, reason) tuples for invalid files.

    Raises:
        AMSError: If the directory does not exist or no valid files are found.
    """
    file_dir = Path(file_dir).resolve()
    if not file_dir.is_dir():
        raise AMSError(f"Directory '{file_dir}' does not exist", function=function)

    valid_extensions = {'.png', '.jpg', '.jpeg'} if is_avatar else {'.pdf', '.doc', '.docx', '.txt', '.csv', '.png', '.jpg', '.jpeg', '.gif', '.heic', '.HEIC', '.xls', '.xlsx', '.xlsm', '.tiff', '.tif', '.odt', '.mp4', '.MP4', '.zip', '.ZIP', '.ppt', '.pptx', '.eml'}
    valid_files = []
    invalid_files = []

    for file_name in file_names:
        file_path = file_dir / file_name
        if file_path.is_file():
            ext = file_path.suffix.lower()
            if ext in valid_extensions:
                valid_files.append((file_path, file_name))
            else:
                invalid_files.append((file_name, f"Invalid file type '{ext}'. Allowed: {', '.join(valid_extensions)}"))
        else:
            invalid_files.append((file_name, f"File not found in '{file_dir}'"))

    if invalid_files and option and option.interactive_mode:
        print(f"⚠️ Skipping {len(invalid_files)} invalid files:")
        for file_name, reason in invalid_files:
            print(f"  - '{file_name}': {reason}")

    if not valid_files:
        raise AMSError(f"No valid files found in '{file_dir}' for provided file names", function=function)

    return valid_files, invalid_files