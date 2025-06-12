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

- :func:`teamworksams.import_main.update_event_data`: Function using `UpdateEventOption`.
- :ref:`vignettes/importing_data`: Event update workflows.