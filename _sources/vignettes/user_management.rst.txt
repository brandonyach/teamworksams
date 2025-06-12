User and Group Management
=========================

This vignette provides a comprehensive guide to managing users and groups in a Teamworks AMS instance using **teamworksams**. This guide equips you to leverage **teamworksams**’s powerful user management functions effectively to fetching user and group data, update user accounts, and create new users with practical examples, best practices, and troubleshooting tips.

Overview
--------

**teamworksams** simplifies user and group management through the Teamworks AMS API, offering functions to:

- **Fetch Users**: Retrieve user data (e.g., IDs, names, account info, groups) with flexible filtering.
- **Fetch Groups**: List groups accessible to the user.
- **Update Users**: Modify user fields (e.g., email, name) for existing accounts.
- **Create Users**: Add new user accounts with required and optional attributes.

The functions covered in this vignette are:

- ``get_user``: Fetch user data, optionally filtered by attributes like group or email.
- ``get_group``: Retrieve a list of groups.
- ``edit_user``: Update existing user accounts.
- ``create_user``: Create new user accounts.

All examples use the placeholder AMS instance URL ``https://example.smartabase.com/site``, username ``username``, and password ``password``, with credentials managed via a ``.env`` file for security and ease of use.

Prerequisites
-------------

Ensure **teamworksams** is installed and credentials are configured, as described in :ref:`vignettes/getting_started`. The recommended setup is a ``.env`` file:

.. code-block:: text
   :caption: .env

   AMS_URL = https://example.smartabase.com/site
   AMS_USERNAME = username
   AMS_PASSWORD = password

Load credentials with ``python-dotenv``:

.. code-block:: python

   from dotenv import load_dotenv
   load_dotenv()

Alternatively, use ``os``, direct arguments, or ``keyring`` (see :ref:`vignettes/credentials`).

Fetching User Data with ``get_user``
-----------------------------------

The ``get_user`` function retrieves user data as a pandas DataFrame, with optional filtering using a ``UserFilter`` object to narrow results by attributes like username, email, group, or about field. It’s ideal for auditing user accounts, generating reports, or identifying specific users.

**Basic Usage**:

Fetch all accessible users:

.. code-block:: python

   from dotenv import load_dotenv
   from teamworksams import get_user, UserOption

   load_dotenv()

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

**Filtering Users**:

Use ``UserFilter`` to retrieve users in a specific group:

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

**Customizing Output**:

Select specific columns:

.. code-block:: python

   df = get_user(
       url="https://example.smartabase.com/site",
       option=UserOption(columns=["user_id", "email"], interactive_mode=True)
   )

   print(df)

**Best Practices**:

- Use ``UserFilter`` to reduce API load when targeting specific users.
- Limit columns with ``option.columns`` to optimize DataFrame size.
- Enable ``interactive_mode`` for real-time feedback during long operations.

Fetching Group Data with ``get_group``
-------------------------------------

The ``get_group`` function retrieves a list of groups (e.g., teams, departments) as a pandas DataFrame. It’s useful for auditing group structures or preparing data for user assignments.

**Usage**:

