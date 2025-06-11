get_client
==========

.. autofunction:: teamworksams.utils.get_client

Additional Notes
----------------

- The ``cache`` parameter is recommended for workflows with multiple API calls (e.g., fetching users then groups), as it reuses a single :class:`AMSClient` instance, reducing authentication overhead.
- Set ``interactive_mode=True`` for real-time feedback in interactive environments like Jupyter notebooks, showing messages like "Successfully logged in."
- If credentials are not provided via ``username`` and ``password``, the function falls back to :envvar:`AMS_USERNAME`, :envvar:`AMS_PASSWORD`, or :class:`keyring` credentials (service name 'smartabasepy').

See Also
--------

- :class:`AMSClient`: The client class created or reused.
- :func:`teamworksams.login_main.login`: Alternative for explicit authentication.
- :ref:`vignettes/credentials`: Credential management workflows.