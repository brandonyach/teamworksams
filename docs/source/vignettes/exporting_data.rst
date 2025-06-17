.. _get_event_data_ref: ../reference/get_event_data.html
.. _sync_event_data_ref: ../reference/sync_event_data.html
.. _event_filter_ref: ../reference/event_filter.html
.. _event_option_ref: ../reference/event_option.html
.. _sync_event_filter_ref: ../reference/sync_event_filter.html
.. _sync_event_option_ref: ../reference/sync_event_option.html
.. _ams_client_ref: ../reference/ams_client.html
.. _get_client_ref: ../reference/get_client.html

.. _exporting_data:

Exporting Data
==============

This vignette provides an in-depth guide to exporting event data from Teamworks AMS using
**teamworksams**, focusing on the `get_event_data() <get_event_data_ref_>`_ and `sync_event_data() <sync_event_data_ref_>`_
functions. It covers practical workflows for retrieving event data within a date range, 
synchronizing updated events, and applying filters and options to customize outputs. 
This guide equips you to efficiently export AMS event data for analysis or reporting. See
:ref:`reference` for detailed function documentation and
:ref:`importing_data` for additional data workflows.

Overview
--------

**teamworksams** simplifies exporting AMS event data, offering two key functions:

- `get_event_data() <get_event_data_ref_>`_: Retrieves event data from an AMS Event Form (e.g., 'Training
  Log') for a specified date range, with optional filtering by user attributes or data
  fields and support for downloading attachments.
- `sync_event_data() <sync_event_data_ref_>`_: Fetches events inserted or updated since a synchronization
  time, ideal for incremental data updates, with options to include user metadata or UUIDs.

These functions return :class:`pandas.DataFrame` objects, enabling seamless integration
with Python data analysis tools like pandas. Filters (`EventFilter() <event_filter_ref_>`_,
`SyncEventFilter() <sync_event_filter_ref_>`_) and options (`EventOption() <event_option_ref_>`_, `SyncEventOption() <sync_event_option_ref_>`_)
provide fine-grained control over data retrieval. All examples use the placeholder URL
``https://example.smartabase.com/site``, username ``username``, and password ``password``,
managed via a ``.env`` file.

Prerequisites
-------------

Ensure **teamworksams** is installed and credentials are configured, as described in
:ref:`getting_started`. Use a ``.env`` file for secure credential management:

.. code-block:: text
   :caption: .env

   AMS_URL=https://example.smartabase.com/site
   AMS_USERNAME=username
   AMS_PASSWORD=password

Load credentials:

.. code-block:: python

   from dotenv import load_dotenv
   load_dotenv()

Required dependencies (installed with **teamworksams**): ``pandas``, ``requests``,
``python-dotenv``, ``tqdm``. See :ref:`credentials` for alternative credential
methods (``os``, direct arguments, ``keyring``).

Exporting Event Data
--------------------

Use `get_event_data() <get_event_data_ref_>`_ to retrieve event data from an AMS Event Form within a date
range, optionally filtering by user attributes or data fields and customizing outputs
with `EventOption() <event_option_ref_>`_.

**Basic Usage**

Fetch all events from the 'Training Log' form for January 2025:

.. code-block:: python

   from teamworksams import get_event_data
   df = get_event_data(
       form = "Training Log",
       start_date = "01/01/2025",
       end_date = "31/01/2025",
       url = "https://example.smartabase.com/site",
       option = EventOption(interactive_mode = True)
   )
   print(df.head())

**Output**:

.. code-block:: text

   ℹ Requesting event data for 'Training Log' between 01/01/2025 and 31/01/2025
   ✔ Retrieved 10 event records for form 'Training Log'.
      about  user_id  event_id  form         start_date  duration  intensity
        0  John Doe    12345    67890  Training Log  01/01/2025        60       High
        1  Jane Smith  12346    67891  Training Log  02/01/2025        45     Medium
   ...

**Filtering Events**

Use `EventFilter() <event_filter_ref_>`_ to narrow results, e.g., events for users in 'TeamA' with
'intensity' equal to 'High':

.. code-block:: python

   from teamworksams import EventFilter, EventOption
   df = get_event_data(
       form = "Training Log",
       start_date = "01/01/2025",
       end_date = "31/01/2025",
       url = "https://example.smartabase.com/site",
       filter = EventFilter(
           user_key = "group",
           user_value = "TeamA",
           data_key = "intensity",
           data_value = "High",
           data_condition = "equals"
       ),
       option = EventOption(interactive_mode = True, clean_names = True)
   )
   print(df[['user_id', 'intensity']].head())

**Output**:

.. code-block:: text

   ℹ Requesting event data for 'Training Log' between 01/01/2025 and 31/01/2025
   ✔ Retrieved 5 event records for form 'Training Log'.
      user_id intensity
   0    12345      High
   1    12347      High
   ...

**Downloading Attachments**

Download event attachments to a specified directory - either a specified absolute 
or relative path. If None, attachments will be saved in the current working directory. 

.. code-block:: python

   df = get_event_data(
       form = "Training Log",
       start_date = "01/01/2025",
       end_date = "31/01/2025",
       url = "https://example.smartabase.com/site",
       option = EventOption(
           interactive_mode = True,
           download_attachment = True,
           attachment_directory = "./attachments"
       )
   )
   print(df.columns)

**Output**:

.. code-block:: text

   ℹ Requesting event data for 'Training Log' between 01/01/2025 and 31/01/2025
   ✔ Retrieved 10 event records for form 'Training Log'.
   Index(['about', 'user_id', 'event_id', 'form', 'start_date', 'attachment_path'], ...)

See `get_event_data() <get_event_data_ref_>`_, `EventFilter() <event_filter_ref_>`_, and `EventOption() <event_option_ref_>`_ for details.

Synchronizing Event Data
------------------------

Use `sync_event_data() <sync_event_data_ref_>`_ to fetch events inserted or updated since a synchronization
time, ideal for incremental updates. Returns a :class:`pandas.DataFrame` and a new
synchronization time.

**Basic Usage**

Synchronize events from 'Training Log' since March 1, 2023:

.. code-block:: python

   from teamworksams import sync_event_data, SyncEventOption
   df, new_sync_time = sync_event_data(
       form = "Training Log",
       last_synchronisation_time = 1677654321000,  # 2023-03-01 12:25:21
       url = "https://example.smartabase.com/site",
       option = SyncEventOption(interactive_mode = True)
   )
   print(df[['user_id', 'start_date']].head())
   print(f"New sync time: {new_sync_time}")

**Output**:

.. code-block:: text

   ℹ Requesting event data for 'Training Log' since 2023-03-01 12:25:21
   ✔ Retrieved 5 event records for 'Training Log' since 2023-03-01 12:25:21
      user_id start_date
   0    12345 2025-03-01
   ...
   New sync time: 1677654400000

Now, the next time you synchronise with that form, you can use the newly acquired 
'new_sync_time' value to find any records that have been inserted/updated since 
you last called `sync_event_data() <sync_event_data_ref_>`_:

.. code-block:: python

   df, new_sync_time = sync_event_data(
       form = "Training Log",
       last_synchronisation_time = new_sync_time,
       url = "https://example.smartabase.com/site",
       option = SyncEventOption(interactive_mode = True)
   )

By querying which records have been inserted/updated in a form beyond a certain time, 
you can set up workflows that automatically trigger Python scripts whenever new data 
is detected. 

**Filtering Synchronized Events**

Synchronize events for users in 'TeamA':

.. code-block:: python

   from teamworksams import SyncEventFilter
   df, new_sync_time = sync_event_data(
       form = "Training Log",
       last_synchronisation_time = 1677654321000,
       url = "https://example.smartabase.com/site",
       filter = SyncEventFilter(user_key = "group", user_value = "TeamA"),
       option = SyncEventOption(interactive_mode = True, include_user_data = True)
   )
   print(df[['about', 'start_date']].head())

**Output**:

.. code-block:: text

   ℹ Requesting event data for 'Training Log' since 2023-03-01 12:25:21
   ✔ Retrieved 3 event records for 'Training Log' since 2023-03-01 12:25:21
      about      start_date
   0  John Doe  2025-03-01
   ...

**Handling Deleted Events**

Access deleted event IDs from the DataFrame’s attributes:

.. code-block:: python

   deleted_ids = df.attrs['deleted_event_ids']
   print(f"Deleted event IDs: {deleted_ids}")

**Output**:

.. code-block:: text

   Deleted event IDs: [67888, 67889]

See `sync_event_data() <sync_event_data_ref_>`_, `SyncEventFilter() <sync_event_filter_ref_>`_, and `SyncEventOption() <sync_event_option_ref_>`_ for
details.

Options and Usage Notes
-----------------------

This section provides detailed guidance on using option classes (`EventOption() <event_option_ref_>`_,
`SyncEventOption() <sync_event_option_ref_>`_) and filter classes (`EventFilter() <event_filter_ref_>`_,
`SyncEventFilter() <sync_event_filter_ref_>`_) to customize export operations, along with key usage notes for
date/time handling, caching, column types, interactive mode, and attachment storage.

**Option Classes**

Each export function requires a specific option class to configure its behavior. These
classes must be instantiated with parameters like `interactive_mode`, `cache`, and
others. For example, to disable column type casting in `get_event_data() <get_event_data_ref_>`_:

.. code-block:: python

   from teamworksams import get_event_data, EventOption
   df = get_event_data(
       form = "Training Log",
       start_date = "01/01/2025",
       end_date = "31/01/2025",
       url = "https://example.smartabase.com/site",
       option = EventOption(guess_col_type = False)
   )

The option classes and their associated functions are:

- `get_event_data() <get_event_data_ref_>`_: `EventOption() <event_option_ref_>`_
- `sync_event_data() <sync_event_data_ref_>`_: `SyncEventOption() <sync_event_option_ref_>`_

Available parameters for `EventOption() <event_option_ref_>`_ (and similar for `SyncEventOption() <sync_event_option_ref_>`_,
except where noted):

- **interactive_mode (bool)**: If True, displays status messages (e.g., “Retrieved 10
  event records”) and :mod:`tqdm` progress bars, ideal for interactive environments like
  Jupyter notebooks. Set to False for silent execution in automated pipelines. Defaults
  to True. Example:

  .. code-block:: python

     option = EventOption(interactive_mode = False)
     df = get_event_data(..., option = option)  # No output, suitable for scripts

- **cache (bool)**: If True, reuses an existing `AMSClient() <ams_client_ref_>`_ via
  `get_client() <get_client_ref_>`_, reducing API calls for authentication or data retrieval. Set to
  False for fresh data, increasing API overhead. Defaults to True. See “Caching” below.

- **guess_col_type (bool)**: If True, attempts to cast DataFrame columns to appropriate
  types (e.g., numeric for 'duration', datetime for 'start_date'). If False, all columns
  are returned as strings, useful for consistent string handling. Defaults to True.
  Example:

  .. code-block:: python

     option = EventOption(cast_to_type = False)
     df = get_event_data(..., option = option)  # All columns as strings

- **download_attachment (bool)**: If True, downloads event attachments (e.g., PDFs,
  images) to `attachment_directory`. Adds columns like 'attachment_path' to the
  DataFrame. Defaults to False. Example:

  .. code-block:: python

     option = EventOption(download_attachment = True, attachment_directory = "./files")
     df = get_event_data(..., option = option)

- **attachment_directory (Optional[str])**: Directory path for saving attachments
  (e.g., “./files”). Must be valid if `download_attachment=True`. Defaults to None.
  See “Attachments” below.

- **clean_names (bool)**: If True, converts column names to snake_case (e.g.,
  'Session RPE' to 'session_rpe'), improving compatibility with Python. Defaults to
  False. Example:

  .. code-block:: python

     option = EventOption(clean_names = True)
     df = get_event_data(..., option = option)  # Columns like 'session_rpe'

- **include_user_data (bool)**: Only for `SyncEventOption() <sync_event_option_ref_>`_. If True, includes
  user metadata (e.g., 'about', 'email') in the DataFrame. Defaults to False. Example:

  .. code-block:: python

     option = SyncEventOption(include_user_data = True)
     df, _ = sync_event_data(..., option = option)  # Includes 'about' column

- **include_uuid (bool)**: Only for `SyncEventOption() <sync_event_option_ref_>`_. If True, includes user
  UUIDs in the DataFrame. Defaults to False. Example:

  .. code-block:: python

     option = SyncEventOption(include_uuid = True)
     df, _ = sync_event_data(..., option = option)  # Includes 'uuid' column

**Filter Classes**

Filters narrow data retrieval for efficiency. Use `EventFilter() <event_filter_ref_>`_ for
`get_event_data() <get_event_data_ref_>`_ and `SyncEventFilter() <sync_event_filter_ref_>`_ for `sync_event_data() <sync_event_data_ref_>`_. For
example, to filter by email in `get_event_data() <get_event_data_ref_>`_:

.. code-block:: python

   from teamworksams import EventFilter
   df = get_event_data(
       form = "Training Log",
       start_date = "01/01/2025",
       end_date = "31/01/2025",
       url = "https://example.smartabase.com/site",
       filter = EventFilter(user_key = "email", user_value = "john.doe@example.com")
   )

Available parameters for `EventFilter() <event_filter_ref_>`_ (and similar for `SyncEventFilter() <sync_event_filter_ref_>`_):

- **user_key (str)**: User identification method. Must be one of 'user_id',
  'username', 'email', 'about', 'group', or 'current_group'. Specifies how to filter
  users. Example:

  .. code-block:: python

     filter = EventFilter(user_key = "group", user_value = "TeamA")
     df = get_event_data(..., filter = filter)  # Events for 'TeamA'

- **user_value (Union[str, List[str]])**: Value(s) for `user_key`. For 'group',
  specify a group name (e.g., “TeamA”). For 'current_group', `user_value` is ignored.
  Example:

  .. code-block:: python

     filter = EventFilter(user_key = "email", user_value = ["john.doe@example.com"])
     df = get_event_data(..., filter = filter)

- **data_key (Optional[str])**: Field name in the form (e.g., 'duration') to filter
  data. Only for `EventFilter() <event_filter_ref_>`_. Example:

  .. code-block:: python

     filter = EventFilter(data_key = "duration", data_value = "60")
     df = get_event_data(..., filter = filter)

- **data_value (Optional[str])**: Value for `data_key` (e.g., “60”). Only for
  `EventFilter() <event_filter_ref_>`_.

- **data_condition (str)**: Condition for `data_key`/`data_value`. Options: 'equals',
  'not_equals', 'greater_than', 'less_than', 'greater_than_or_equals',
  'less_than_or_equals', 'contains'. Numeric conditions (e.g., 'greater_than') apply
  to numeric fields only. Defaults to 'equals'. Example:

  .. code-block:: python

     filter = EventFilter(
         data_key = "duration",
         data_value = "60",
         data_condition = "greater_than"
     )
     df = get_event_data(..., filter = filter)

Valid `user_key` values and their `user_value` requirements:

- **user_id**: AMS-generated user IDs (e.g., [12345, 12346]).
- **username**: AMS usernames (e.g., ["john.doe", "jane.smith"]).
- **email**: User emails (e.g., ["john.doe@example.com"]).
- **about**: Full names (e.g., ["John Doe"]).
- **group**: Group name (e.g., “TeamA”). Use :func:`get_group` to list groups.
- **current_group**: Uses the group loaded during the last AMS login; `user_value`
  is ignored.

Multiple filters example:

.. code-block:: python

   filter = EventFilter(
       user_key = "email",
       user_value = ["john.doe@example.com", "jane.smith@example.com"],
       data_key = ["duration", "rpe"],
       data_value = ["60", "7"],
       data_condition = ["greater_than", "equals"]
   )
   df = get_event_data(..., filter = filter)  # Duration > 60 and RPE = 7

Note: All filter conditions must be met (logical AND). Ensure `data_key`,
`data_value`, and `data_condition` have equal lengths.

**Caching**

When `option.cache=True` (default), export functions reuse an existing
`AMSClient() <ams_client_ref_>`_ created by `get_client() <get_client_ref_>`_, maintaining an authenticated
session and reducing API calls for login or data retrieval. For example:

.. code-block:: python

   option = EventOption(cache = True)
   df1 = get_event_data(form = "Training Log", ..., option = option)
   df2 = get_event_data(form = "Wellness", ..., option = option)  # Reuses client

Set `cache=False` for independent sessions, ensuring fresh data but increasing API
overhead.

**Date and Time Handling**

The AMS API requires specific formats for date and time parameters:

- **start_date, end_date**: Must be `DD/MM/YYYY` (e.g., “01/01/2025”) for
  `get_event_data() <get_event_data_ref_>`_. Both are required and must be valid dates, with
  `end_date` not before `start_date`. Example:

  .. code-block:: python

     df = get_event_data(start_date = "01/01/2025", end_date = "31/01/2025", ...)

- **time_range**: Optional for `get_event_data() <get_event_data_ref_>`_, a tuple of `h:mm AM/PM`
  times (e.g., `("12:00 AM", "11:59 PM")`). Defaults to full day if unset.
  Example:

  .. code-block:: python

     df = get_event_data(
         form = "Training Log",
         start_date = "01/01/2025",
         end_date = "01/01/2025",
         time_range = ("9:00 AM", "5:00 PM"),
         url = "..."
     )

- **last_synchronisation_time**: Required for `sync_event_data() <sync_event_data_ref_>`_, a Unix
  timestamp in milliseconds (e.g., 1677654321000 for 2023-03-01 12:25:21 UTC).
  Use the returned `new_sync_time` for subsequent calls. Example:

  .. code-block:: python

     df, new_sync_time = sync_event_data(
         last_synchronisation_time = 1677654321000,
         ...
     )

**Column Types**

By default, `cast_to_type=True` converts DataFrame columns to appropriate types
(e.g., numeric for 'duration', datetime for 'start_date'). Set
`cast_to_type=False` to return all columns as strings, ensuring consistency:

.. code-block:: python

   option = EventOption(cast_to_type = False)
   df = get_event_data(..., option = option)
   print(df.dtypes)  # All columns as object (string)

Metadata columns (`user_id`, `event_id`, `entered_by_user_id`) are always numeric,
and event dates (`start_date`, `end_date`) are strings, as required for AMS imports.

**Interactive Mode**

When `interactive_mode=True` (default), export functions display progress messages
(e.g., “ℹ Requesting event data”) and :mod:`tqdm` progress bars, enhancing feedback
in interactive environments. Set `interactive_mode=False` for silent execution in
automated pipelines:

.. code-block:: python

   option = SyncEventOption(interactive_mode = False)
   df, _ = sync_event_data(..., option = option)  # No output

**Attachments**

When `download_attachment=True`, attachments are saved to `attachment_directory`
(e.g., “./files”), with paths added to the DataFrame (e.g., 'attachment_path').
Supported file types include `.pdf`, `.png`, `.jpg`, etc. Ensure the directory
exists and is writable. Example:

.. code-block:: python

   import os
   os.makedirs("./files", exist_ok = True)
   option = EventOption(download_attachment = True, attachment_directory = "./files")
   df = get_event_data(..., option = option)
   print(df['attachment_path'].head())  # Paths to saved files

Files are named with AMS-generated IDs (e.g., `12345_1747654002120.pdf`).

Error Handling
--------------

**teamworksams** functions provide descriptive :class:`AMSError` messages with interactive
feedback. For simple scripts, rely on these:

.. code-block:: python

   df = get_event_data(
       form = "Invalid Form",
       start_date = "01/01/2025",
       end_date = "31/01/2025",
       url = "https://example.smartabase.com/site",
       option = EventOption(interactive_mode = True)
   )

**Output**:

.. code-block:: text

   ✖ Failed to fetch events: No events found for form 'Invalid Form'...
   AMSError: No events found for form 'Invalid Form'...

Best Practices
--------------

- **Filtering**: Use `EventFilter() <event_filter_ref_>`_ or `SyncEventFilter() <sync_event_filter_ref_>`_ to limit data
  retrieval (e.g., `user_key="group"`) for performance.
- **Caching**: Enable ``option.cache=True`` to reuse a `AMSClient() <ams_client_ref_>`_ across
  multiple calls, reducing API overhead.
- **Attachments**: Specify a valid ``attachment_directory`` when
  ``download_attachment=True`` to avoid file write errors.
- **Synchronization**: Store the `new_sync_time` from `sync_event_data() <sync_event_data_ref_>`_ for
  subsequent calls to maintain incremental updates.
- **Data Validation**: Ensure `form` matches an existing AMS form and dates are in
  'DD/MM/YYYY' format to avoid :class:`ValueError`.

Troubleshooting
---------------

- **Invalid Form**:

  .. code-block:: text

     AMSError: No events found for form 'Invalid Form'...

  **Solution**: Verify the form name with your AMS administrator.

- **Invalid Date Format**:

  .. code-block:: text

     ValueError: start_date must be in 'DD/MM/YYYY' format...

  **Solution**: Use correct format:

    .. code-block:: python

       df = get_event_data(form = "Training Log", start_date = "01/01/2025", ...)

- **No Events Found**:

  .. code-block:: text

     AMSError: No events found for form 'Training Log'...

  **Solution**: Check date range or filter settings:

    .. code-block:: python

       df = get_event_data(form = "Training Log", start_date = "01/01/2024", ...)

Next Steps
----------

- Explore :ref:`importing_data` for additional data workflows.
- Consult :ref:`reference` for detailed function and class documentation.
- Visit `GitHub <https://github.com/brandonyach/teamworksams>`_ for support.