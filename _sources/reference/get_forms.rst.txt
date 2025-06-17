.. _form_option_ref: ../reference/form_option.html
.. _get_form_schema_ref: ../reference/get_form_schema.html
.. _get_event_data_ref: ../reference/get_event_data.html

.. _get_forms:

get_forms
=========

.. autofunction:: teamworksams.form_main.get_forms

Additional Notes
----------------

- The returned :class:`pandas.DataFrame` includes columns like 'form_id',
  'form_name', and 'type'; use it to filter forms for specific operations
  (e.g., event forms for `get_event_data() <get_event_data_ref_>`_).
- Enable ``option.interactive_mode=True`` to confirm the number of forms
  retrieved, helpful for auditing large AMS instances.
- Use ``option.cache=True`` to optimize performance when repeatedly listing
  forms in a session.

See Also
--------

- `FormOption() <form_option_ref_>`_: Configuration options for form retrieval.
- `get_form_schema() <get_form_schema_ref_>`_: For detailed schema of a specific form.
- :ref:`managing_forms`: Form listing workflows.