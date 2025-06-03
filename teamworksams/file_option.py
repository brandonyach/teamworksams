from typing import Optional

class FileUploadOption:
    """Configuration options for file upload operations.

    Defines customization options for the `upload_files` function, controlling aspects such as
    enabling interactive feedback, caching API responses, and saving upload results to a file.
    These options allow users to tailor the upload process, optimizing performance and user
    experience.

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
        >>> from teamworksams import FileUploadOption
        >>> option = FileUploadOption(
        ...     interactive_mode = True,
        ...     cache = True,
        ...     save_to_file = "upload_results.csv"
        ... )
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