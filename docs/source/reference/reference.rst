Function and Class Reference
===========================

This section provides detailed documentation for all **teamworksams** functions and classes, organized by module. Each entry links to a dedicated page with full parameter details, usage examples, return values, and error conditions. Use this reference to explore specific functionality, complemented by the :ref:`vignettes` section for practical workflows.

Credentials and Authentication
------------------------------

.. toctree::
   :maxdepth: 1
   :hidden:

   get_client
   login
   ams_client
   ams_error
   login_option

- :func:`get_client`: Create or retrieve an authenticated AMS client for API interactions.
- :func:`login`: Authenticate with an AMS instance and return session details.
- :class:`AMSClient`: Client class for handling AMS API requests and authentication.
- :class:`AMSError`: Custom exception for AMS API errors with descriptive messages.
- :class:`LoginOption`: Configuration options for the login process.