.. _group_option_ref: ../reference/group_option.html
.. _get_user_ref: ../reference/get_user.html

.. _get_group:

get_group
=========

.. autofunction:: teamworksams.user_main.get_group

Additional Notes
----------------

- Set ``option.guess_col_type=True`` to ensure group names are treated as strings, avoiding type mismatches in :class:`pandas.DataFrame` operations.
- Use with `get_user() <get_user_ref_>`_ to map users to groups, as shown in :ref:`user_management`.
- Enable ``option.interactive_mode=True`` for feedback like "Retrieved 3 groups," useful in interactive environments.

See Also
--------

- `GroupOption() <group_option_ref_>`_: Configuration options for group retrieval.
- `get_user() <get_user_ref_>`_: For fetching user data with group filters.
- :ref:`user_management`: User and group workflows.