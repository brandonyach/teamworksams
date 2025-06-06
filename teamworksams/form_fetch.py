from typing import Optional, Dict, Tuple
from .utils import AMSClient, AMSError
from .form_option import FormOption


def _fetch_form_id_and_type(
    form_name: str,
    url: str,
    username: Optional[str],
    password: Optional[str],
    option: FormOption,
    client: AMSClient
) -> Tuple[str, str]:
    """Fetch the form ID and type for a given form name using get_forms.

    Args:
        form_name (str): The name of the form to look up.
        url (str): The AMS instance URL.
        username (Optional[str]): The username for authentication.
        password (Optional[str]): The password for authentication.
        option (FormOption): The FormOption object for configuration.
        client (AMSClient): The AMSClient instance.

    Returns:
        tuple[str, str]: A tuple of (form_id, form_type).

    Raises:
        AMSError: If the form is not found or multiple forms match the name.
    """
    # Silence interactive mode for get_forms
    silent_option = FormOption(
        interactive_mode=False,
        cache=option.cache,
        raw_output=option.raw_output,
        field_details=option.field_details,
        include_instructions=option.include_instructions
    )
    from .form_main import get_forms
    forms_df = get_forms(url, username, password, silent_option, client)
    if forms_df.empty:
        raise AMSError("No forms found in the AMS instance", function="get_form_schema")

    # Filter for the specified form name
    matching_forms = forms_df[forms_df["form_name"] == form_name]
    if matching_forms.empty:
        raise AMSError(f"Form '{form_name}' not found in the AMS instance", function="get_form_schema")
    if len(matching_forms) > 1:
        raise AMSError(f"Multiple forms found with the name '{form_name}'. Form names must be unique.", 
                       function="get_form_schema")

    form_id = matching_forms.iloc[0]["form_id"]
    form_type = matching_forms.iloc[0]["type"]
    return form_id, form_type



def _fetch_form_schema(
    form_id: str,
    form_type: str,
    client: AMSClient,
    option: FormOption
) -> Dict:
    """Fetch the raw schema data for a form from the AMS API.

    Args:
        form_id (str): The ID of the form.
        form_type (str): The type of the form (e.g., 'event', 'profile').
        client (AMSClient): The AMSClient instance.
        option (FormOption): The FormOption object for configuration.

    Returns:
        Dict: The raw API response containing the form schema.

    Raises:
        AMSError: If the API request fails or the response is invalid.
    """
    endpoint = f"forms/{form_type}/{form_id}"
    data = client._fetch(endpoint, method="GET", cache=option.cache, api_version="v3")
    
    if not isinstance(data, dict):
        AMSError(f"Invalid response from forms/{form_type}/{form_id} endpoint", 
                           function="get_form_summary", endpoint=endpoint)
    
    return data