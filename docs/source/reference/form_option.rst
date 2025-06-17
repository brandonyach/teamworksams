.. _get_forms_ref: ../reference/get_forms.html
.. _get_form_schema_ref: ../reference/get_form_schema.html

.. _form_option:

FormOption
==========

.. autoclass:: teamworksams.form_option.FormOption
   :members:
   :undoc-members:
   :show-inheritance:

Additional Notes
----------------

- Set ``interactive_mode=True`` for status messages like "Retrieved 5 forms,"
  useful for administrative tasks in interactive environments.
- Use ``raw_output=True`` with `get_forms() <get_forms_ref_>`_ to process the raw API
  response programmatically, bypassing the formatted string.
- Enable ``field_details=True`` and ``include_instructions=True`` to get
  verbose schema summaries, ideal for form documentation or integration
  planning.

See Also
--------

- `get_forms() <get_forms_ref_>`_ Function for listing forms.
- `get_form_schema() <get_form_schema_ref_>`_ Function for schema summaries.
- :ref:`managing_forms`: Form management workflows.