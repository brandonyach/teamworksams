Functions and Classes
=====================

This section provides detailed documentation for all **teamworksams** functions and classes, organized by module. Each entry links to a dedicated page with full parameter details, usage examples, return values, and error conditions. Use this reference to explore specific functionality, complemented by the :ref:`vignettes` section for practical workflows.

Credentials and Authentication
------------------------------

.. toctree::
   :maxdepth: 1

   get_client
   login
   ams_client
   ams_error
   login_option

- :class:`AMSClient`: Client class for handling AMS API requests and authentication.
- :class:`AMSError`: Custom exception for AMS API errors with descriptive messages.
- :func:`get_client`: Create or retrieve an authenticated client for API interactions.
- :func:`login`: Authenticate with an AMS instance and return session details.
- :class:`LoginOption`: Configuration options for the login process.

User Management
---------------

.. toctree::
   :maxdepth: 1

   get_user
   get_group
   edit_user
   create_user
   user_option
   group_option
   user_filter

- :func:`create_user`: Create new user accounts.
- :func:`edit_user`: Update user fields for existing accounts.
- :func:`get_user`: Retrieve user data as a pandas DataFrame, with optional filtering.
- :func:`get_group`: Fetch group data as a pandas DataFrame.
- :class:`UserFilter`: Filter object for narrowing user data queries.
- :class:`UserOption`: Configuration options for user-related functions.
- :class:`GroupOption`: Configuration options for group-related functions.


Exporting Data
-----------

.. toctree::
   :maxdepth: 1

   get_event_data
   sync_event_data
   get_profile_data
   event_filter
   sync_event_filter
   profile_filter
   event_option
   sync_event_option
   profile_option

- :func:`get_event_data`: Retrieve event data from an AMS Event Form within a date range.
- :func:`sync_event_data`: Fetch event data modified since the last synchronization time.
- :func:`get_profile_data`: Retrieve profile data from an AMS Profile Form.
- :class:`EventFilter`: Filter object for event data queries.
- :class:`EventOption`: Configuration options for event data retrieval.
- :class:`SyncEventFilter`: Filter object for synchronized event queries.
- :class:`SyncEventOption`: Configuration options for synchronized event retrieval.
- :class:`ProfileFilter`: Filter object for profile data queries.
- :class:`ProfileOption`: Configuration options for profile data retrieval.

Importing Data
-----------

.. toctree::
   :maxdepth: 1

   insert_event_data
   update_event_data
   upsert_event_data
   upsert_profile_data
   insert_event_option
   update_event_option
   upsert_event_option
   upsert_profile_option

- :func:`insert_event_data`: Insert new event records into an AMS Event Form.
- :func:`update_event_data`: Update existing event records in an AMS Event Form.
- :func:`upsert_event_data`: Insert and update event records in an AMS Event Form.
- :func:`upsert_profile_data`: Upsert profile data in an AMS Profile Form.
- :class:`InsertEventOption`: Configuration options for event insertion.
- :class:`UpdateEventOption`: Configuration options for event updates.
- :class:`UpsertEventOption`: Configuration options for event upserts.
- :class:`UpsertProfileOption`: Configuration options for profile upserts.

Database Operations
-------------------

.. toctree::
   :maxdepth: 1

   get_database
   delete_database_entry
   insert_database_entry
   update_database_entry
   get_database_option
   insert_database_option
   update_database_option

- :func:`get_database`: Retrieve database entries from an AMS database form.
- :func:`delete_database_entry`: Delete a specific database entry by ID.
- :func:`insert_database_entry`: Insert new database entries into a form.
- :func:`update_database_entry`: Update existing database entries in a form.
- :class:`GetDatabaseOption`: Configuration options for database retrieval.
- :class:`InsertDatabaseOption`: Configuration options for database insertion.
- :class:`UpdateDatabaseOption`: Configuration options for database updates.

Uploading Files
---------------

.. toctree::
   :maxdepth: 1

   upload_and_attach_to_events
   upload_and_attach_to_avatars
   file_upload_option

- :func:`upload_and_attach_to_events`: Upload files and attach to events in an AMS Event Form.
- :func:`upload_and_attach_to_avatars`: Upload images and attach as user profile avatars.
- :class:`FileUploadOption`: Configuration options for file upload operations.

Managing Forms
---------------

.. toctree::
   :maxdepth: 1

   get_forms
   get_form_schema
   form_option

- :func:`get_forms`: Fetch a list of forms accessible to the user.
- :func:`get_form_schema`: Fetch and summarize a specific form’s schema.
- :class:`FormOption`: Configuration options for form metadata and schema retrieval.

Deleting Data
-------------

.. toctree::
   :maxdepth: 1

   delete_event_data
   delete_multiple_events
   delete_event_option

- :func:`delete_event_data`: Delete a single event from an AMS instance.
- :func:`delete_multiple_events`: Delete multiple events from an AMS instance.
- :class:`DeleteEventOption`: Configuration options for event deletion.