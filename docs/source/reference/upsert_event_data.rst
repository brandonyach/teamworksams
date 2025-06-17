.. _update_event_data_ref: ../reference/update_event_data.html
.. _insert_event_data_ref: ../reference/insert_event_data.html
.. _upsert_event_option_ref: ../reference/upsert_event_option.html
.. _ams_client_ref: ../reference/ams_client.html

.. _upsert_event_data:

upsert_event_data
=================

.. autofunction:: teamworksams.import_main.upsert_event_data

Additional Notes
----------------

- Records with 'event_id' are updated; those without require 'start_date' and are
  inserted. Splitting is automatic based on 'event_id' presence.
- Use ``option.require_confirmation=True`` to prompt for update confirmation,
  ensuring safe operations in interactive mode.
- Enable ``option.cache=True`` to reuse a `AMSClient() <ams_client_ref_>`_ for both insert and
  update operations, improving performance.

See Also
--------

- `UpsertEventOption() <upsert_event_option_ref_>`_: Configuration options for event upserts.
- `insert_event_data() <insert_event_data_ref_>`_: For inserting new events.
- `update_event_data() <update_event_data_ref_>`_: For updating existing events.
- :ref:`importing_data`: Event upsert workflows.