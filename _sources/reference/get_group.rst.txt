get_group
=========

.. autofunction:: teamworksams.user_main.get_group

Additional Notes
----------------

- Set ``option.guess_col_type=True`` to ensure group names are treated as strings, avoiding type mismatches in :class:`pandas.DataFrame` operations.
- Use with :func:`get_user` to map users to groups, as shown in :ref:`vignettes/user_management`.
- Enable ``option.interactive_mode=True`` for feedback like "Retrieved 3 groups," useful in interactive environments.

See Also
--------

- :class:`GroupOption`: Configuration options for group retrieval.
- :func:`get_user`: For fetching user data with group filters.
- :ref:`vignettes/user_management`: User and group workflows.