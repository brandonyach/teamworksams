delete_database_entry
=====================

.. autofunction:: teamworksams.database_main.delete_database_entry

Additional Notes
----------------

- The ``database_entry_id`` must be a valid ID from the AMS database form,
  obtainable via :func:`get_database`; invalid IDs raise :class:`AMSError`.
- Use a pre-authenticated :class:`AMSClient` with ``client`` to reduce
  authentication overhead in batch deletions.
- Deletion is permanent; ensure correct ID before executing.

See Also
--------

- :func:`get_database`: For retrieving entry IDs.
- :ref:`vignettes/database_operations`: Database workflows.