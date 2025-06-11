delete_event_data
=================

.. autofunction:: teamworksams.delete_main.delete_event_data

Additional Notes
----------------

- Obtain valid `event_id` values using :func:`get_event_data` to avoid
  :class:`AMSError` for non-existent events.
- The confirmation prompt in ``option.interactive_mode=True`` ensures safe
  deletion, critical for administrative tasks.
- The returned string (e.g., "SUCCESS: Deleted 134273") can be parsed for
  automation or logged for auditing.

See Also
--------

- :class:`DeleteEventOption`: Configuration options for deletion.
- :func:`delete_multiple_events`: For deleting multiple events.
- :func:`get_event_data`: For retrieving event IDs.
- :ref:`vignettes/deleting_data`: Single event deletion workflows.