.. _get_profile_data_ref: ../reference/get_profile_data.html

.. _profile_filter:

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
- Use with `get_profile_data() <get_profile_data_ref_>`_ to limit profiles to
  specific users, reducing API load for large datasets.

See Also
--------

- `get_profile_data() <get_profile_data_ref_>`_: Function using `ProfileFilter`.
- :class:`ProfileOption`: Configuration options for profile retrieval.