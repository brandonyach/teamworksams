class FormOption:
    """Options for configuring form schema export and summary functions.

    Customizes the behavior of :func:`get_forms` and
    :func:`get_form_schema`, controlling interactive feedback,
    caching, output format, and schema detail level. These options optimize form metadata
    retrieval for administrative tasks like auditing or integration. See
    :ref:`managing_forms` for form management workflows.

    Args:
        interactive_mode (bool): If True, prints status messages during execution,
            such as "Retrieved 5 forms" or schema details, ideal for interactive
            environments like Jupyter notebooks. Set to False for silent execution.
            Defaults to False.
        cache (bool): If True, reuses cached API responses via the :class:`AMSClient`,
            reducing API calls for repeated form queries. Set to False for fresh data.
            Defaults to True.
        raw_output (bool): If True, :func:`get_form_schema` returns the raw API
            response as a dictionary instead of a formatted string, useful for custom
            processing. Defaults to False.
        field_details (bool): If True, :func:`get_form_schema` includes detailed field
            information (e.g., options, scores, date selection) in the schema summary,
            increasing verbosity. Defaults to False.
        include_instructions (bool): If True, :func:`get_form_schema` includes section
            and field instructions in the schema summary, useful for documentation.
            Defaults to False.

    Attributes:
        interactive_mode (bool): Indicates whether interactive mode is enabled.
        cache (bool): Indicates whether caching is enabled.
        raw_output (bool): Indicates whether raw output is enabled.
        field_details (bool): Indicates whether field details are included.
        include_instructions (bool): Indicates whether instructions are included.

    Examples:
        >>> from teamworksams import get_form_schema, FormOption
        >>> option = FormOption(
        ...     interactive_mode = True,
        ...     cache = True,
        ...     raw_output = False,
        ...     field_details = True,
        ...     include_instructions = True
        ... )
        >>> summary = get_form_schema(
        ...     form_name = "Allergies",
        ...     url = "https://example.smartabase.com/site",
        ...     option = option
        ... )
        ℹ Fetching summary for form 'Allergies'...
        ✔ Retrieved summary for form 'Allergies'.
        Form Schema Summary
        ==================
        Form Name: Allergies
        ...
    """
    def __init__(
            self, 
            interactive_mode: bool = True, 
            cache: bool = True,
            raw_output: bool = False,
            field_details: bool = False,
            include_instructions: bool = False
        ):
        self.interactive_mode = interactive_mode
        self.cache = cache
        self.raw_output = raw_output
        self.field_details = field_details
        self.include_instructions = include_instructions