.. code-block:: python

   from teamworksams import get_group, GroupOption

   group_df = get_group(
       url="https://example.smartabase.com/site",
       option=GroupOption(interactive_mode=True)
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

- Use ``guess_col_type=True`` in ``GroupOption`` to infer data types automatically.
- Combine with ``get_user`` to map users to groups:

  .. code-block:: python

     user_df = get_user(
         url="https://example.smartabase.com/site",
         filter=UserFilter(user_key="group", user_value="TeamA")
     )

     print(user_df.merge(group_df, left_on="groups", right_on="name", how="inner"))

Updating User Profiles with ``edit_user``
----------------------------------------

The ``edit_user`` function updates existing user fields (e.g., email, name) based on a mapping DataFrame, using a user key (e.g., username, email) to identify users. It returns a DataFrame of results, making it easy to track updates and issues.

**Example**:

Update user emails:

.. code-block:: python

   import pandas as pd
   from teamworksams import edit_user, import UserOption

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
   ✔ Successfully updated 2 users.
   ✔ No failed operations.


**Best Practices**:

- Validate `mapping_df` columns against supported fields (e.g., `first_name`, `email`).
- Use `interactive_mode` for progress tracking.
- Check `results_df` for successful updates and errors


Creating New Users with ``create_user``
--------------------------------------

The ``create_user`` function adds new user accounts, requiring fields like `first_name`, `username`, and `password`. It returns a DataFrame of failed creations.

**Example**:

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

   ℹ Creating users...
   ✔ Successfully created 1 users.
   Empty DataFrame
   Columns: [user_key, reason]

**Best Practices**:

- Ensure required fields are present in `user_df`.
- Use strong passwords compliant with AMS policies.
- Verify `failed_df` for creation issues.

Error Handling
--------------

**teamworksams** functions provide descriptive error messages via ``AMSError``, with interactive feedback when ``interactive_mode`` is enabled. For simple scripts or interactive use (e.g., Jupyter notebooks), you can rely on these messages:

.. code-block:: python

   df = get_user(
       url="https://example.smartabase.com/invalid",
       option=UserOption(interactive_mode=True)
   )

**Output**:

.. code-block:: text

   ✖ Failed to log username into https://example.smartabase.com/invalid: Invalid URL or login credentials...
   AMSError: Invalid URL or login credentials...

For advanced workflows (e.g., automated scripts), use try-except blocks to handle errors gracefully, such as retrying or logging:

.. code-block:: python

   from teamworksams import get_user, AMSError
   from time import sleep

   for attempt in range(3):
       try:
           df = get_user(
               url="https://example.smartabase.com/site",
               option=UserOption(interactive_mode=True)
           )
           print(df.head())
           break
       except AMSError as e:
           print(f"Attempt {attempt + 1} failed: {e}")
           if "503" in str(e):  # Service unavailable
               sleep(2 ** attempt)
           else:
               break

**Output** (if 503 error):

.. code-block:: text

   Attempt 1 failed: Failed to fetch data... (status 503)...
   Attempt 2 failed: Failed to fetch data... (status 503)...
   ✔ Retrieved 5 users.
      user_id first_name
   0    12345       John
   ...

**Logging Errors**:

Log errors to a file for auditing:

.. code-block:: python

   import logging
   logging.basicConfig(filename="ams_errors.log", level=logging.ERROR)

   try:
       failed_df = edit_user(
           mapping_df=pd.DataFrame({"username": ["invalid"]}),
           user_key="username",
           url="https://example.smartabase.com/site"
       )
   except AMSError as e:
       logging.error(f"Edit user failed: {e}")
       print(f"Check ams_errors.log for details")

Best Practices
--------------

- **Security**: Store credentials in ``.env`` or ``keyring`` to prevent exposure. Keep ``.env`` files in secure, private directories.
- **Data Validation**: Verify DataFrame inputs before calling `edit_user` or `create_user`:

  .. code-block:: python

     if mapping_df.empty:
         print("Error: Mapping DataFrame is empty")
     else:
         failed_df = edit_user(mapping_df, user_key="username", url="https://example.smartabase.com/site")

- **Interactive Mode**: Enable for user-friendly feedback during operations.
- **Caching**: Use a cached client for multi-call efficiency:

  .. code-block:: python

     from teamworksams import get_client
     client = get_client(url="https://example.smartabase.com/site", cache=True)

Troubleshooting
---------------

- **No Users Found**:

  .. code-block:: text

     AMSError: No users returned from server...

  **Solution**: Check credentials and filter settings. Test without filters:

    .. code-block:: python

       df = get_user(url="https://example.smartabase.com/site")

- **Invalid DataFrame**:

  .. code-block:: text

     ValueError: mapping_df is empty...

  **Solution**: Ensure DataFrame is non-empty and includes required columns:

    .. code-block:: python

       print(mapping_df.columns)  # Verify columns
       failed_df = edit_user(mapping_df, user_key="username", url="https://example.smartabase.com/site")

- **API Errors**:

  .. code-block:: text

     AMSError: Failed to fetch data... (status 503)...

  **Solution**: Check AMS server status. Retry with delay:

    .. code-block:: python

       from time import sleep
       for i in range(3):
           try:
               df = get_group(url="https://example.smartabase.com/site")
               break
           except AMSError as e:
               print(f"Retry {i+1}: {e}")
               sleep(2)

Next Steps
----------

- Explore database management in :ref:`vignettes/database_operations`.
- Consult :ref:`api_reference` for function details.
- Visit `GitHub <https://github.com/yachb35/teamworksams>`_ for support.