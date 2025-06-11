upload_and_attach_to_avatars
============================

.. autofunction:: teamworksams.file_main.upload_and_attach_to_avatars

Additional Notes
----------------

- If ``mapping_df`` is None, the function generates it from image filenames in
  `file_dir`, using names (without extension) as `user_key` values, simplifying
  batch avatar uploads.
- Valid image types include .png, .jpg, .jpeg, .gif, and .heic; non-image
  files are skipped with failure reasons.
- Ensure users exist in the AMS instance (verify with :func:`get_user`) to
  avoid “User not found” errors.
- Use ``option.interactive_mode=True`` to monitor progress, as the function
  involves user mapping, file validation, and profile updates.

See Also
--------

- :class:`FileUploadOption`: Configuration options for file uploads.
- :func:`get_user`: For retrieving user data to prepare `mapping_df`.
- :ref:`vignettes/uploading_files`: Avatar upload workflows.