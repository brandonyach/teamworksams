.. _get_client_ref: ../reference/get_client.html
.. _ams_error_ref: ../reference/ams_error.html

.. _ams_client:

AMSClient
=========

.. autoclass:: teamworksams.utils.AMSClient
   :members:
   :undoc-members:
   :show-inheritance:

Additional Notes
----------------

- Typically created via `get_client() <get_client_ref_>`_ rather than directly, ensuring proper authentication.
- The ``_fetch`` method is used internally for API requests but can be called for custom endpoints (e.g., 'usersearch').
- The ``_cache`` attribute stores API responses when ``cache=True`` in :meth:`_fetch`, improving performance for repeated calls.

See Also
--------

- `get_client() <get_client_ref_>`_: Recommended way to create an `AMSClient`.
- `AMSError() <ams_error_ref_>`_: Exception raised for API errors.
- :ref:`credentials`: Client setup guide.