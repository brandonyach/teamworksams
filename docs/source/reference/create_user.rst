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

- :class:`UserOption`: Configuration options for user operations.
- :func:`edit_user`: For updating existing users.
- :ref:`vignettes/user_management`: User creation workflows.