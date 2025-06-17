.. _delete_event_data_ref: ../reference/delete_event_data.html
.. _delete_event_option_ref: ../reference/delete_event_option.html
.. _delete_multiple_events_ref: ../reference/delete_multiple_events.html
.. _get_event_data_ref: ../reference/get_event_data.html

.. _deleting_data:

Deleting Data
=============

This vignette provides a guide to deleting event data in Teamworks AMS using
**teamworksams**, covering `delete_event_data() <delete_event_data_ref_>`_ and
`delete_multiple_events() <delete_multiple_events_ref_>`_. It outlines
safe workflows for removing single or multiple events from AMS Event Forms, with
Python/pandas examples. emphasizing safety features like confirmation prompts and integration with
`get_event_data() <get_event_data_ref_>`_ for event ID retrieval. See :ref:`reference` for detailed
documentation and :ref:`getting_started` if you haven't already.

Overview
--------

**teamworksams** supports event deletion with two key functions:

- `delete_event_data() <delete_event_data_ref_>`_: Deletes a single event by ID.
- `delete_multiple_events() <delete_multiple_events_ref_>`_: Deletes multiple events by a list of IDs.

These functions are used for data cleanup, removing outdated or erroneous events.
Deletion is permanent, so the `delete_event_option() <delete_event_option_ref_>`_ provides interactive
confirmation prompts for safety. Examples use the placeholder URL
``https://example.smartabase.com/site`` and credentials in a ``.env`` file.

Prerequisites
-------------

Ensure **teamworksams** is installed and credentials are configured, as in
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
``python-dotenv``, ``tqdm``. Use `get_event_data() <get_event_data_ref_>`_ to retrieve valid event IDs.

Deleting a Single Event
-----------------------

Use `delete_event_data() <delete_event_data_ref_>`_ to remove a single event by its ID:

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

See `delete_event_data() <delete_event_data_ref_>`_ and `delete_event_option() <delete_event_option_ref_>`_ for details.

Deleting Multiple Events
------------------------

Use `delete_multiple_events() <delete_multiple_events_ref_>`_ to remove multiple events by their IDs:

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

See `delete_multiple_events() <delete_multiple_events_ref_>`_ and `delete_event_option() <delete_event_option_ref_>`_ for details.

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


Common errors include:
- Invalid or non-existent `event_id`.
- User cancellation in interactive mode.
- Authentication or API failures.

Best Practices
--------------

- **Validate Event IDs**: Use `get_event_data() <get_event_data_ref_>`_ to ensure `event_id` values
  are valid before deletion.
- **Use Confirmation**: Enable ``option.interactive_mode=True`` to prompt for
  confirmation, preventing accidental deletions.
- **Batch Deletion**: Prefer `delete_multiple_events() <delete_multiple_events_ref_>`_ for efficiency when
  removing multiple events.
- **Log Results**: Capture returned messages for auditing deletion outcomes.
- **Test First**: Filter events with `get_event_data() <get_event_data_ref_>`_ to review before
  deleting.

Next Steps
----------

- Explore :ref:`exporting_data` for retrieving event data and IDs.
- Consult :ref:`reference` for detailed function and class documentation.
- Visit `GitHub <https://github.com/brandonyach/teamworksams>`_ for support.