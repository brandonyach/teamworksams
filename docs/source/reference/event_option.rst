EventOption
===========

.. autoclass:: teamworksams.export_option.EventOption
   :members:
   :undoc-members:
   :show-inheritance:

Additional Notes
----------------

- Set ``download_attachment=True`` to save event attachments, ensuring
  ``attachment_directory`` is a valid path to avoid errors.
- Use ``clean_names=True`` to standardize column names (e.g., 'Training Log' to
  'training_log') for consistency in analysis.
- Enable ``interactive_mode=True`` for :mod:`tqdm` progress bars and status messages,
  ideal for interactive environments like Jupyter notebooks.

See Also
--------

- :func:`teamworksams.export_main.get_event_data`: Function using `EventOption`.
- :class:`EventFilter`: For filtering event data.
- :ref:`vignettes/exporting_data`: Event data workflows.