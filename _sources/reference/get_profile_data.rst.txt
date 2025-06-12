get_profile_data
================

.. autofunction:: teamworksams.export_main.get_profile_data

Additional Notes
----------------

- The ``form`` parameter must match an existing AMS Profile Form exactly
  (case-sensitive).
- Use ``option.clean_names=True`` to standardize column names (e.g., 'Athlete
  Profile' to 'athlete_profile') for consistency in analysis.
- The ``filter`` parameter with :class:`ProfileFilter` limits profiles to specific
  users, reducing API load for large datasets.

See Also
--------

- :class:`ProfileFilter`: For filtering profile data.
- :class:`ProfileOption`: Configuration options for profile retrieval.