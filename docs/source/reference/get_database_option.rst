.. _get_database_ref: ../reference/get_database.html

.. _get_database_option:

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
- Use with `get_database() <get_database_ref_>`_ for occasional data
  retrieval tasks, such as auditing or reporting.

See Also
--------

- `get_database() <get_database_ref_>`_: Function using `GetDatabaseOption`.
- :ref:`database_operations`: Database retrieval workflows.