.. _login_ref: ../reference/login.html
.. _login_option_ref: ../reference/login_option.html
.. _get_user_ref: ../reference/get_user.html
.. _get_client_ref: ../reference/get_client.html
.. _ams_client_ref: ../reference/ams_client.html

.. _credentials:

Managing Credentials, Authentication, and Caching
=================================================

This vignette provides a comprehensive guide to managing credentials for the Teamworks AMS API, authenticating with the `login() <login_ref_>`_ function, and optimizing performance using caching with the `get_client() <get_client_ref_>`_ function. This guide covers best practices, security considerations, and troubleshooting tips to ensure a smooth experience with **teamworksams**.

Overview
--------

Interacting with the Teamworks AMS API requires authentication using a valid AMS instance URL, username, and password. **teamworksams** offers flexible credential management to balance security, convenience, and performance:

- **Credentials**: Provided via environment variables, direct arguments, or `keyring` for secure storage.
- **Authentication**: Handled by the `login() <login_ref_>`_ function or automatically via `get_client() <get_client_ref_>`_ in other functions.
- **Caching**: Enabled through `get_client() <get_client_ref_>`_ to reuse authenticated sessions, reducing API overhead.

Credential Management
---------------------

**teamworksams** supports three methods for supplying credentials, each suited to different use cases. The choice depends on your security needs, project structure, and deployment environment.

**1. Environment Variables (Recommended)**

Storing credentials in a ``.env`` file is the most secure and scalable approach, especially for scripts shared across teams or deployed in production. It prevents accidental exposure in version control and simplifies credential management.

**Steps**:

1. Create a ``.env`` file in your project root:

   .. code-block:: text
      :caption: .env

      AMS_URL = https://example.smartabase.com/site
      AMS_USERNAME = username
      AMS_PASSWORD = password

2. Install ``python-dotenv`` (included with **teamworksams**):

   .. code-block:: bash

      pip install python-dotenv

3. Load the ``.env`` file and authenticate:

   .. code-block:: python

      from dotenv import load_dotenv
      from teamworksams import login, LoginOption

      load_dotenv()

      login_result = login(
          url = "https://example.smartabase.com/site",
          option = LoginOption(interactive_mode = True, cache = True)
      )

      print(f"Session Cookie: {login_result['cookie']}")
      print(f"Application ID: {login_result['login_data']['applicationId']}")

   Expected output:

   .. code-block:: text

      ℹ Logging username into https://example.smartabase.com/site...
      ✔ Successfully logged username into https://example.smartabase.com/site.
      Session Cookie: JSESSIONID=abc123
      Application ID: 45678


**Advantages**:

- **Security**: Credentials are stored outside scripts, reducing exposure risks.
- **Portability**: Works consistently across platforms without manual shell configuration.
- **Ease of Use**: No need to set environment variables manually; ``python-dotenv`` handles loading.

**Considerations**:

- Ensure the ``.env`` file is stored in a secure location (e.g., not shared publicly).

**Using Environment Variables Without Explicit Credentials**:

The `login()` function automatically uses `AMS_USERNAME` and `AMS_PASSWORD` from the `.env` file if no `username` or `password` is provided:

.. code-block:: python

   from dotenv import load_dotenv
   from teamworksams import login, LoginOption

   load_dotenv()

   login_result = login(
       url = "https://example.smartabase.com/site",
       option = LoginOption(interactive_mode = True, cache = True)
   )

   print(f"Session Cookie: {login_result['cookie']}")

**Output**:

.. code-block:: text

   ℹ Logging username into https://example.smartabase.com/site...
   ✔ Successfully logged username into https://example.smartabase.com/site.
   Session Cookie: JSESSIONID=abc123

See `login() <login_ref_>`_ for more details.


**Alternatively: Access Environment Variables with os**

**teamworksams** supports direct access to environment variables using Python’s ``os`` module, an alternative for users comfortable with shell configuration or existing workflows that set variables manually. This method is less automated than ``python-dotenv`` but provides flexibility for advanced users.

