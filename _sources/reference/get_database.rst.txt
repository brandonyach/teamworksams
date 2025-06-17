.. _get_database_ref: ../reference/get_database.html
.. _insert_database_entry_ref: ../reference/insert_database_entry.html
.. _get_database_option_ref: ../reference/get_database_option.html

.. _get_database:

get_database
============

.. autofunction:: teamworksams.database_main.get_database

Additional Notes
----------------

- The ``form_name`` must match an existing AMS database form exactly
  (case-sensitive); invalid forms raise :class:`AMSError`.
- Use ``limit`` and ``offset`` for pagination, e.g., set ``limit=1000`` and
  increment ``offset`` by 1000 to fetch large datasets in batches.
- Enable ``option.interactive_mode=True`` for feedback like "Retrieved 100
  entries," useful in interactive environments.

See Also
--------

- `GetDatabaseOption() <get_database_option_ref_>`_: Configuration options for database retrieval.
- `insert_database_entry() <insert_database_entry_ref_>`_: For inserting new entries.
- :ref:`database_operations`: Database workflows.