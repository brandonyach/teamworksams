from typing import Optional

class DeleteEventOption:
    """Options for configuring event data deletion.

    Defines customization options for the `delete_event_data` and `delete_multiple_events`
    functions, enabling interactive feedback such as confirmation prompts and status messages.
    Allows users to control whether the deletion process provides verbose output.

    Args:
        interactive_mode (bool): Whether to print status messages and prompt for confirmation
            during the deletion process. If True, users are prompted to confirm before deletion,
            and success or failure messages are displayed. If False, the operation runs silently.
            Defaults to True.

    Attributes:
        interactive_mode (bool): Indicates whether interactive mode is enabled.

    Examples:
        >>> from teamworksams import DeleteEventOption
        >>> option = DeleteEventOption(interactive_mode = True)

    """
    def __init__(
        self, 
        interactive_mode: bool = True
    ):
        self.interactive_mode = interactive_mode