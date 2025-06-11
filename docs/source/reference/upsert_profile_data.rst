upsert_profile_data
===================

.. autofunction:: teamworksams.import_main.upsert_profile_data

Additional Notes
----------------

- Each user can have only one profile record per AMS Profile Form; upserts overwrite
  existing profiles for the same user.
- The ``df`` must include a user identifier column (e.g., 'username'); other
  columns represent profile fields (e.g., 'height_cm').
- Set ``option.require_confirmation=True`` to prompt for confirmation, preventing
  accidental overwrites in interactive mode.

See Also
--------

- :class:`UpsertProfileOption`: Configuration options for profile upserts.
- :func:`get_profile_data`: For retrieving profile data.