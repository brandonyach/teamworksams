.. _update_event_data_ref: ../reference/update_event_data.html
.. _insert_event_option_ref: ../reference/insert_event_option.html

.. _insert_event_data:

insert_event_data
=================

.. autofunction:: teamworksams.import_main.insert_event_data

Additional Notes
----------------

- The ``df`` must include 'start_date' in 'DD/MM/YYYY' format and a user identifier
  column (specified by ``option.id_col``, e.g., 'username'). Missing or invalid data
  raises :class:`AMSError`.
- Use ``option.table_fields`` to specify table fields in the AMS form, ensuring
  column names match exactly.
- Enable ``option.interactive_mode=True`` for status messages like "Inserted 2
  events," useful in interactive environments.

See Also
--------

- `InsertEventOption() <insert_event_option_ref_>`_: Configuration options for event insertion.
- `update_event_data() <update_event_data_ref_>`_: For updating existing events.
- :ref:`importing_data`: Event import workflows.