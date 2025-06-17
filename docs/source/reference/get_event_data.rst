.. _event_filter_ref: ../reference/event_filter.html
.. _event_option_ref: ../reference/event_option.html

.. _get_event_data:

get_event_data
==============

.. autofunction:: teamworksams.export_main.get_event_data

Additional Notes
----------------

- The ``form`` parameter must match an existing AMS Event Form exactly (case-sensitive).
- Use ``option.download_attachment=True`` to fetch attachments, storing them in
  ``option.attachment_directory`` (defaults to current directory if unset).
- The ``filter`` parameter, when combined with `EventFilter() <event_filter_ref_>`_, reduces API load by
  limiting events to specific users or field values (e.g., 'intensity=High').

See Also
--------

- `EventFilter() <event_filter_ref_>`_: For filtering event data.
- `EventOption() <event_option_ref_>`_: Configuration options for event retrieval.
- :ref:`exporting_data`: Event data export workflows.