Set environment variables in your shell or via a .env file, then access variables with ``os.getenv``:

.. code-block:: python

   import os
   from teamworksams import get_user, UserOption

   url = os.getenv("AMS_URL")
   username = os.getenv("AMS_USERNAME")
   password = os.getenv("AMS_PASSWORD") 

   df = get_user(
         url = url,
         option = UserOption(interactive_mode = True)
   )
   print(df[['user_id', 'first_name', 'groups']].head())

**Output**:

.. code-block:: text

   ℹ Fetching user data...
   ✔ Retrieved 5 users.
      user_id first_name      groups
   0    12345       John     [TeamA]
   1    12346       Jane     [TeamB]
   ...

**Advantages**:

- **Flexibility**: Integrates with existing shell-based workflows.
- **No Dependencies**: Uses Python’s standard library, avoiding extra packages.
- **System Integration**: Leverages system environment variables for CI/CD or scripts.

**Considerations**:

- **Complexity**: Requires manual setup, which may confuse non-technical users.
- **Platform Differences**: Shell commands vary across Windows, macOS, and Linux.
- **Recommendation**: Use ``python-dotenv`` for end users due to its simplicity, reserving ``os`` for advanced users or specific environments.


**2. Direct Arguments**

Passing credentials directly to functions is convenient for quick prototyping or one-off scripts but should be avoided in production due to security risks.

**Example**:

.. code-block:: python

   from teamworksams import get_client, get_user, UserOption

   client = get_client(
       url = "https://example.smartabase.com/site",
       username = "username",
       password = "password",
       interactive_mode = True
   )

   df = get_user(
       client = client,
       option = UserOption(interactive_mode = True)
   )

   print(df[['user_id', 'first_name']].head())

**Output**:

.. code-block:: text

   ✔ Successfully logged username into https://example.smartabase.com/site.
   ℹ Fetching user data...
   ✔ Retrieved 5 users.
      user_id first_name
   0    12345       John
   1    12346       Jane
   ...

**Warning**:

.. warning::

   Hardcoding credentials in scripts risks exposure in version control or logs. Use this method only for temporary testing in secure environments.

**3. Keyring (Secure Storage)**

The ``keyring`` library (included with **teamworksams**) stores credentials in your system’s secure credential store (e.g., macOS Keychain, Windows Credential Locker). This is ideal for local development or automated scripts requiring high security without environment variables.

**Steps**:

1. Store credentials:

.. code-block:: python

   import keyring
   keyring.set_password("teamworksams", "username", "username")
   keyring.set_password("teamworksams", "password", "password")

2. Use **teamworksams** functions, which automatically fall back to ``keyring`` if environment variables are unset:

.. code-block:: python

   from teamworksams import get_group, GroupOption

   group_df = get_group(
         url = "https://example.smartabase.com/site",
         option = GroupOption(interactive_mode = True)
   )

   print(group_df)

**Output**:

.. code-block:: text

   ℹ Fetching group data...
   ✔ Retrieved 3 groups.
         name
   0  TeamA
   1  TeamB
   2  TeamC

**Best Practices**:

- Use the service name ``teamworksams`` for consistency.
- Test keyring access before deployment:

.. code-block:: python

   import keyring
   print(keyring.get_password("teamworksams", "username"))  # Should print: username

Authentication with `login() <login_ref_>`_
-------------------------------------------

The `login() <login_ref_>`_ function authenticates with the AMS API, returning a dictionary with session details (login data, session header, cookie). It’s useful for manual authentication, debugging, or initializing a client for custom API calls. The `LoginOption() <login_option_ref_>`_ class configures interactive feedback and client caching.


**Basic Usage**:

.. code-block:: python

   from teamworksams import login, LoginOption

   result = login(
       url = "https://example.smartabase.com/site",
       username = "username",
       password = "password",
       option = LoginOption(interactive_mode = True, cache = True)
   )

   print(result)

