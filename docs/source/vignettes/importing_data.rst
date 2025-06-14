Importing Data
==============

This vignette provides an in-depth guide to importing event and profile data into Teamworks
AMS using **teamworksams**, covering :func:`insert_event_data`,
:func:`update_event_data`, :func:`upsert_event_data`, and
:func:`upsert_profile_data`. It offers practical workflows for inserting new events, updating existing ones, upserting
mixed datasets, and managing profile records. With rich Python/pandas examples and
performance tips, this guide equips you to efficiently import AMS data. See
:ref:`reference` for detailed function documentation and
:ref:`vignettes/exporting_data` for data export workflows.

Overview
--------

**teamworksams** streamlines importing data into AMS Event and Profile Forms, offering
four key functions:

- :func:`insert_event_data`: Inserts new event records into an Event Form (e.g.,
  'Training Log').
- :func:`update_event_data`: Updates existing event records using 'event_id'.
- :func:`upsert_event_data`: Combines inserting new events and updating existing ones
  based on 'event_id' presence.
- :func:`upsert_profile_data`: Upserts profile records in a Profile Form (e.g.,
  'Athlete Profile'), with one record per user.

These functions process :class:`pandas.DataFrame` inputs, mapping user identifiers to
user IDs and validating data before sending to the AMS API. Options
(:class:`InsertEventOption`, :class:`UpdateEventOption`, :class:`UpsertEventOption`,
:class:`UpsertProfileOption`) customize behavior, including interactive feedback and
confirmation prompts. All examples use the placeholder URL
``https://example.smartabase.com/site``, username ``username``, and password
``password``, managed via a ``.env`` file.

Prerequisites
-------------

Ensure **teamworksams** is installed and credentials are configured, as described in
:ref:`vignettes/getting_started`. Use a ``.env`` file for secure credentials:

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
``python-dotenv``, ``tqdm``. See :ref:`vignettes/credentials` for alternative methods
(``os``, direct arguments, ``keyring``).

Inserting Event Data
--------------------

Use :func:`insert_event_data` to add new event records to an AMS Event Form, mapping
user identifiers with :class:`InsertEventOption`.

**Basic Usage**

Insert events into the 'Training Log' form:

.. code-block:: python

   import pandas as pd
   from teamworksams import insert_event_data, InsertEventOption
   df = pd.DataFrame({
       "username": ["john.doe", "jane.smith"],
       "start_date": ["01/01/2025", "01/01/2025"],
       "duration": [60, 45],
       "intensity": ["High", "Medium"]
   })

   insert_event_data(
       df = df,
       form = "Training Log",
       url = "https://example.smartabase.com/site",
       option = InsertEventOption(id_col = "username", interactive_mode = True)
   )

**Output**:

.. code-block:: text

   ℹ Inserting 2 events for 'Training Log'
   ✔ Processed 2 events for 'Training Log'
   ℹ Form: Training Log
   ℹ Result: Success
   ℹ Records inserted: 2
   ℹ Records attempted: 2

**Using Table Fields**

Insert events with table fields (e.g., 'session_details'):

.. code-block:: python

   df = pd.DataFrame({
       "username": ["john.doe"],
       "start_date": ["01/01/2025"],
       "session_details": [{"activity": "Run", "distance_km": 5}]
   })

   insert_event_data(
       df = df,
       form = "Training Log",
       url = "https://example.smartabase.com/site",
       option = InsertEventOption(
           id_col = "username",
           interactive_mode = True,
           table_fields = ["session_details"]
       )
   )

See :func:`insert_event_data` and :class:`InsertEventOption` for details.

Updating Event Data
-------------------

Use :func:`update_event_data` to modify existing events, identified by 'event_id',
with :class:`UpdateEventOption`. 

‘Updating’ data in Teamworks AMS means you are editing existing events in the 
Teamworks AMS event database. :func:`update_event_data` requires a valid event_id 
column in the supplied data frame. These are Teamworks AMS-generated unique IDs 
that ensure only the correct events are updated/overwritten.

**Updating is the same as overwriting**
Important note: Every event in the data frame supplied to :func:`update_event_data`
completely overwrites the existing event in the Teamworks AMS event database.

Practically this also means that most calls to :func:`update_event_data` should be 
preceded by a call to :func:`get_event_data` / :func:`sync_event_data`. The latter 
return a data frame that contain the entire Teamworks AMS form, including every 
column/field that contains data; as well as the necessary event_id column.

**Basic Usage**

Update events in 'Training Log' using data retreved with :func:`get_event_data`,
applying transformations, and then updating the events wth :func:`update_event_data`:

