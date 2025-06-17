.. _delete_event_data_ref: ../reference/delete_event_data.html
.. _delete_multiple_events_ref: ../reference/delete_multiple_events.html
.. _get_event_data_ref: ../reference/get_event_data.html
.. _ams_error_ref: ../reference/ams_error.html

.. _delete_event_option:

DeleteEventOption
=================

.. autoclass:: teamworksams.delete_option.DeleteEventOption
   :members:
   :undoc-members:
   :show-inheritance:

Additional Notes
----------------

- Enable ``interactive_mode=True`` to prompt for confirmation before deletion,
  preventing accidental data loss, and to display status messages like
  "SUCCESS: Deleted 134273".
- Set ``interactive_mode=False`` for automated scripts where silent execution
  is preferred, but ensure robust error handling with `AMSError() <ams_error_ref_>`_.
- Use with `delete_event_data() <delete_event_data_ref_>`_ or `delete_multiple_events() <delete_multiple_events_ref_>`_ for
  safe event deletion.

See Also
--------

- `delete_event_data() <delete_event_data_ref_>`_: Function for single event deletion.
- `delete_multiple_events() <delete_multiple_events_ref_>`_: Function for batch event deletion.
- :ref:`deleting_data`: Event deletion workflows.