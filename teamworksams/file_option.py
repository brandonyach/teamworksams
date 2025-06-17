from typing import Optional

class FileUploadOption:
    """Configuration options for file upload operations.

    Customizes the behavior of :func:`upload_and_attach_to_events`
    and :func:`upload_and_attach_to_avatars`, controlling
    interactive feedback, caching, and result storage. These options optimize the
    upload process for attaching files to events or user avatars. See
    :ref:`uploading_files` for file upload workflows.

    Args:
        interactive_mode (bool): If True, prints status messages (e.g., "Uploading 2
            files") and :mod:`tqdm` progress bars during execution, ideal for
            interactive environments like Jupyter notebooks. Set to False for silent
            execution. Defaults to True.
        cache (bool): If True, reuses cached API responses via the :class:`AMSClient`,
            reducing API calls for user/event data retrieval or uploads. Set to False
            for fresh data. Defaults to True.
        save_to_file (Optional[str]): File path to save upload results as a CSV
            (e.g., 'results.csv'). The CSV includes columns like `user_key`,
            `file_name`, `status`, and `reason`. If None, results are not saved.
            Defaults to None.

    Args:
        interactive_mode (bool): Whether to print status messages during execution, such as
            the list of files being uploaded and their file IDs. Defaults to True.
        cache (bool): Whether to cache API responses to improve performance for repeated
            requests. Defaults to True.
        save_to_file (Optional[str]): The file path to save upload results as a CSV, including
            file names, file IDs, and server-assigned names. If None, results are not saved to
            a file. Defaults to None.

    Attributes:
        interactive_mode (bool): Indicates whether interactive mode is enabled.
        cache (bool): Indicates whether caching is enabled.
        save_to_file (Optional[str]): The file path for saving results, if specified.

    Examples:
        >>> from teamworksams import FileUploadOption, upload_and_attach_to_events
        >>> import pandas as pd
        >>> mapping_df = pd.DataFrame({
        ...     "username": ["user1"],
        ...     "file_name": ["doc1.pdf"],
        ...     "attachment_id": ["ATT123"]
        ... })
        >>> option = FileUploadOption(interactive_mode = True, save_to_file = "results.csv")
        >>> results = upload_and_attach_to_events(
        ...     mapping_df = mapping_df,
        ...     file_dir = "/path/to/files",
        ...     user_key = "username",
        ...     form = "Document Store",
        ...     file_field_name = "attachment",
        ...     url = "https://example.smartabase.com/site",
        ...     option = option
        ... )
        ℹ Uploading 1 files...
        ✔ Successfully attached 1 files to 1 events.
        ℹ Saved results to 'results.csv'
    """
    def __init__(
        self,
        interactive_mode: bool = True,
        cache: bool = True,
        save_to_file: Optional[str] = None
    ):
        self.interactive_mode = interactive_mode
        self.cache = cache
        self.save_to_file = save_to_file