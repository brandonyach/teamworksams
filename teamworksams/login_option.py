class LoginOption:
    """Options for configuring the :func:`teamworksams.login_main.login` function.

    Customizes the behavior of :func:`teamworksams.login_main.login`, controlling
    interactive feedback and client caching during authentication. Used to tailor
    the login experience for interactive or automated workflows. See
    :ref:`credentials` for usage.

    Args:
        interactive_mode (bool): If True, prints status messages during login
            (e.g., "Logging in...", "Successfully logged in"). Set to False for
            silent operation in scripts. Defaults to True.
        cache (bool): If True, stores the authenticated client for reuse by other
            functions (e.g., :func:`teamworksams.user_main.get_user`). Set to False
            for independent sessions. Defaults to True.

    Attributes:
        interactive_mode (bool): Indicates whether interactive mode is enabled.
        cache (bool): Indicates whether client caching is enabled.

    Examples:
        >>> from teamworksams import LoginOption, login
        >>> option = LoginOption(interactive_mode=True, cache=True)
        >>> login_result = login(
        ...     url="https://example.smartabase.com/site",
        ...     username="username",
        ...     password="password",
        ...     option=option
        ... )
        ℹ Logging username into https://example.smartabase.com/site...
        ✔ Successfully logged username into https://example.smartabase.com/site.
    """
    def __init__(self, interactive_mode: bool = True, cache: bool = True):
        self.interactive_mode = interactive_mode
        self.cache = cache