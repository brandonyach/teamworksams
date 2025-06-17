.. _get_user_ref: ../reference/get_user.html
.. _get_event_data_ref: ../reference/get_event_data.html
.. _upload_and_attach_to_events_ref: ../reference/upload_and_attach_to_events.html
.. _upload_and_attach_to_avatars_ref: ../reference/upload_and_attach_to_avatars.html
.. _file_upload_option_ref: ../reference/file_option.html

.. _upload_and_attach_to_events:

upload_and_attach_to_events
===========================

.. autofunction:: teamworksams.file_main.upload_and_attach_to_events

Additional Notes
----------------

- The ``mapping_df`` must include `user_key`, `file_name`, and `mapping_col`
  (e.g., 'attachment_id'); missing columns or invalid files raise
  :class:`AMSError`.
- Valid file types include .pdf, .doc, .docx, .txt, .csv, .png, .jpg, .jpeg,
  .gif, .xls, .xlsx, and .heic; others are skipped with failure reasons.
- Ensure the AMS form has a file field (`file_field_name`) and `mapping_col`
  (e.g., 'attachment_id') to match events correctly.
- Use ``option.save_to_file`` to save results for troubleshooting, as the
  function performs multiple steps (user mapping, event matching, upload,
  update).

See Also
--------

- `FileUploadOption() <file_upload_option_ref_>`_: Configuration options for file uploads.
- `get_event_data() <get_event_data_ref_>`_: For retrieving event data to prepare `mapping_df`.
- :ref:`uploading_files`: Event file upload workflows.