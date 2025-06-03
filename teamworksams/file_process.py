import pandas as pd
from pandas import DataFrame
import os
from typing import List, Dict, Tuple, Optional
from requests_toolbelt.multipart.encoder import MultipartEncoder
import mimetypes
from pathlib import Path
from .file_option import FileUploadOption
from .user_fetch import _fetch_user_ids
from .utils import AMSError, AMSClient
from .file_validate import _validate_output_directory


def _format_file_reference(file_df: DataFrame, file_field_name: str) -> DataFrame:
    """Format the file reference in the format 'file_id|server_file_name'.

    Args:
        file_df (DataFrame): The DataFrame containing file_id and server_file_name.
        file_field_name (str): The name of the file upload field (e.g., 'Upload Attachment').

    Returns:
        DataFrame: The DataFrame with the formatted file reference column.
    """
    file_df = file_df.copy()
    file_df[file_field_name] = file_df["file_id"].astype(str) + "|" + file_df["server_file_name"]
    return file_df


def _map_user_ids_to_file_df(
    file_df: DataFrame,
    user_key: str,
    client: AMSClient,
    interactive_mode: bool,
    cache: bool
) -> Tuple[DataFrame, DataFrame]:
    """Map user IDs to a file DataFrame and return updated DataFrame and failed mappings."""
    failed_df = DataFrame(columns=[user_key, "file_name", "reason"])
    
    user_values = file_df[user_key].unique().tolist()
    
    try:
        user_ids, user_data = _fetch_user_ids(client=client, cache=cache)
    except AMSError as e:
        if interactive_mode:
            print(f"⚠️ Failed to retrieve user data: {str(e)}")
        return file_df, pd.concat([
            failed_df,
            DataFrame({
                user_key: file_df[user_key],
                "file_name": file_df["file_name"],
                "reason": f"Failed to retrieve user data: {str(e)}"
            })
        ], ignore_index=True)
    
    if not user_ids:
        if interactive_mode:
            print(f"⚠️ No users found for the provided {user_key} values")
        return file_df, pd.concat([
            failed_df,
            DataFrame({
                user_key: file_df[user_key],
                "file_name": file_df["file_name"],
                "reason": f"No users found for the provided {user_key} values"
            })
        ], ignore_index=True)
    
    if user_data is None:
        user_data = DataFrame()
    
    user_data = user_data.rename(columns={"userId": "user_id"})
    user_data["user_id"] = user_data["user_id"].astype(str)
    if user_key == "about":
        user_data["about"] = (user_data["firstName"].str.strip() + " " + user_data["lastName"].str.strip())
        file_df = file_df.copy()
        file_df[user_key] = file_df[user_key].str.strip()
    
    merge_key = user_key if user_key != "email" else "emailAddress"
    # Preserve string types in file_df
    file_df = file_df.copy()
    for col in file_df.columns:
        if col not in ["user_id"]:
            file_df[col] = file_df[col].astype(str)
    file_df = file_df.merge(
        user_data[["user_id", merge_key]],
        left_on=user_key,
        right_on=merge_key,
        how="left"
    )
    
    unmapped = file_df[file_df["user_id"].isna()]
    if not unmapped.empty:
        failed_df = pd.concat([
            failed_df,
            DataFrame({
                user_key: unmapped[user_key],
                "file_name": unmapped["file_name"],
                "reason": f"User not found for {user_key} value"
            })
        ], ignore_index=True)
        file_df = file_df[file_df["user_id"].notna()]
    
    return file_df, failed_df


