class LoginOption:
    """Options for configuring the login function.

    Defines customization options for the `login` function, controlling whether interactive
    feedback is provided during the authentication process. This allows users to enable or
    disable status messages, tailoring the login experience to their needs.

    Args:
        interactive_mode (bool): Whether to print status messages during execution, such as
            login attempts and success or failure notifications. Defaults to True.

    Attributes:
        interactive_mode (bool): Indicates whether interactive mode is enabled.

    Examples:
        >>> from teamworksams import LoginOption
        >>> option = LoginOption(interactive_mode = True)

    """
    def __init__(self, interactive_mode: bool = True):
        self.interactive_mode = interactive_mode