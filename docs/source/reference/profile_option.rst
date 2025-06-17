.. _get_profile_data_ref: ../reference/get_profile_data.html

.. _profile_option:

ProfileOption
=============

.. autoclass:: teamworksams.export_option.ProfileOption
   :members:
   :undoc-members:
   :show-inheritance:

Additional Notes
----------------

- Use ``clean_names=True`` to standardize column names (e.g., 'Athlete Profile' to
  'athlete_profile') for consistency in data analysis.
- Set ``include_missing_users=True`` to include users without profiles in the output
  :class:`pandas.DataFrame`, ensuring complete user coverage.
- Enable ``interactive_mode=True`` for feedback like "Retrieved 5 profiles," useful
  in interactive environments.

See Also
--------

- `get_profile_data() <get_profile_data_ref_>`_: Function using `ProfileOption`.
- :class:`ProfileFilter`: For filtering profile data.