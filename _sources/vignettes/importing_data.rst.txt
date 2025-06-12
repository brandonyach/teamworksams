Importing Data
==============

This vignette provides an in-depth guide to importing event and profile data into Teamworks
AMS using **teamworksams**, covering :func:`insert_event_data`,
:func:`update_event_data`, :func:`upsert_event_data`, and
:func:`upsert_profile_data`. Designed for analysts, administrators, and data scientists,
it offers practical workflows for inserting new events, updating existing ones, upserting
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
       df=df,
       form="Training Log",
       url="https://example.smartabase.com/site",
       option=InsertEventOption(id_col="username", interactive_mode=True)
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
       df=df,
       form="Training Log",
       url="https://example.smartabase.com/site",
       option=InsertEventOption(
           id_col="username",
           interactive_mode=True,
           table_fields=["session_details"]
       )
   )

See :func:`insert_event_data` and :class:`InsertEventOption` for details.

Updating Event Data
-------------------

Use :func:`update_event_data` to modify existing events, identified by 'event_id',
with :class:`UpdateEventOption`.

**Basic Usage**

Update events in 'Training Log' using event IDs from :func:`get_event_data`:

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
       df=update_df,
       form="Training Log",
       url="https://example.smartabase.com/site",
       option=UpdateEventOption(id_col="username", interactive_mode=True)
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
'event_id' presence, with :class:`UpsertEventOption`.

**Basic Usage**

Upsert a mixed dataset:

.. code-block:: python

   df = pd.DataFrame({
       "event_id": [67890, None],
       "username": ["john.doe", "jane.smith"],
       "start_date": ["01/01/2025", "02/01/2025"],
       "duration": [65, 45],
       "intensity": ["High Updated", "Medium"]
   })
   upsert_event_data(
       df=df,
       form="Training Log",
       url="https://example.smartabase.com/site",
       option=UpsertEventOption(id_col="username", interactive_mode=True)
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
       df=df,
       form="Athlete Profile",
       url="https://example.smartabase.com/site",
       option=UpsertProfileOption(id_col="username", interactive_mode=True)
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
       df=valid_df,
       form="Athlete Profile",
       url="https://example.smartabase.com/site",
       option=UpsertProfileOption(id_col="username", interactive_mode=True)
   )

See :func:`upsert_profile_data` and :class:`UpsertProfileOption` for details.

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

For automated workflows, use try-except:

.. code-block:: python

   from teamworksams import AMSError
   try:
       upsert_event_data(
           df=df,
           form="Training Log",
           url="https://example.smartabase.com/site"
       )
   except AMSError as e:
       print(f"Error: {e}")

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
- Visit `GitHub <https://github.com/yachb35/teamworksams>`_ for support.