import os
import pandas as pd
from typing import Optional
from pandas import DataFrame
from datetime import datetime
from tqdm import tqdm
from pathlib import Path
from .utils import AMSClient, AMSError, get_client
from .import_main import update_event_data
from .import_option import UpdateEventOption
from .file_option import FileUploadOption
from .file_validate import _validate_file_df, _validate_file_path
from .file_process import _format_file_reference, _map_user_ids_to_file_df, _build_result_df, _validate_and_prepare_files, _upload_single_file, _create_avatar_mapping_df
from .user_fetch import _fetch_all_user_data, _update_single_user
from .user_process import _map_user_updates
from .user_validate import _validate_user_key
from .user_option import UserOption
from .export_main import get_event_data
from .export_option import EventOption
from .export_filter import EventFilter


def upload_and_attach_to_events(
    mapping_df: DataFrame,
    file_dir: str,
    user_key: str,
    form: str,
    file_field_name: str,
    url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    option: Optional[FileUploadOption] = None,
    client: Optional[AMSClient] = None,
    mapping_col: str = "attachment_id"
) -> DataFrame:
    """Upload files and attach them to events in an AMS Event Form.

    Matches the provided :class:`pandas.DataFrame` to users and events using `user_key`
    and `mapping_col` (default 'attachment_id'), uploads valid files from `file_dir`,
    and attaches them to the specified `file_field_name` in the AMS Event Form using
    file references (e.g., `file_id|server_file_name`). Preserves existing event fields
    during updates. Returns a :class:`pandas.DataFrame` with upload and attachment
    results, including successes and failures. See :ref:`uploading_files` for
    detailed workflows.

    Args:
        mapping_df (:class:`pandas.DataFrame`): DataFrame with columns:
            - `user_key` (str): User identifier (e.g., 'username', 'email', 'about',
            'uuid').
            - `file_name` (str): File name in `file_dir` (e.g., 'doc1.pdf').
            - `mapping_col` (str): Matches the event form’s field (e.g.,
            'attachment_id'). Used for mapping files to events. Must not be empty.
        file_dir (str): Directory path containing files to upload (e.g.,
            '/path/to/files'). Must be a valid directory.
        user_key (str): Column name in `mapping_df` for user identification. Must be
            one of 'username', 'email', 'about', or 'uuid'.
        form (str): Name of the AMS Event Form (e.g., 'Document Store'). Must exist
            and contain `file_field_name`.
        file_field_name (str): File upload field in the form (e.g., 'attachment').
            Must be a valid file field.
        mapping_col (str): Column name in `mapping_df` and event form for matching
            events to files (e.g., 'attachment_id'). Defaults to 'attachment_id'.
        url (str): AMS instance URL (e.g., 'https://example.smartabase.com/site').
            Must include a valid site name.
        username (Optional[str]): Username for authentication. If None, uses
            :envvar:`AMS_USERNAME` or :class:`keyring` credentials. Defaults to None.
        password (Optional[str]): Password for authentication. If None, uses
            :envvar:`AMS_PASSWORD` or :class:`keyring` credentials. Defaults to None.
        option (FileUploadOption, optional): Configuration options for
            interactive feedback (e.g., progress bars), caching, and saving results
            to a CSV. Defaults to None (uses default :class:`FileUploadOption` with
            `interactive_mode=True`).
        client (AMSClient, optional): Pre-authenticated client from
            :func:`get_client`. If None, a new client is created. Defaults to None.

    Returns:
        :class:`pandas.DataFrame`: Results with columns:
            - user_key (str): The user identifier from `mapping_df`.
            - file_name (str): The file name from `mapping_df`.
            - event_id (str): Matched event ID (None if failed).
            - user_id (str): Matched user ID (None if failed).
            - file_id (str): Uploaded file ID (None if failed).
            - server_file_name (str): Server-assigned file name (None if failed).
            - status (str): 'SUCCESS' or 'FAILED'.
            - reason (str): Failure reason (None if successful).

    Raises:
        :class:`AMSError`: If:
            - `file_dir` is not a valid directory.
            - User data retrieval fails (e.g., invalid credentials, API errors).
            - No users are found in the AMS instance.
            - Event data retrieval fails (e.g., invalid form name, API errors).
            - No events are found for the specified form and users.
            - The event form lacks an 'attachment_id' field.
            - File validation fails (e.g., unsupported file type).
            - File upload or event update fails (e.g., network issues, server errors).

    Example:
        >>> import pandas as pd
        >>> from teamworksams import upload_and_attach_to_events, FileUploadOption
        >>> mapping_df = DataFrame({
        ...     "username": ["user1", "user2"],
        ...     "file_name": ["doc1.pdf", "doc2.pdf"],
        ...     "attachment_id": ["ATT123", "ATT456"]
        ... })
        >>> results = upload_and_attach_to_events(
        ...     mapping_df = mapping_df,
        ...     mapping_col = "attachment_id",
        ...     user_key = "about",
        ...     file_dir = "/path/to/files",
        ...     form = "Document Store",
        ...     file_field_name = "attachment",
        ...     url = "https://example.smartabase.com/site",
        ...     username = "user",
        ...     password = "password",
        ...     option = FileUploadOption(interactive_mode = True, save_to_file = "results.csv")
        )
        ℹ Fetching all user data from site to match provided files...
        ℹ Retrieved 50 users.
        ℹ Fetching all event data from 'Document Store' to match provided files...
        ℹ Retrieved 500 events.
        ℹ Merged 500 rows from mapping_df with 1500 events from 'Document Store', resulting in 1500 matched records.
        ℹ Found 450 valid files in directory matching 500 mapping_df records.
        ℹ Finding a match for 2 events from mapping_df...
        ℹ Identified and mapped 2 events from mapping_df.
        ℹ Uploading 450 files...
        Uploading files: 100%|██████████| 450/450 [00:02<00:00,  1.00s/it]
        ℹ Preparing to update 500 events corresponding to 450 uploaded files for 'Document Store'.
        ℹ Updating 500 events for 'Document Store'
        ✔ Processed 500 events for 'Document Store'                   
        ℹ Form: Document Store
        ℹ Result: Success
        ℹ Records updated: 500
        ℹ Records attempted: 500
        ✔ Successfully attached 450 files to 500 events.
        ℹ Saved results to 'results.csv'   
        >>> print(results.head())
           username file_name event_id user_id file_id server_file_name status reason
        0   user1   doc1.pdf  123456  78901   94196 doc1_1747654002120.pdf SUCCESS None
        1   user2   doc2.pdf  123457  78902   94197 doc2_1747654003484.pdf SUCCESS None
    """
    
    option = option or FileUploadOption(interactive_mode=True)
    client = client or get_client(url, username, password, cache=option.cache, interactive_mode=option.interactive_mode)

    # Validate mapping_df
    initial_rows = len(mapping_df)
    mapping_df = _validate_file_df(mapping_df, user_key, mapping_col=mapping_col, require_mapping_col=True)
    _validate_user_key(user_key)

    # Initialize result lists
    success_results = []
    failed_results = []

    # Validate file directory
    file_dir = Path(file_dir).resolve()
    if not file_dir.is_dir():
        raise AMSError(f"'{file_dir}' is not a valid directory", function="upload_and_attach_to_events")

    # Pre-validate file extensions
    valid_extensions = {'.pdf', '.doc', '.docx', '.txt', '.csv', '.png', '.jpg', '.jpeg', '.gif', '.heic', '.HEIC', '.xls', '.xlsx', '.xlsm', '.tiff', '.tif', '.odt', '.zip', '.ZIP', '.ppt', '.pptx', '.eml', '.bmp'}
    
    invalid_files = []
    for file_name in mapping_df["file_name"]:
        ext = Path(file_name).suffix.lower()
        if ext not in valid_extensions:
            invalid_files.append((file_name, f"Invalid file type '{ext}'. Allowed: {', '.join(valid_extensions)}"))
    if invalid_files and option.interactive_mode:
        print(f"⚠️ Skipping {len(invalid_files)} invalid files:")
        for file_name, reason in invalid_files:
            print(f"  - '{file_name}': {reason}")
    if invalid_files:
        failed_results.append(_build_result_df({
            user_key: [mapping_df[mapping_df["file_name"] == file_name][user_key].iloc[0] for file_name, _ in invalid_files],
            "file_name": [file_name for file_name, _ in invalid_files],
            "event_id": [None] * len(invalid_files),
            "user_id": [None] * len(invalid_files),
            "file_id": [None] * len(invalid_files),
            "server_file_name": [None] * len(invalid_files),
            "status": ["FAILED"] * len(invalid_files),
            "reason": [reason for _, reason in invalid_files]
        }, user_key, is_event=True))

    # Match mapping_df to users
    if option.interactive_mode:
        print(f"ℹ Fetching all user data from site to match provided files...")
    try:
        user_df = _fetch_all_user_data(
            url=url,
            username=username,
            password=password,
            option=UserOption(interactive_mode=False, cache=option.cache),
            client=client
        )
        if option.interactive_mode:
            print(f"ℹ Retrieved {len(user_df)} users.")
    except AMSError as e:
        raise AMSError(f"Failed to retrieve user data: {str(e)}", function="upload_and_attach_to_events")

    if user_df.empty:
        raise AMSError("No users found.", function="upload_and_attach_to_events")

    # Map users to get user_id
    mapping_df, failed_matches = _map_user_ids_to_file_df(
        mapping_df, user_key, client, option.interactive_mode, option.cache
    )
    if not failed_matches.empty:
        failed_results.append(_build_result_df({
            user_key: failed_matches[user_key].tolist(),
            "file_name": failed_matches["file_name"].tolist(),
            "event_id": [None] * len(failed_matches),
            "user_id": failed_matches["user_id"].tolist() if "user_id" in failed_matches else [None] * len(failed_matches),
            "file_id": [None] * len(failed_matches),
            "server_file_name": [None] * len(failed_matches),
            "status": ["FAILED"] * len(failed_matches),
            "reason": failed_matches["reason"].tolist()
        }, user_key, is_event=True))
        if option.interactive_mode:
            print(f"⚠️ {len(failed_matches)} files failed to match {user_key} values in user data.")

    if option.interactive_mode and len(mapping_df) > initial_rows:
        print(f"⚠️ Warning: mapping_df increased from {initial_rows} to {len(mapping_df)} rows due to duplicate {user_key} matches in user data.")
    
    if mapping_df.empty:
        results_df = pd.DataFrame(columns=[user_key, "file_name", "event_id", "user_id", "file_id", "server_file_name", "status", "reason"])
        if option.interactive_mode:
            print(f"⚠️ Failed to attach 0 files.")
        if option.save_to_file:
            results_df.to_csv(option.save_to_file, index=False)
            print(f"ℹ Saved results to '{option.save_to_file}'")
        return results_df

    # Cast potential numeric string columns to strings
    dtype_changes = {
        col: 'string'
        for col in [mapping_col] + [c for c in mapping_df.columns if c not in ["user_id", "event_id", "start_date", "end_date", "start_time", "end_time"]]
        if col in mapping_df.columns and pd.api.types.is_numeric_dtype(mapping_df[col])
    }
    if dtype_changes:
        mapping_df = mapping_df.astype(dtype_changes)

    # Match mapping_df to events
    if option.interactive_mode:
        print(f"ℹ Fetching event data from '{form}' to match provided files...")
        
    user_values = mapping_df[user_key].unique().tolist()
    end_date = datetime.now().strftime("%d/%m/%Y")
    start_date = "01/01/1970"
    
    try:
        event_df = get_event_data(
            form=form,
            start_date=start_date,
            end_date=end_date,
            url=url,
            username=username,
            password=password,
            filter=EventFilter(user_key=user_key, user_value=user_values),
            option=EventOption(interactive_mode=False, cache=option.cache),
            client=client
        )
        if option.interactive_mode:
            print(f"ℹ Retrieved {len(event_df)} events.")
        dtype_changes = {
            col: 'string'
            for col in event_df.columns
            if col not in ["user_id", "event_id", "start_date", "end_date", "start_time", "end_time"]
            and pd.api.types.is_numeric_dtype(event_df[col])
        }
        dtype_changes["event_id"] = 'string'
        if dtype_changes:
            event_df = event_df.astype(dtype_changes)
        event_df = event_df.drop(columns=["user_id", "about"], errors="ignore")
        
    except AMSError as e:
        failed_results.append(_build_result_df({
            user_key: mapping_df[user_key].tolist(),
            "file_name": mapping_df["file_name"].tolist(),
            "event_id": [None] * len(mapping_df),
            "user_id": mapping_df["user_id"].tolist() if "user_id" in mapping_df else [None] * len(mapping_df),
            "file_id": [None] * len(mapping_df),
            "server_file_name": [None] * len(mapping_df),
            "status": ["FAILED"] * len(mapping_df),
            "reason": [f"Failed to retrieve events: {str(e)}"] * len(mapping_df)
        }, user_key, is_event=True))
        results_df = pd.concat(failed_results, ignore_index=True)
        if option.interactive_mode:
            print(f"⚠️ Failed to attach {len(results_df)} files.")
        if option.save_to_file:
            results_df.to_csv(option.save_to_file, index=False)
            print(f"ℹ Saved results to '{option.save_to_file}'")
        return results_df

    if event_df.empty:
        failed_results.append(_build_result_df({
            user_key: mapping_df[user_key].tolist(),
            "file_name": mapping_df["file_name"].tolist(),
            "event_id": [None] * len(mapping_df),
            "user_id": mapping_df["user_id"].tolist() if "user_id" in mapping_df else [None] * len(mapping_df),
            "file_id": [None] * len(mapping_df),
            "server_file_name": [None] * len(mapping_df),
            "status": ["FAILED"] * len(mapping_df),
            "reason": [f"No events found for form '{form}'"] * len(mapping_df)
        }, user_key, is_event=True))
        results_df = pd.concat(failed_results, ignore_index=True)
        if option.interactive_mode:
            print(f"⚠️ Failed to attach {len(results_df)} files.")
        if option.save_to_file:
            results_df.to_csv(option.save_to_file, index=False)
            print(f"ℹ Saved results to '{option.save_to_file}'")
        return results_df

    if mapping_col not in event_df.columns:
        failed_results.append(_build_result_df({
            user_key: mapping_df[user_key].tolist(),
            "file_name": mapping_df["file_name"].tolist(),
            "event_id": [None] * len(mapping_df),
            "user_id": mapping_df["user_id"].tolist() if "user_id" in mapping_df else [None] * len(mapping_df),
            "file_id": [None] * len(mapping_df),
            "server_file_name": [None] * len(mapping_df),
            "status": ["FAILED"] * len(mapping_df),
            "reason": [f"Event form '{form}' does not have a '{mapping_col}' field"] * len(mapping_df)
        }, user_key, is_event=True))
        results_df = pd.concat(failed_results, ignore_index=True)
        if option.interactive_mode:
            print(f"⚠️ Failed to attach {len(results_df)} files.")
        if option.save_to_file:
            results_df.to_csv(option.save_to_file, index=False)
            print(f"ℹ Saved results to '{option.save_to_file}'")
        return results_df

    unmatched_ids = mapping_df[~mapping_df[mapping_col].isin(event_df[mapping_col])]
    if not unmatched_ids.empty:
        failed_results.append(_build_result_df({
            user_key: unmatched_ids[user_key].tolist(),
            "file_name": unmatched_ids["file_name"].tolist(),
            "event_id": [None] * len(unmatched_ids),
            "user_id": unmatched_ids["user_id"].tolist() if "user_id" in unmatched_ids else [None] * len(unmatched_ids),
            "file_id": [None] * len(unmatched_ids),
            "server_file_name": [None] * len(unmatched_ids),
            "status": ["FAILED"] * len(unmatched_ids),
            "reason": [f"No matching event found for {mapping_col}"] * len(unmatched_ids)
        }, user_key, is_event=True))
        mapping_df = mapping_df[mapping_df[mapping_col].isin(event_df[mapping_col])]

    if mapping_df.empty:
        results_df = pd.concat(failed_results, ignore_index=True)
        if option.interactive_mode:
            print(f"⚠️ Failed to attach {len(results_df)} files.")
        if option.save_to_file:
            results_df.to_csv(option.save_to_file, index=False)
            print(f"ℹ Saved results to '{option.save_to_file}'")
        return results_df

    # Merge with events
    pre_merge_rows = len(mapping_df)
    mapping_df = mapping_df.merge(
        event_df,
        left_on=mapping_col,
        right_on=mapping_col,
        how="left"
    )
    mapping_df = mapping_df[mapping_df["event_id"].notna()]
    if option.interactive_mode and not mapping_df.empty:
        print(f"ℹ Merged {pre_merge_rows} rows from mapping_df with {len(event_df)} events from '{form}', resulting in {len(mapping_df)} matched observations.")

    # Validate and prepare files for upload
    failed_files = set()
    files_to_upload, results_df = _validate_and_prepare_files(
        mapping_df, user_key, file_dir, failed_files, failed_results, option, is_event=True
    )
    if files_to_upload is None:
        return results_df

    # Validate file types for existing files
    try:
        files_to_upload, invalid_files = _validate_file_path(file_dir, files_to_upload, function="upload_and_attach_to_events", is_avatar=False, option=option)
        if invalid_files:
            failed_results.append(_build_result_df({
                user_key: [mapping_df[mapping_df["file_name"] == file_name][user_key].iloc[0] if file_name in mapping_df["file_name"].values else Path(file_name).stem for file_name, _ in invalid_files],
                "file_name": [file_name for file_name, _ in invalid_files],
                "event_id": [None] * len(invalid_files),
                "user_id": [None] * len(invalid_files),
                "file_id": [None] * len(invalid_files),
                "server_file_name": [None] * len(invalid_files),
                "status": ["FAILED"] * len(invalid_files),
                "reason": [reason for _, reason in invalid_files]
            }, user_key, is_event=True))
        if option.interactive_mode:
            matching_users = len(mapping_df[mapping_df["user_id"].notna()][user_key].unique())
            print(f"ℹ Found {len(files_to_upload)} valid files in directory for matching events on the site.")
            print(f"ℹ Uploading {len(files_to_upload)} files...")
            
    except AMSError as e:
        failed_results.append(_build_result_df({
            user_key: mapping_df[user_key].tolist(),
            "file_name": mapping_df["file_name"].tolist(),
            "event_id": mapping_df["event_id"].tolist(),
            "user_id": mapping_df["user_id"].tolist() if "user_id" in mapping_df else [None] * len(mapping_df),
            "file_id": [None] * len(mapping_df),
            "server_file_name": [None] * len(mapping_df),
            "status": ["FAILED"] * len(mapping_df),
            "reason": [str(e)] * len(mapping_df)
        }, user_key, is_event=True))
        results_df = pd.concat(failed_results, ignore_index=True)
        if option.interactive_mode:
            print(f"⚠️ Failed to attach {len(results_df)} files.")
        if option.save_to_file:
            results_df.to_csv(option.save_to_file, index=False)
            print(f"ℹ Saved results to '{option.save_to_file}'")
        return results_df

    # Upload files
    upload_results = []
    for file_path, file_name in tqdm(files_to_upload, desc="Uploading files", disable=not option.interactive_mode):
        if file_name in failed_files or file_name not in mapping_df["file_name"].values:
            continue
        try:
            upload_result = _upload_single_file(file_path, file_name, client, "document-key")
            if upload_result.get("file_id"):
                upload_result["file_id"] = str(upload_result["file_id"])
                upload_results.append(upload_result)
                # Track successful upload
                success_results.append(_build_result_df({
                    user_key: mapping_df[mapping_df["file_name"] == file_name][user_key].iloc[0],
                    "file_name": file_name,
                    "event_id": mapping_df[mapping_df["file_name"] == file_name]["event_id"].iloc[0],
                    "user_id": mapping_df[mapping_df["file_name"] == file_name]["user_id"].iloc[0] if "user_id" in mapping_df else None,
                    "file_id": upload_result["file_id"],
                    "server_file_name": upload_result["server_file_name"],
                    "status": "SUCCESS",
                    "reason": None
                }, user_key, is_event=True))
            else:
                failed_files.add(file_name)
                failed_results.append(_build_result_df({
                    user_key: mapping_df[mapping_df["file_name"] == file_name][user_key].iloc[0],
                    "file_name": file_name,
                    "event_id": mapping_df[mapping_df["file_name"] == file_name]["event_id"].iloc[0],
                    "user_id": mapping_df[mapping_df["file_name"] == file_name]["user_id"].iloc[0] if "user_id" in mapping_df else None,
                    "file_id": None,
                    "server_file_name": None,
                    "status": "FAILED",
                    "reason": "Upload failed: No file ID returned"
                }, user_key, is_event=True))
        except AMSError as e:
            failed_files.add(file_name)
            failed_results.append(_build_result_df({
                user_key: mapping_df[mapping_df["file_name"] == file_name][user_key].iloc[0],
                "file_name": file_name,
                "event_id": mapping_df[mapping_df["file_name"] == file_name]["event_id"].iloc[0],
                "user_id": mapping_df[mapping_df["file_name"] == file_name]["user_id"].iloc[0] if "user_id" in mapping_df else None,
                "file_id": None,
                "server_file_name": None,
                "status": "FAILED",
                "reason": f"Upload failed: {str(e)}"
            }, user_key, is_event=True))

    # Merge upload results
    upload_results_df = DataFrame(upload_results)
    mapping_df = mapping_df.merge(
        upload_results_df[["file_name", "file_id", "server_file_name"]],
        on="file_name",
        how="left"
    )
    mapping_df = mapping_df[mapping_df["file_id"].notna()]

    if mapping_df.empty:
        results_df = pd.concat(failed_results + success_results, ignore_index=True)
        if option.interactive_mode:
            print(f"⚠️ Failed to attach {len(results_df)} files.")
        if option.save_to_file:
            results_df.to_csv(option.save_to_file, index=False)
            print(f"ℹ Saved results to '{option.save_to_file}'")
        return results_df

    # Format file references and update events
    mapping_df = _format_file_reference(mapping_df, file_field_name)
    event_update_df = mapping_df.drop(columns=["file_name"], errors="ignore")
    try:
        if option.interactive_mode:
            print(f"ℹ Preparing to update {len(event_update_df)} events corresponding to {len(files_to_upload)} uploaded files for '{form}'.")
        update_event_data(
            df=event_update_df,
            form=form,
            url=url,
            username=username,
            password=password,
            option=UpdateEventOption(
                interactive_mode=option.interactive_mode,
                cache=option.cache,
                require_confirmation=False
            ),
            client=client
        )
    except AMSError as e:
        if option.interactive_mode:
            print(f"✖ ERROR - Failed to update events: {str(e)}")
        failed_results.append(_build_result_df({
            user_key: mapping_df[user_key].tolist(),
            "file_name": mapping_df["file_name"].tolist(),
            "event_id": mapping_df["event_id"].tolist(),
            "user_id": mapping_df["user_id"].tolist() if "user_id" in mapping_df else [None] * len(mapping_df),
            "file_id": mapping_df["file_id"].tolist(),
            "server_file_name": mapping_df["server_file_name"].tolist(),
            "status": ["FAILED"] * len(mapping_df),
            "reason": [f"Event update failed: {str(e)}"] * len(mapping_df)
        }, user_key, is_event=True))

    # Concatenate results
    
    # Concatenate results
    success_df = pd.concat(success_results, ignore_index=True) if success_results else DataFrame(
        columns=[user_key, "file_name", "user_id", "file_id", "server_file_name", "status", "reason"]
    )
    failed_df = pd.concat(failed_results, ignore_index=True) if failed_results else DataFrame(
        columns=[user_key, "file_name", "user_id", "file_id", "server_file_name", "status", "reason"]
    )
    results_df = pd.concat([success_df, failed_df], ignore_index=True)
    
    # results_df = pd.concat(failed_results + success_results, ignore_index=True)
    if option.interactive_mode:
        successes = results_df[results_df["status"] == "SUCCESS"]
        failures = results_df[results_df["status"] == "FAILED"]
        
        missing_users = len(failed_df[failed_df["reason"].str.contains("User not found", na=False)]['file_name'].unique())
        
        unmatched_events = len(failed_df[failed_df["reason"].str.contains("No matching event", na=False)]['file_name'].unique())
        
        invalid_file_types = len(failed_df[failed_df["reason"].str.contains("Invalid file type", na=False)]['file_name'].unique())
        
        missing_files = len(failed_df[failed_df["reason"].str.contains("not found in", na=False)]['file_name'].unique())
        
        other_failures = len(failed_df[failed_df["reason"].str.contains("Upload failed|User ID.*not found in user data", na=False)]['file_name'].unique())
        
        print(f"✔ Successfully attached {len(successes['file_name'].unique())} files to {len(successes)} events.")
        
        if not failures.empty:
            failure_msg = f"⚠️ Failed to attach {len(failures['file_name'].unique())} files: "
            failure_details = []
            
            if missing_users > 0:
                failure_details.append(f"{missing_users} due to non-existent {user_key}")
                
            if unmatched_events > 0:
                failure_details.append(f"{unmatched_events} due to unmatched {mapping_col}")
                
            if invalid_file_types > 0:
                failure_details.append(f"{invalid_file_types} due to invalid file types")
                
            if missing_files > 0:
                failure_details.append(f"{missing_files} due to missing files in directory")
                
            if other_failures > 0:
                failure_details.append(f"{other_failures} due to upload or update failures")
                
            print(failure_msg + "; ".join(failure_details) + ".")

    if option.save_to_file:
        results_df.to_csv(option.save_to_file, index=False)
        if option.interactive_mode:
            print(f"ℹ Saved results to '{option.save_to_file}'")

    return results_df
    
    




