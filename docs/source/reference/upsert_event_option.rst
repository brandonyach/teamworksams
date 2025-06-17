.. _upsert_event_data_ref: ../reference/upsert_event_data.html
.. _ams_client_ref: ../reference/ams_client.html


.. _upsert_event_option:

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
  reusing a `AMSClient() <ams_client_ref_>`_ for both inserts and updates.
- Specify ``table_fields`` for table fields (e.g., ['session_details']),
  ensuring DataFrame columns match the AMS form exactly.

See Also
--------

- `upsert_event_data() <upsert_event_data_ref_>`_: Function using `UpsertEventOption`.
- :ref:`importing_data`: Event upsert workflows.