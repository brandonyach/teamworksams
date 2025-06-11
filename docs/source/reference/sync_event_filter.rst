SyncEventFilter
===============

.. autoclass:: teamworksams.export_filter.SyncEventFilter
   :members:
   :undoc-members:
   :show-inheritance:

Additional Notes
----------------

- The ``user_key`` must be one of 'username', 'email', 'group', or 'about';
  ``user_value`` is case-sensitive and supports lists for multiple values (e.g.,
  ['TeamA']).
- Use with :func:`teamworksams.export_main.sync_event_data` to limit synchronized
  events to specific users, optimizing performance for incremental updates.

See Also
--------

- :func:`teamworksams.export_main.sync_event_data`: Function using `SyncEventFilter`.
- :class:`SyncEventOption`: Configuration options for synchronization.
- :ref:`vignettes/exporting_data`: Synchronization workflows.