def upload_and_attach_to_avatars(
    mapping_df: Optional[DataFrame] = None,
    file_dir: str = None,
    user_key: str = None,
    url: str = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    option: Optional[FileUploadOption] = None,
    client: Optional[AMSClient] = None
) -> DataFrame:
    """Upload files and attach them as avatars to user profiles in an AMS instance.

    Matches the provided or auto-generated :class:`pandas.DataFrame` to users using
    `user_key`, uploads valid image files from `file_dir`, and updates the `avatarId`
    field in user profiles. If `mapping_df` is None, generates it from image filenames
    in `file_dir` (without extension) as `user_key` values. Preserves other profile
    fields during updates. Returns a :class:`pandas.DataFrame` with results. See
    :ref:`uploading_files` for detailed workflows.

    Args:
        mapping_df (Optional[:class:`pandas.DataFrame`]): DataFrame with columns:
            - `user_key` (str): User identifier (e.g., 'username', 'email', 'about',
            'uuid').
            - `file_name` (str): Image file name in `file_dir` (e.g., 'avatar1.png').
            If None, generates from `file_dir` filenames. Defaults to None.
        file_dir (str): Directory path containing image files (e.g.,
            '/path/to/avatars'). Must be a valid directory.
        user_key (str): Column name for user identification ('username', 'email',
            'about', 'uuid'). Required if `mapping_df` is None or provided.
        url (str): AMS instance URL (e.g., 'https://example.smartabase.com/site').
            Must include a valid site name.
        username (Optional[str]): Username for authentication. If None, uses
            :envvar:`AMS_USERNAME` or :class:`keyring` credentials. Defaults to None.
        password (Optional[str]): Password for authentication. If None, uses
            :envvar:`AMS_PASSWORD` or :class:`keyring` credentials. Defaults to None.
        option (FileUploadOption, optional): Configuration options for
            interactive feedback, caching, and saving results to a CSV. Defaults to
            None (uses default :class:`FileUploadOption` with
            `interactive_mode=True`).
        client (AMSClient, optional): Pre-authenticated client from
            :func:`get_client`. If None, a new client is created. Defaults to None.

    Returns:
        :class:`pandas.DataFrame`: Results with columns:
            - user_key (str): The user identifier from `mapping_df`.
            - file_name (str): The file name from `mapping_df`.
            - user_id (str): Matched user ID (None if failed).
            - file_id (str): Uploaded file ID (None if failed).
            - server_file_name (str): Server-assigned file name (None if failed).
            - status (str): 'SUCCESS' or 'FAILED'.
            - reason (str): Failure reason (None if successful).

    Raises:
        :class:`AMSError`: If:
            - `file_dir` is invalid or empty.
            - `mapping_df` is None and no valid images are found.
            - User data retrieval fails.
            - No users are found.
            - File validation fails (e.g., non-image files).
            - File upload or profile update fails.
        :class:`ValueError`: If `user_key` is invalid or `mapping_df` is malformed.
            
    Examples:
        >>> import pandas as pd
        >>> from teamworksams import upload_and_attach_to_avatars, FileUploadOption
        >>> mapping_df = DataFrame({
        ...     "username": ["user1", "user2"],
        ...     "file_name": ["avatar1.png", "avatar2.jpg"]
        ... })
        >>> results = upload_and_attach_to_avatars(
        ...     mapping_df = mapping_df,
        ...     file_dir = "/path/to/avatars",
        ...     user_key = "username",
        ...     url = "https://example.smartabase.com/site",
        ...     username = "user",
        ...     password = "password",
        ...     option = FileUploadOption(
        ...         interactive_mode = True, 
        ...         save_to_file = "avatar_results.csv"
        ...     )
        ... )
        ℹ Fetching all user data from site to match provided files...
        ℹ Retrieved 50 users.
        ℹ Found 2 valid avatar files in directory for 2 matching users on the site.
        ℹ Uploading 2 avatar files...
        Uploading files: 100%|██████████| 2/2 [00:02<00:00,  1.00s/it]
        Preparing to update avatars for 2 users with 2 avatar files.
        Updating avatars: 100%|██████████| 2/2 [00:02<00:00,  1.00s/it]
        ✔ Successfully updated 2 avatar files to 2 users.
        ℹ Saved results to 'avatar_results.csv'
        >>> print(results)
           username  file_name user_id file_id server_file_name status reason
        0   user1  avatar1.png 78901   94196 avatar1_1747654002120.png SUCCESS None
        1   user2  avatar2.jpg 78902   94197 avatar2_1747654003484.jpg SUCCESS None
    """
    option = option or FileUploadOption(interactive_mode=True)
    client = client or get_client(url, username, password, cache=option.cache, interactive_mode=option.interactive_mode)
    
    # Generate mapping_df if not provided
    if mapping_df is None:
        if not file_dir:
            raise AMSError("file_dir must be provided when mapping_df is None.", function="upload_and_attach_to_avatars")
        if not user_key:
            raise AMSError("user_key must be provided when mapping_df is None.", function="upload_and_attach_to_avatars")
        try:
            mapping_df = _create_avatar_mapping_df(file_dir, user_key)
            if option.interactive_mode:
                print(f"ℹ Generated mapping DataFrame from {len(mapping_df)} image files in directory.")
        except AMSError as e:
            raise AMSError(f"Failed to generate mapping DataFrame: {str(e)}", function="upload_and_attach_to_avatars")

    # Validate mapping_df
    initial_rows = len(mapping_df)
    mapping_df = _validate_file_df(mapping_df, user_key, require_mapping_col=False)
    _validate_user_key(user_key)

    # Initialize result lists
    success_results = []
    failed_results = []

    # Validate file directory
    file_dir = Path(file_dir).resolve()
    if not file_dir.is_dir():
        raise AMSError(f"'{file_dir}' is not a valid directory", function="upload_and_attach_to_avatars")

    # Match mapping_df to users
    if option.interactive_mode:
        print(f"ℹ Fetching all user data from site to match provided files...")
    try:
        user_df = _fetch_all_user_data(
            url=url,
            username=username,
            password=password,
            option=UserOption(interactive_mode=False, cache=option.cache),
            client=client
        )
        if option.interactive_mode:
            print(f"ℹ Retrieved {len(user_df)} users.")
    except AMSError as e:
        raise AMSError(f"Failed to retrieve user data: {str(e)}", function="upload_and_attach_to_avatars")

    if user_df.empty:
        raise AMSError("No users found", function="upload_and_attach_to_avatars")

    # Map users
    mapping_df, failed_matches = _map_user_ids_to_file_df(
        mapping_df, user_key, client, option.interactive_mode, option.cache
    )
    if not failed_matches.empty:
        failed_results.append(_build_result_df({
            user_key: failed_matches[user_key].tolist(),
            "file_name": failed_matches["file_name"].tolist(),
            "user_id": [None] * len(failed_matches),
            "file_id": [None] * len(failed_matches),
            "server_file_name": [None] * len(failed_matches),
            "status": ["FAILED"] * len(failed_matches),
            "reason": failed_matches["reason"].tolist()
        }, user_key))
        if option.interactive_mode:
            print(f"⚠️ {len(failed_matches)} files failed to match {user_key} values in user data.")

    if option.interactive_mode and len(mapping_df) > initial_rows:
        print(f"⚠️ Warning: mapping_df increased from {initial_rows} to {len(mapping_df)} rows due to duplicate {user_key} matches in user data.")

    if mapping_df.empty:
        results_df = pd.concat(failed_results, ignore_index=True)
        if option.interactive_mode:
            print(f"⚠️ Failed to update avatars for {len(results_df)} users.")
        if option.save_to_file:
            results_df.to_csv(option.save_to_file, index=False)
            print(f"ℹ Saved results to '{option.save_to_file}'")
        return results_df

    # Validate and prepare files for upload
    failed_files = set()
    
    files_to_upload, results_df = _validate_and_prepare_files(
        mapping_df, user_key, file_dir, failed_files, failed_results, option
    )
    if files_to_upload is None:
        return results_df

    # Validate file types for existing files
    try:
        files_to_upload, invalid_files = _validate_file_path(file_dir, files_to_upload, function="upload_and_attach_to_avatars", is_avatar=True, option=option)
        if invalid_files:
            failed_results.append(_build_result_df({
                user_key: [mapping_df[mapping_df["file_name"] == file_name][user_key].iloc[0] if file_name in mapping_df["file_name"].values else Path(file_name).stem for file_name, _ in invalid_files],
                "file_name": [file_name for file_name, _ in invalid_files],
                "user_id": [None] * len(invalid_files),
                "file_id": [None] * len(invalid_files),
                "server_file_name": [None] * len(invalid_files),
                "status": ["FAILED"] * len(invalid_files),
                "reason": [reason for _, reason in invalid_files]
            }, user_key))
        if option.interactive_mode:
            matching_users = len(mapping_df[mapping_df["user_id"].notna()][user_key].unique())
            print(f"ℹ Found {len(files_to_upload)} valid avatar files in directory for {matching_users} matching users on the site.")
            print(f"ℹ Uploading {len(files_to_upload)} avatars...")
            
    except AMSError as e:
        failed_results.append(_build_result_df({
            user_key: mapping_df[user_key].tolist(),
            "file_name": mapping_df["file_name"].tolist(),
            "user_id": mapping_df["user_id"].tolist(),
            "file_id": [None] * len(mapping_df),
            "server_file_name": [None] * len(mapping_df),
            "status": ["FAILED"] * len(mapping_df),
            "reason": [str(e)] * len(mapping_df)
        }, user_key))
        results_df = pd.concat(failed_results, ignore_index=True)
        if option.interactive_mode:
            print(f"⚠️ Failed to update avatars for {len(results_df)} users.")
        if option.save_to_file:
            results_df.to_csv(option.save_to_file, index=False)
            print(f"ℹ Saved results to '{option.save_to_file}'")
        return results_df

    # Upload files
    upload_results = []
    for file_path, file_name in tqdm(files_to_upload, desc="Uploading files", disable=not option.interactive_mode):
        if file_name in failed_files or file_name not in mapping_df["file_name"].values:
            continue
        try:
            upload_result = _upload_single_file(file_path, file_name, client, "avatar-key")
            if upload_result.get("file_id"):
                upload_result["file_id"] = str(upload_result["file_id"])
                upload_results.append(upload_result)
            else:
                failed_files.add(file_name)
                failed_results.append(_build_result_df({
                    user_key: mapping_df[mapping_df["file_name"] == file_name][user_key].iloc[0],
                    "file_name": file_name,
                    "user_id": mapping_df[mapping_df["file_name"] == file_name]["user_id"].iloc[0],
                    "file_id": None,
                    "server_file_name": None,
                    "status": "FAILED",
                    "reason": "Upload failed: No file ID returned"
                }, user_key))
                
        except AMSError as e:
            failed_files.add(file_name)
            failed_results.append(_build_result_df({
                user_key: mapping_df[mapping_df["file_name"] == file_name][user_key].iloc[0],
                "file_name": file_name,
                "user_id": mapping_df[mapping_df["file_name"] == file_name]["user_id"].iloc[0],
                "file_id": None,
                "server_file_name": None,
                "status": "FAILED",
                "reason": f"Upload failed: {str(e)}"
            }, user_key))

    # Merge upload results
    upload_results_df = DataFrame(upload_results)
    
    mapping_df = mapping_df.merge(
        upload_results_df[["file_name", "file_id", "server_file_name"]],
        on="file_name",
        how="left"
    )
    mapping_df = mapping_df[mapping_df["file_id"].notna()]

    if mapping_df.empty:
        results_df = pd.concat(failed_results, ignore_index=True)
        if option.interactive_mode:
            print(f"⚠️ Failed to update avatars for {len(results_df)} users.")
        if option.save_to_file:
            results_df.to_csv(option.save_to_file, index=False)
            print(f"ℹ Saved results to '{option.save_to_file}'")
        return results_df

    # Update avatars
    if option.interactive_mode:
        print(f"ℹ Preparing to update avatars for {len(mapping_df)} users with {len(mapping_df['file_name'].unique())} avatar files.")
        
    for _, row in tqdm(mapping_df.iterrows(), desc="Updating avatars", total=len(mapping_df), disable=not option.interactive_mode, dynamic_ncols=True, leave=False, position=0):
        user_id = row["user_id"]
        file_id = row["file_id"]
        file_name = row["file_name"]
        user_data = user_df[user_df["id"] == int(user_id)].to_dict("records")
        if not user_data:
            failed_results.append(_build_result_df({
                user_key: row[user_key],
                "file_name": file_name,
                "user_id": user_id,
                "file_id": file_id,
                "server_file_name": row["server_file_name"],
                "status": "FAILED",
                "reason": f"User ID {user_id} not found in user data"
            }, user_key))
            continue
        user_data = _map_user_updates({"avatarId": file_id}, user_data[0])
        error_msg = _update_single_user(
            user_data,
            client,
            int(user_id),
            file_name,
            interactive_mode=option.interactive_mode
        )
        if error_msg:
            failed_results.append(_build_result_df({
                user_key: row[user_key],
                "file_name": file_name,
                "user_id": user_id,
                "file_id": file_id,
                "server_file_name": row["server_file_name"],
                "status": "FAILED",
                "reason": error_msg
            }, user_key))
        else:
            success_results.append(_build_result_df({
                user_key: row[user_key],
                "file_name": file_name,
                "user_id": user_id,
                "file_id": file_id,
                "server_file_name": row["server_file_name"],
                "status": "SUCCESS",
                "reason": None
            }, user_key))

    # Concatenate results
    success_df = pd.concat(success_results, ignore_index=True) if success_results else DataFrame(
        columns=[user_key, "file_name", "user_id", "file_id", "server_file_name", "status", "reason"]
    )
    failed_df = pd.concat(failed_results, ignore_index=True) if failed_results else DataFrame(
        columns=[user_key, "file_name", "user_id", "file_id", "server_file_name", "status", "reason"]
    )
    results_df = pd.concat([success_df, failed_df], ignore_index=True)

    if option.interactive_mode:
        successes = results_df[results_df["status"] == "SUCCESS"]
        
        failures = results_df[results_df["status"] == "FAILED"]
        
        missing_users = len(failed_df[failed_df["reason"].str.contains("User not found", na=False)]['file_name'].unique())
        
        invalid_file_types = len(failed_df[failed_df["reason"].str.contains("Invalid file type", na=False)]['file_name'].unique())
        
        missing_files = len(failed_df[failed_df["reason"].str.contains("not found in", na=False)]['file_name'].unique())
        
        other_failures = len(failed_df[failed_df["reason"].str.contains("Upload failed|User ID.*not found in user data", na=False)]['file_name'].unique())
        
        print(f"✔ Successfully attached {len(successes['file_name'].unique())} avatar files to {len(successes)} users.")
        
        if not failures.empty:
            failure_msg = f"⚠️ Failed to attach {len(failures['file_name'].unique())} avatar files: "
            failure_details = []
            if missing_users > 0:
                failure_details.append(f"{missing_users} due to non-existent {user_key}")
                
            if invalid_file_types > 0:
                failure_details.append(f"{invalid_file_types} due to invalid file type")
                
            if missing_files > 0:
                failure_details.append(f"{missing_files} due to missing files in directory")
                
            if other_failures > 0:
                failure_details.append(f"{other_failures} due to upload or update failures")
                
            print(failure_msg + "; ".join(failure_details) + ".")

    if option.save_to_file:
        results_df.to_csv(option.save_to_file, index=False)
        if option.interactive_mode:
            print(f"ℹ Saved results to '{option.save_to_file}'")

    return results_df