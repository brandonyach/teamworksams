update_database_entry
=====================

.. autofunction:: teamworksams.database_main.update_database_entry

Additional Notes
----------------

- The ``df`` must include 'entry_id' with valid integer IDs; invalid IDs raise
  :class:`AMSError`. Use :func:`get_database` to retrieve IDs.
- Set ``option.interactive_mode=True`` to prompt for confirmation before
  updating, preventing accidental changes.
- Use ``option.table_fields`` to update table fields, ensuring column names
  match the AMS form.

See Also
--------

- :class:`UpdateDatabaseOption`: Configuration options for updates.
- :func:`insert_database_entry`: For inserting new entries.
- :ref:`vignettes/database_operations`: Database workflows.