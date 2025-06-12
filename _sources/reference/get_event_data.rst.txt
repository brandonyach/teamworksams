get_event_data
==============

.. autofunction:: teamworksams.export_main.get_event_data

Additional Notes
----------------

- The ``form`` parameter must match an existing AMS Event Form exactly (case-sensitive).
- Use ``option.download_attachment=True`` to fetch attachments, storing them in
  ``option.attachment_directory`` (defaults to current directory if unset).
- The ``filter`` parameter, when combined with :class:`EventFilter`, reduces API load by
  limiting events to specific users or field values (e.g., 'intensity=High').

See Also
--------

- :class:`EventFilter`: For filtering event data.
- :class:`EventOption`: Configuration options for event retrieval.
- :ref:`vignettes/exporting_data`: Event data export workflows.