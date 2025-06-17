.. _profile_filter_ref: ../reference/profile_filter.html
.. _profile_option_ref: ../reference/profile_option.html

.. _get_profile_data:

get_profile_data
================

.. autofunction:: teamworksams.export_main.get_profile_data

Additional Notes
----------------

- The ``form`` parameter must match an existing AMS Profile Form exactly
  (case-sensitive).
- Use ``option.clean_names=True`` to standardize column names (e.g., 'Athlete
  Profile' to 'athlete_profile') for consistency in analysis.
- The ``filter`` parameter with `ProfileFilter() <Profile_filter_ref_>`_ limits profiles to specific
  users, reducing API load for large datasets.

See Also
--------

- `ProfileFilter() <Profile_filter_ref_>`_: For filtering profile data.
- `ProfileOption() <Profile_option_ref_>`_: Configuration options for profile retrieval.