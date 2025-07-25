import requests
import os
from datetime import datetime
import hashlib
from typing import Optional, Dict, Tuple
try:
    import keyring
except ImportError:
    keyring = None


class AMSError(Exception):
    """Base exception for AMS operations and errors.

    Raised for errors during AMS API interactions, such as authentication failures or
    invalid responses. Provides detailed error information, including function, endpoint,
    and HTTP status code, to aid debugging. Used by functions like
    :func:`get_client` and :func:`login`.

    Args:
        message (str): The primary error message describing the issue.
        function (Optional[str]): Name of the function where the error occurred (e.g., 'login'). Defaults to None.
        endpoint (Optional[str]): API endpoint involved (e.g., 'user/loginUser'). Defaults to None.
        status_code (Optional[int]): HTTP status code of the error (e.g., 401 for unauthorized). Defaults to None.

    Attributes:
        message (str): The primary error message.
        function (Optional[str]): The function where the error occurred.
        endpoint (Optional[str]): The API endpoint involved.
        status_code (Optional[int]): The HTTP status code.

    Examples:
        >>> try:
        ...     raise AMSError(
        ...         message="Invalid credentials",
        ...         function="login",
        ...         endpoint="user/loginUser",
        ...         status_code=401
        ...     )
        ... except AMSError as e:
        ...     print(str(e))
        Invalid credentials - Function: login - Endpoint: user/loginUser - Status Code: 401. Please check inputs or contact your site administrator.
    """
    def __init__(
        self,
        message: str,
        function: Optional[str] = None,
        endpoint: Optional[str] = None,
        status_code: Optional[int] = None
    ):
        self.message = message
        self.function = function
        self.endpoint = endpoint
        self.status_code = status_code
        error_parts = [message]
        if function:
            error_parts.append(f"Function: {function}")
        if endpoint:
            error_parts.append(f"Endpoint: {endpoint}")
        if status_code is not None:
            error_parts.append(f"Status Code: {status_code}")
        full_message = " - ".join(error_parts) + ". Please check inputs or contact your site administrator."
        super().__init__(full_message)



