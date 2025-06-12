delete_multiple_events
======================

.. autofunction:: teamworksams.delete_main.delete_multiple_events

Additional Notes
----------------

- Use :func:`get_event_data` to collect `event_ids` for batch deletion,
  ensuring all IDs are valid to avoid :class:`AMSError`.
- Batch deletion is more efficient than multiple calls to
  :func:`delete_event_data`, but confirmation prompts remain critical for
  safety.
- The returned string (e.g., "SUCCESS: Deleted 3 events") indicates the
  overall result; individual failures may require API-level debugging.

See Also
--------

- :class:`DeleteEventOption`: Configuration options for deletion.
- :func:`delete_event_data`: For single event deletion.
- :func:`get_event_data`: For retrieving event IDs.
- :ref:`vignettes/deleting_data`: Batch event deletion workflows.