**Output**:

.. code-block:: text

   ℹ Logging username into https://example.smartabase.com/site...
   ✔ Successfully logged username into https://example.smartabase.com/site.
   {'login_data': {...}, 'session_header': 'abc123', 'cookie': 'JSESSIONID=abc123'}

**Using Environment Variables**:

Authenticate without explicit credentials by loading a `.env` file, and enable caching with `LoginOption(cache=True)` to reuse the authenticated client in subsequent calls:

.. code-block:: python

   from dotenv import load_dotenv
   from teamworksams import login, LoginOption

   load_dotenv()

   result = login(
       url = "https://example.smartabase.com/site",
       option = LoginOption(interactive_mode = True, cache = True)
   )

   print(result['session_header'])  # abc123

**Interactive Mode**:

Control feedback with `LoginOption() <login_option_ref_>`_

.. code-block:: python

   result = login(
       url = "https://example.smartabase.com/site",
       username = "username",
       password = "password",
       option = LoginOption(interactive_mode = False)
   )

   print(result['session_header'])  # abc123

**Error Handling**:

Handle authentication failures gracefully:

.. code-block:: python

   from teamworksams import login, AMSError

   try:
       result = login(
           url = "https://example.smartabase.com/site",
           username = "wrong",
           password = "wrong",
           option = LoginOption(interactive_mode = True, cache = True)
       )
   except AMSError as e:
       print(f"Authentication failed: {e}")

**Output**:

.. code-block:: text

   ℹ Logging wrong into https://example.smartabase.com/site...
   ✖ Failed to log wrong into https://example.smartabase.com/site: Invalid URL or login credentials...
   Authentication failed: Invalid URL or login credentials...


Caching with `get_client() <get_client_ref_>`_
----------------------------------------------

The `get_client() <get_client_ref_>`_ function creates or reuses an authenticated `AMSClient() <ams_client_ref_>`_ instance, optimizing performance by caching sessions. Caching reduces authentication overhead for repeated API calls, making it ideal for workflows involving multiple operations, custom calls, or batch operations. The `login()` function also supports caching via `LoginOption(cache=True)`, internally using `get_client()`.

**Enabling Caching**:

Use `cache=True` (default) in `get_client()` or `LoginOption` to reuse a client:

.. code-block:: python

   from teamworksams import get_client, get_user, get_group
   from teamworksams.user_option import UserOption, GroupOption

   # Create a cached client
   client = get_client(
       url = "https://example.smartabase.com/site",
       username = "username",
       password = "password",
       cache = True,
       interactive_mode = True
   )

   # Reuse client for multiple calls
   user_df = get_user(
       client = client,
       option = UserOption(interactive_mode = True)
   )

   group_df = get_group(
       client = client,
       option = GroupOption(interactive_mode = True)
   )

   print(user_df[['user_id', 'first_name']].head())
   print(group_df)

**Output**:

.. code-block:: text

   ✔ Successfully logged username into https://example.smartabase.com/site.
   ℹ Fetching user data...
   ✔ Retrieved 5 users.
   ℹ Fetching group data...
   ✔ Retrieved 3 groups.
      user_id first_name
   0    12345       John
   ...
         name
   0  TeamA
   ...

**Disabling Caching**:

Use `cache=False` for independent sessions:

.. code-block:: python

   client1 = get_client(
       url = "https://example.smartabase.com/site",
       username = "username",
       password = "password",
       cache = False,
       interactive_mode = True
   )

   client2 = get_client(
       url = "https://example.smartabase.com/site",
       username = "username",
       password = "password",
       cache = False,
       interactive_mode = True
   )

   print(client1 is client2)  # False

**Use Cases for Caching**:

- **Enabled**: Batch operations (e.g., fetching users, then groups).
- **Disabled**: Parallel scripts or testing different credentials.

**Performance Benefits**:

Caching avoids repeated logins, reducing latency and API rate limit consumption. For example, a workflow fetching multiple datasets benefits significantly:

