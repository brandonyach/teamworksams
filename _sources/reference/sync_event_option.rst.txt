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

- :func:`teamworksams.export_main.sync_event_data`: Function using `SyncEventOption`.
- :class:`SyncEventFilter`: For filtering synchronized events.
- :ref:`vignettes/exporting_data`: Synchronization workflows.