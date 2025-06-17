.. _delete_event_option_ref: ../reference/delete_event_option.html
.. _delete_multiple_events_ref: ../reference/delete_multiple_events.html
.. _get_event_data_ref: ../reference/get_event_data.html
.. _ams_error_ref: ../reference/ams_error.html

.. _delete_event_data:

delete_event_data
=================

.. autofunction:: teamworksams.delete_main.delete_event_data

Additional Notes
----------------

- Obtain valid `event_id` values using `get_event_data() <get_event_data_ref_>`_ to avoid
  `AMSError() <ams_error_ref_>`_ for non-existent events.
- The confirmation prompt in ``option.interactive_mode=True`` ensures safe
  deletion, critical for administrative tasks.
- The returned string (e.g., "SUCCESS: Deleted 134273") can be parsed for
  automation or logged for auditing.

See Also
--------

- `delete_event_option() <delete_event_option_ref_>`_: Configuration options for deletion.
- `delete_multiple_events() <delete_multiple_events_ref_>`_: For deleting multiple events.
- :ref:`deleting_data`: Single event deletion workflows.