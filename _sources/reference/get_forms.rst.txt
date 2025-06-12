get_forms
=========

.. autofunction:: teamworksams.form_main.get_forms

Additional Notes
----------------

- The returned :class:`pandas.DataFrame` includes columns like 'form_id',
  'form_name', and 'type'; use it to filter forms for specific operations
  (e.g., event forms for :func:`get_event_data`).
- Enable ``option.interactive_mode=True`` to confirm the number of forms
  retrieved, helpful for auditing large AMS instances.
- Use ``option.cache=True`` to optimize performance when repeatedly listing
  forms in a session.

See Also
--------

- :class:`FormOption`: Configuration options for form retrieval.
- :func:`get_form_schema`: For detailed schema of a specific form.
- :ref:`vignettes/managing_forms`: Form listing workflows.