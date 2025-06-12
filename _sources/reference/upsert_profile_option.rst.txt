UpsertProfileOption
===================

.. autoclass:: teamworksams.import_option.UpsertProfileOption
   :members:
   :undoc-members:
   :show-inheritance:

Additional Notes
----------------

- The ``id_col`` must be one of 'user_id', 'about', 'username', or 'email' and
  present in the input :class:`pandas.DataFrame` to map user identifiers;
  invalid columns raise :class:`ValueError`.
- Enable ``interactive_mode=True`` for feedback like "Upserted 2 profiles,"
  useful in interactive environments.
- Use ``cache=True`` to reduce API calls when upserting multiple profiles,
  improving performance.

See Also
--------

- :func:`teamworksams.import_main.upsert_profile_data`: Function using `UpsertProfileOption`.