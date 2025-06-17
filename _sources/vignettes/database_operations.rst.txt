.. _get_client_ref: ../reference/get_client.html
.. _ams_client_ref: ../reference/ams_client.html
.. _get_database_ref: ../reference/get_database.html
.. _insert_database_entry_ref: ../reference/insert_database_entry.html
.. _update_database_entry_ref: ../reference/update_database_entry.html
.. _delete_database_entry_ref: ../reference/delete_database_entry.html
.. _get_database_option_ref: ../reference/get_database_option.html
.. _insert_database_option_ref: ../reference/insert_database_option.html
.. _update_database_option_ref: ../reference/update_database_option.html

.. _database_operations:

Database Operations
===================

This vignette provides a concise guide to managing database entries in Teamworks AMS using
**teamworksams**, covering `get_database() <get_database_ref_>`_, `delete_database_entry() <delete_database_entry_ref_>`_,
`insert_database_entry() <insert_database_entry_ref_>`_, and `update_database_entry() <update_database_entry_ref_>`_. It outlines simple workflows 
for retrieving, deleting, inserting, and updating entries in AMS database forms 
(e.g., 'Allergies'). See :ref:`reference` for detailed function documentation and
:ref:`exporting_data` or :ref:`importing_data` for event form data tasks.

Overview
--------

**teamworksams** supports managing AMS database forms, which store structured data like
allergies or equipment lists, with four key functions:

- `get_database() <get_database_ref_>`_: Retrieves entries as a :class:`pandas.DataFrame`.
- `delete_database_entry() <delete_database_entry_ref_>`_: Deletes a specific entry by ID.
- `insert_database_entry() <insert_database_entry_ref_>`_: Inserts new entries.
- `update_database_entry() <update_database_entry_ref_>`_: Updates existing entries by ID.

These functions are typically used for one-off tasks, such as auditing or updating a
database form. Options (`GetDatabaseOption() <get_database_option_ref_>`_, `InsertDatabaseOption() <insert_database_option_ref_>`_,
`UpdateDatabaseOption() <update_database_option_ref_>`_) customize behavior, like enabling interactive feedback or
specifying table fields. Examples use the placeholder URL
``https://example.smartabase.com/site`` and credentials managed via a ``.env`` file.

Prerequisites
-------------

Ensure **teamworksams** is installed and credentials are set, as described in
:ref:`getting_started`. Use a ``.env`` file:

.. code-block:: text
   :caption: .env

   AMS_URL=https://example.smartabase.com/site
   AMS_USERNAME=username
   AMS_PASSWORD=password

Load credentials:

.. code-block:: python

   from dotenv import load_dotenv
   load_dotenv()

Dependencies (installed with **teamworksams**): ``pandas``, ``requests``,
``python-dotenv``, ``tqdm``.

Retrieving Entries
------------------

Use `get_database() <get_database_ref_>`_ to fetch entries from a database form, such as 'Allergies':

.. code-block:: python

   import pandas as pd
   from teamworksams import get_database, GetDatabaseOption
   df = get_database(
       form_name = "Allergies",
       url = "https://example.smartabase.com/site",
       limit = 100,
       offset = 0,
       option = GetDatabaseOption(interactive_mode = True)
   )

   print(df.head())

**Output**:

.. code-block:: text

   ℹ Fetching database entries for form 'Allergies'...
   ✔ Retrieved 100 database entries for form 'Allergies'.
      id  Allergy
   0  386197   Dairy
   1  386198    Eggs

See `get_database() <get_database_ref_>`_ and `GetDatabaseOption() <get_database_option_ref_>`_ for pagination options.

Deleting Entries
----------------

Use `delete_database_entry() <delete_database_entry_ref_>`_ to remove a specific entry by ID:

.. code-block:: python

   from teamworksams import delete_database_entry

   result = delete_database_entry(
       database_entry_id = 386197,
       url = "https://example.smartabase.com/site"
   )
   print(result)

**Output**:

.. code-block:: text

   ✔ Successfully deleted database entry 386197.

See `delete_database_entry() <delete_database_entry_ref_>`_ for details.

Inserting Entries
-----------------

Use `insert_database_entry() <insert_database_entry_ref_>`_ to add new entries to a form:

.. code-block:: python

   from teamworksams import insert_database_entry, InsertDatabaseOption

   df = pd.DataFrame({"Allergy": ["Peanuts"]})

   insert_database_entry(
       df = df,
       form = "Allergies",
       url = "https://example.smartabase.com/site",
       option = InsertDatabaseOption(interactive_mode = True)
   )

**Output**:

.. code-block:: text

   ℹ Inserting 1 database entries for form 'Allergies'
   ✔ Processed 1 database entries for form 'Allergies'
   ℹ Form: Allergies
   ℹ Result: Success
   ℹ Records inserted: 1
   ℹ Records attempted: 1

