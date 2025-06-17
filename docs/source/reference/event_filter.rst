.. _get_event_data_ref: ../reference/get_event_data.html
.. _event_option_ref: ../reference/event_option.html

.. _event_filter:

EventFilter
===========

.. autoclass:: teamworksams.export_filter.EventFilter
   :members:
   :undoc-members:
   :show-inheritance:

Additional Notes
----------------

- The ``user_key`` must be one of 'username', 'email', 'group', or 'about';
  ``user_value`` is case-sensitive and can be a string or list (e.g.,
  ['TeamA', 'TeamB']).
- Use ``data_key`` and ``data_value`` to filter by event fields (e.g.,
  ``data_key="intensity"``, ``data_value="High"``), with ``data_condition`` like
  'equals' or 'contains'.
- Set ``events_per_user`` to limit the number of events per user, reducing API load
  for large datasets.

See Also
--------

- `get_event_data() <get_event_data_ref_>`_: Function using `EventFilter`.
- `EventOption() <event_option_ref_>`_: Configuration options for event retrieval.
- :ref:`exporting_data`: Event filtering workflows.