.. code-block:: python

   from teamworksams import get_event_data, update_event_data, UpdateEventOption
   event_df = get_event_data(
       form="Training Log",
       start_date="01/01/2025",
       end_date="31/01/2025",
       url="https://example.smartabase.com/site"
   )

   update_df = event_df[["event_id", "username", "duration"]].copy()
   update_df["duration"] = update_df["duration"] + 5  # Increase duration

   update_event_data(
       df = update_df,
       form = "Training Log",
       url = "https://example.smartabase.com/site",
       option=UpdateEventOption(id_col = "username", interactive_mode=True)
   )

**Output**:

.. code-block:: text

   ℹ Updating 10 events for 'Training Log'
   Are you sure you want to update 10 existing events in 'Training Log'? (y/n): y
   ✔ Processed 10 events for 'Training Log'
   ℹ Form: Training Log
   ℹ Result: Success
   ℹ Records updated: 10
   ℹ Records attempted: 10

See :func:`update_event_data` and :class:`UpdateEventOption` for details.

Upserting Event Data
--------------------

Use :func:`upsert_event_data` to insert new events and update existing ones based on
'event_id' presence, with :class:`UpsertEventOption`. Rows with valid event IDs will 
update the matching rows in the Teamworks AMS event database, whereas rows with no 
'event_id' will be inserted as new rows in the Teamworks AMS event database.

**Basic Usage**

Upsert a mixed dataset - note that the second observation in this dataframe does not 
contain an 'event_id' - this might be commmon in situaitons where existing data was 
retrieved from Teamworks AMS using :func:`get_event_data`, then merged with new data 
created based on transformations or new records obtained. Upserting the dataframe 
below will invoke two API calls: one to insert the rows where event_id = None and 
another to update the existing events:

.. code-block:: python

   df = pd.DataFrame({
       "event_id": [67890, None],
       "username": ["john.doe", "jane.smith"],
       "start_date": ["01/01/2025", "02/01/2025"],
       "duration": [65, 45],
       "intensity": ["High Updated", "Medium"]
   })

   upsert_event_data(
       df = df,
       form = "Training Log",
       url = "https://example.smartabase.com/site",
       option=UpsertEventOption(id_col = "username", interactive_mode = True)
   )

**Output**:

.. code-block:: text

   ℹ Updating 1 existing events for 'Training Log'
   ℹ Inserting 1 new events for 'Training Log'
   ✔ Processed 2 events for 'Training Log'
   ℹ Form: Training Log
   ℹ Result: Success
   ℹ Records upserted: 2
   ℹ Records attempted: 2

See :func:`upsert_event_data` and :class:`UpsertEventOption` for details.

Upserting Profile Data
----------------------

Use :func:`upsert_profile_data` to update or insert profile records, with one record
per user, using :class:`UpsertProfileOption`.

**Basic Usage**

Upsert profile data in 'Athlete Profile':

.. code-block:: python

   df = pd.DataFrame({
       "username": ["john.doe", "jane.smith"],
       "height_cm": [180, 165],
       "weight_kg": [75, 60]
   })

   upsert_profile_data(
       df = df,
       form = "Athlete Profile",
       url = "https://example.smartabase.com/site",
       option = UpsertProfileOption(id_col = "username", interactive_mode = True)
   )

**Output**:

.. code-block:: text

   ℹ Upserting 2 profile records for 'Athlete Profile'
   ✔ Processed 2 profile records for 'Athlete Profile'
   ℹ Form: Athlete Profile
   ℹ Result: Success
   ℹ Records upserted: 2
   ℹ Records attempted: 2

**Combining with User Data**

Ensure valid user identifiers by merging with :func:`get_user`:

.. code-block:: python

   from teamworksams import get_user, upsert_profile_data, UpsertProfileOption
   from teamworksams.user_option import UserOption

   user_df = get_user(
       url="https://example.smartabase.com/site",
       option=UserOption(columns=["username"])
   )

   profile_df = pd.DataFrame({
       "username": ["john.doe", "invalid.user"],
       "height_cm": [180, 170]
   })

   valid_df = profile_df.merge(user_df, on="username", how="inner")

   upsert_profile_data(
       df = valid_df,
       form = "Athlete Profile",
       url = "https://example.smartabase.com/site",
       option = UpsertProfileOption(id_col = "username", interactive_mode = True)
   )

See :func:`upsert_profile_data` and :class:`UpsertProfileOption` for details.

Options 
-----------------------

This section provides detailed guidance on using option classes
(:class:`InsertEventOption`, :class:`UpdateEventOption`, :class:`UpsertEventOption`,
:class:`UpsertProfileOption`) to customize import operations, along with key usage
notes for caching, table fields, date/time columns, and interactive mode.

**Option Classes**

