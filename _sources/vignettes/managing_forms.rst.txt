Managing Forms
==============

This vignette provides a concise guide to managing AMS forms using **teamworksams**,
covering :func:`get_forms` and :func:`get_form_schema`. Designed for administrators and
analysts, it outlines workflows for listing accessible forms and summarizing form schemas
to understand their structure (e.g., sections, fields, types). These functions support
one-off tasks like auditing or preparing for data operations, with simple Python/pandas
examples. See :ref:`reference` for detailed documentation and
:ref:`vignettes/exporting_data` for related tasks.

Overview
--------

**teamworksams** enables exploration of AMS forms with two key functions:

- :func:`get_forms`: Retrieves a :class:`pandas.DataFrame` listing all forms accessible
  to the user, including IDs, names, and types (e.g., event, profile, database).
- :func:`get_form_schema`: Summarizes a form’s schema as a formatted string or raw
  dictionary, detailing sections, fields, and types.

These functions are typically used for administrative tasks, such as auditing forms or
understanding field requirements before importing/exporting data. The
:class:`FormOption` customizes behavior, like enabling interactive feedback. Examples use
the placeholder URL ``https://example.smartabase.com/site`` and credentials in a
``.env`` file.

Prerequisites
-------------

Ensure **teamworksams** is installed and credentials are set, as in
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

Listing Forms
-------------

Use :func:`get_forms` to retrieve a list of accessible forms:

.. code-block:: python

   import pandas as pd
   from teamworksams import get_forms, FormOption
   df = get_forms(
       url="https://example.smartabase.com/site",
       option=FormOption(interactive_mode=True)
   )
   print(df)

**Output**:

.. code-block:: text

   ℹ Requesting list of accessible forms...
   ✔ Retrieved 5 accessible forms.
      form_id       form_name     type
   0     2937       Allergies  database
   1     1234    Training Log    event
   2     5678  Athlete Profile  profile

Filter the DataFrame to find specific form types:

.. code-block:: python

   event_forms = df[df["type"] == "event"]
   print(event_forms["form_name"].tolist())
   ['Training Log']

See :func:`get_forms` and :class:`FormOption` for details.

Inspecting Schemas
------------------

Use :func:`get_form_schema` to summarize a form’s schema:

.. code-block:: python

   from teamworksams import get_form_schema, FormOption
   summary = get_form_schema(
       form_name="Allergies",
       url="https://example.smartabase.com/site",
       option=FormOption(interactive_mode=True, field_details=True)
   )
   print(summary)

**Output**:

.. code-block:: text

   ℹ Fetching summary for form 'Allergies'...
   ✔ Retrieved summary for form 'Allergies'.
   Form Schema Summary
   ==================
   Form Name: Allergies
   Form ID: 2937
   Form Type: database
   Sections: 2
   - General
   - Details
   Required Fields: 1
   - Allergy
   ...

Retrieve raw schema for custom processing:

.. code-block:: python

   raw_schema = get_form_schema(
       form_name="Allergies",
       url="https://example.smartabase.com/site",
       option=FormOption(raw_output=True)
   )
   print(raw_schema.keys())
   dict_keys(['form_id', 'name', 'type', 'sections', ...])

See :func:`get_form_schema` and :class:`FormOption` for output options.

Error Handling
--------------

Form functions raise :class:`AMSError` with descriptive messages:

.. code-block:: python

   get_form_schema(form_name="Invalid Form", url="https://example.smartabase.com/site")

**Output**:

.. code-block:: text

   AMSError: Form 'Invalid Form' not found...

For robust scripts, use try-except:

.. code-block:: python

   from teamworksams import AMSError
   try:
       df = get_forms(url="https://example.smartabase.com/site")
   except AMSError as e:
       print(f"Error: {e}")

Best Practices
--------------

- **Verify Form Names**: Use :func:`get_forms` to confirm `form_name` before
  calling :func:`get_form_schema`.
- **Use Caching**: Enable ``option.cache=True`` for efficiency in repeated
  form queries.
- **Raw Output**: Set ``option.raw_output=True`` for :func:`get_form_schema`
  when integrating with custom tools.
- **Detailed Summaries**: Use ``option.field_details=True`` to understand
  field options before data operations (e.g., :func:`insert_event_data`).
- **Interactive Mode**: Enable ``option.interactive_mode=True`` for feedback
  during administrative tasks.

Next Steps
----------

- Explore :ref:`vignettes/uploading_files` for attaching files to forms.
- Consult :ref:`reference` for detailed function and class documentation.
- Visit `GitHub <https://github.com/yachb35/teamworksams>`_ for support.