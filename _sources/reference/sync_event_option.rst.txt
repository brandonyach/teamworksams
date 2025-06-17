.. _sync_event_data_ref: ../reference/sync_event_data.html
.. _sync_event_filter_ref: ../reference/sync_event_filter.html

.. _sync_event_option:

SyncEventOption
===============

.. autoclass:: teamworksams.export_option.SyncEventOption
   :members:
   :undoc-members:
   :show-inheritance:

Additional Notes
----------------

- Set ``include_user_data=True`` to append user metadata (e.g., 'about') to the
  :class:`pandas.DataFrame`, useful for reporting without additional API calls.
- Use ``include_uuid=True`` to include user UUIDs, requiring user data retrieval and
  increasing API load.
- Enable ``interactive_mode=True`` for status messages like "Retrieved 5 events,"
  enhancing visibility in interactive scripts.

See Also
--------

- `sync_event_data() <sync_event_data_ref_>`_: Function using `SyncEventOption`.
- `SyncEventFilter() <sync_event_filter_ref_>`_`: For filtering synchronized events.
- :ref:`exporting_data`: Synchronization workflows.