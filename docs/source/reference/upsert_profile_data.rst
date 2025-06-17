.. _get_profile_data_ref: ../reference/get_profile_data.html
.. _upsert_profile_option_ref: ../reference/upsert_profile_option.html


.. _upsert_profile_data:

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

- `UpsertProfileOption() <upsert_profile_option_ref_>`_: Configuration options for profile upserts.
- `get_profile_data() <get_profile_data_ref_>`_: For retrieving profile data.