def _build_result_df(
    data: Dict,
    user_key: str,
    is_event: bool = False
) -> DataFrame:
    """Build a result DataFrame for success or failure with consistent dtypes.

    Args:
        data (Dict): Dictionary with result data (e.g., user_key, file_name, user_id/event_id, file_id, server_file_name, status, reason).
        user_key (str): The user identifier column name.
        is_event (bool): Whether the result is for an event (uses event_id) or avatar (uses user_id). Default: False.

    Returns:
        DataFrame: A DataFrame with specified columns and dtypes.
    """
    id_col = "event_id" if is_event else "user_id"
    columns = [user_key, "file_name", id_col, "file_id", "server_file_name", "status", "reason"]

    # Handle batch inputs (e.g., multiple failures)
    user_keys = data.get(user_key)
    file_names = data.get("file_name")
    ids = data.get(id_col)
    file_ids = data.get("file_id")
    server_file_names = data.get("server_file_name")
    status = data.get("status")
    reasons = data.get("reason")

    # Convert scalars to lists for consistency
    if not isinstance(user_keys, list):
        user_keys = [user_keys]
        file_names = [file_names]
        ids = [ids]
        file_ids = [file_ids]
        server_file_names = [server_file_names]
        status = [status]
        reasons = [reasons]

    # Build DataFrame row by row
    rows = []
    for uk, fn, id_val, fid, sfn, st, rs in zip(user_keys, file_names, ids, file_ids, server_file_names, status, reasons):
        rows.append({
            user_key: uk,
            "file_name": fn,
            id_col: str(id_val) if id_val is not None else None,
            "file_id": str(fid) if fid is not None else None,
            "server_file_name": sfn,
            "status": st,
            "reason": rs
        })

    return DataFrame(rows, columns=columns).astype({
        user_key: "object",
        "file_name": "object",
        id_col: "object",
        "file_id": "object",
        "server_file_name": "object",
        "status": "object",
        "reason": "object"
    })


def _download_attachment(
    client: AMSClient, 
    attachment_url: str, 
    file_name: str, 
    output_dir: Optional[str] = None
) -> str:
    """Download an attachment from a URL and save it to a local file.

    Args:
        client (AMSClient): The authenticated AMSClient instance to use for the download.
        attachment_url (str): The URL of the attachment to download.
        file_name (str): The name to give the downloaded file.
        output_dir (Optional[str]): The directory to save the file in. If None, uses the current working directory.

    Returns:
        str: The full path to the downloaded file.

    Raises:
        AMSError: If the directory is not writable or the download fails.
    """
    output_dir = _validate_output_directory(output_dir, function="_download_attachment")

    full_path = os.path.join(output_dir, file_name)
    response = client.session.get(attachment_url)
    if response.status_code == 200:
        with open(full_path, "wb") as f:
            f.write(response.content)
        return full_path
    else:
        raise AMSError(f"Failed to download attachment from {attachment_url}: {response.status_code}")
    

def _validate_and_prepare_files(
    mapping_df: DataFrame,
    user_key: str,
    file_dir: Path,
    failed_files: set,
    failed_results: List[DataFrame],
    option: FileUploadOption,
    is_event: bool = False
) -> Tuple[Optional[List[str]], Optional[DataFrame]]:
    """Validate file existence and prepare files for upload.

    Args:
        mapping_df (DataFrame): DataFrame with user_key and file_name columns.
        user_key (str): The user identifier column in mapping_df.
        file_dir (Path): Resolved directory containing the files.
        failed_files (set): Set to track failed file names (updated in-place).
        failed_results (List[DataFrame]): List to store failed result DataFrames (updated in-place).
        option (FileUploadOption): Options for interactive mode and saving results.
        is_event (bool): Whether the result is for an event (uses event_id) or avatar (uses user_id). Default: False.

    Returns:
        Tuple[Optional[List[str]], Optional[DataFrame]]: 
            - List of valid file names to upload, or None if no valid files.
            - Result DataFrame if no valid files (for early return), or None if files are valid.
    """
    files_to_upload = []
    id_col = "event_id" if is_event else "user_id"
    for _, row in mapping_df.iterrows():
        file_path = file_dir / row["file_name"]
        if file_path.is_file():
            files_to_upload.append(row["file_name"])
        else:
            failed_files.add(row["file_name"])
            failed_results.append(_build_result_df({
                user_key: row[user_key],
                "file_name": row["file_name"],
                id_col: row[id_col] if id_col in row else None,
                "file_id": None,
                "server_file_name": None,
                "status": "FAILED",
                "reason": f"File '{row['file_name']}' not found in '{file_dir}'"
            }, user_key, is_event=is_event))

    if not files_to_upload:
        results_df = pd.concat(failed_results, ignore_index=True)
        if option.interactive_mode:
            print(f"⚠️ Failed to {'attach' if is_event else 'update avatars for'} {len(results_df)} {'files' if is_event else 'users'}:")
            print(results_df.to_string(index=False))
        if option.save_to_file:
            results_df.to_csv(option.save_to_file, index=False)
            print(f"ℹ Saved results to '{option.save_to_file}'")
        return None, results_df

    return files_to_upload, None


    
