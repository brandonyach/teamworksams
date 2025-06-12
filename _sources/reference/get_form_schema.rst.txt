get_form_schema
===============

.. autofunction:: teamworksams.form_main.get_form_schema

Additional Notes
----------------

- The formatted string output is ideal for console display in Jupyter
  notebooks; use ``option.raw_output=True`` for programmatic access to the
  raw schema dictionary.
- Ensure ``form_name`` matches an existing AMS form exactly
  (case-sensitive); invalid names raise :class:`AMSError`.
- Use ``option.field_details=True`` to include field options (e.g., dropdown
  values), crucial for understanding form requirements before data operations.

See Also
--------

- :class:`FormOption`: Configuration options for schema retrieval.
- :func:`get_forms`: For listing accessible forms.
- :ref:`vignettes/managing_forms`: Form schema workflows.