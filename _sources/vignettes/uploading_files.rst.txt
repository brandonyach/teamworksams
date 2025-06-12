Uploading Files
===============

This vignette provides a comprehensive guide to uploading files in Teamworks AMS using
**teamworksams**, covering :func:`upload_and_attach_to_events` and
:func:`upload_and_attach_to_avatars`. Designed for analysts and administrators, it
outlines detailed workflows for attaching files to event forms (e.g., 'Document Store')
or setting user profile avatars. These complex, multi-step functions require careful
setup, so this guide breaks down each step with Python/pandas examples. See
:ref:`reference` for detailed function documentation and
:ref:`vignettes/exporting_data` for related data tasks.

Overview
--------

**teamworksams** supports file uploads to AMS with two key functions:

- :func:`upload_and_attach_to_events`: Uploads files and attaches them to events in an
  Event Form, matching users and events via a mapping DataFrame.
- :func:`upload_and_attach_to_avatars`: Uploads images and sets them as user profile
  avatars, with optional auto-generated mapping.

Both functions return a :class:`pandas.DataFrame` with results, detailing successes and
failures. They involve multiple steps: user/event mapping, file validation, uploading,
and AMS updates. The :class:`FileUploadOption` customizes behavior, such as saving
results to CSV. Examples use the placeholder URL
``https://example.smartabase.com/site`` and credentials in a ``.env`` file.

Prerequisites
-------------

Ensure **teamworksams** is installed and credentials are configured, as in
:ref:`vignettes/getting_started`. Use a ``.env`` file:

.. code-block:: text
   :caption: .env

   AMS_URL=https://example.smartabase.com/site
   AMS_USERNAME=username
   AMS_PASSWORD=password

Load credentials:

.. code-block:: python

   from dotenv import load_dotenv
   load_dotenv()

Dependencies (installed with **teamworksams**): ``pandas``, ``requests``,
``python-dotenv``, ``tqdm``. Prepare files in a directory (e.g., '/path/to/files')
and ensure the AMS form has appropriate fields (e.g., 'attachment' for events).

Uploading Files to Events
------------------------

Use :func:`upload_and_attach_to_events` to upload files and attach them to an AMS Event
Form, matching users and events via a mapping DataFrame.

**Preparing the Mapping DataFrame**

Create a :class:`pandas.DataFrame` with `user_key`, `file_name`, and `attachment_id`:

.. code-block:: python

   import pandas as pd
   from teamworksams import get_event_data, EventOption
   # Fetch events to get attachment IDs
   event_df = get_event_data(
       form="Document Store",
       start_date="01/01/2025",
       end_date="31/12/2025",
       url="https://example.smartabase.com/site",
       option=EventOption(interactive_mode=True)
   )
   mapping_df = pd.DataFrame({
       "username": ["user1", "user2"],
       "file_name": ["doc1.pdf", "doc2.png"],
       "attachment_id": event_df["attachment_id"].head(2).tolist()
   })

**Uploading and Attaching Files**

Upload files from a directory and attach to the 'attachment' field:

.. code-block:: python

   from teamworksams import upload_and_attach_to_events, FileUploadOption
   results = upload_and_attach_to_events(
       mapping_df=mapping_df,
       file_dir="/path/to/files",
       user_key="username",
       form="Document Store",
       file_field_name="attachment",
       url="https://example.smartabase.com/site",
       option=FileUploadOption(interactive_mode=True, save_to_file="results.csv")
   )
   print(results)

**Output**:

.. code-block:: text

   ℹ Fetching all user data...
   ✔ Retrieved 50 users.
   ℹ Fetching event data from 'Document Store'...
   ✔ Retrieved 100 events.
   ℹ Uploading 2 files...
   Uploading files: 100%|██████████| 2/2 [00:02<00:00, 1.00s/it]
   ✔ Successfully attached 2 files to 2 events.
   ℹ Saved results to 'results.csv'
      username file_name event_id user_id file_id server_file_name  status reason
   0   user1   doc1.pdf  123456  78901   94196 doc1_1747654002120.pdf SUCCESS None
   1   user2   doc2.png  123457  78902   94197 doc2_1747654003484.png SUCCESS None

**Steps Performed**:
1. Validates `mapping_df` for required columns and `user_key`.
2. Fetches user data to map `user_key` to `user_id`.
3. Fetches event data from `form` to match `attachment_id`.
4. Validates files in `file_dir` (e.g., .pdf, .png).
5. Uploads files and generates file references.
6. Updates events with file references in `file_field_name`.
7. Returns results, optionally saving to CSV.

See :func:`upload_and_attach_to_events` and :class:`FileUploadOption` for details.

Uploading Avatars
-----------------

Use :func:`upload_and_attach_to_avatars` to upload images and set them as user profile
avatars, with optional automatic mapping.

**Using a Mapping DataFrame**

Create a :class:`pandas.DataFrame` with `user_key` and `file_name`:

.. code-block:: python

   mapping_df = pd.DataFrame({
       "username": ["user1", "user2"],
       "file_name": ["avatar1.png", "avatar2.jpg"]
   })

