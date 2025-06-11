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

- :class:`FileUploadOption`: Configuration options for file uploads.
- :func:`get_event_data`: For retrieving event data to prepare `mapping_df`.
- :ref:`vignettes/uploading_files`: Event file upload workflows.