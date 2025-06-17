.. _get_forms_ref: ../reference/get_forms.html
.. _get_form_schema_ref: ../reference/get_form_schema.html
.. _form_option_ref: ../reference/form_option.html
.. _insert_event_data_ref: ../reference/insert_event_data.html

.. _managing_forms:

Managing Forms
==============

This vignette provides a concise guide to managing AMS forms using **teamworksams**,
covering `get_forms() <get_forms_ref_>`_ and `get_form_schema() <get_form_schema_ref_>`_. It outlines workflows for listing accessible forms and summarizing form schemas
to understand their structure (e.g., sections, fields, types). These functions support
one-off tasks like auditing or preparing for data operations, with simple Python/pandas
examples. See :ref:`reference` for detailed documentation and
:ref:`exporting_data` for related tasks.

Overview
--------

**teamworksams** enables exploration of AMS forms with two key functions:

- `get_forms() <get_forms_ref_>`_: Retrieves a :class:`pandas.DataFrame` listing all forms accessible
  to the user, including IDs, names, and types (e.g., event, profile, database).
- `get_form_schema() <get_form_schema_ref_>`_: Summarizes a form’s schema as a formatted string or raw
  dictionary, detailing sections, fields, and types.

These functions are typically used for administrative tasks, such as auditing forms or
understanding field requirements before importing/exporting data. The
`FormOption() <form_option_ref_>`_ customizes behavior, like enabling interactive feedback. Examples use
the placeholder URL ``https://example.smartabase.com/site`` and credentials in a
``.env`` file.

Prerequisites
-------------

Ensure **teamworksams** is installed and credentials are set, as in
:ref:`getting_started`. Use a ``.env`` file:

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

Listing Accessible Forms
------------------------

Use `get_forms() <get_forms_ref_>`_ to retrieve a list of accessible forms:

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
      form_id       form_name       type    mainCategory    isReadOnly     groupEntryEnabled
   0     2937       Allergies   database            None         False                 False       
   1     1234    Training Log      event      Monitoring         False                  True
   2     5678  Athlete Profile   profile    Demographics         False                 False

Filter the DataFrame to find specific form types:

.. code-block:: python

   event_forms = df[df["type"] == "event"]
   print(event_forms["form_name"].tolist())
   ['Training Log']

See `get_forms() <get_forms_ref_>`_ and `FormOption() <form_option_ref_>`_ for details.

Inspecting Schemas
------------------

Use `get_form_schema() <get_form_schema_ref_>`_ to summarize a form’s schema:

.. code-block:: python

   from teamworksams import get_form_schema, FormOption
   summary = get_form_schema(
       form ="Training Log",
       url = "https://example.smartabase.com/site",
       option = FormOption(interactive_mode = True, field_details = True)
   )
   print(summary)

**Output**:

