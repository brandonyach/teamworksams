.. _get_client_ref: ../reference/get_client.html
.. _ams_client_ref: ../reference/ams_client.html
.. _login_option_ref: ../reference/login_option.html

.. _login:

login
=====

.. autofunction:: teamworksams.login_main.login

Additional Notes
----------------

- The returned dictionary includes a 'session_header' and 'cookie' for use in custom API calls with a `AMSClient() <ams_client_ref_>`_.
- Use ``option.interactive_mode=True`` to display status messages, helpful for debugging or interactive scripts.
- If credentials are not provided, the function checks :envvar:`AMS_USERNAME`, :envvar:`AMS_PASSWORD`, or :class:`keyring` credentials.

See Also
--------

- `LoginOption() <login_option_ref_>`_: Configuration options for login.
- `get_client() <get_client_ref_>`_: For automatic client creation.
- :ref:`credentials`: Authentication workflows.