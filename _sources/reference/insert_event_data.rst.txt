insert_event_data
=================

.. autofunction:: teamworksams.import_main.insert_event_data

Additional Notes
----------------

- The ``df`` must include 'start_date' in 'DD/MM/YYYY' format and a user identifier
  column (specified by ``option.id_col``, e.g., 'username'). Missing or invalid data
  raises :class:`AMSError`.
- Use ``option.table_fields`` to specify table fields in the AMS form, ensuring
  column names match exactly.
- Enable ``option.interactive_mode=True`` for status messages like "Inserted 2
  events," useful in interactive environments.

See Also
--------

- :class:`InsertEventOption`: Configuration options for event insertion.
- :func:`update_event_data`: For updating existing events.
- :ref:`vignettes/importing_data`: Event import workflows.