.. code-block:: text

   ℹ Fetching summary for form 'Training Log' (ID: 5285, Type: event)...
   ✔ Retrieved summary for form 'Training Log'.
   =====================================
   Form Schema Summary: RPE Training Log
   =====================================

   Form Details
   ------------
   - Form Name: RPE Training Log
   - Form ID: 5285

   Sections
   --------
   - Total: 5
   • Session Details
   • Summary Calculations
   • User Account Details
   • Day of the Week
   • Profile Details

   Required Fields
   ---------------
   - Total: 0
   - No required fields found.

   Defaults to Last Known Value
   ----------------------------
   - Total: 0
   - No fields default to the last known value.

   Linked Fields
   -------------
   - Total: 7
   • Sport
   • Position
   • Height
   • Dominant Hand
   • Dominant Foot
   • Preferred Language
   • Season

   Form Item Types
   ---------------
   - Total Unique Types: 14
   - Dropdown: 1 field(s)
      • Session Type
   - Number: 1 field(s)
      • Duration
   - Single Selection: 1 field(s)
      • Rate your Perceived Exertion (RPE)
   - Calculation: 5 field(s)
      • RPE
      • Session Load
      • Index
      • ACWR
      • Total ACWR
   - History Calculation: 10 field(s)
      • Daily Average RPE
      • Daily Total RPE
      • Daily Average Duration
      • Daily Total Duration
      • Daily Average Load
      • Daily Total Load
      • Acute Load
      • Chronic Load
      • Total Acute Load
      • Total Chronic Load
   - History Text Calculation: 1 field(s)
      • All Session Types Today
   - Time Calculation: 1 field(s)
      • Time Entered
   - Text Calculation: 7 field(s)
      • RPE Session Load Filter
      • Day of the Week
      • Week
      • Month
      • Month with Number
      • Year
      • Date Reverse
   - Personal Details: 8 field(s)
      • First Name
      • Last Name
      • Full Name
      • Full Name Reverse
      • Sex
      • Date of Birth
      • Email
      • Phone Number
   - Age Calculation: 1 field(s)
      • Age
   - Date Calculation: 1 field(s)
      • Session Date
   - Linked Option: 1 field(s)
      • Sport
   - Linked Text: 5 field(s)
      • Position
      • Dominant Hand
      • Dominant Foot
      • Preferred Language
      • Season
   - Linked Value: 1 field(s)
      • Height
      ...


Set `field_details` within `FormOption() <form_option_ref_>`_ to  include detailed field
            information, such as options, scores, date ranges, etc. in the schema summary,
            increasing verbosity:

.. code-block:: python

   detailed_schema = get_form_schema(
       form_name="Allergies",
       url="https://example.smartabase.com/site",
       option=FormOption(
         interactive_mode = True,
         field_details = True
      )
   )
   print(detailed_schema.keys())

See `get_form_schema() <get_form_schema_ref_>`_ and `FormOption() <form_option_ref_>`_ for output options.


Set `include_instructions` within `FormOption() <form_option_ref_>`_ to include section
            and field instructions in the schema summary, useful for documentation:

.. code-block:: python

   instructions_schema = get_form_schema(
       form_name="Allergies",
       url="https://example.smartabase.com/site",
       option=FormOption(
         interactive_mode = True,
         include_instructions = True
      )
   )
   print(instructions_schema.keys())

See `get_form_schema() <get_form_schema_ref_>`_ and `FormOption() <form_option_ref_>`_ for output options.


Retrieve raw schema for custom processing:

.. code-block:: python

   raw_schema = get_form_schema(
       form_name="Allergies",
       url="https://example.smartabase.com/site",
       option=FormOption(raw_output=True)
   )
   print(raw_schema.keys())
   dict_keys(['form_id', 'name', 'type', 'sections', ...])

See `get_form_schema() <get_form_schema_ref_>`_ and `FormOption() <form_option_ref_>`_ for output options.

Error Handling
--------------

Form functions raise :class:`AMSError` with descriptive messages:

.. code-block:: python

   get_form_schema(form_name="Invalid Form", url="https://example.smartabase.com/site")

**Output**:

.. code-block:: text

   AMSError: Form 'Invalid Form' not found...


Best Practices
--------------

- **Verify Form Names**: Use `get_forms() <get_forms_ref_>`_ to confirm `form` name before
  calling `get_form_schema() <get_form_schema_ref_>`_.
- **Use Caching**: Enable ``option.cache=True`` for efficiency in repeated
  form queries.
- **Raw Output**: Set ``option.raw_output=True`` for `get_form_schema() <get_form_schema_ref_>`_
  when integrating with custom tools.
- **Detailed Summaries**: Use ``option.field_details=True`` to understand
  field options before data operations (e.g., `insert_event_data() <insert_event_data_ref_>`_).
- **Interactive Mode**: Enable ``option.interactive_mode=True`` for feedback
  during administrative tasks.

Next Steps
----------

- Explore :ref:`importing_data` for inserting and updating event data.
- Consult :ref:`reference` for detailed function and class documentation.
- Visit `GitHub <https://github.com/brandonyach/teamworksams>`_ for support.