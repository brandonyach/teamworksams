from typing import Optional

class DeleteEventOption:
    """Options for configuring event data deletion.

    Customizes the behavior of :func:`teamworksams.delete_main.delete_event_data` and
    :func:`teamworksams.delete_main.delete_multiple_events`, controlling whether
    interactive feedback, such as confirmation prompts and status messages, is enabled.
    Ensures safe deletion of AMS events. See :ref:`vignettes/deleting_data` for
    deletion workflows.

    Args:
        interactive_mode (bool): If True, prompts for user confirmation before deletion
            and prints status messages (e.g., "Deleted event with SUCCESS"),
            ideal for interactive environments like Jupyter notebooks. Set to
            False for silent execution in automated scripts. Defaults to True.

    Attributes:
        interactive_mode (bool): Indicates whether interactive mode is enabled.

    Examples:
        >>> from teamworksams import DeleteEventOption, delete_event_data
        >>> option = DeleteEventOption(interactive_mode = True)
        >>> result = delete_event_data(
        ...     event_id = 134273,
        ...     url = "https://example.smartabase.com/site",
        ...     option = option
        ... )
        Are you sure you want to delete event '134273'? (y/n): y
        ℹ Deleting event with ID 134273...
        ✔ SUCCESS: Deleted 134273

    """
    def __init__(
        self, 
        interactive_mode: bool = True
    ):
        self.interactive_mode = interactive_mode