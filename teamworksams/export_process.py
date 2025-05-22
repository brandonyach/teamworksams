from datetime import datetime
from pandas import DataFrame
from typing import Optional, List, Dict, Any
from tqdm import tqdm
from .file_process import _download_attachment
from .utils import AMSError


def _process_events_to_rows(
    events: List[Dict],
    start: datetime,
    end: datetime,
    filter: Optional[Any] = None,
    download_attachment: bool = False,
    client: Optional[Any] = None,
    option: Optional[Any] = None
) -> List[Dict]:
    """Process raw event data into a list of row dictionaries, handling multi-row events.

    Converts event data into a flat list of dictionaries, where each dictionary represents a row
    of data. Handles table data by creating separate rows for each table entry. Optionally downloads
    attachments if enabled.

    Args:
        events (List[Dict]): The list of event dictionaries from the API response.
        start (datetime): The start date for filtering events.
        end (datetime): The end date for filtering events.
        filter (Optional[Any]): An EventFilter object to apply additional filters (e.g., events per user).
        download_attachment (bool): Whether to download attachments associated with events.
        client (Optional[Any]): The AMSClient instance for downloading attachments.
        option (Optional[Any]): The EventOption object containing settings like attachment directory.

    Returns:
        List[Dict]: A list of dictionaries, each representing a row of event data.

    Raises:
        AMSError: If downloading an attachment fails.
    """
    rows = []
    user_event_counts = {}
    attachment_count = 0
    
    event_iterator = tqdm(events, desc="Processing events", leave=False) if (option and option.interactive_mode) else events
    
    for event in event_iterator:
        base_row = {
            "event_id": int(event["id"]),
            "form": event["formName"],
            "start_date": event["startDate"],
            "start_time": event["startTime"],
            "end_date": event["finishDate"],
            "end_time": event["finishTime"],
            "user_id": event["userId"],
            "entered_by_user_id": int(event["enteredByUserId"])
        }
        
        event_rows = event.get("rows", [])
        if not event_rows: 
            row = base_row.copy()
            rows.append(row)
        else:
            for row_data in event_rows:  # Process each row
                pairs = {pair["key"]: pair["value"] for pair in row_data.get("pairs", [])}
                row = base_row.copy()
                row.update(pairs)  # Add row-specific data
                rows.append(row)
        
        # Handle attachments
        attachments = event.get("attachmentUrl")
        if download_attachment and attachments and client:
            if isinstance(attachments, list):
                for attachment in attachments:
                    url = attachment.get("attachmentUrl")
                    name = attachment.get("name", "unnamed")
                    if url:
                        file_name = f"{event['formName']}_{event['id']}_{name}"
                        file_name = file_name.replace("/", "").replace(":", "").replace(" ", "")
                        try:
                            _download_attachment(client, url, file_name, 
                                                output_dir=option.attachment_directory if option else None)
                            attachment_count += 1
                        except AMSError as e:
                            if option and option.interactive_mode:
                                print(f"✖ Warning: Could not download attachment {name} for event {event['id']}: {e}")
            elif isinstance(attachments, str):
                file_name = f"{event['formName']}_{event['id']}_{event['startDate']}_{event.get('startTime', 'notime')}"
                file_name = file_name.replace("/", "").replace(":", "").replace(" ", "")
                try:
                    _download_attachment(client, attachments, file_name, 
                                        output_dir=option.attachment_directory if option else None)
                    attachment_count += 1
                except AMSError as e:
                    if option and option.interactive_mode:
                        print(f"✖ Warning: Could not download attachment for event {event['id']}: {e}")
        
        # Filter by date and events_per_user
        event_date = datetime.strptime(event["startDate"], "%d/%m/%Y")
        if start <= event_date <= end:
            if filter and filter.events_per_user:
                user_id = event["userId"]
                user_event_counts[user_id] = user_event_counts.get(user_id, 0) + 1
                if user_event_counts[user_id] <= filter.events_per_user:
                    rows.extend([r for r in rows if r["user_id"] == user_id][-len(event_rows):])
    
    if option and download_attachment:
        option.attachment_count = attachment_count
    
    return rows


def _process_profile_rows(
        profiles: List[Dict], 
        filter: Optional[Any], 
        option: Optional[Any]
    ) -> List[Dict]:
    """Process profile data into a list of row dictionaries.

    Converts profile data into a flat list of dictionaries, where each dictionary represents a row
    of data. Handles table data by creating separate rows for each table entry.

    Args:
        profiles (List[Dict]): The list of profile dictionaries from the API response.
        filter (Optional[Any]): A ProfileFilter object to apply additional filters.
        option (Optional[Any]): The ProfileOption object containing settings.

    Returns:
        List[Dict]: A list of dictionaries, each representing a row of profile data.
    """
    rows = []
    
    profile_iterator = tqdm(profiles, desc="Processing profiles", leave=False) if (option and option.interactive_mode) else profiles
    
    for profile in profile_iterator:
        base_row = {
            "profile_id": int(profile["id"]),
            "form": profile["formName"],
            "user_id": profile["userId"],
            "entered_by_user_id": int(profile["enteredByUserId"])
        }
        profile_rows = profile.get("rows", [])
        if not profile_rows:
            rows.append(base_row.copy())
        else:
            for row_data in profile_rows:
                pairs = {pair["key"]: pair["value"] for pair in row_data.get("pairs", [])}
                row = base_row.copy()
                row.update(pairs)
                rows.append(row)
    return rows


def _append_user_data(
        df: DataFrame, 
        user_df: Optional[DataFrame], 
        include_missing_users: bool = False
    ) -> DataFrame:
    """Append user metadata to an event or profile DataFrame.

    Merges user metadata (e.g., 'about') into the event or profile DataFrame based on user_id.

    Args:
        df (DataFrame): The event or profile DataFrame to append user data to.
        user_df (Optional[DataFrame]): The DataFrame containing user data.
        include_missing_users (bool): Whether to include users from user_df who don't have events/profiles (default: False).

    Returns:
        DataFrame: The DataFrame with appended user metadata.
    """
    if user_df is not None and not user_df.empty:
        user_df["about"] = user_df["firstName"] + " " + user_df["lastName"]
        user_df = user_df.rename(columns={"userId": "user_id"})
        if include_missing_users:
            df = user_df[["user_id", "about"]].merge(df, on="user_id", how="left")
        else:
            df = df.merge(user_df[["user_id", "about"]], on="user_id", how="left")
    return df