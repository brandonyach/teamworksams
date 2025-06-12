edit_user
=========

.. autofunction:: teamworksams.user_main.edit_user

Additional Notes
----------------

- The ``mapping_df`` must include a column matching ``user_key`` (e.g., 'username')
  and at least one updatable field (e.g., 'email', 'first_name'). Empty values are
  sent as empty strings to the AMS API, which may overwrite existing data.
- The returned DataFrame lists failed updates with reasons like "User not found" or
  "API request failed," enabling easy troubleshooting.
- Use ``option.interactive_mode=True`` to display progress bars via :mod:`tqdm` for
  large updates, enhancing visibility in interactive scripts.

See Also
--------

- :class:`UserOption`: Configuration options for user operations.
- :func:`create_user`: For creating new users.
- :ref:`vignettes/user_management`: User update workflows.