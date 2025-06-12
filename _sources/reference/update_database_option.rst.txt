UpdateDatabaseOption
====================

.. autoclass:: teamworksams.database_option.UpdateDatabaseOption
   :members:
   :undoc-members:
   :show-inheritance:

Additional Notes
----------------

- When ``interactive_mode=True``, users are prompted to confirm updates,
  preventing accidental changes to existing entries.
- Specify ``table_fields`` for table fields in the AMS form, ensuring
  :class:`pandas.DataFrame` columns align to avoid errors.
- Set ``cache=True`` for efficient updates in one-off operations, reusing the
  :class:`AMSClient`.

See Also
--------

- :func:`teamworksams.database_main.update_database_entry`: Function using `UpdateDatabaseOption`.
- :ref:`vignettes/database_operations`: Database update workflows.