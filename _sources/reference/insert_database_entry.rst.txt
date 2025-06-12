insert_database_entry
=====================

.. autofunction:: teamworksams.database_main.insert_database_entry

Additional Notes
----------------

- The ``df`` must contain columns matching the AMS form’s fields (e.g.,
  'Allergy'); missing or invalid data raises :class:`AMSError`.
- Use ``option.table_fields`` to specify table fields, ensuring column names
  match exactly to avoid errors.
- Enable ``option.interactive_mode=True`` for status messages like "Inserted 3
  entries," ideal for interactive scripts.

See Also
--------

- :class:`InsertDatabaseOption`: Configuration options for insertion.
- :func:`update_database_entry`: For updating existing entries.
- :ref:`vignettes/database_operations`: Database workflows.