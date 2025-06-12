DeleteEventOption
=================

.. autoclass:: teamworksams.delete_option.DeleteEventOption
   :members:
   :undoc-members:
   :show-inheritance:

Additional Notes
----------------

- Enable ``interactive_mode=True`` to prompt for confirmation before deletion,
  preventing accidental data loss, and to display status messages like
  "SUCCESS: Deleted 134273".
- Set ``interactive_mode=False`` for automated scripts where silent execution
  is preferred, but ensure robust error handling with :class:`AMSError`.
- Use with :func:`delete_event_data` or :func:`delete_multiple_events` for
  safe event deletion.

See Also
--------

- :func:`teamworksams.delete_main.delete_event_data`: Function for single event deletion.
- :func:`teamworksams.delete_main.delete_multiple_events`: Function for batch event deletion.
- :ref:`vignettes/deleting_data`: Event deletion workflows.