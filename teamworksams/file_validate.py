import os
from pandas import DataFrame
from pathlib import Path
from typing import Optional, List, Tuple
from .utils import AMSError

def _validate_file_df(df: DataFrame, user_key: str, require_attachment_id: bool = True) -> None:
    """Validate the file DataFrame for required columns and duplicates.

    Args:
        df (DataFrame): The DataFrame to validate.
        user_key (str): The user identifier column name (e.g., 'username').
        require_attachment_id (bool): Whether to require the 'attachment_id' column (default: True).

    Raises:
        AMSError: If required columns are missing or duplicates are found.
    """
    required_columns = [user_key, "file_name"]
    if require_attachment_id:
        required_columns.append("attachment_id")
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise AMSError(f"Missing required columns in file_df: {missing_columns}", function="validate_file_df")

    if df["file_name"].duplicated().any():
        duplicates = df[df["file_name"].duplicated(keep=False)]["file_name"].tolist()
        raise AMSError(f"Duplicate file names found in file_df: {duplicates}", function="validate_file_df")
    if require_attachment_id and df["attachment_id"].duplicated().any():
        duplicates = df[df["attachment_id"].duplicated(keep=False)]["attachment_id"].tolist()
        raise AMSError(f"Duplicate attachment IDs found in file_df: {duplicates}", function="validate_file_df")

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

def _validate_file_path(file_dir: str, file_names: List[str], function: str, is_avatar: bool = False) -> List[Tuple[Path, str]]:
    """Validate a list of file names for existence and type.

    Args:
        file_dir (str): The directory containing the files.
        file_names (List[str]): List of file names to validate.
        function (str): The name of the calling function for error reporting.
        is_avatar (bool): Whether to validate for avatar files (PNG, JPG, JPEG only). Default: False.

    Returns:
        List[Tuple[Path, str]]: A list of tuples containing the resolved Path and file name for valid files.

    Raises:
        AMSError: If no valid files are found.
    """
    file_dir = Path(file_dir).resolve()
    if not file_dir.is_dir():
        raise AMSError(f"Directory '{file_dir}' does not exist", function=function)

    valid_extensions = {'.png', '.jpg', '.jpeg'} if is_avatar else {'.pdf', '.doc', '.docx', '.txt', '.csv', '.png', '.jpg', '.jpeg', '.gif'}
    valid_files = []

    for file_name in file_names:
        file_path = file_dir / file_name
        if file_path.is_file():
            ext = file_path.suffix.lower()
            if ext in valid_extensions:
                valid_files.append((file_path, file_name))
            else:
                print(f"⚠️ Skipping '{file_name}': Invalid file type '{ext}'. Allowed: {', '.join(valid_extensions)}")
        else:
            print(f"⚠️ Skipping '{file_name}': File not found in '{file_dir}'")

    if not valid_files:
        raise AMSError(f"No valid files found in '{file_dir}' for provided file names", function=function)

    return valid_files