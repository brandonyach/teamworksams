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
- Use ``raw_output=True`` with :func:`get_form_schema` to process the raw API
  response programmatically, bypassing the formatted string.
- Enable ``field_details=True`` and ``include_instructions=True`` to get
  verbose schema summaries, ideal for form documentation or integration
  planning.

See Also
--------

- :func:`teamworksams.form_main.get_forms`: Function for listing forms.
- :func:`teamworksams.form_main.get_form_schema`: Function for schema summaries.
- :ref:`vignettes/managing_forms`: Form management workflows.