.. _login_ref: ../reference/login.html
.. _ams_client_ref: ../reference/ams_client.html

.. _get_client:

get_client
==========

.. autofunction:: teamworksams.utils.get_client

Additional Notes
----------------

- The ``cache`` parameter is recommended for workflows with multiple API calls (e.g., fetching users then groups), as it reuses a single `AMSClient() <ams_client_ref_>`_ instance, reducing authentication overhead.
- Set ``interactive_mode=True`` for real-time feedback in interactive environments like Jupyter notebooks, showing messages like "Successfully logged in."
- If credentials are not provided via ``username`` and ``password``, the function falls back to :envvar:`AMS_USERNAME`, :envvar:`AMS_PASSWORD`, or :class:`keyring` credentials (service name 'smartabasepy').

See Also
--------

- `AMSClient() <ams_client_ref_>`_: The client class created or reused.
- `login() <login_ref_>`_: Alternative for explicit authentication.
- :ref:`credentials`: Credential management workflows.