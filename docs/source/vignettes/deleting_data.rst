Deleting Data
=============

This vignette provides a guide to deleting event data in Teamworks AMS using
**teamworksams**, covering :func:`delete_event_data` and
:func:`delete_multiple_events`. Designed for administrators and analysts, it outlines
safe workflows for removing single or multiple events from AMS Event Forms, with
Python/pandas examples. Inspired by the SmartabaseR equivalent
(`<https://teamworksapp.github.io/smartabaseR/articles/deleting-data.html>`_), it
emphasizes safety features like confirmation prompts and integration with
:func:`get_event_data` for event ID retrieval. See :ref:`reference` for detailed
documentation and :ref:`vignettes/exporting_data` for related tasks.

Overview
--------

**teamworksams** supports event deletion with two key functions:

- :func:`delete_event_data`: Deletes a single event by ID.
- :func:`delete_multiple_events`: Deletes multiple events by a list of IDs.

These functions are used for data cleanup, removing outdated or erroneous events.
Deletion is permanent, so the :class:`DeleteEventOption` provides interactive
confirmation prompts for safety. Examples use the placeholder URL
``https://example.smartabase.com/site`` and credentials in a ``.env`` file.

Prerequisites
-------------

Ensure **teamworksams** is installed and credentials are configured, as in
:ref:`vignettes/getting_started`. Use a ``.env`` file:

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
``python-dotenv``, ``tqdm``. Use :func:`get_event_data` to retrieve valid event IDs.

Deleting a Single Event
-----------------------

Use :func:`delete_event_data` to remove a single event by its ID:

**Retrieving Event ID**

Fetch event IDs from an Event Form:

.. code-block:: python

   import pandas as pd
   from teamworksams import get_event_data, EventOption
   event_df = get_event_data(
       form="Training Log",
       start_date="01/01/2025",
       end_date="31/01/2025",
       url="https://example.smartabase.com/site",
       option=EventOption(interactive_mode=True)
   )
   event_id = event_df["event_id"].iloc[0]

**Deleting the Event**

Delete the event with confirmation:

.. code-block:: python

   from teamworksams import delete_event_data, DeleteEventOption
   result = delete_event_data(
       event_id=event_id,
       url="https://example.smartabase.com/site",
       option=DeleteEventOption(interactive_mode=True)
   )
   print(result)

**Output**:

.. code-block:: text

   Are you sure you want to delete event '134273'? (y/n): y
   ℹ Deleting event with ID 134273...
   ✔ SUCCESS: Deleted 134273
   SUCCESS: Deleted 134273

See :func:`delete_event_data` and :class:`DeleteEventOption` for details.

Deleting Multiple Events
------------------------

Use :func:`delete_multiple_events` to remove multiple events by their IDs:

**Retrieving Event IDs**

Filter events to delete (e.g., specific user or date):

.. code-block:: python

   event_df = get_event_data(
       form="Training Log",
       start_date="01/01/2025",
       end_date="01/01/2025",
       url="https://example.smartabase.com/site",
       option=EventOption(interactive_mode=True)
   )
   event_ids = event_df["event_id"].head(3).tolist()

**Deleting the Events**

Delete multiple events with confirmation:

.. code-block:: python

   from teamworksams import delete_multiple_events, DeleteEventOption
   result = delete_multiple_events(
       event_ids=event_ids,
       url="https://example.smartabase.com/site",
       option=DeleteEventOption(interactive_mode=True)
   )
   print(result)

**Output**:

.. code-block:: text

   Are you sure you want to delete 3 events with IDs [134273, 134274, 134275]? (y/n): y
   ℹ Deleting 3 events with IDs [134273, 134274, 134275]...
   ✔ SUCCESS: Deleted 3 events
   SUCCESS: Deleted 3 events

See :func:`delete_multiple_events` and :class:`DeleteEventOption` for details.

Error Handling
--------------

Deletion functions raise :class:`AMSError` with descriptive messages:

.. code-block:: python

   delete_event_data(event_id=999999, url="https://example.smartabase.com/site")

**Output**:

.. code-block:: text

   Are you sure you want to delete event '999999'? (y/n): y
   ✖ Failed to delete event with ID 999999: Invalid event ID
   AMSError: Invalid event ID...

For automated scripts, use try-except:

.. code-block:: python

   from teamworksams import AMSError, DeleteEventOption
   try:
       result = delete_multiple_events(
           event_ids=[134273],
           url="https://example.smartabase.com/site",
           option=DeleteEventOption(interactive_mode=False)
       )
   except AMSError as e:
       print(f"Error: {e}")

Common errors include:
- Invalid or non-existent `event_id`.
- User cancellation in interactive mode.
- Authentication or API failures.

Best Practices
--------------

- **Validate Event IDs**: Use :func:`get_event_data` to ensure `event_id` values
  are valid before deletion.
- **Use Confirmation**: Enable ``option.interactive_mode=True`` to prompt for
  confirmation, preventing accidental deletions.
- **Batch Deletion**: Prefer :func:`delete_multiple_events` for efficiency when
  removing multiple events.
- **Log Results**: Capture returned messages for auditing deletion outcomes.
- **Test First**: Filter events with :func:`get_event_data` to review before
  deleting.

Next Steps
----------

- Explore :ref:`vignettes/exporting_data` for retrieving event data and IDs.
- Consult :ref:`reference` for detailed function and class documentation.
- Visit `GitHub <https://github.com/yachb35/teamworksams>`_ for support.