class AMSClient:
    """A client for interacting with the AMS API.

    Handles authentication, API requests, and caching for AMS operations. Created by
    :func:`get_client` and used internally by functions like
    :func:`get_user`. Supports direct use for custom API calls
    with methods like :meth:`_fetch`. Uses stateless connections for each request to
    ensure reliability. See :ref:`credentials` for setup.

    Args:
        url (str): The AMS instance URL (e.g., 'https://example.smartabase.com/site'). Must include a valid site name.
        username (Optional[str]): Username for authentication. If None, uses :envvar:`AMS_USERNAME` or :class:`keyring` credentials. Defaults to None.
        password (Optional[str]): Password for authentication. If None, uses :envvar:`AMS_PASSWORD` or :class:`keyring` credentials. Defaults to None.

    Attributes:
        url (str): The validated AMS instance URL.
        app_name (str): The site name extracted from the URL.
        headers (Dict[str, str]): HTTP headers for API requests.
        username (str): The username used for authentication.
        password (str): The password used for authentication.
        authenticated (bool): Whether the client is authenticated.
        session (requests.Session): Legacy session object (maintained for compatibility).
        login_data (Dict): The response data from the login API call.
        _cache (Dict[str, Dict]): Cache for API responses.
    """
    def __init__(
            self, 
            url: str, 
            username: Optional[str] = None, 
            password: Optional[str] = None
        ):
        self.url = self._validate_url(url)
        self.app_name = self.url.split('/')[-1].strip()
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "python-teamworksams",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
            "X-APP-ID": "external.example.postman"
        }
        self._cache: Dict[str, Dict] = {}
        self.username = username or os.getenv("AMS_USERNAME")
        self.password = password or os.getenv("AMS_PASSWORD")
        self.authenticated = False
        self.session = requests.Session()
        self.session_header = None  
        self.login_data = {}
        self.last_uploaded_files = []
        if not self.username or not self.password:
                 raise AMSError("No valid credentials provided. Supply 'username' and 'password' or set AMS_USERNAME/AMS_PASSWORD env vars.")
        self.session.auth = (self.username, self.password)
        self._login()


    def _login(self) -> None:
        """Authenticate with AMS and store login data.

        Sends a login request to the AMS API using the provided username and password.
        Updates the session headers with the session token received from the server.

        Raises:
            AMSError: If login fails due to invalid credentials, URL, or missing session header.
        """
        if not self.username or not self.password:
            raise AMSError("No valid credentials provided for login. Supply 'username' and 'password' or set AMS_USERNAME/AMS_PASSWORD env vars.")
        login_url = self._AMS_url("user/loginUser", api_version="v2")
        payload = {
            "username": self.username,
            "password": self.password,
            "loginProperties": {"appName": self.app_name, "clientTime": datetime.now().isoformat()[:19]}
        }
        response = self.session.post(login_url, json=payload, headers=self.headers)
        if response.status_code != 200:
            error_text = response.text.lower()
            if response.status_code == 401:
                raise AMSError("Invalid URL or login credentials.")
            raise AMSError(f"Login failed with status {response.status_code}.")
        self.session_header = response.headers.get("session-header")
        if not self.session_header:
            raise AMSError("No session header received from server.")
        
        self.login_data = response.json()
        if self.login_data.get('__is_rpc_exception__', False):
            error_message = self.login_data.get('value', {}).get('detailMessage', 'Unknown login error')
            raise AMSError(f"Login failed: {error_message}")
        
        self.headers["session-header"] = self.session_header
        self.headers["Cookie"] = f"JSESSIONID={self.session_header}"
        self.session.headers.update(self.headers)
        self.authenticated = True

    
    
    def _AMS_url(self, endpoint: str, api_version: str = "v1") -> str:
        """Construct an AMS API URL for the given endpoint and API version.

        Args:
            endpoint (str): The API endpoint (e.g., 'usersearch').
            api_version (str): The API version to use (default: 'v1').

        Returns:
            str: The full API URL (e.g., 'https://example.smartabase.com/site/api/v1/usersearch?informat=json&format=json').
        """
        return f"{self.url}/api/{api_version}/{endpoint.lstrip('/')}?informat=json&format=json"

    
    
    def _fetch(
            self, 
            endpoint: str, 
            method: str = "POST", 
            payload: Optional[dict] = None, 
            cache: bool = True, 
            api_version: str = "v1",
            timeout: Tuple[float, float] = (300, 300)
        ):
        """Fetch data from the AMS API with caching.

        Sends an HTTP request to the specified endpoint using a new connection for each request.
        Returns the JSON response. Uses caching to avoid redundant API calls if enabled.

        Args:
            endpoint (str): The API endpoint to fetch (e.g., 'usersearch').
            method (str): HTTP method to use ('POST' or 'GET', default: 'POST').
            payload (Optional[dict]): The JSON payload to send with the request (default: None).
            cache (bool): Whether to cache the response (default: True).
            api_version (str): The API version to use for this request (default: 'v1').

        Returns:
            Any: The JSON response from the API, or None if the response is empty.

        Raises:
            AMSError: If the API request fails or returns a non-200 status code.
        """
        import requests.exceptions
        
        if not self.authenticated:
            self._login()
        cache_key = hashlib.sha256(f"{self.url}{endpoint}{str(payload or '')}".encode()).hexdigest()
        
        if cache and cache_key in self._cache:
            return self._cache[cache_key]
        url = self._AMS_url(endpoint, api_version=api_version) if method == "POST" else f"{self.url}/api/v3/{endpoint.lstrip('/')}"
        kwargs = {"headers": self.headers}
        
        if payload and method != "GET":
            kwargs["json"] = payload
        # response = self.session.request(method, url, **kwargs)
        try:
            response = requests.request(method, url, timeout = timeout, **kwargs)
        except requests.exceptions.ConnectionError as e:
            raise AMSError(
                f"Connection aborted, possibly due to network issues or session expiration: {str(e)}. Try re-running the function or re-authenticating with login().",
                function="_fetch",
                endpoint=endpoint
            )
        except requests.exceptions.Timeout as e:
            raise AMSError(
                f"Timeout occurred during request to endpoint '{endpoint}': {str(e)}.",
                function="_fetch",
                endpoint=endpoint
            )
        if response.status_code != 200:
            if response.status_code == 403:
                error_message = (
                    f"Access denied, possibly due to invalid URL, credentials, or insufficient permissions for endpoint '{endpoint}'. "
                    f"Verify AMS_URL (e.g., 'https://example.smartabase.com/site'), AMS_USERNAME, AMS_PASSWORD, or contact your site administrator."
                )
                if "access denied" in response.text.lower():
                    error_message = (
                        f"Access denied to endpoint '{endpoint}', possibly due to invalid URL, credentials, or insufficient permissions. "
                        f"Verify AMS_URL (e.g., 'https://example.smartabase.com/site'), AMS_USERNAME, AMS_PASSWORD, or check group permissions."
                    )
            elif response.status_code == 401:
                error_message = (
                    f"Authentication failed for endpoint '{endpoint}'. Ensure AMS_URL, AMS_USERNAME, and AMS_PASSWORD are correct, "
                    f"or re-authenticate with :py:func:`teamworksams.login_main.login`."
                )
            else:
                error_message = f"Failed to fetch data from {endpoint} (status {response.status_code}): {response.text[:200]}..."
            raise AMSError(
                error_message,
                function="_fetch",
                endpoint=endpoint,
                status_code=response.status_code
            )
        try:
            data = response.json()
        except ValueError:
            data = None
        if cache:
            self._cache[cache_key] = data
        else:
            self._cache.clear()
        return data
        
    
    

    def _validate_url(self, url: str) -> str:
        """Validate the AMS URL.

        Args:
            url (str): The AMS instance URL (e.g., 'https://example.smartabase.com/site').

        Returns:
            str: The validated URL with trailing slashes removed.

        Raises:
            AMSError: If the URL is invalid or missing a site name.
        """
        app_name = url.rstrip('/').split('/')[-1].strip()
        if not app_name:
            raise AMSError("Invalid AMS URL. Ensure it includes a valid site name (e.g., 'https://example.smartabase.com/site_name').")
        return url.rstrip('/')