See `insert_database_entry() <insert_database_entry_ref_>`_ and `InsertDatabaseOption() <insert_database_option_ref_>`_ for table fields.

Updating Entries
----------------

Use `update_database_entry() <update_database_entry_ref_>`_ to modify existing entries by `entry_id`:

.. code-block:: python

   from teamworksams import update_database_entry, UpdateDatabaseOption

   df = pd.DataFrame({"entry_id": [386198], "Allergy": ["Eggs Updated"]})

   update_database_entry(
       df = df,
       form = "Allergies",
       url = "https://example.smartabase.com/site",
       option = UpdateDatabaseOption(interactive_mode = True)
   )

**Output**:

.. code-block:: text

   ℹ Updating 1 database entries for form 'Allergies'
   Are you sure you want to update 1 existing database entries in 'Allergies'? (y/n): y
   ✔ Processed 1 database entries for form 'Allergies'
   ℹ Form: Allergies
   ℹ Result: Success
   ℹ Records updated: 1
   ℹ Records attempted: 1

See `update_database_entry() <update_database_entry_ref_>`_ and `UpdateDatabaseOption() <update_database_option_ref_>`_ for details.

Options and Usage Notes
-----------------------

This section provides detailed guidance on using option classes
(`GetDatabaseOption() <get_database_option_ref_>`_, `InsertDatabaseOption() <insert_database_option_ref_>`_, `UpdateDatabaseOption() <update_database_option_ref_>`_)
to customize database operations, along with key usage notes for caching, table fields,
pagination, entry IDs, and interactive mode.

**Option Classes**

Each database function supports a specific option class to configure its behavior. These
classes must be instantiated with parameters like `interactive_mode`, `cache`, and
`table_fields`. For example, to disable caching in `get_database() <get_database_ref_>`_:

.. code-block:: python

   from teamworksams import get_database, GetDatabaseOption

   df = get_database(
       form_name = "Allergies",
       url = "https://example.smartabase.com/site",
       option = GetDatabaseOption(cache = False)
   )

The option classes and their associated functions are:

- `get_database() <get_database_ref_>`_: `GetDatabaseOption() <get_database_option_ref_>`_
- `insert_database_entry() <insert_database_entry_ref_>`_: `InsertDatabaseOption() <insert_database_option_ref_>`_
- `update_database_entry() <update_database_entry_ref_>`_: `UpdateDatabaseOption() <update_database_option_ref_>`_

Available parameters for each option class:

- **interactive_mode (bool)**: If True, displays status messages (e.g., “Retrieved 100
  entries” for `get_database() <get_database_ref_>`_, “Processed 1 entries” for
  `insert_database_entry() <insert_database_entry_ref_>`_) and prompts for confirmation in
  `update_database_entry() <update_database_entry_ref_>`_, ideal for interactive environments like Jupyter
  notebooks. Set to False for silent execution in automated scripts. Defaults to True.
  Example:

  .. code-block:: python

     option = UpdateDatabaseOption(interactive_mode = False)
     update_database_entry(..., option = option)  # No output or prompts

- **cache (bool)**: If True, reuses an existing :class:`AMSClient` via
  :func:`get_client`, reducing API calls for authentication or form metadata retrieval.
  Set to False for fresh data, increasing API overhead. Defaults to True. See “Caching”
  below.

- **table_fields (Optional[List[str]])**: Only for `InsertDatabaseOption() <insert_database_option_ref_>`_ and
  `UpdateDatabaseOption() <update_database_option_ref_>`_. List of AMS form table field names (e.g.,
  ['Exercise']). Must match :class:`pandas.DataFrame` columns if specified. If None,
  no fields are treated as table fields. Defaults to None. See “Table Fields” below.
  Example:

  .. code-block:: python

     df = pd.DataFrame({"Exercise": ["Bench Press"], "Reps": [10]})
     option = InsertDatabaseOption(table_fields = ["Exercise", "Reps"])
     insert_database_entry(df = df, form = "Workouts", url = "...", option = option)

**Caching**

When `option.cache=True` (default), database functions reuse an existing
`AMSClient() <ams_client_ref_>`_ created by `get_client() <get_client_ref_>`_, maintaining an authenticated session
and reducing API calls for login or form metadata (e.g., form ID, type). For example:

.. code-block:: python

   option = GetDatabaseOption(cache = True)
   df1 = get_database(form_name = "Allergies", url = "...", option = option)
   df2 = get_database(form_name = "Workouts", url = "...", option = option)  # Reuses client

This improves performance for multiple operations in a session. Set `cache=False` for
independent sessions, ensuring fresh data but increasing API overhead.

