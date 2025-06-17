.. _insert_database_entry_ref: ../reference/insert_database_entry.html

.. _insert_database_option:

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

- `insert_database_entry() <insert_database_entry_ref_>`_: Function using `InsertDatabaseOption`.
- :ref:`database_operations`: Database insertion workflows.