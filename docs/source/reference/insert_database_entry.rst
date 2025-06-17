.. _insert_database_option_ref: ../reference/insert_database_option.html
.. _update_database_entry_ref: ../reference/update_database_entry.html

.. _insert_database_entry:

insert_database_entry
=====================

.. autofunction:: teamworksams.database_main.insert_database_entry

Additional Notes
----------------

- The ``df`` must contain columns matching the AMS form’s fields (e.g.,
  'Allergy'); missing or invalid data raises :class:`AMSError`.
- Use ``option.table_fields`` to specify table fields, ensuring column names
  match exactly to avoid errors.
- Enable ``option.interactive_mode=True`` for status messages like "Inserted 3
  entries," ideal for interactive scripts.

See Also
--------

- `InsertDatabaseOption() <insert_database_option_ref_>`_: Configuration options for insertion.
- `update_database_entry() <update_database_entry_ref_>`_: For updating existing entries.
- :ref:`database_operations`: Database workflows.