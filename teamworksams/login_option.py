class LoginOption:
    """Options for configuring the :func:`teamworksams.login_main.login` function.

    Customizes the behavior of :func:`login`, controlling whether interactive feedback
    is displayed during authentication. Used to tailor the login experience for
    interactive or automated workflows. See :ref:`credentials` for usage.

    Args:
        interactive_mode (bool): If True, prints status messages during login (e.g., "Logging in...", "Successfully logged in"). Set to False for silent operation in scripts. Defaults to True.

    Attributes:
        interactive_mode (bool): Indicates whether interactive mode is enabled.

    Examples:
        >>> from teamworksams import LoginOption, login
        >>> option = LoginOption(interactive_mode = True)
        >>> login_result = login(
        ...     url="https://example.smartabase.com/site",
        ...     username = "username",
        ...     password = "password",
        ...     option = option
        ... )
        ℹ Logging username into https://example.smartabase.com/site...
        ✔ Successfully logged username into https://example.smartabase.com/site.

    """
    def __init__(self, interactive_mode: bool = True):
        self.interactive_mode = interactive_mode