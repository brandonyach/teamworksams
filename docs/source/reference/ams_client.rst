AMSClient
=========

.. autoclass:: teamworksams.utils.AMSClient
   :members:
   :undoc-members:
   :show-inheritance:

Additional Notes
----------------

- Typically created via :func:`get_client` rather than directly, ensuring proper authentication.
- The ``_fetch`` method is used internally for API requests but can be called for custom endpoints (e.g., 'usersearch').
- The ``_cache`` attribute stores API responses when ``cache=True`` in :meth:`_fetch`, improving performance for repeated calls.

See Also
--------

- :func:`get_client`: Recommended way to create an `AMSClient`.
- :class:`AMSError`: Exception raised for API errors.
- :ref:`vignettes/credentials`: Client setup guide.