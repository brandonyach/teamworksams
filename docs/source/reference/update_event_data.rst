.. _insert_event_data_ref: ../reference/insert_event_data.html
.. _update_event_option_ref: ../reference/update_event_option.html
.. _get_event_data_ref: ../reference/get_event_data.html

.. _update_event_data:

update_event_data
=================

.. autofunction:: teamworksams.import_main.update_event_data

Additional Notes
----------------

- The ``df`` must include 'event_id' with valid integer IDs; invalid IDs raise
  :class:`AMSError`. Use `get_event_data() <get_event_data_ref_>`_ to retrieve IDs.
- Set ``option.require_confirmation=True`` to prompt for confirmation before
  updating, preventing accidental changes in interactive mode.
- Use ``option.table_fields`` to update table fields, ensuring column names match
  the AMS form.

See Also
--------

- `UpdateEventOption() <update_event_option_ref_>`_: Configuration options for event updates.
- `insert_event_data() <insert_event_data_ref_>`_: For inserting new events.
- :ref:`importing_data`: Event update workflows.