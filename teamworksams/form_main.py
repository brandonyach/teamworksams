from pandas import DataFrame
from typing import Dict, Union, Optional
from .form_option import FormOption
from .utils import AMSClient, AMSError, get_client
from .form_fetch import _fetch_form_id_and_type, _fetch_form_schema
from .form_print import _print_forms_status
from .form_process import _parse_forms_response, _parse_form_schema, _create_forms_df, _format_form_summary


def get_forms(
    url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    option: Optional[FormOption] = None,
    client: Optional[AMSClient] = None
) -> DataFrame:
    """Fetch a list of forms accessible to the user from an AMS instance.

    Retrieves metadata for all forms accessible to the authenticated user, returning a
    :class:`pandas.DataFrame` with columns like 'form_id', 'form_name', and 'type' (e.g.,
    event, profile, database). Ideal for auditing or selecting forms for further operations.
    Supports interactive feedback and caching. See :ref:`vignettes/managing_forms` for
    form management workflows.

    Args:
        url (str): AMS instance URL (e.g., 'https://example.smartabase.com/site'). Must
            include a valid site name.
        username (Optional[str]): Username for authentication. If None, uses
            :envvar:`AMS_USERNAME` or :class:`keyring` credentials. Defaults to None.
        password (Optional[str]): Password for authentication. If None, uses
            :envvar:`AMS_PASSWORD` or :class:`keyring` credentials. Defaults to None.
        option (:class:`FormOption`, optional): Configuration options, including
            `interactive_mode` for status messages (e.g., "Retrieved 5 forms"), `cache`
            to reuse API responses, `raw_output`, `field_details`, and
            `include_instructions` (used in other form functions). Defaults to None
            (uses default :class:`FormOption`).
        client (:class:`AMSClient`, optional): Pre-authenticated client from
            :func:`get_client`. If None, a new client is created. Defaults to None.

    Returns:
        :class:`pandas.DataFrame`: Form metadata with columns like 'form_id',
            'form_name', 'type', and other attributes (e.g., 'application_id'). Returns
            an empty DataFrame if no forms are accessible.

    Raises:
        :class:`AMSError`: If authentication fails, the API request returns an invalid response,
            or no accessible forms are found.

    Examples:
        >>> from teamworksams import get_forms, FormOption
        >>> df = get_forms(
        ...     url = "https://example.smartabase.com/site",
        ...     username = "user",
        ...     password = "pass",
        ...     option = FormOption(interactive_mode = True)
        ... )
        ℹ Requesting list of accessible forms...
        ✔ Retrieved 5 accessible forms.
        >>> print(df)
           form_id    form_name     type
        0     2937    Allergies  database
        1     1234  Training Log    event
        2     5678  Athlete Profile profile
    """
    option = option or FormOption()
    client = client or get_client(url, username, password, cache=option.cache, interactive_mode=option.interactive_mode)
    
    if option.interactive_mode:
        print("ℹ Requesting list of accessible forms...")
    
    data = client._fetch("forms/summaries", method="GET", cache=option.cache, api_version="v3")
    if not isinstance(data, dict) or all(data.get(key) is None for key in ["event", "linkedOnlyEvent", "linkedOnlyProfile"]):
        AMSError("No valid forms data returned from server", 
                           function="get_forms", endpoint="forms/summaries")
    
    forms = _parse_forms_response(data)
    if not forms:
        AMSError("No accessible forms found", function="get_forms", endpoint="forms/summaries")
    
    forms_df = _create_forms_df(forms)
    
    _print_forms_status(forms_df, option)
    
    return forms_df




def get_form_schema(
    form_name: str,
    url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    option: Optional[FormOption] = None,
    client: Optional[AMSClient] = None
) -> Union[str, Dict]:
    """Fetch and summarize the schema of a specific form from an AMS instance.

    Retrieves the schema for a specified AMS form, detailing sections, required fields,
    default-to-last-value fields, linked fields, and item types. Returns a formatted
    string summary for console output (ideal for Jupyter notebooks) or the raw API
    response as a dictionary if `option.raw_output` is True. Supports interactive
    feedback and detailed output options. See :ref:`vignettes/managing_forms` for form
    management workflows.

    Args:
        form_name (str): Name of the form (e.g., 'Allergies'). Must be a non-empty
            string and correspond to a valid form.
        url (str): AMS instance URL (e.g., 'https://example.smartabase.com/site'). Must
            include a valid site name.
        username (Optional[str]): Username for authentication. If None, uses
            :envvar:`AMS_USERNAME` or :class:`keyring` credentials. Defaults to None.
        password (Optional[str]): Password for authentication. If None, uses
            :envvar:`AMS_PASSWORD` or :class:`keyring` credentials. Defaults to None.
        option (:class:`FormOption`, optional): Configuration options, including
            `interactive_mode` for status messages, `cache` to reuse API responses,
            `raw_output` for raw API data, `field_details` for field options/scores,
            and `include_instructions` for section/field instructions. Defaults to None
            (uses default :class:`FormOption`).
        client (:class:`AMSClient`, optional): Pre-authenticated client from
            :func:`get_client`. If None, a new client is created. Defaults to None.

    Returns:
        Union[str, Dict]: If `option.raw_output` is True, returns the raw API response as a
            dictionary containing the form schema. Otherwise, returns a formatted text string
            summarizing the form schema, including:
            - Form details (name, ID, type).
            - Sections (count, names).
            - Required fields (count, names).
            - Fields that default to the last known value (count, names).
            - Linked fields (count, names).
            - Form item types (count of unique types, count per type, field names per type).
            - Optionally, field instructions and details (options, scores, date selection) if
              enabled in `option`.

    Raises:
        :class:`AMSError`: If the form_name is empty, the form is not found, authentication fails,
            or the API request returns an invalid response.

    Examples:
        >>> from teamworksams import get_form_schema
        >>> from teamworksams import FormOption
        >>> summary = get_form_schema(
        ...     form_name = "Allergies",
        ...     url = "https://example.smartabase.com/site",
        ...     username = "user",
        ...     password = "pass",
        ...     option = FormOption(interactive_mode = True, field_details = True)
        ... )
        ℹ Fetching summary for form 'Allergies' (ID: 2937, Type: database)...
        ✔ Retrieved summary for form 'Allergies'.
        Form Schema Summary
        ==================
        Form Name: Allergies
        Form ID: 2937
        Form Type: database
        Sections: 2
        - Section 1: General
        - Section 2: Details
        Required Fields: 1
        - Allergy
        ...
    """
    option = option or FormOption()
    client = client or get_client(url, username, password, cache=option.cache, interactive_mode=option.interactive_mode)
    
    if not form_name:
        AMSError("Form name is required", function="get_form_summary")
    
    # Step 1: Fetch the form ID and type
    form_id, form_type = _fetch_form_id_and_type(form_name, url, username, password, option, client)
    
    # Step 2: Fetch the form schema
    if option.interactive_mode:
        print(f"ℹ Fetching summary for form '{form_name}' (ID: {form_id}, Type: {form_type})...")
    
    schema_data = _fetch_form_schema(form_id, form_type, client, option)
    
    # Step 3: If raw_output is True, return the raw schema data
    if option.raw_output:
        return schema_data
    
    # Step 4: Parse the schema
    schema_info = _parse_form_schema(schema_data)
    
    # Step 5: Format and print the summary
    if option.interactive_mode:
        print(f"✔ Retrieved summary for form '{form_name}'.")
    
    formatted_output = _format_form_summary(
        schema_info,
        include_instructions=option.include_instructions,
        field_details=option.field_details
    )
    print(formatted_output)
    
    return formatted_output