Each import function requires a specific option class to configure its behavior. These
classes must be instantiated with parameters like `interactive_mode`, `cache`,
`id_col`, `table_fields`, and (for :class:`UpdateEventOption`)
`require_confirmation`. For example, to set `id_col="email"` for
:func:`insert_event_data`, use:

.. code-block:: python

   from teamworksams import insert_event_data, InsertEventOption
   import pandas as pd
   df = pd.DataFrame({
       "email": ["john.doe@example.com"],
       "start_date": ["01/01/2025"],
       "duration": [60]
   })

   insert_event_data(
       df = df,
       form = "Training Log",
       url = "https://example.smartabase.com/site",
       option = InsertEventOption(id_col = "email")
   )

The option classes and their associated functions are:

- :func:`insert_event_data`: :class:`InsertEventOption`
- :func:`update_event_data`: :class:`UpdateEventOption`
- :func:`upsert_event_data`: :class:`UpsertEventOption`
- :func:`upsert_profile_data`: :class:`UpsertProfileOption`

Below are the available parameters for each option class:

- **interactive_mode (bool)**: If True, displays status messages (e.g., “Processed 2
  events”) and :mod:`tqdm` progress bars, ideal for interactive environments like
  Jupyter notebooks. For :class:`UpdateEventOption`, also prompts for confirmation
  if `require_confirmation=True`. Set to False for silent execution in automated
  scripts. Defaults to True. Example:

  .. code-block:: python

     option = UpdateEventOption(interactive_mode = False)
     update_event_data(..., option = option)  # No output, suitable for pipelines

- **cache (bool)**: If True, reuses an existing :class:`AMSClient` via
  :func:`get_client`, reducing API calls for authentication or user mapping. Set to
  False to create a new client for each call, ensuring fresh data. Defaults to True.
  See “Caching” below for details.

- **id_col (str)**: Specifies the DataFrame column for user identifiers. Must be one
  of 'user_id', 'username', 'email', or 'about'. Defaults to 'user_id'. See “id_col”
  below for usage. Example:

  .. code-block:: python

     df = pd.DataFrame({"email": ["john.doe@example.com"], "duration": [60]})
     option = InsertEventOption(id_col = "email")
     insert_event_data(..., df = df, option = option)

- **table_fields (Optional[List[str]])**: List of AMS form table field names (e.g.,
  ['session_details']). Must match DataFrame columns if specified. If None, assumes
  no table fields. Not available for :class:`UpsertProfileOption`. Defaults to None.
  See “Table Fields” below for details.

- **require_confirmation (bool)**: Only for :class:`UpdateEventOption`. If True and
  `interactive_mode=True`, prompts for confirmation before updating events,
  preventing accidental overwrites. Defaults to True. Example:

  .. code-block:: python

     option = UpdateEventOption(require_confirmation = False)
     update_event_data(..., option = option)  # Skips prompt, use cautiously

**Caching**

When `option.cache=True` (default), the import functions reuse an existing
:class:`AMSClient` created by :func:`get_client`. This client maintains an
authenticated session, reducing API calls for login or user data retrieval (e.g.,
mapping `id_col` to `user_id`). For example, in a workflow with multiple imports:

.. code-block:: python

   option = InsertEventOption(cache=True)
   insert_event_data(df1, form = "Training Log", url = "...", option = option)
   insert_event_data(df2, form = "Training Log", url = "...", option = option)  # Reuses client

This improves performance, especially for large datasets or repeated calls. Set
`cache=False` for independent sessions, ensuring fresh authentication but increasing
API overhead.

**id_col**

The AMS API requires a `user_id` column in the input DataFrame, representing
AMS-generated user IDs. By default, `id_col = "user_id"`. If your DataFrame lacks
`user_id` but includes an alternative identifier ('username', 'email', or 'about'),
set `id_col` to that column. The function maps these identifiers to `user_id` using
:func:`get_user` internally. Example:

.. code-block:: python

   df = pd.DataFrame({
       "about": ["John Doe"],
       "start_date": ["01/01/2025"],
       "duration": [60]
   })

   option = InsertEventOption(id_col="about")
   insert_event_data(df = df, form = "Training Log", url = "...", option = option)

Valid `id_col` values: 'user_id', 'username', 'email', 'about'.

**Table Fields**

Table fields in AMS forms store multiple rows of data within a single event, such as
exercise details in a strength training session. Specify `table_fields` as a list of
column names matching the AMS form’s table fields. For example:

.. code-block:: python

   df = pd.DataFrame({
       "user_id": [12345, 12345],
       "start_date": ["01/01/2025", "01/01/2025"],
       "session_rpe": [7, None],
       "exercise": ["Bench Press", "Squat"],
       "load": [120, 150],
       "reps": [3, 3]
   })

   option = InsertEventOption(table_fields = ["exercise", "load", "reps"])
   insert_event_data(df = df, form = "Strength Testing", url = "...", option = option)

