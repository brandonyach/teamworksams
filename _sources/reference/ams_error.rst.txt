.. _get_client_ref: ../reference/get_client.html
.. _login_option_ref: ../reference/login_option.html

.. _ams_error:

AMSError
========

.. autoclass:: teamworksams.utils.AMSError
   :members:
   :undoc-members:
   :show-inheritance:

Additional Notes
----------------

- The error message includes context like function name and endpoint, aiding debugging (e.g., "Invalid credentials - Function: login - Endpoint: user/loginUser").
- Raised by all **teamworksams** functions for consistent error handling, with interactive feedback when ``interactive_mode`` is enabled (e.g., in `LoginOption() <login_option_ref_>`_).

See Also
--------

- `get_client() <get_client_ref_>`_: Example function raising `AMSError`.
- :ref:`credentials`: Error handling in authentication.