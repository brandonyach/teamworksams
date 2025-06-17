.. _delete_event_data_ref: ../reference/delete_event_data.html
.. _delete_event_option_ref: ../reference/delete_event_option.html
.. _get_event_data_ref: ../reference/get_event_data.html
.. _ams_error_ref: ../reference/ams_error.html
.. _get_client_ref: ../reference/get_client.html

.. _delete_multiple_events:

delete_multiple_events
======================

.. autofunction:: teamworksams.delete_main.delete_multiple_events

Additional Notes
----------------

- Use `get_event_data() <get_event_data_ref_>`_ to collect `event_ids` for batch deletion,
  ensuring all IDs are valid to avoid `AMSError() <ams_error_ref_>`_.
- Batch deletion is more efficient than multiple calls to
  `delete_event_data() <delete_event_data_ref_>`_, but confirmation prompts remain critical for
  safety.
- The returned string (e.g., "SUCCESS: Deleted 3 events") indicates the
  overall result; individual failures may require API-level debugging.

See Also
--------

- `delete_event_option() <delete_event_option_ref_>`_: Configuration options for deletion.
- `delete_event_data() <delete_event_data_ref_>`_: For single event deletion.
- `get_event_data() <get_event_data_ref_>`_: For retrieving event IDs.
- :ref:`deleting_data`: Batch event deletion workflows.