def _upload_single_file(file_path: Path, file_name: str, client: AMSClient, processor_key: str) -> Dict:
    """Upload a single file to the AMS API.

    Args:
        file_path (Path): Path to the file.
        file_name (str): Name of the file.
        client (AMSClient): Authenticated AMSClient instance.
        processor_key (str): Processor key for the upload ('document-key' or 'avatar-key').

    Returns:
        Dict: Dictionary with 'file_name', 'file_id', and 'server_file_name'.

    Raises:
        AMSError: If upload or status retrieval fails.
    """
    if not client.authenticated:
        client.login()

    skype_name = client.login_data.get("user", {}).get("skypeName")
    if not skype_name:
        raise AMSError("skypeName not found in login response", function="_upload_single_file")

    base_url = client.url.rsplit('/', 1)[0]
    file_upload_url = f"{base_url}/x/fileupload"
    mime_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"

    with open(file_path, 'rb') as f:
        multipart_data = MultipartEncoder(
            fields={
                'session-token': skype_name,
                'filename': file_name,
                'processorkey': processor_key,
                'filedata': (file_name, f, mime_type)
            }
        )
        headers = client.headers.copy()
        headers['Content-Type'] = multipart_data.content_type
        response = client.session.post(file_upload_url, data=multipart_data, headers=headers)

    if response.status_code != 200:
        raise AMSError(
            f"Failed to upload file '{file_name}': Status {response.status_code}",
            function="_upload_single_file",
            endpoint=file_upload_url
        )

    status_url = client._AMS_url("fileupload/getUploadStatus", api_version="v2")
    status_response = client.session.post(status_url, json={}, headers=client.headers)

    if status_response.status_code != 200:
        raise AMSError(
            f"Failed to retrieve upload status for '{file_name}': Status {response.status_code}",
            function="_upload_single_file",
            endpoint=status_url
        )

    try:
        status_data = status_response.json()
    except ValueError:
        raise AMSError(
            f"Invalid response format for upload status of '{file_name}'",
            function="_upload_single_file"
        )

    if status_data.get("uploadStatus", {}).get("error", True) or not status_data.get("data"):
        error_message = status_data.get("uploadStatus", {}).get("message", "Unknown error")
        raise AMSError(
            f"Upload failed for '{file_name}': {error_message}",
            function="_upload_single_file"
        )

    file_id = status_data["data"][0]["value"].get("id")
    if file_id is None:
        raise AMSError(
            f"Failed to retrieve file ID for '{file_name}'",
            function="_upload_single_file"
        )

    server_file_name = status_data["data"][0]["value"].get("name")
    return {
        "file_name": file_name,
        "file_id": file_id,
        "server_file_name": server_file_name
    }
    
    
def _create_avatar_mapping_df(file_dir: str, user_key: str) -> DataFrame:
    """Create a DataFrame from a folder of image files with columns for user_key and file_name.

    Args:
        file_dir (str): Path to the folder containing image files.
        user_key (str): Column name for user identification (e.g., 'username', 'about').

    Returns:
        DataFrame: DataFrame with columns [user_key, 'file_name'].

    Raises:
        AMSError: If the folder does not exist, is not a directory, or contains no valid image files.
    """
    image_extensions = {'.png', '.jpg', '.jpeg', '.svg', '.gif', '.webp', '.tiff', '.heic', '."HEIC'}
    data = []

    folder = Path(file_dir)
    if not folder.is_dir():
        raise AMSError(f"The folder {file_dir} does not exist or is not a directory.", function="create_avatar_mapping_df")

    for file_path in folder.iterdir():
        if file_path.suffix.lower() in image_extensions:
            person_name = file_path.stem
            data.append({
                user_key: person_name,
                'file_name': file_path.name
            })

    if not data:
        raise AMSError(f"No valid image files found in {file_dir}. Supported extensions: {', '.join(image_extensions)}", function="create_avatar_mapping_df")

    df = pd.DataFrame(data)
    if df['file_name'].duplicated().any():
        duplicates = df[df['file_name'].duplicated(keep=False)]['file_name'].tolist()
        raise AMSError(f"Duplicate file names found in {file_dir}: {duplicates}", function="create_avatar_mapping_df")

    return df