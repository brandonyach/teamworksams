Database Management
==================

This vignette provides a concise guide to managing database entries in Teamworks AMS using
**teamworksams**, covering :func:`get_database`, :func:`delete_database_entry`,
:func:`insert_database_entry`, and :func:`update_database_entry`. It outlines simple workflows for retrieving, deleting, inserting, and updating entries in AMS database forms (e.g., 'Allergies'). See :ref:`reference` for detailed function documentation and
:ref:`vignettes/exporting_data` or :ref:`vignettes/importing_data` for event form data tasks.

Overview
--------

**teamworksams** supports managing AMS database forms, which store structured data like
allergies or equipment lists, with four key functions:

- :func:`get_database`: Retrieves entries as a :class:`pandas.DataFrame`.
- :func:`delete_database_entry`: Deletes a specific entry by ID.
- :func:`insert_database_entry`: Inserts new entries.
- :func:`update_database_entry`: Updates existing entries by ID.

These functions are typically used for one-off tasks, such as auditing or updating a
database form. Options (:class:`GetDatabaseOption`, :class:`InsertDatabaseOption`,
:class:`UpdateDatabaseOption`) customize behavior, like enabling interactive feedback.
Examples use the placeholder URL ``https://example.smartabase.com/site`` and credentials
managed via a ``.env`` file.

Prerequisites
-------------

Ensure **teamworksams** is installed and credentials are set, as described in
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
``python-dotenv``, ``tqdm``.

Retrieving Entries
-----------------

Use :func:`get_database` to fetch entries from a database form, such as 'Allergies':

.. code-block:: python

   import pandas as pd
   from teamworksams import get_database, GetDatabaseOption
   df = get_database(
       form_name = "Allergies",
       url = "https://example.smartabase.com/site",
       limit = 100,
       option = GetDatabaseOption(interactive_mode=  True)
   )
   print(df.head())

**Output**:

.. code-block:: text

   ℹ Fetching database entries for form 'Allergies'...
   ✔ Retrieved 100 database entries for form 'Allergies'.
      id  Allergy
   0  386197   Dairy
   1  386198    Eggs

See :func:`get_database` and :class:`GetDatabaseOption` for pagination options.

Deleting Entries
----------------

Use :func:`delete_database_entry` to remove a specific entry by ID:

.. code-block:: python

   from teamworksams import delete_database_entry
   result = delete_database_entry(
       database_entry_id=  386197,
       url = "https://example.smartabase.com/site"
   )
   print(result)

**Output**:

.. code-block:: text

   ✔ Successfully deleted database entry 386197.

See :func:`delete_database_entry` for details.

Inserting Entries
-----------------

Use :func:`insert_database_entry` to add new entries to a form:

.. code-block:: python

   from teamworksams import insert_database_entry, InsertDatabaseOption
   df = pd.DataFrame({"Allergy": ["Peanuts"]})
   insert_database_entry(
       df = df,
       form=  "Allergies",
       url = "https://example.smartabase.com/site",
       option = InsertDatabaseOption(interactive_mode = True)
   )

**Output**:

.. code-block:: text

   ℹ Inserting 1 database entries for form 'Allergies'
   ✔ Processed 1 database entries for form 'Allergies'
   ℹ Form: Allergies
   ℹ Result: Success
   ℹ Records inserted: 1
   ℹ Records attempted: 1

See :func:`insert_database_entry` and :class:`InsertDatabaseOption` for table fields.

Updating Entries
----------------

Use :func:`update_database_entry` to modify existing entries by `entry_id`:

.. code-block:: python

   from teamworksams import update_database_entry, UpdateDatabaseOption
   df = pd.DataFrame({"entry_id": [386198], "Allergy": ["Eggs Updated"]})
   update_database_entry(
       df = df,
       form = "Allergies",
       url = "https://example.smartabase.com/site",
       option = UpdateDatabaseOption(interactive_mode = True)
   )

**Output**:

.. code-block:: text

   ℹ Updating 1 database entries for form 'Allergies'
   Are you sure you want to update 1 existing database entries in 'Allergies'? (y/n): y
   ✔ Processed 1 database entries for form 'Allergies'
   ℹ Form: Allergies
   ℹ Result: Success
   ℹ Records updated: 1
   ℹ Records attempted: 1

See :func:`update_database_entry` and :class:`UpdateDatabaseOption` for details.

Error Handling
--------------

Database functions raise :class:`AMSError` with descriptive messages:

.. code-block:: python

   get_database(form_name = "Invalid Form", url = "https://example.smartabase.com/site")

**Output**:

.. code-block:: text

   AMSError: Form 'Invalid Form' is not a database form...

For automated scripts, use try-except:

.. code-block:: python

   from teamworksams import AMSError
   try:
       get_database(form_name = "Allergies", url = "https://example.smartabase.com/site")
   except AMSError as e:
       print(f"Error: {e}")

Best Practices
--------------

- **Validate Form**: Ensure ``form_name`` matches an AMS database form to avoid
  :class:`AMSError`.
- **Check IDs**: Use :func:`get_database` to obtain valid ``entry_id`` values for
  updates or deletions.
- **Use Caching**: Enable ``option.cache=True`` for efficiency in one-off tasks.
- **Confirm Updates**: Leverage ``interactive_mode=True`` in
  :class:`UpdateDatabaseOption` for confirmation prompts to prevent errors.
- **Table Fields**: Specify ``table_fields`` accurately for forms with table data.

Next Steps
----------

- Explore :ref:`vignettes/exporting_data` or :ref:`vignettes/importing_data` for
  frequent data tasks.
- Consult :ref:`reference` for detailed function and class documentation.
- Visit `GitHub <https://github.com/yachb35/teamworksams>`_ for support.