Upload and attach avatars:

.. code-block:: python

   from teamworksams import upload_and_attach_to_avatars, FileUploadOption
   results = upload_and_attach_to_avatars(
       mapping_df=mapping_df,
       file_dir="/path/to/avatars",
       user_key="username",
       url="https://example.smartabase.com/site",
       option=FileUploadOption(interactive_mode=True, save_to_file="avatars.csv")
   )
   print(results)

**Output**:

.. code-block:: text

   ℹ Fetching all user data...
   ✔ Retrieved 50 users.
   ℹ Uploading 2 avatars...
   Uploading files: 100%|██████████| 2/2 [00:02<00:00, 1.00s/it]
   ✔ Successfully attached 2 avatar files to 2 users.
   ℹ Saved results to 'avatars.csv'
      username file_name user_id file_id server_file_name  status reason
   0   user1   avatar1.png 78901 94196 avatar1_1747654002120.png SUCCESS None
   1   user2   avatar2.jpg 78902 94197 avatar2_1747654003484.jpg SUCCESS None

**Automatic Mapping from Directory**

Generate `mapping_df` from filenames (without extension) as `user_key`:

.. code-block:: python

   results = upload_and_attach_to_avatars(
       file_dir="/path/to/avatars",
       user_key="username",
       url="https://example.smartabase.com/site",
       option=FileUploadOption(interactive_mode=True)
   )

**Output**:

.. code-block:: text

   ℹ Generated mapping DataFrame from 2 image files in directory.
   ℹ Fetching all user data...
   ✔ Retrieved 50 users.
   ℹ Uploading 2 avatars...
   ✔ Successfully attached 2 avatar files to 2 users.

**Steps Performed**:
1. Generates `mapping_df` if None, using filenames as `user_key`.
2. Validates `mapping_df` and `user_key`.
3. Fetches user data to map `user_key` to `user_id`.
4. Validates image files in `file_dir` (e.g., .png, .jpg).
5. Uploads images and updates user profiles’ `avatarId`.
6. Returns results, optionally saving to CSV.

See :func:`upload_and_attach_to_avatars` and :class:`FileUploadOption` for details.

Error Handling
--------------

File functions raise :class:`AMSError` with detailed messages:

.. code-block:: python

   upload_and_attach_to_events(
       mapping_df=mapping_df,
       file_dir="/invalid/path",
       user_key="username",
       form="Document Store",
       file_field_name="attachment",
       url="https://example.smartabase.com/site"
   )

**Output**:

.. code-block:: text

   AMSError: '/invalid/path' is not a valid directory...

Common errors include:
- Invalid `file_dir` or missing files.
- Non-existent users or events.
- Unsupported file types (e.g., .exe for events).
- API failures during upload or update.

For robust scripts, use try-except:

.. code-block:: python

   from teamworksams import AMSError
   try:
       results = upload_and_attach_to_avatars(
           file_dir="/path/to/avatars",
           user_key="username",
           url="https://example.smartabase.com/site"
       )
   except AMSError as e:
       print(f"Error: {e}")

Best Practices
--------------

- **Prepare Mapping DataFrame**: Use :func:`get_user` or :func:`get_event_data` to
  ensure valid `user_key` and `attachment_id` values.
- **Validate Files**: Place only supported files (.pdf, .png, etc., for events;
  images for avatars) in `file_dir` to avoid failures.
- **Use Interactive Mode**: Enable ``option.interactive_mode=True`` to monitor
  progress and identify issues in multi-step operations.
- **Save Results**: Set ``option.save_to_file`` to a CSV path for auditing and
  troubleshooting, especially for large uploads.
- **Optimize Caching**: Use ``option.cache=True`` to reduce API calls when
  fetching user or event data.

Troubleshooting
---------------

- **Invalid Directory**:

  .. code-block:: text

     AMSError: '/invalid/path' is not a valid directory...

  **Solution**: Verify `file_dir` exists:

    .. code-block:: python

       import os
       assert os.path.isdir("/path/to/files")

- **Missing Files**:

  .. code-block:: text

     ⚠️ Failed to attach files: ... not found in directory...

  **Solution**: Ensure files in `mapping_df` exist in `file_dir`:

    .. code-block:: python

       mapping_df = mapping_df[mapping_df["file_name"].apply(lambda x: os.path.exists(os.path.join("/path/to/files", x)))]

- **Invalid User Key**:

  .. code-block:: text

     ⚠️ Failed to attach files: User not found...

  **Solution**: Validate users with :func:`get_user`:

    .. code-block:: python

       user_df = get_user(url="https://example.smartabase.com/site")
       mapping_df = mapping_df[mapping_df["username"].isin(user_df["username"])]

Next Steps
----------

- Explore :ref:`vignettes/exporting_data` for retrieving event data.
- Consult :ref:`reference` for detailed function and class documentation.
- Visit `GitHub <https://github.com/yachb35/teamworksams>`_ for support.