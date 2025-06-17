.. _ams_client_ref: ../reference/ams_client.html
.. _get_database_ref: ../reference/get_database.html

.. _delete_database_entry:

delete_database_entry
=====================

.. autofunction:: teamworksams.database_main.delete_database_entry

Additional Notes
----------------

- The ``database_entry_id`` must be a valid ID from the AMS database form,
  obtainable via `get_database() <get_database_ref_>`_; invalid IDs raise :class:`AMSError`.
- Use a pre-authenticated `AMSClient() <ams_client_ref_>`_ with ``client`` to reduce
  authentication overhead in batch deletions.
- Deletion is permanent; ensure correct ID before executing.

See Also
--------

- `get_database() <get_database_ref_>`_: For retrieving entry IDs.
- :ref:`database_operations`: Database workflows.