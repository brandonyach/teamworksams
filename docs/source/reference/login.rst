login
=====

.. autofunction:: teamworksams.login_main.login

Additional Notes
----------------

- The returned dictionary includes a 'session_header' and 'cookie' for use in custom API calls with a :class:`AMSClient`.
- Use ``option.interactive_mode=True`` to display status messages, helpful for debugging or interactive scripts.
- If credentials are not provided, the function checks :envvar:`AMS_USERNAME`, :envvar:`AMS_PASSWORD`, or :class:`keyring` credentials.

See Also
--------

- :class:`LoginOption`: Configuration options for login.
- :func:`get_client`: For automatic client creation.
- :ref:`vignettes/credentials`: Authentication workflows.