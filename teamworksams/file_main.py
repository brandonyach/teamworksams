import os
import pandas as pd
from typing import Optional, Dict, List, Tuple
from pandas import DataFrame
from datetime import datetime
from tqdm import tqdm
from pathlib import Path
from .utils import AMSClient, AMSError, get_client
from .import_main import update_event_data
from .import_option import UpdateEventOption
from .file_option import FileUploadOption
from .file_validate import _validate_file_df, _validate_file_path
from .file_process import _format_file_reference, _map_user_ids_to_file_df, _build_result_df, _validate_and_prepare_files, _upload_single_file
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
    client: Optional[AMSClient] = None
) -> DataFrame:
    """Upload files and attach them to events in an AMS Event Form.

    Matches the provided mapping DataFrame to users and events using `user_key` and `attachment_id`,
    uploads valid files from `file_dir`, and updates the images into the specified `file_field_name` within the event form
    with file references (format: `file_id|server_file_name`). Preserves all other event form fields
    during updates. Returns a DataFrame with results for all files, including successes and failures.

    Args:
        mapping_df (DataFrame): A DataFrame with columns:
            - user_key (str): User identifier (e.g., 'username', 'email', 'about', 'uuid').
            - file_name (str): Name of the file to upload, located in `file_dir`.
            - attachment_id (str): Matches the 'attachment_id' field in the event form.
        file_dir (str): Directory path containing the files to upload.
        user_key (str): Column name in `mapping_df` for user identification ('username', 'email', 'about', 'uuid').
        form (str): Name of the AMS Event Form (e.g., 'Training Log').
        file_field_name (str): File upload field in the form (e.g., 'attachment').
        url (str): AMS instance URL (e.g., 'https://example.smartabase.com/site').
        username (Optional[str]): The username for authentication. If None, uses the
            AMS_USERNAME environment variable. Defaults to None.
        password (Optional[str]): The password for authentication. If None, uses the
            AMS_USERNAME environment variable. Defaults to None.
        option (Optional[FileUploadOption]): Configuration for interactive mode, caching, and result saving.
            Defaults to FileUploadOption(interactive_mode=True).
        client (Optional[AMSClient]): A pre-authenticated AMSClient instance. If None,
            a new client is created using the provided url, username, and password.
            Defaults to None.

    Returns:
        DataFrame: Results with columns:
            - user_key (str): The user identifier from `mapping_df`.
            - file_name (str): The file name from `mapping_df`.
            - event_id (str): Matched event ID (None if failed).
            - user_id (str): Matched user ID (None if failed).
            - file_id (str): Uploaded file ID (None if failed).
            - server_file_name (str): Server-assigned file name (None if failed).
            - status (str): 'SUCCESS' or 'FAILED'.
            - reason (str): Failure reason (None if successful).

    Raises:
        AMSError: If any of the following occur:
            - `file_dir` is not a valid directory.
            - User data retrieval fails (e.g., invalid credentials, API errors).
            - No users are found in the AMS instance.
            - Event data retrieval fails (e.g., invalid form name, API errors).
            - No events are found for the specified form and users.
            - The event form lacks an 'attachment_id' field.
            - File validation fails (e.g., unsupported file type).
            - File upload or event update fails (e.g., network issues, server errors).

    Example:
        ```python
        from pandas import DataFrame
        from teamworksams import upload_and_attach_to_events
        from teamworksams import FileUploadOption

        # Sample mapping DataFrame
        mapping_df = DataFrame({
            "username": ["user1", "user2"],
            "file_name": ["doc1.pdf", "doc2.pdf"],
            "attachment_id": ["ATT123", "ATT456"]
        })

        # Upload and attach files to events
        results = upload_and_attach_to_events(
            mapping_df = mapping_df,
            file_dir = "/path/to/files",
            user_key = "about",
            form = "Training Log",
            file_field_name = "attachment",
            url = "https://example.smartabase.com/site",
            username = "user",
            password = "password",
            option = FileUploadOption(interactive_mode = True, save_to_file = "results.csv")
        )

        # Expected output (example):
        # ℹ Fetching all user data from site to match provided files...
        # ℹ Retrieved 50 users.
        # ℹ Fetching all event data from site to match provided files...
        # ℹ Retrieved 10 events.
        # ℹ Finding a match for 2 events from mapping_df...
        # ℹ Identified and mapped 2 events from mapping_df.
        # ℹ Uploading and updating events for 2 files...
        # Uploading files: 100%|██████████| 2/2 [00:02<00:00,  1.00s/it]
        # ✔ Successfully attached 2 files to events.
        # ℹ Saved results to 'results.csv'
        #
        # Results DataFrame:
        #    username file_name event_id user_id file_id server_file_name status reason
        # 0   user1   doc1.pdf  123456  78901   94196 doc1_1747654002120.pdf SUCCESS None
        # 1   user2   doc2.pdf  123457  78902   94197 doc2_1747654003484.pdf SUCCESS None
    """
    option = option or FileUploadOption(interactive_mode=True)
    client = client or get_client(url, username, password, cache=option.cache, interactive_mode=option.interactive_mode)

    # Validate mapping_df
    _validate_file_df(mapping_df, user_key, require_attachment_id=True)
    _validate_user_key(user_key)

    # Initialize result lists
    success_results = []
    failed_results = []

    # Validate file directory
    file_dir = Path(file_dir).resolve()
    if not file_dir.is_dir():
        raise AMSError(f"'{file_dir}' is not a valid directory", function="upload_and_attach_to_events")

    # Match mapping_df to users to get user_id
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
        raise AMSError("No users found.", function="upload_and_attach_to_avatars")

    # Map users to get user_id
    mapping_df, failed_matches = _map_user_ids_to_file_df(
        mapping_df, user_key, client, False, option.cache
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

    if mapping_df.empty:
        results_df = pd.concat(failed_results, ignore_index=True)
        if option.interactive_mode:
            print(f"⚠️ Failed to attach {len(results_df)} files.")
        if option.save_to_file:
            results_df.to_csv(option.save_to_file, index=False)
            print(f"ℹ Saved results to '{option.save_to_file}'")
        return results_df

    # Match mapping_df to events
    if option.interactive_mode:
        print(f"ℹ Fetching all event data from site to match provided files...")
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
        # Cast event_id to string to prevent float conversion
        event_df["event_id"] = event_df["event_id"].astype(str)
        # Drop event_df's user_id to avoid merge conflict
        event_df = event_df.drop(columns=["user_id"], errors="ignore")
        
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

    if option.interactive_mode:
        num_events = len(mapping_df[user_key].unique())
        print(f"ℹ Finding a match for {num_events} events from mapping_df...")

    # Merge with events using attachment_id, retaining all event fields
    if "attachment_id" not in event_df.columns:
        failed_results.append(_build_result_df({
            user_key: mapping_df[user_key].tolist(),
            "file_name": mapping_df["file_name"].tolist(),
            "event_id": [None] * len(mapping_df),
            "user_id": mapping_df["user_id"].tolist() if "user_id" in mapping_df else [None] * len(mapping_df),
            "file_id": [None] * len(mapping_df),
            "server_file_name": [None] * len(mapping_df),
            "status": ["FAILED"] * len(mapping_df),
            "reason": [f"Event form '{form}' does not have an 'attachment_id' field"] * len(mapping_df)
        }, user_key, is_event=True))
        results_df = pd.concat(failed_results, ignore_index=True)
        if option.interactive_mode:
            print(f"⚠️ Failed to attach {len(results_df)} files.")
        if option.save_to_file:
            results_df.to_csv(option.save_to_file, index=False)
            print(f"ℹ Saved results to '{option.save_to_file}'")
        return results_df

    mapping_df = mapping_df.merge(
        event_df,
        left_on="attachment_id",
        right_on="attachment_id",
        how="left"
    )
    failed_matches = mapping_df[mapping_df["event_id"].isna()]
    mapping_df = mapping_df[mapping_df["event_id"].notna()]

    if option.interactive_mode and not mapping_df.empty:
        print(f"ℹ Identified and mapped {len(mapping_df)} events from mapping_df.")

    if not failed_matches.empty:
        failed_results.append(_build_result_df({
            user_key: failed_matches[user_key].tolist(),
            "file_name": failed_matches["file_name"].tolist(),
            "event_id": [None] * len(failed_matches),
            "user_id": failed_matches["user_id"].tolist() if "user_id" in failed_matches else [None] * len(failed_matches),
            "file_id": [None] * len(failed_matches),
            "server_file_name": [None] * len(failed_matches),
            "status": ["FAILED"] * len(failed_matches),
            "reason": ["No matching event found for attachment_id"] * len(failed_matches)
        }, user_key, is_event=True))

    if mapping_df.empty:
        results_df = pd.concat(failed_results, ignore_index=True)
        if option.interactive_mode:
            print(f"⚠️ Failed to attach {len(results_df)} files.")
        if option.save_to_file:
            results_df.to_csv(option.save_to_file, index=False)
            print(f"ℹ Saved results to '{option.save_to_file}'")
        return results_df

    # Validate and prepare files for upload
    failed_files = set()
    files_to_upload, results_df = _validate_and_prepare_files(
        mapping_df, user_key, file_dir, failed_files, failed_results, option, is_event=True
    )
    if files_to_upload is None:
        return results_df

    # Validate file types for existing files
    try:
        files_to_upload = _validate_file_path(file_dir, files_to_upload, function="upload_and_attach_to_events", is_avatar=False)
        if option.interactive_mode:
            print(f"ℹ Uploading and updating events for {len(files_to_upload)} files...")
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
                upload_result["file_id"] = str(upload_result["file_id"])  # Cast to string
                upload_results.append(upload_result)
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
        results_df = pd.DataFrame(
            columns=[user_key, "file_name", "event_id", "user_id", "file_id", "server_file_name", "status", "reason"]
        ) if not failed_results else pd.concat(failed_results, ignore_index=True)
        if option.interactive_mode:
            print(f"⚠️ Failed to attach {len(results_df)} files:")
        if option.save_to_file:
            results_df.to_csv(option.save_to_file, index=False)
            print(f"ℹ Saved results to '{option.save_to_file}'")
        return results_df

    # Format file references and update events
    mapping_df = _format_file_reference(mapping_df, file_field_name)
    # Include all event fields, drop merge artifacts
    event_update_df = mapping_df.drop(columns=["file_name"], errors="ignore")
    try:
        update_event_data(
            df=event_update_df,
            form=form,
            url=url,
            username=username,
            password=password,
            option=UpdateEventOption(interactive_mode=option.interactive_mode, cache=option.cache),
            client=client
        )
        success_results.append(_build_result_df({
            user_key: mapping_df[user_key].tolist(),
            "file_name": mapping_df["file_name"].tolist(),
            "event_id": mapping_df["event_id"].tolist(),
            "user_id": mapping_df["user_id"].tolist() if "user_id" in mapping_df else [None] * len(mapping_df),
            "file_id": mapping_df["file_id"].tolist(),
            "server_file_name": mapping_df["server_file_name"].tolist(),
            "status": ["SUCCESS"] * len(mapping_df),
            "reason": [None] * len(mapping_df)
        }, user_key, is_event=True))
    except AMSError as e:
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
    success_df = pd.concat(success_results, ignore_index=True) if success_results else DataFrame(
        columns=[user_key, "file_name", "event_id", "user_id", "file_id", "server_file_name", "status", "reason"]
    )
    failed_df = pd.concat(failed_results, ignore_index=True) if failed_results else DataFrame(
        columns=[user_key, "file_name", "event_id", "user_id", "file_id", "server_file_name", "status", "reason"]
    )
    results_df = pd.concat([success_df, failed_df], ignore_index=True)

    if option.interactive_mode:
        successes = results_df[results_df["status"] == "SUCCESS"]
        failures = results_df[results_df["status"] == "FAILED"]
        print(f"✔ Successfully attached {len(successes)} files to events.")
        if not failures.empty:
            print(f"⚠️ Failed to attach {len(failures)} files.")

    if option.save_to_file:
        results_df.to_csv(option.save_to_file, index=False)
        if option.interactive_mode:
            print(f"ℹ Saved results to '{option.save_to_file}'")

    return results_df



def upload_and_attach_to_avatars(
    mapping_df: DataFrame,
    file_dir: str,
    user_key: str,
    url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    option: Optional[FileUploadOption] = None,
    client: Optional[AMSClient] = None
) -> DataFrame:
    """Upload files and attach them as avatars to user profiles in an AMS instance.

    Matches the provided mapping DataFrame to users using `user_key`, uploads valid image files
    from `file_dir`, and updates the `avatarId` field in user profiles. Preserves all other user
    profile fields during updates. Returns a DataFrame with results for all files, including
    successes and failures.

    Args:
        mapping_df (DataFrame): A DataFrame with columns:
            - user_key (str): User identifier (e.g., 'username', 'email', 'about', 'uuid').
            - file_name (str): Name of the image file to upload, located in `file_dir`.
        file_dir (str): Directory path containing the image files to upload.
        user_key (str): Column name in `mapping_df` for user identification ('username', 'email', 'about', 'uuid').
        url (str): AMS instance URL (e.g., 'https://example.smartabase.com/site').
        username (Optional[str]): The username for authentication. If None, uses the
            AMS_USERNAME environment variable. Defaults to None.
        password (Optional[str]): The password for authentication. If None, uses the
            AMS_USERNAME environment variable. Defaults to None.
        option (Optional[FileUploadOption]): Configuration for interactive mode, caching, and result saving.
            Defaults to FileUploadOption(interactive_mode=True).
        client (Optional[AMSClient]): A pre-authenticated AMSClient instance. If None,
            a new client is created using the provided url, username, and password.
            Defaults to None.

    Returns:
        DataFrame: Results with columns:
            - user_key (str): The user identifier from `mapping_df`.
            - file_name (str): The file name from `mapping_df`.
            - user_id (str): Matched user ID (None if failed).
            - file_id (str): Uploaded file ID (None if failed).
            - server_file_name (str): Server-assigned file name (None if failed).
            - status (str): 'SUCCESS' or 'FAILED'.
            - reason (str): Failure reason (None if successful).

    Raises:
        AMSError: If any of the following occur:
            - `file_dir` is not a valid directory.
            - User data retrieval fails (e.g., invalid credentials, API errors).
            - No users are found in the AMS instance.
            - File validation fails (e.g., unsupported image type, file not found).
            - File upload or user profile update fails (e.g., network issues, server errors).

    Example:
        ```python
        from pandas import DataFrame
        from teamworksams import upload_and_attach_to_avatars
        from teamworksams import FileUploadOption

        # Sample mapping DataFrame
        mapping_df = DataFrame({
            "username": ["user1", "user2"],
            "file_name": ["avatar1.png", "avatar2.jpg"]
        })

        # Upload and attach avatars
        results = upload_and_attach_to_avatars(
            mapping_df = mapping_df,
            file_dir = "/path/to/avatars",
            user_key = "username",
            url = "https://example.smartabase.com/site",
            username = "user",
            password = "password",
            option = FileUploadOption(interactive_mode = True, save_to_file = "avatar_results.csv")
        )

        # Expected output (example):
        # ℹ Fetching all user data from site to match provided files...
        # ℹ Retrieved 50 users.
        # ℹ Finding a match for 2 users from mapping_df...
        # ℹ Identified and mapped 2 users from mapping_df.
        # ℹ Uploading and updating avatars for 2 users...
        # Uploading files: 100%|██████████| 2/2 [00:02<00:00,  1.00s/it]
        # Updating avatars: 2it [00:00,  4.00it/s]
        # ✔ Successfully updated avatars for 2 users.
        # ℹ Saved results to 'avatar_results.csv'
        #
        # Results DataFrame:
        #    username  file_name user_id file_id server_file_name status reason
        # 0   user1  avatar1.png 78901   94196 avatar1_1747654002120.png SUCCESS None
        # 1   user2  avatar2.jpg 78902   94197 avatar2_1747654003484.jpg SUCCESS None
    """
    option = option or FileUploadOption(interactive_mode=True)
    client = client or get_client(url, username, password, cache=option.cache, interactive_mode=option.interactive_mode)

    # Validate mapping_df
    _validate_file_df(mapping_df, user_key, require_attachment_id=False)
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

    if option.interactive_mode:
        num_users = len(mapping_df[user_key].unique())
        print(f"ℹ Finding a match for {num_users} users from mapping_df...")

    # Match users
    mapping_df, failed_matches = _map_user_ids_to_file_df(
        mapping_df, user_key, client, False, option.cache  
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

    if option.interactive_mode and not mapping_df.empty:
        print(f"ℹ Identified and mapped {len(mapping_df)} users from mapping_df.")

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
        files_to_upload = _validate_file_path(file_dir, files_to_upload, function="upload_and_attach_to_avatars", is_avatar=True)
        if option.interactive_mode:
            print(f"ℹ Uploading and updating avatars for {len(files_to_upload)} users...")
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
                upload_result["file_id"] = str(upload_result["file_id"])  # Cast to string
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
        results_df = pd.DataFrame(
            columns=[user_key, "file_name", "user_id", "file_id", "server_file_name", "status", "reason"]
        ) if not failed_results else pd.concat(failed_results, ignore_index=True)
        if option.interactive_mode:
            print(f"⚠️ Failed to update avatars for {len(results_df)} users.")
        if option.save_to_file:
            results_df.to_csv(option.save_to_file, index=False)
            print(f"ℹ Saved results to '{option.save_to_file}'")
        return results_df

    # Update avatars
    for _, row in tqdm(mapping_df.iterrows(), desc="Updating avatars", disable=not option.interactive_mode):
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
        print(f"✔ Successfully updated avatars for {len(successes)} users.")
        if not failures.empty:
            print(f"⚠️ Failed to update avatars for {len(failures)} users.")

    if option.save_to_file:
        results_df.to_csv(option.save_to_file, index=False)
        if option.interactive_mode:
            print(f"ℹ Saved results to '{option.save_to_file}'")

    return results_df