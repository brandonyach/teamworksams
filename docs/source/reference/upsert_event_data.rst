upsert_event_data
=================

.. autofunction:: teamworksams.import_main.upsert_event_data

Additional Notes
----------------

- Records with 'event_id' are updated; those without require 'start_date' and are
  inserted. Splitting is automatic based on 'event_id' presence.
- Use ``option.require_confirmation=True`` to prompt for update confirmation,
  ensuring safe operations in interactive mode.
- Enable ``option.cache=True`` to reuse a :class:`AMSClient` for both insert and
  update operations, improving performance.

See Also
--------

- :class:`UpsertEventOption`: Configuration options for event upserts.
- :func:`insert_event_data`: For inserting new events.
- :func:`update_event_data`: For updating existing events.
- :ref:`vignettes/importing_data`: Event upsert workflows.