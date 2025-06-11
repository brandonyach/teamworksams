Exporting Data
==============

This vignette provides an in-depth guide to exporting event data from Teamworks AMS using
**teamworksams**, focusing on the :func:`get_event_data` and :func:`sync_event_data`
functions. Designed for analysts, administrators, and data scientists, it covers practical
workflows for retrieving event data within a date range, synchronizing updated events, and
applying filters and options to customize outputs. With rich examples and performance tips,
this guide equips you to efficiently export AMS event data for analysis or reporting. See
:ref:`reference` for detailed function documentation and
:ref:`vignettes/importing_data` for additional data workflows.

Overview
--------

**teamworksams** simplifies exporting AMS event data, offering two key functions:

- :func:`get_event_data`: Retrieves event data from an AMS Event Form (e.g., 'Training
  Log') for a specified date range, with optional filtering by user attributes or data
  fields and support for downloading attachments.
- :func:`sync_event_data`: Fetches events inserted or updated since a synchronization
  time, ideal for incremental data updates, with options to include user metadata or UUIDs.

These functions return :class:`pandas.DataFrame` objects, enabling seamless integration
with Python data analysis tools like pandas. Filters (:class:`EventFilter`,
:class:`SyncEventFilter`) and options (:class:`EventOption`, :class:`SyncEventOption`)
provide fine-grained control over data retrieval. All examples use the placeholder URL
``https://example.smartabase.com/site``, username ``username``, and password ``password``,
managed via a ``.env`` file.

Prerequisites
-------------

Ensure **teamworksams** is installed and credentials are configured, as described in
:ref:`vignettes/getting_started`. Use a ``.env`` file for secure credential management:

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
``python-dotenv``, ``tqdm``. See :ref:`vignettes/credentials` for alternative credential
methods (``os``, direct arguments, ``keyring``).

Exporting Event Data
--------------------

Use :func:`get_event_data` to retrieve event data from an AMS Event Form within a date
range, optionally filtering by user attributes or data fields and customizing outputs
with :class:`EventOption`.

**Basic Usage**

Fetch all events from the 'Training Log' form for January 2025:

.. code-block:: python

   from teamworksams import get_event_data
   df = get_event_data(
       form="Training Log",
       start_date="01/01/2025",
       end_date="31/01/2025",
       url="https://example.smartabase.com/site",
       option=EventOption(interactive_mode=True)
   )
   print(df[['user_id', 'start_date', 'duration']].head())

**Output**:

.. code-block:: text

   ℹ Requesting event data for 'Training Log' between 01/01/2025 and 31/01/2025
   ✔ Retrieved 10 event records for form 'Training Log'.
      user_id start_date duration
   0    12345 2025-01-01       60
   1    12346 2025-01-02       45
   ...

**Filtering Events**

Use :class:`EventFilter` to narrow results, e.g., events for users in 'TeamA' with
'intensity' equal to 'High':

.. code-block:: python

   from teamworksams import EventFilter, EventOption
   df = get_event_data(
       form="Training Log",
       start_date="01/01/2025",
       end_date="31/01/2025",
       url="https://example.smartabase.com/site",
       filter=EventFilter(
           user_key="group",
           user_value="TeamA",
           data_key="intensity",
           data_value="High",
           data_condition="equals"
       ),
       option=EventOption(interactive_mode=True, clean_names=True)
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

Download event attachments to a specified directory:

.. code-block:: python

   df = get_event_data(
       form="Training Log",
       start_date="01/01/2025",
       end_date="31/01/2025",
       url="https://example.smartabase.com/site",
       option=EventOption(
           interactive_mode=True,
           download_attachment=True,
           attachment_directory="./attachments"
       )
   )
   print(df.columns)

**Output**:

.. code-block:: text

   ℹ Requesting event data for 'Training Log' between 01/01/2025 and 31/01/2025
   ✔ Retrieved 10 event records for form 'Training Log'.
   Index(['about', 'user_id', 'event_id', 'form', 'start_date', 'attachment_path'], ...)


See :func:`get_event_data`, :class:`EventFilter`, and :class:`EventOption` for details.

Synchronizing Event Data
------------------------

Use :func:`sync_event_data` to fetch events inserted or updated since a synchronization
time, ideal for incremental updates. Returns a :class:`pandas.DataFrame` and a new
synchronization time.

**Basic Usage**

Synchronize events from 'Training Log' since March 1, 2023:

.. code-block:: python

   from teamworksams import sync_event_data, SyncEventOption
   df, new_sync_time = sync_event_data(
       form="Training Log",
       last_synchronisation_time=1677654321000,  # 2023-03-01 12:25:21
       url="https://example.smartabase.com/site",
       option=SyncEventOption(interactive_mode=True)
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

**Filtering Synchronized Events**

Synchronize events for users in 'TeamA':

.. code-block:: python

   from teamworksams import SyncEventFilter
   df, new_sync_time = sync_event_data(
       form="Training Log",
       last_synchronisation_time=1677654321000,
       url="https://example.smartabase.com/site",
       filter=SyncEventFilter(user_key="group", user_value="TeamA"),
       option=SyncEventOption(interactive_mode=True, include_user_data=True)
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

See :func:`sync_event_data`, :class:`SyncEventFilter`, and :class:`SyncEventOption` for
details.

Error Handling
--------------

**teamworksams** functions provide descriptive :class:`AMSError` messages with interactive
feedback. For simple scripts, rely on these:

.. code-block:: python

   df = get_event_data(
       form="Invalid Form",
       start_date="01/01/2025",
       end_date="31/01/2025",
       url="https://example.smartabase.com/site",
       option=EventOption(interactive_mode=True)
   )

**Output**:

.. code-block:: text

   ✖ Failed to fetch events: No events found for form 'Invalid Form'...
   AMSError: No events found for form 'Invalid Form'...

For automated workflows, use try-except blocks to handle errors gracefully:

.. code-block:: python

   from teamworksams import AMSError
   try:
       df = get_event_data(
           form="Training Log",
           start_date="01/01/2025",
           end_date="31/01/2025",
           url="https://example.smartabase.com/site"
       )
   except AMSError as e:
       print(f"Error: {e}")

Best Practices
--------------

- **Filtering**: Use :class:`EventFilter` or :class:`SyncEventFilter` to limit data
  retrieval (e.g., `user_key="group"`) for performance.
- **Caching**: Enable ``option.cache=True`` to reuse a :class:`AMSClient` across
  multiple calls, reducing API overhead.
- **Attachments**: Specify a valid ``attachment_directory`` when
  ``download_attachment=True`` to avoid file write errors.
- **Synchronization**: Store the `new_sync_time` from :func:`sync_event_data` for
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

       df = get_event_data(form="Training Log", start_date="01/01/2025", ...)

- **No Events Found**:

  .. code-block:: text

     AMSError: No events found for form 'Training Log'...

  **Solution**: Check date range or filter settings:

    .. code-block:: python

       df = get_event_data(form="Training Log", start_date="01/01/2024", ...)

Next Steps
----------

- Explore :ref:`vignettes/importing_data` for additional data workflows.
- Consult :ref:`reference` for detailed function and class documentation.
- Visit `GitHub <https://github.com/yachb35/teamworksams>`_ for support.