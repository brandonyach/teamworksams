User and Group Management
=========================

This vignette provides a comprehensive guide to managing users and groups in a Teamworks
AMS instance using **teamworksams**, covering :func:`get_user`, :func:`get_group`,
:func:`edit_user`, and :func:`create_user`. It equips you to fetch user and group data, 
update user accounts, and create new users withpractical workflows, detailed examples, 
best practices, and troubleshooting tips. See :ref:`reference` for detailed function 
documentation and :ref:`vignettes/database_operations` for additional administrative tasks.

Overview
--------

**teamworksams** simplifies user and group management through the Teamworks AMS API,
offering functions to:

- **Fetch Users**: Retrieve user data (e.g., IDs, names, account info, groups) with
  flexible filtering.
- **Fetch Groups**: List groups accessible to the user.
- **Update Users**: Modify user fields (e.g., email, name) for existing accounts.
- **Create Users**: Add new user accounts with required and optional attributes.

The functions covered in this vignette are:

- :func:`get_user`: Fetch user data, optionally filtered by attributes like group or
  email.
- :func:`get_group`: Retrieve a list of groups.
- :func:`edit_user`: Update existing user accounts.
- :func:`create_user`: Create new user accounts.

All examples use the placeholder AMS instance URL
``https://example.smartabase.com/site``, username ``username``, and password
``password``, with credentials managed via a ``.env`` file for security and ease of use.

Prerequisites
-------------

Ensure **teamworksams** is installed and credentials are configured, as described in
:ref:`vignettes/getting_started`. The recommended setup is a ``.env`` file:

.. code-block:: text
   :caption: .env

   AMS_URL = https://example.smartabase.com/site
   AMS_USERNAME = username
   AMS_PASSWORD = password

Load credentials with ``python-dotenv``:

.. code-block:: python

   from dotenv import load_dotenv
   load_dotenv()

Alternatively, use ``os``, direct arguments, or ``keyring`` (see
:ref:`vignettes/credentials`). Required dependencies (installed with
**teamworksams**): ``pandas``, ``requests``, ``python-dotenv``, ``tqdm``.

Fetching User Data with :func:`get_user`
---------------------------------------

The :func:`get_user` function retrieves user data as a :class:`pandas.DataFrame`, with
optional filtering using a :class:`UserFilter` object to narrow results by attributes
like username, email, group, or about field. It’s ideal for auditing user accounts,
generating reports, or identifying specific users.

**Basic Usage**

Fetch all accessible users:

.. code-block:: python

   from teamworksams import get_user, UserOption

   df = get_user(
       url = "https://example.smartabase.com/site",
       option = UserOption(
           columns = ["user_id", "first_name", "last_name", "email", "groups"],
           interactive_mode = True
       )
   )

   print(df)

**Output**:

.. code-block:: text

   ℹ Fetching user data...
   ✔ Retrieved 5 users.
      user_id first_name last_name                email      groups
   0    12345       John       Doe   john.doe@example.com     [TeamA]
   1    12346       Jane     Smith jane.smith@example.com     [TeamB]
   ...

**Filtering Users**

Use :class:`UserFilter` to retrieve users in a specific group:

.. code-block:: python

   from teamworksams import UserFilter

   df = get_user(
       url = "https://example.smartabase.com/site",
       filter = UserFilter(user_key = "group", user_value = "TeamA"),
       option = UserOption(interactive_mode = True)
   )

   print(df[['user_id', 'first_name', 'groups']])

**Output**:

.. code-block:: text

   ℹ Fetching user data...
   ✔ Retrieved 2 users.
      user_id first_name  groups
   0    12345       John  [TeamA]
   1    12347        Bob  [TeamA]

**Customizing Output**

Select specific columns:

.. code-block:: python

   df = get_user(
       url = "https://example.smartabase.com/site",
       option = UserOption(columns = ["user_id", "email"], interactive_mode = True)
   )
   print(df)

Fetch users by email:

.. code-block:: python

   df = get_user(
       url = "https://example.smartabase.com/site",
       filter = UserFilter(user_key = "email", user_value = ["john.doe@example.com"])
   )
   print(df[['user_id', 'email']])

**Best Practices**

- Use :class:`UserFilter` to target specific users for efficiency.
- Limit columns with ``option.columns`` to optimize DataFrame size.
- Enable ``interactive_mode`` for real-time feedback during long operations.

Fetching Group Data with :func:`get_group`
-----------------------------------------

The :func:`get_group` function retrieves a list of groups (e.g., teams, departments) as
a :class:`pandas.DataFrame`. It’s useful for auditing group structures or preparing data
for user assignments.

**Basic Usage**

Fetch all accessible groups:

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


**Best Practices**

- Use ``guess_col_type=True`` in :class:`GroupOption` to ensure consistent data types.
- Cache the client for efficiency when combining with :func:`get_user`.

