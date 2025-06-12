update_event_data
=================

.. autofunction:: teamworksams.import_main.update_event_data

Additional Notes
----------------

- The ``df`` must include 'event_id' with valid integer IDs; invalid IDs raise
  :class:`AMSError`. Use :func:`get_event_data` to retrieve IDs.
- Set ``option.require_confirmation=True`` to prompt for confirmation before
  updating, preventing accidental changes in interactive mode.
- Use ``option.table_fields`` to update table fields, ensuring column names match
  the AMS form.

See Also
--------

- :class:`UpdateEventOption`: Configuration options for event updates.
- :func:`insert_event_data`: For inserting new events.
- :ref:`vignettes/importing_data`: Event update workflows.