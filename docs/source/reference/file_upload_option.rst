FileUploadOption
================

.. autoclass:: teamworksams.file_option.FileUploadOption
   :members:
   :undoc-members:
   :show-inheritance:

Additional Notes
----------------

- Enable ``interactive_mode=True`` for detailed progress updates and
  :mod:`tqdm` progress bars, crucial for monitoring large file uploads.
- Use ``save_to_file`` to store results in a CSV (e.g., 'results.csv') for
  auditing successes and failures, especially when attaching files to events.
- Set ``cache=True`` to optimize performance by reusing user and event data
  during the upload process.

See Also
--------

- :func:`teamworksams.file_main.upload_and_attach_to_events`: Function for event file uploads.
- :func:`teamworksams.file_main.upload_and_attach_to_avatars`: Function for avatar uploads.
- :ref:`vignettes/uploading_files`: File upload workflows.