AMSError
========

.. autoclass:: teamworksams.utils.AMSError
   :members:
   :undoc-members:
   :show-inheritance:

Additional Notes
----------------

- The error message includes context like function name and endpoint, aiding debugging (e.g., "Invalid credentials - Function: login - Endpoint: user/loginUser").
- Raised by all **teamworksams** functions for consistent error handling, with interactive feedback when ``interactive_mode`` is enabled (e.g., in :class:`LoginOption`).

See Also
--------

- :func:`get_client`: Example function raising `AMSError`.
- :ref:`vignettes/credentials`: Error handling in authentication.