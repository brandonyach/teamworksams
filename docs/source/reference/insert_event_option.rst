InsertEventOption
=================

.. autoclass:: teamworksams.import_option.InsertEventOption
   :members:
   :undoc-members:
   :show-inheritance:

Additional Notes
----------------

- The ``id_col`` must be a valid column in the input :class:`pandas.DataFrame`
  (e.g., 'username', 'user_id') and one of 'user_id', 'about', 'username', or
  'email'; invalid values raise :class:`ValueError`.
- Specify ``table_fields`` for AMS forms with table data (e.g.,
  ['session_details']), ensuring column names match exactly to avoid
  :class:`AMSError`.
- Enable ``interactive_mode=True`` for feedback like "Inserted 2 events," ideal
  for interactive environments like Jupyter notebooks.

See Also
--------

- :func:`teamworksams.import_main.insert_event_data`: Function using `InsertEventOption`.
- :ref:`vignettes/importing_data`: Event insertion workflows.