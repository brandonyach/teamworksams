ProfileFilter
=============

.. autoclass:: teamworksams.export_filter.ProfileFilter
   :members:
   :undoc-members:
   :show-inheritance:

Additional Notes
----------------

- The ``user_key`` must be one of 'username', 'email', 'group', or 'about';
  ``user_value`` is case-sensitive and supports lists (e.g., ['TeamA']).
- Use with :func:`teamworksams.export_main.get_profile_data` to limit profiles to
  specific users, reducing API load for large datasets.

See Also
--------

- :func:`teamworksams.export_main.get_profile_data`: Function using `ProfileFilter`.
- :class:`ProfileOption`: Configuration options for profile retrieval.