Updating User Profiles with :func:`edit_user`
--------------------------------------------

The :func:`edit_user` function updates existing user fields (e.g., email, name) based on
a mapping DataFrame, using a user key (e.g., username, email) to identify users. It
returns a :class:`pandas.DataFrame` of results, making it easy to track updates and
issues. This is a powerful function as it will only update the fields based on columns
provided in the `mapping_df` - meaning that it's possible to just update things like 
username, email, e.g. alone. 

**Basic Usage**

Update user emails:

.. code-block:: python

   import pandas as pd
   from teamworksams import edit_user, UserOption
   mapping_df = pd.DataFrame({
       "username": ["john.doe", "jane.smith"],
       "email": ["john.doe@new.com", "jane.smith@new.com"]
   })

   results_df = edit_user(
       mapping_df = mapping_df,
       user_key = "username",
       url = "https://example.smartabase.com/site",
       option = UserOption(interactive_mode = True)
   )

   print(results_df)

**Output**:

.. code-block:: text

   ℹ Fetching all user data...
   ✔ Retrieved 30 users.
   ℹ Attempting to map 2 users using username from provided dataframe...
   ℹ Successfully mapped 2 users.
   ℹ Updating 2 users...
   Processing users: 100%|██████████| 2/2 [00:04<00:00, 3.46it/s]
   ✔ Successfully updated 2 users.
   Empty DataFrame
   Columns: [user_id, user_key, status, reason]
   Index: []

**Updating Multiple Fields**

Update names and emails using `about` as the key:

.. code-block:: python

   mapping_df = pd.DataFrame({
       "about": ["John Doe", "Jane Smith"],
       "first_name": ["Jonathan", "Janet"],
       "email": ["jonathan.doe@new.com", "janet.smith@new.com"]
   })

   results_df = edit_user(
       mapping_df = mapping_df,
       user_key = "about",
       url = "https://example.smartabase.com/site"
   )

   print(results_df)

**Best Practices**

- Validate ``mapping_df`` columns against supported fields (e.g., ``first_name``,
  ``email``, ``dob``).
- Use ``interactive_mode`` for progress tracking and confirmation prompts.
- Check ``results_df`` for successful updates and errors.

Creating New Users with :func:`create_user`
------------------------------------------

The :func:`create_user` function adds new user accounts, requiring fields like
``first_name``, ``username``, and ``password``. It returns a :class:`pandas.DataFrame`
of failed creations.

**Basic Usage**

Create a new user:

.. code-block:: python

   user_df = pd.DataFrame({
       "first_name": ["Alice"],
       "last_name": ["Yu"],
       "username": ["alice.yu"],
       "email": ["alice.yu@example.com"],
       "dob": ["1990-01-01"],
       "password": ["secure789"],
       "active": [True]
   })

   failed_df = create_user(
       user_df = user_df,
       url = "https://example.smartabase.com/site",
       option = UserOption(interactive_mode = True)
   )

   print(failed_df)

**Output**:

.. code-block:: text

   ℹ Creating 1 users...
   ✔ Successfully created 1 users.
   Empty DataFrame
   Columns: [user_key, reason]
   Index: []

**Creating Multiple Users**

Create users with optional fields:

.. code-block:: python

   user_df = pd.DataFrame({
       "first_name": ["Bob", "Carol"],
       "last_name": ["Lee", "Wong"],
       "username": ["bob.lee", "carol.wong"],
       "email": ["bob.lee@example.com", "carol.wong@example.com"],
       "dob": ["1985-06-15", "1992-03-22"],
       "password": ["pass123", "pass456"],
       "active": [True, False],
       "sex": ["Male", "Female"],
       "uuid": ["025380", "024854"]
   })
   failed_df = create_user(user_df = user_df, url = "https://example.smartabase.com/site")

   print(failed_df)

**Best Practices**

- Ensure required fields (``first_name``, ``last_name``, ``username``, ``email``,
  ``dob``, ``password``, ``active``) are present in ``user_df``.
- Use strong passwords compliant with AMS policies.
- Verify ``failed_df`` for creation issues.

Options and Usage Notes
-----------------------

This section provides detailed guidance on using option classes (:class:`UserOption`,
:class:`GroupOption`) and the filter class (:class:`UserFilter`) to customize user and
group operations, along with key usage notes for caching, column selection, data
validation, and interactive mode.

**Option Classes**

Each user and group function supports a specific option class to configure its behavior.
These classes must be instantiated with parameters like ``interactive_mode``,
``cache``, and others. For example, to select specific columns in :func:`get_user`:

.. code-block:: python

   from teamworksams import get_user, UserOption

   df = get_user(
       url = "https://example.smartabase.com/site",
       option = UserOption(columns = ["user_id", "email"])
   )

The option classes and their associated functions are:

