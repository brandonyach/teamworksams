GetDatabaseOption
=================

.. autoclass:: teamworksams.database_option.GetDatabaseOption
   :members:
   :undoc-members:
   :show-inheritance:

Additional Notes
----------------

- Enable ``interactive_mode=True`` for status messages like "Retrieved 100
  entries," useful for one-off queries in interactive environments.
- Set ``cache=False`` to ensure fresh data when retrieving entries, especially
  if the AMS database form has been recently updated.
- Use with :func:`teamworksams.database_main.get_database` for occasional data
  retrieval tasks, such as auditing or reporting.

See Also
--------

- :func:`teamworksams.database_main.get_database`: Function using `GetDatabaseOption`.
- :ref:`vignettes/database_operations`: Database retrieval workflows.