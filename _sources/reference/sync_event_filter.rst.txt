.. _sync_event_data_ref: ../reference/sync_event_data.html
.. _sync_event_filter_ref: ../reference/sync_event_filter.html
.. _sync_event_option_ref: ../reference/sync_event_option.html

.. _sync_event_filter:

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
- Use with `sync_event_data() <sync_event_data_ref_>`_ to limit synchronized
  events to specific users, optimizing performance for incremental updates.

See Also
--------

- `sync_event_data() <sync_event_data_ref_>`_: Function using `SyncEventFilter`.
- `SyncEventOption() <sync_event_option_ref_>`_: Configuration options for synchronization.
- :ref:`exporting_data`: Synchronization workflows.