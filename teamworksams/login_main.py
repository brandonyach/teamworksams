from typing import Optional, Dict, Any
from .utils import AMSClient, AMSError
from .login_option import LoginOption
import os


def login(
    url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    option: Optional[LoginOption] = None
) -> Dict[str, Any]:
    """Authenticate with an AMS instance and return session details.

    Establishes a session with the AMS API using provided credentials, returning a
    dictionary with login data, session header, and cookie. Useful for verifying
    credentials or initializing a :class:`AMSClient` for custom API calls. See
    :ref:`vignettes/credentials` for authentication workflows.

    Args:
        url (str): The AMS instance URL (e.g., 'https://example.smartabase.com/site'). Must include a valid site name.
        username (Optional[str]): Username for authentication. If None, uses :envvar:`AMS_USERNAME` or :class:`keyring` credentials. Defaults to None.
        password (Optional[str]): Password for authentication. If None, uses :envvar:`AMS_PASSWORD` or :class:`keyring` credentials. Defaults to None.
        option (:class:`LoginOption`, optional): Configuration options, including `interactive_mode` to enable status messages (e.g., "Successfully logged in"). Defaults to None (uses default :class:`LoginOption`).

    Returns:
        Dict[str, Any]: A dictionary containing:
            - 'login_data': The JSON response from the login API, including user details
              (e.g., user ID, application ID).
            - 'session_header': The session header from the response headers, used for
              subsequent API calls.
            - 'cookie': The formatted cookie string (e.g., 'JSESSIONID = session_header').

    Raises:
        AMSError: If the URL is invalid, credentials are missing or invalid, the login
            request fails (e.g., HTTP 401), or the session header is not provided.

    Examples:
        >>> from teamworksams import login
        >>> from teamworksams import LoginOption
        >>> login_result = login(
        ...     url = "https://example.smartabase.com/site",
        ...     username = "user",
        ...     password = "pass",
        ...     option = LoginOption(interactive_mode = True)
        ... )
        ℹ Logging user into https://example.smartabase.com/site...
        ✔ Successfully logged user into https://example.smartabase.com/site.
        >>> print(login_result.keys())
        dict_keys(['login_data', 'session_header', 'cookie'])
        >>> print(login_result['cookie'])
        JSESSIONID=abc123
    """
    option = option or LoginOption()
    
    if option.interactive_mode:
        username_display = username or "AMS_USERNAME"
        print(f"ℹ Logging {username_display} into {url}...")
    
    # Validate credentials
    if not username or not password:
        username = os.getenv("AMS_USERNAME")
        password = os.getenv("AMS_PASSWORD")
        if not username or not password:
            if option.interactive_mode:
                print(f"✖ Failed to log {username_display} into {url}: No valid credentials provided")
            raise AMSError("No valid credentials provided. Supply 'username' and 'password' or set AMS_USERNAME/AMS_PASSWORD env vars.")
    
    try:
        client = AMSClient(url, username, password)
        
        if not client.authenticated:
            if option.interactive_mode:
                print(f"✖ Failed to log {username} into {url}: Authentication failed")
            raise AMSError("Authentication failed")
        
        login_object = {
            "login_data": client.login_data,
            "session_header": client.session_header,
            "cookie": f"JSESSIONID={client.session_header}"
        }
        
        if option.interactive_mode:
            print(f"✔ Successfully logged {username_display} into {url}.")
        
        return login_object
    
    except AMSError as e:
        if option.interactive_mode:
            print(f"✖ Failed to log {username_display} into {url}: {str(e)}")