persistent_client: Optional['AMSClient'] = None


def get_client(
        url: str, 
        username: Optional[str] = None, 
        password: Optional[str] = None, 
        cache: bool = True, 
        interactive_mode: bool = False
    ) -> AMSClient:
    """Create or retrieve an authenticated :class:`AMSClient` instance.

    Creates a new :class:`AMSClient` instance with the provided credentials or reuses an existing
    authenticated client if caching is enabled. The client is used for all AMS API
    interactions, handling authentication and session management. Provides interactive
    feedback on login success if enabled. This function is typically called internally by
    other public-facing functions but can be used directly to initialize a client. Use this 
    function for custom API calls or batch operations requiring an authenticated client.

    Args:
        url (str): The AMS instance URL (e.g., 'https://example.smartabase.com/site'). Must include a valid site name (e.g., '/site').
        username (Optional[str]): Username for authentication. If None, uses :envvar:`AMS_USERNAME` or :class:`keyring` credentials. Defaults to None.
        password (Optional[str]): Password for authentication. If None, uses :envvar:`AMS_PASSWORD` or :class:`keyring` credentials. Defaults to None.
        cache (bool): Reuse an existing authenticated client if available. Set to False for independent sessions (e.g., parallel scripts). Defaults to True.
        interactive_mode (bool): Print status messages (e.g., login success). Useful for interactive workflows. Defaults to False.

    Returns:
        :class:`AMSClient`: An authenticated client ready for API interactions.

    Raises:
        :class:`AMSError`: If the URL is invalid, credentials are missing, or authentication fails.

    Examples:
        >>> from teamworksams import get_client
        >>> client = get_client(
        ...     url="https://example.smartabase.com/site",
        ...     username = "user",
        ...     password = "pass",
        ...     cache = True,
        ...     interactive_mode = True
        ... )
        ✔ Successfully logged user into https://example.smartabase.com/site.
        >>> print(client.authenticated)
        True
    """
    global persistent_client
    if cache and persistent_client and persistent_client.authenticated:
        return persistent_client
    
    if not username or not password:
        username = username or os.getenv("AMS_USERNAME")
        password = password or os.getenv("AMS_PASSWORD")
        if not username or not password and keyring is not None:
            username = username or keyring.get_password("teamworksams", "username")
            password = password or keyring.get_password("teamworksams", "password")
    
    if not username or not password:
        raise AMSError("No valid credentials provided and no cached client available. Supply 'username' and 'password'.")
    
    client = AMSClient(url, username, password)
    if interactive_mode:
        print(f"✔ Successfully logged {username} into {url}.")
    
    if cache:
        persistent_client = client  
    else:
        persistent_client = None 
    
    return client