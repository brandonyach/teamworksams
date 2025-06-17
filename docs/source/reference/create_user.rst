.. _user_option_ref: ../reference/user_option.html
.. _edit_user_ref: ../reference/edit_user.html

.. _create_user:

create_user
===========

.. autofunction:: teamworksams.user_main.create_user

Additional Notes
----------------

- The ``user_df`` must include required columns ('first_name', 'last_name', 'username', 'email', 'dob', 'password', 'active') to avoid :class:`ValueError`. Optional columns like 'uuid' or 'sex' enhance user profiles.
- Check the returned DataFrame for failed creations, which lists reasons like "Invalid data" or "API request failed."
- Use ``option.interactive_mode=True`` to track progress with :mod:`tqdm` progress bars for multiple users.

See Also
--------

- `UserOption() <user_option_ref_>`_: Configuration options for user operations.
- `edit_user() <edit_user_ref_>`_: For updating existing users.
- :ref:`user_management`: User creation workflows.