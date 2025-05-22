class FormOption:
    """Options for configuring form schema export and summary functions.

    Defines customization options for the `get_forms` and `get_form_schema` functions,
    controlling aspects such as caching API responses, enabling interactive feedback,
    specifying output format, and including additional details in the schema summary.
    These options allow users to tailor the retrieval process, optimizing performance
    and output verbosity.

    Args:
        interactive_mode (bool): Whether to print status messages during execution, such
            as the number of forms retrieved or schema details. Defaults to False.
        cache (bool): Whether to cache API responses to improve performance for repeated
            requests. Defaults to True.
        raw_output (bool): Whether to return the raw API response as a dictionary instead
            of a formatted summary (for `get_form_schema`). Defaults to False.
        field_details (bool): Whether to include detailed field information (e.g., options,
            scores, date selection) in the schema summary for `get_form_schema`. Defaults
            to False.
        include_instructions (bool): Whether to include section and field instructions in
            the schema summary for `get_form_schema`. Defaults to False.

    Attributes:
        interactive_mode (bool): Indicates whether interactive mode is enabled.
        cache (bool): Indicates whether caching is enabled.
        raw_output (bool): Indicates whether raw output is enabled.
        field_details (bool): Indicates whether field details are included.
        include_instructions (bool): Indicates whether instructions are included.

    Examples:
        >>> from teamworksams import FormOption
        >>> option = FormOption(
        ...     interactive_mode = True,
        ...     cache = True,
        ...     raw_output = False,
        ...     field_details = True,
        ...     include_instructions = True
        ... )
    """
    def __init__(
            self, 
            interactive_mode: bool = False, 
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