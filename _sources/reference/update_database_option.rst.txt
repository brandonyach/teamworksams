.. _ams_client_ref: ../reference/ams_client.html
.. _update_database_entry_ref: ../reference/update_database_entry.html

.. _update_database_option:

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
  `AMSClient() <ams_client_ref_>`_.

See Also
--------

- `update_database_entry() <update_database_entry_ref_>`_: Function using :class:`UpdateDatabaseOption`.
- :ref:`database_operations`: Database update workflows.