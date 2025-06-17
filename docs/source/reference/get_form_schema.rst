.. _form_option_ref: ../reference/form_option.html
.. _get_forms_ref: ../reference/get_forms.html

.. _get_form_schema:

get_form_schema
===============

.. autofunction:: teamworksams.form_main.get_form_schema

Additional Notes
----------------

- The formatted string output is ideal for console display in Jupyter
  notebooks; use ``option.raw_output=True`` for programmatic access to the
  raw schema dictionary.
- Ensure ``form`` matches an existing AMS form exactly
  (case-sensitive); invalid names raise :class:`AMSError`.
- Use ``option.field_details=True`` to include field options (e.g., dropdown
  values), crucial for understanding form requirements before data operations.

See Also
--------

- `FormOption() <form_option_ref_>`_: Configuration options for schema retrieval.
- `get_forms() <get_forms_ref_>`_: For listing accessible forms.
- :ref:`managing_forms`: Form schema workflows.