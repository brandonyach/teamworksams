sync_event_data
===============

.. autofunction:: teamworksams.export_main.sync_event_data

Additional Notes
----------------

- The ``last_synchronisation_time`` is in milliseconds since 1970-01-01 (Unix epoch).
  Use the returned new synchronization time for subsequent calls to avoid duplicate
  data.
- Set ``option.include_user_data=True`` to append user metadata (e.g., 'about') to the
  :class:`pandas.DataFrame`, useful for reporting.
- The DataFrame’s ``attrs['deleted_event_ids']`` contains IDs of deleted events, which
  can be used to update local datasets.

See Also
--------

- :class:`SyncEventFilter`: For filtering synchronized events.
- :class:`SyncEventOption`: Configuration options for synchronization.
- :ref:`vignettes/exporting_data`: Synchronization workflows.