- :func:`get_user`, :func:`edit_user`, :func:`create_user`: :class:`UserOption`
- :func:`get_group`: :class:`GroupOption`

Available parameters for :class:`UserOption`:

- **columns (Optional[List[str]])**: Only for :func:`get_user`. List of column names
  to include in the output DataFrame (e.g., ['user_id', 'first_name', 'email']). If
  None, includes all available columns (e.g., 'user_id', 'first_name', 'last_name',
  'email', 'groups', 'about', 'active', 'dob', 'sex', 'uuid'). Defaults to None.
  Example:

  .. code-block:: python

     option = UserOption(columns = ["user_id", "email", "groups"])
     df = get_user(url = "...", option = option)

- **interactive_mode (bool)**: If True, displays status messages (e.g., “Retrieved 5
  users” for :func:`get_user`, “Successfully updated 2 users” for :func:`edit_user`)
  and :mod:`tqdm` progress bars for :func:`edit_user` and :func:`create_user`. Set to
  False for silent execution in automated scripts. Defaults to True. Example:

  .. code-block:: python

     option = UserOption(interactive_mode = False)
     failed_df = create_user(..., option = option)  # No output

- **cache (bool)**: If True, reuses an existing :class:`AMSClient` via
  :func:`get_client`, reducing API calls for authentication or data retrieval. Set to
  False for fresh data, increasing API overhead. Defaults to True. See “Caching” below.

Available parameters for :class:`GroupOption`:

- **guess_col_type (bool)**: If True, infers column data types in the output DataFrame
  (e.g., string for 'name'), ensuring compatibility with operations like merging with
  :func:`get_user` results. Set to False to use default pandas types (e.g., object).
  Defaults to True. Example:

  .. code-block:: python

     option = GroupOption(guess_col_type = False)
     group_df = get_group(url = "...", option = option)
     print(group_df.dtypes)  # name: object

- **interactive_mode (bool)**: If True, displays status messages (e.g., “Retrieved 3
  groups”). Set to False for silent execution. Defaults to True.

- **cache (bool)**: If True, reuses an existing :class:`AMSClient`, reducing API calls.
  Defaults to True.

**Filter Class**

The :class:`UserFilter` class filters users in :func:`get_user` by attributes. For
example, to filter by email:

.. code-block:: python

   from teamworksams import UserFilter
   df = get_user(
       url = "https://example.smartabase.com/site",
       filter = UserFilter(user_key = "email", user_value = "john.doe@example.com")
   )

Available parameters for :class:`UserFilter`:

- **user_key (Optional[str])**: Attribute to filter by. Must be one of 'username',
  'email', 'group', or 'about'. For example, 'group' filters by group membership (e.g.,
  'TeamA'). If None, no filtering is applied. Defaults to None.
- **user_value (Optional[Union[str, List[str]]])**: Value(s) to match for `user_key`.
  For example, 'TeamA' or ['TeamA', 'TeamB'] for `user_key="group"`. Case-sensitive.
  If None, no filtering is applied. Defaults to None. Example:

  .. code-block:: python

     filter = UserFilter(user_key = "username", user_value = ["john.doe", "jane.smith"])
     df = get_user(url = "...", filter = filter)

Valid `user_key` values and their `user_value` requirements:

- **username**: AMS usernames (e.g., ["john.doe"]).
- **email**: User emails (e.g., ["john.doe@example.com"]).
- **about**: Full names (e.g., ["John Doe"]).
- **group**: Group name (e.g., “TeamA”). Use :func:`get_group` to list groups.

**Caching**

When `option.cache=True` (default), functions reuse an existing :class:`AMSClient`
created by :func:`get_client`, maintaining an authenticated session and reducing API
calls for login or data retrieval. For example:

.. code-block:: python

   option = UserOption(cache = True)
   user_df = get_user(url = "...", option = option)
   group_df = get_group(url = "...", option = GroupOption(cache = True))  # Reuses client

Set `cache=False` for independent sessions, ensuring fresh data but increasing API
overhead.

**Column Selection**

For :func:`get_user`, the `columns` parameter in :class:`UserOption` allows selecting
specific columns from the API response. Supported columns include:

- `user_id`: Unique AMS-generated user ID.
- `first_name`, `last_name`: User’s name.
- `email`: User’s email address.
- `groups`: List of group memberships (e.g., ['TeamA']).
- `about`: Full name (concatenation of first and last names).
- `active`: Boolean indicating account status.
- `dob`: Date of birth (format: YYYY-MM-DD).
- `sex`: Gender (e.g., “Male”, “Female”).
- `uuid`: Optional unique identifier.
- Others: Additional fields like `known_as`, `language`, `sidebar_width` (if available).

Example:

.. code-block:: python

   option = UserOption(columns = ["user_id", "email", "active"])
   df = get_user(url = "...", option = option)
   print(df.dtypes)  # user_id: int64, email: object, active: bool

