.. _get_event_data_ref: ../reference/get_event_data.html
.. _event_filter_ref: ../reference/event_filter.html

.. _event_option:

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

- `get_event_data() <get_event_data_ref_>`_: Function using `EventOption`.
- `EventFilter() <event_filter_ref_>`_: For filtering event data.
- :ref:`exporting_data`: Event data workflows.