.. code-block:: python

   from teamworksams import get_client, get_database
   from teamworksams.database_option import GetDatabaseOption

   client = get_client(
       url = "https://example.smartabase.com/site",
       username = "username",
       password = "password",
       cache = True
   )

   for form in ["Allergies", "Training Log"]:
       df = get_database(
           form_name = form,
           client = client,
           option = GetDatabaseOption(interactive_mode = True)
       )

       print(f"{form} data: {len(df)} rows")

Best Practices
--------------

- **Security**:
  - Use `.env` or `keyring` for credentials.
  - Avoid logging credentials (e.g., disable interactive mode in production logs).
- **Session Management**:
  - Enable caching for performance in multi-call workflows.
  - Disable caching for isolated or concurrent operations.
- **Error Handling**:
  - Wrap API calls in try-except blocks to handle `:class:AMSError`.
  - Log errors with context (e.g., URL, function) for debugging.
- **Environment Setup**:
  - Use virtual environments to isolate dependencies.
  - Test credentials before production deployment:

   .. code-block:: python

      from teamworksams import login
      login(url = "https://example.smartabase.com/site", username = "username", password = "password")

Troubleshooting
---------------

**Invalid URL**:

.. code-block:: text

   AMSError: Invalid AMS URL. Ensure it includes a valid site name...

**Solution**: Verify the URL format (e.g., ``https://example.smartabase.com/site``).

**Authentication Failure**:

.. code-block:: text

   AMSError: Invalid URL or login credentials...

**Solution**: Check credentials and network connectivity. Example:

.. code-block:: python

   try:
       login(
           url="https://example.smartabase.com/site",
           username="username",
           password="password"
       )
   except AMSError as e:
       print(f"Check credentials: {e}")

**Keyring Issues**:

.. code-block:: text

   keyring.errors.NoKeyringError...
   AMSError: No valid credentials provided...

**Solution**:
- Ensure `keyring` is installed and a backend is available. Install `keyrings.alt` for CI or alternative systems:

   .. code-block:: bash

      pip install keyrings.alt

- Verify credentials are set correctly:

   .. code-block:: python

      import keyring
      print(keyring.get_password("teamworksams", "username"))  # Should print: username

- If issues persist, use environment variables or direct arguments as a fallback.

**Caching Conflicts**:

.. code-block:: text

   AMSError: No valid credentials provided and no cached client available...

**Solution**: Disable caching or ensure credentials are provided:

.. code-block:: python

   client = get_client(
       url="https://example.smartabase.com/site",
       username="username",
       password="password",
       cache=False
   )

**Session Timeouts**:

.. code-block:: text

   AMSError: Connection aborted, possibly due to network issues or session expiration...

**Solution**:
- Session timeouts or network issues may occur in long-running interactive environments like Jupyter Notebook if the AMS API session expires or connectivity is interrupted. Try re-running the function, as a second attempt often succeeds by establishing a new connection. Alternatively, re-authenticate to refresh the session:

   .. code-block:: python

      from teamworksams import login, LoginOption
      from dotenv import load_dotenv

      load_dotenv()
      login(
          url = os.getenv("AMS_URL"),
          option = LoginOption(interactive_mode = True, cache = True)
      )

- To avoid session reuse issues, disable caching to create a new client per request:

   .. code-block:: python

      from teamworksams import get_event_data, EventOption

      df = get_event_data(
          url = os.getenv("AMS_URL"),
          form = "Training Log",
          start_date = "01/01/2025",
          end_date = "31/01/2025",
          option = EventOption(interactive_mode = True, cache = False)
      )

- Restarting the Jupyter kernel can clear any stale state. If issues persist, contact your AMS administrator to check server session settings or network stability.

Next Steps
----------

- Explore user management in :ref:`user_management`.
- Check the :ref:`reference` for detailed function documentation.
- Visit `GitHub <https://github.com/brandonyach/teamworksams>`_ for issues or contributions.