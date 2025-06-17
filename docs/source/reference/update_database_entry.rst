.. _insert_database_entry_ref: ../reference/insert_database_entry.html
.. _update_database_option_ref: ../reference/update_database_option.html
.. _get_database_ref: ../reference/get_database.html

.. _update_database_entry:

update_database_entry
=====================

.. autofunction:: teamworksams.database_main.update_database_entry

Additional Notes
----------------

- The ``df`` must include 'entry_id' with valid integer IDs; invalid IDs raise
  :class:`AMSError`. Use `get_database() <get_database_ref_>`_ to retrieve IDs.
- Set ``option.interactive_mode=True`` to prompt for confirmation before
  updating, preventing accidental changes.
- Use ``option.table_fields`` to update table fields, ensuring column names
  match the AMS form.

See Also
--------

- `UpdateDatabaseOption() <update_database_option_ref_>`_: Configuration options for updates.
- `insert_database_entry() <insert_database_entry_ref_>`_: For inserting new entries.
- :ref:`database_operations`: Database workflows.