In this example, `exercise`, `load`, and `reps` are table fields, while `session_rpe`
is a non-table field recorded once per event. The DataFrame must include `user_id`
and `start_date` for each row, with non-table fields populating only the first row
for each `user_id`/`start_date` pair.

If `table_fields=None` (default) and duplicate `user_id`/`start_date` pairs are
detected, the function splits the DataFrame into multiple API calls, each containing
unique `user_id`/`start_date` pairs. For example:

.. code-block:: python

   df = pd.DataFrame({
       "user_id": [12345, 12345],
       "start_date": ["01/01/2025", "01/01/2025"],
       "duration": [60, 45]
   })
   insert_event_data(df = df, form = "Training Log", url = "...", option = InsertEventOption())

This splits into two API calls, each with one row, to avoid conflicts.

**Date/Time Columns**

The AMS API requires metadata for event timing. The import functions search for
columns named `start_date`, `end_date`, `start_time`, and `end_time` in the
DataFrame:

- `start_date`, `end_date`: Must be formatted as `dd/mm/YYYY` (e.g., “01/01/2025”).
  If missing, both default to the current date. If `start_time` and `end_time` span
  midnight, `end_date` is set to the next day.
- `start_time`, `end_time`: Must be formatted as `h:mm AM` or `h:mm PM` (e.g.,
  “9:00 AM”). If missing, `start_time` defaults to the current time, and `end_time`
  to one hour later.

Example:

.. code-block:: python

   df = pd.DataFrame({
       "user_id": [12345],
       "start_date": ["01/01/2025"],
       "start_time": ["9:00 AM"],
       "duration": [60]
   })
   insert_event_data(df=df, form="Training Log", url="...")

If `start_date` is missing, add it explicitly:

.. code-block:: python

   df["start_date"] = "01/01/2025"

**Interactive Mode**

When `interactive_mode=True` (default), import functions display progress messages
(e.g., “ℹ Inserting 2 events”) and :mod:`tqdm` progress bars, enhancing user feedback
in interactive environments. For :func:`update_event_data`, it also prompts for
confirmation if `require_confirmation=True`. Set `interactive_mode=False` for
silent execution in automated pipelines:

.. code-block:: python

   option = UpsertEventOption(interactive_mode=False)
   upsert_event_data(..., option=option)  # No output, ideal for scripts

Error Handling
--------------

**teamworksams** functions provide descriptive :class:`AMSError` messages with
interactive feedback. For simple scripts, rely on these:

.. code-block:: python

   insert_event_data(
       df=pd.DataFrame({"username": ["john.doe"]}),  # Missing start_date
       form="Training Log",
       url="https://example.smartabase.com/site",
       option=InsertEventOption(interactive_mode=True)
   )

**Output**:

.. code-block:: text

   ✖ Failed to insert events: DataFrame is invalid: missing 'start_date'...
   AMSError: DataFrame is invalid...


Best Practices
--------------

- **Data Validation**: Ensure `df` includes required columns (e.g., 'start_date' for
  inserts, 'event_id' for updates) and valid user identifiers to avoid
  :class:`AMSError`.
- **Caching**: Enable ``option.cache=True`` to reuse a :class:`AMSClient` across
  multiple imports, improving performance.
- **Confirmation**: Use ``require_confirmation=True`` in :class:`UpdateEventOption`
  for safe updates in interactive mode.
- **Table Fields**: Specify ``table_fields`` accurately for event forms with table
  data, matching DataFrame columns to AMS field names.
- **User Mapping**: Merge with :func:`get_user` data to validate user identifiers
  before importing profiles or events.

Troubleshooting
---------------

- **Invalid Form**:

  .. code-block:: text

     AMSError: Form 'Invalid Form' is not an event form...

  **Solution**: Verify the form name with your AMS administrator.

- **Missing Required Columns**:

  .. code-block:: text

     AMSError: DataFrame is invalid: missing 'start_date'...

  **Solution**: Include required columns:

    .. code-block:: python

       df["start_date"] = "01/01/2025"

- **Invalid Event IDs**:

  .. code-block:: text

     AMSError: Invalid event_id values provided...

  **Solution**: Use :func:`get_event_data` to retrieve valid IDs:

    .. code-block:: python

       event_df = get_event_data(form="Training Log", ...)

Next Steps
----------

- Explore :ref:`vignettes/exporting_data` for data export workflows.
- Consult :ref:`reference` for detailed function and class documentation.
- Visit `GitHub <https://github.com/brandonyach/teamworksams>`_ for support.