**Data Validation**

For :func:`edit_user`, the `mapping_df` DataFrame must include a `user_key` column
(one of 'username', 'email', 'about', 'uuid') and updatable columns from the supported
list (e.g., `first_name`, `email`, `dob`, `sex`, `active`, `uuid`). Empty values are
sent as empty strings. Example:

.. code-block:: python

   mapping_df = pd.DataFrame({
       "uuid": ["025380"],
       "email": ["new.email@example.com"],
       "active": [False]
   })
   results_df = edit_user(mapping_df = mapping_df, user_key = "uuid", url = "...")

For :func:`create_user`, the `user_df` DataFrame must include required columns:
`first_name`, `last_name`, `username`, `email`, `dob` (format: YYYY-MM-DD),
`password`, `active` (boolean). Optional columns include `uuid`, `known_as`, `sex`,
`middle_names`, `language`, `sidebar_width`. Example:

.. code-block:: python

   user_df = pd.DataFrame({
       "first_name": ["Alice"],
       "last_name": ["Yu"],
       "username": ["alice.yu"],
       "email": ["alice.yu@example.com"],
       "dob": ["1990-01-01"],
       "password": ["secure789"],
       "active": [True],
       "sex": ["Female"]
   })
   failed_df = create_user(user_df = user_df, url = "...")

Validate data before submission to avoid :class:`AMSError`:

.. code-block:: python

   required = ["first_name", "last_name", "username", "email", "dob", "password", "active"]
   if not all(col in user_df.columns for col in required):
       print("Missing required columns:", set(required) - set(user_df.columns))
   else:
       failed_df = create_user(user_df = user_df, url = "...")

**Interactive Mode**

When `interactive_mode=True` (default), functions display progress messages (e.g.,
“ℹ Creating 1 users”) and :mod:`tqdm` progress bars for :func:`edit_user` and
:func:`create_user`, enhancing feedback in interactive environments. For
:func:`edit_user`, it includes detailed success/failure summaries. Set
`interactive_mode=False` for silent execution in automated pipelines:

.. code-block:: python

   option = UserOption(interactive_mode = False)
   results_df = edit_user(..., option = option)  # No output

Error Handling
--------------

**teamworksams** functions provide descriptive error messages via :class:`AMSError`,
with interactive feedback when ``interactive_mode`` is enabled. For simple scripts or
interactive use (e.g., Jupyter notebooks), rely on these messages:

.. code-block:: python

   df = get_user(
       url = "https://example.smartabase.com/invalid",
       option = UserOption(interactive_mode = True)
   )

**Output**:

.. code-block:: text

   ✖ Failed to log username into https://example.smartabase.com/invalid: Invalid URL or login credentials...
   AMSError: Invalid URL or login credentials...


Best Practices
--------------

- **Security**: Store credentials in ``.env`` or ``keyring`` to prevent exposure. Keep
  ``.env`` files in secure, private directories.
- **Data Validation**: Verify DataFrame inputs before calling :func:`edit_user` or
  :func:`create_user`:

  .. code-block:: python

     if mapping_df.empty:
         print("Error: Mapping DataFrame is empty")
     else:
         failed_df = edit_user(mapping_df, user_key = "username", url = "https://example.smartabase.com/site")

- **Interactive Mode**: Enable for user-friendly feedback during operations.
- **Caching**: Use a cached client for multi-call efficiency:

  .. code-block:: python

     from teamworksams import get_client
     client = get_client(url = "https://example.smartabase.com/site", cache = True)

Troubleshooting
---------------

- **No Users Found**:

  .. code-block:: text

     AMSError: No users returned from server...

  **Solution**: Check credentials and filter settings. Test without filters:

    .. code-block:: python

       df = get_user(url = "https://example.smartabase.com/site")

- **Invalid DataFrame**:

  .. code-block:: text

     ValueError: mapping_df is empty...

  **Solution**: Ensure DataFrame is non-empty and includes required columns:

    .. code-block:: python

       print(mapping_df.columns)  # Verify columns
       failed_df = edit_user(mapping_df, user_key = "username", url = "https://example.smartabase.com/site")

- **API Errors**:

  .. code-block:: text

     AMSError: Failed to fetch data... (status 503)...

  **Solution**: Check AMS server status. Retry with delay:

    .. code-block:: python

       from time import sleep
       for i in range(3):
           try:
               df = get_group(url = "https://example.smartabase.com/site")
               break
           except AMSError as e:
               print(f"Retry {i+1}: {e}")
               sleep(2)

Next Steps
----------

- Explore exporting data in :ref:`exporting_data.rst`.
- Consult :ref:`reference` for function details.
- Visit `GitHub <https://github.com/brandonyach/teamworksams>`_ for support.