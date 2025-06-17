from typing import Optional


class EventOption:  
    """Options for configuring event data export.

    Defines customization options for the :func:`get_event_data` function, controlling aspects such as
    downloading attachments, cleaning column names, caching API responses, and enabling
    interactive feedback. These options allow users to tailor the event data retrieval process,
    including data formatting, performance optimization, and user experience. See
    :ref:`exporting_data` for usage examples.

    Args:
        interactive_mode (bool): Whether to print status messages during execution, such as the
            number of events retrieved. Defaults to True.
        guess_col_type (bool): Whether to infer column data types (e.g., numeric, datetime) in
            the resulting DataFrame. Defaults to True.
        convert_dates (bool): Whether to convert date columns to pandas datetime objects.
            Defaults to False.
        clean_names (bool): Whether to clean column names by converting to lowercase and
            replacing spaces with underscores. Defaults to False.
        cache (bool): Whether to cache API responses to improve performance for repeated
            requests. Defaults to True.
        include_missing_users (bool): Whether to include events for users not found in user
            data, ensuring all events are represented. Defaults to False.
        download_attachment (bool): Whether to download attachments associated with events.
            Defaults to False.
        attachment_directory (Optional[str]): Directory path to save downloaded attachments.
            If None, uses the current working directory. Can be either an absolute path or a 
            relative path. Ignored if download_attachment is False. Defaults to None.

    Attributes:
        interactive_mode (bool): Indicates whether interactive mode is enabled.
        guess_col_type (bool): Indicates whether column type inference is enabled.
        convert_dates (bool): Indicates whether date conversion is enabled.
        clean_names (bool): Indicates whether column name cleaning is enabled.
        cache (bool): Indicates whether caching is enabled.
        include_missing_users (bool): Indicates whether missing users are included.
        download_attachment (bool): Indicates whether attachment downloading is enabled.
        attachment_directory (Optional[str]): The directory for saving attachments.
        attachment_count (int): The number of attachments downloaded (set during processing).

    Examples:
        >>> from teamworksams import get_event_data, EventOption
        >>> option = EventOption(
        ...     interactive_mode = True,
        ...     clean_names = True,
        ...     download_attachment = True,
        ...     attachment_directory = "/path/to/attachments"
        ... )
        >>> df = get_event_data(
        ...     form = "Training Log",
        ...     start_date = "01/01/2025",
        ...     end_date = "31/01/2025",
        ...     url = "https://example.smartabase.com/site",
        ...     option = option
        ... )
    """
    def __init__(
        self,
        interactive_mode: bool = True,
        guess_col_type: bool = True,
        convert_dates: bool = False,
        clean_names: bool = False,
        cache: bool = True,
        include_missing_users: bool = False,
        download_attachment: bool = False,
        attachment_directory: Optional[str] = None
    ):
        self.interactive_mode = interactive_mode
        self.guess_col_type = guess_col_type
        self.convert_dates = convert_dates
        self.clean_names = clean_names
        self.cache = cache
        self.include_missing_users = include_missing_users
        self.download_attachment = download_attachment
        self.attachment_directory = attachment_directory
        self.attachment_count = 0
        
        
        
class SyncEventOption:
    """Options for configuring sync event data export.

    Customizes the behavior of :func:`sync_event_data`,
    controlling output formatting, user metadata inclusion, caching, and interactive
    feedback. Optimizes performance for synchronized event exports. See
    :ref:`exporting_data` for synchronization workflows.

    Args:
        interactive_mode (bool): Whether to print status messages during execution, such as the
            number of events retrieved. Defaults to True.
        include_user_data (bool): Whether to include user metadata (e.g., 'about', 'first_name')
            in the output DataFrame. Defaults to True.
        cache (bool): Whether to cache API responses to improve performance for repeated
            requests. Defaults to True.
        include_missing_users (bool): Whether to include users from the filter without event
            data, ensuring all specified users are represented. Defaults to False.
        guess_col_type (bool): Whether to infer column data types (e.g., numeric, datetime) in
            the resulting DataFrame. Defaults to True.
        include_uuid (bool): Whether to include the user's UUID in the output DataFrame.
            Defaults to False.

    Attributes:
        interactive_mode (bool): Indicates whether interactive mode is enabled.
        include_user_data (bool): Indicates whether user metadata is included.
        cache (bool): Indicates whether caching is enabled.
        include_missing_users (bool): Indicates whether missing users are included.
        guess_col_type (bool): Indicates whether column type inference is enabled.
        include_uuid (bool): Indicates whether UUID inclusion is enabled.

    Examples:
        >>> from teamworksams import sync_event_data, SyncEventOption
        >>> option = SyncEventOption(
        ...     interactive_mode = True,
        ...     include_user_data = True,
        ...     include_uuid = True
        ... )
        >>> df, new_sync_time = sync_event_data(
        ...     form = "Training Log",
        ...     last_synchronisation_time = 1677654321000,
        ...     url = "https://example.smartabase.com/site",
        ...     option = option
        ... )
    """
    def __init__(
        self,
        interactive_mode: bool = True,
        include_user_data: bool = True,
        cache: bool = True,
        include_missing_users: bool = False,
        guess_col_type: bool = True,
        include_uuid: bool = False
    ):
        self.interactive_mode = interactive_mode
        self.include_user_data = include_user_data
        self.cache = cache
        self.include_missing_users = include_missing_users
        self.guess_col_type = guess_col_type
        self.include_uuid = include_uuid
        
        

class ProfileOption:
    """Options for configuring profile data export.

    Customizes the behavior of :func:`get_profile_data`,
    controlling output formatting, caching, and interactive feedback. Optimizes
    performance for profile data exports. 

    Args:
        interactive_mode (bool): Whether to print status messages during execution (default: True).
        guess_col_type (bool): Whether to infer column data types (default: True).
        clean_names (bool): Whether to clean column names (e.g., lowercase, replace spaces) (default: False).
        cache (bool): Whether to cache API responses (default: True).
        include_missing_users (bool): Whether to include users from the filter without profile data (default: False).

    Attributes:
        interactive_mode (bool): Whether interactive mode is enabled.
        guess_col_type (bool): Whether to guess column types.
        clean_names (bool): Whether to clean column names.
        cache (bool): Whether caching is enabled.
        include_missing_users (bool): Whether to include missing users.
        
        Examples:
        >>> from teamworksams import get_profile_data, ProfileOption
        >>> option = ProfileOption(
        ...     interactive_mode = True,
        ...     guess_col_type = True,
        ...     clean_names = True
        ... )
        >>> df = get_profile_data(
        ...     form = "Athlete Profile",
        ...     url = "https://example.smartabase.com/site",
        ...     option = option
        ... )
    """
    def __init__(
        self,
        interactive_mode: bool = True,
        guess_col_type: bool = True,
        clean_names: bool = False,
        cache: bool = True,
        include_missing_users: bool = False
    ):
        self.interactive_mode = interactive_mode
        self.guess_col_type = guess_col_type
        self.clean_names = clean_names
        self.cache = cache
        self.include_missing_users = include_missing_users