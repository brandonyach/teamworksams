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

- :class:`GetDatabaseOption`: Configuration options for database retrieval.
- :func:`insert_database_entry`: For inserting new entries.
- :ref:`vignettes/database_operations`: Database workflows.