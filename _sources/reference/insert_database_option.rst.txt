InsertDatabaseOption
====================

.. autoclass:: teamworksams.database_option.InsertDatabaseOption
   :members:
   :undoc-members:
   :show-inheritance:

Additional Notes
----------------

- Specify ``table_fields`` for AMS forms with table data (e.g., ['Table']),
  ensuring column names in the :class:`pandas.DataFrame` match exactly to avoid
  :class:`AMSError`.
- Enable ``interactive_mode=True`` for feedback like "Inserted 3 entries,"
  ideal for one-off insertions in interactive scripts.
- Use ``cache=True`` to optimize performance when inserting multiple entries
  in a single session.

See Also
--------

- :func:`teamworksams.database_main.insert_database_entry`: Function using `InsertDatabaseOption`.
- :ref:`vignettes/database_operations`: Database insertion workflows.