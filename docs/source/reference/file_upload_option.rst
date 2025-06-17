.. _upload_and_attach_to_events_ref: ../reference/upload_and_attach_to_events.html
.. _upload_and_attach_to_avatars_ref: ../reference/upload_and_attach_to_avatars.html

.. _file_upload_option:

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

- `upload_and_attach_to_events() <upload_and_attach_to_events_ref_>`_: Function for event file uploads.
- `upload_and_attach_to_avatars() <upload_and_attach_to_avatars_ref_>`_: Function for avatar uploads.
- :ref:`uploading_files`: File upload workflows.