UpsertEventOption
=================

.. autoclass:: teamworksams.import_option.UpsertEventOption
   :members:
   :undoc-members:
   :show-inheritance:

Additional Notes
----------------

- The ``id_col`` must be one of 'user_id', 'about', 'username', or 'email' and
  present in the input :class:`pandas.DataFrame` to map user identifiers
  correctly.
- Use ``cache=True`` to optimize performance when upserting large datasets,
  reusing a :class:`AMSClient` for both inserts and updates.
- Specify ``table_fields`` for table fields (e.g., ['session_details']),
  ensuring DataFrame columns match the AMS form exactly.

See Also
--------

- :func:`teamworksams.import_main.upsert_event_data`: Function using `UpsertEventOption`.
- :ref:`vignettes/importing_data`: Event upsert workflows.