**Table Fields**

Table fields in AMS database forms store multiple rows of data within a single entry,
such as exercise details in a workout log. Specify `table_fields` as a list of column
names matching the AMS form’s table fields in `insert_database_entry() <insert_database_entry_ref_>`_ or
`update_database_entry() <update_database_entry_ref_>`_. For example:

.. code-block:: python

   df = pd.DataFrame({
       "user_id": [12345, 12345],
       "session_rpe": [7, None],
       "exercise": ["Bench Press", "Squat"],
       "reps": [10, 8]
   })
   option = InsertDatabaseOption(table_fields = ["exercise", "reps"])
   insert_database_entry(df = df, form = "Workouts", url = "...", option = option)

In this example, `exercise` and `reps` are table fields, while `session_rpe` is a
non-table field recorded once per entry. The DataFrame must include `user_id` for each
row, with non-table fields populating only the first row for each entry. If
`table_fields=None` (default) and duplicate entries are detected, the function raises
an :class:`AMSError` to prevent conflicts.

**Pagination**

The `get_database() <get_database_ref_>`_ function supports pagination via `limit` and `offset` to manage
large datasets. The `limit` parameter sets the maximum number of entries returned per
request (default 10000), and `offset` specifies the starting index (default 0). For
example, to retrieve the next batch of 100 entries:

.. code-block:: python

   df = get_database(
       form_name = "Allergies",
       url = "https://example.smartabase.com/site",
       limit = 100,
       offset = 100
   )

Use smaller `limit` values for large datasets to manage memory, and increment `offset`
to fetch additional pages. Example for fetching all entries in batches:

.. code-block:: python

   dfs = []
   offset = 0
   limit = 100
   while True:
       df = get_database(
           form_name = "Allergies",
           url = "https://example.smartabase.com/site",
           limit = limit,
           offset = offset
       )
       if df.empty:
           break
       dfs.append(df)
       offset += limit
   all_entries = pd.concat(dfs, ignore_index = True)

**Entry IDs**

The `delete_database_entry() <delete_database_entry_ref_>`_ and `update_database_entry() <update_database_entry_ref_>`_ functions require
valid entry IDs (`database_entry_id` or `entry_id` in the DataFrame). Obtain these IDs
using `get_database() <get_database_ref_>`_, which returns a DataFrame with an `id` column. For example:

.. code-block:: python

   df = get_database(form_name = "Allergies", url = "...")
   entry_id = df["id"].iloc[0]
   result = delete_database_entry(database_entry_id = entry_id, url = "...")

For `update_database_entry() <update_database_entry_ref_>`_, the DataFrame must include an `entry_id` column with
valid integer IDs. Invalid or missing IDs raise an :class:`AMSError`. Example:

.. code-block:: python

   df = pd.DataFrame({"entry_id": [386198], "Allergy": ["Eggs Updated"]})
   update_database_entry(df = df, form = "Allergies", url = "...")

Always validate `entry_id` values using `get_database() <get_database_ref_>`_ to avoid errors.

**Interactive Mode**

When `interactive_mode=True` (default), database functions display progress messages
(e.g., “ℹ Inserting 1 entries”) and :mod:`tqdm` progress bars, enhancing feedback in
interactive environments. For `update_database_entry() <update_database_entry_ref_>`_, it also prompts for
confirmation to prevent accidental overwrites. Set `interactive_mode=False` for silent
execution in automated pipelines:

.. code-block:: python

   option = InsertDatabaseOption(interactive_mode = False)
   insert_database_entry(..., option = option)  # No output

Error Handling
--------------

Database functions raise :class:`AMSError` with descriptive messages:

.. code-block:: python

   get_database(form_name = "Invalid Form", url = "https://example.smartabase.com/site")

**Output**:

.. code-block:: text

   AMSError: Form 'Invalid Form' is not a database form...

Best Practices
--------------

- **Validate Form**: Ensure ``form_name`` matches an AMS database form to avoid
  :class:`AMSError`.
- **Check IDs**: Use `get_database() <get_database_ref_>`_ to obtain valid ``entry_id`` values for
  updates or deletions.
- **Use Caching**: Enable ``option.cache=True`` for efficiency in one-off tasks.
- **Confirm Updates**: Leverage ``interactive_mode=True`` in
  `UpdateDatabaseOption() <update_database_option_ref_>`_ for confirmation prompts to prevent errors.
- **Table Fields**: Specify ``table_fields`` accurately for forms with table data.

Next Steps
----------

- Explore :ref:`exporting_data` or :ref:`importing_data` for
  frequent data tasks.
- Consult :ref:`reference` for detailed function and class documentation.
- Visit `GitHub <https://github.com/brandonyach/teamworksams>`_ for support.