.. _update_event_data_ref: ../reference/update_event_data.html

.. _update_event_option:

UpdateEventOption
=================

.. autoclass:: teamworksams.import_option.UpdateEventOption
   :members:
   :undoc-members:
   :show-inheritance:

Additional Notes
----------------

- Set ``require_confirmation=True`` to prompt for confirmation before updating
  events when ``interactive_mode=True``, preventing accidental changes.
- The ``id_col`` must be one of 'user_id', 'about', 'username', or 'email' and
  present in the input :class:`pandas.DataFrame` to map user identifiers.
- Use ``table_fields`` to update table fields, ensuring DataFrame columns align
  with the AMS form to avoid errors.

See Also
--------

- `update_event_data() <update_event_data_ref_>`_: Function using `UpdateEventOption`.
- :ref:`importing_data`: Event update workflows.