from typing import Dict, List, Counter, DefaultDict
from pandas import DataFrame


def _parse_forms_response(data: Dict) -> List[Dict]:
    """Parse the forms API response into a list of form dictionaries.

    Extracts form metadata from the API response, adding a 'type' field to each form.

    Args:
        data (Dict): The raw API response containing form data.

    Returns:
        List[Dict]: A list of dictionaries, each representing a form with its metadata.
    """
    if not isinstance(data, dict):
        return []
    
    forms = []
    for form_type, form_list in data.items():
        if form_list is not None and isinstance(form_list, (list, tuple)):
            for form in form_list:
                form["type"] = form_type
                forms.append(form)
    return forms



def _create_forms_df(forms: List[Dict]) -> DataFrame:
    """Create a DataFrame from a list of form dictionaries.

    Converts a list of form dictionaries into a DataFrame with standardized columns.

    Args:
        forms (List[Dict]): The list of form dictionaries.

    Returns:
        DataFrame: A DataFrame with columns 'form_id', 'form_name', 'type', etc.
    """
    if not forms:
        return DataFrame()
    
    forms_df = DataFrame(forms)
    available_cols = [col for col in ["id", "name", "type", "mainCategory", "isReadOnly", "groupEntryEnabled"] 
                     if col in forms_df.columns]
    forms_df = forms_df[available_cols]
    forms_df = forms_df.rename(columns={"id": "form_id", "name": "form_name"})
    return forms_df



def _find_form_items_and_sections(node: Dict, items: List[Dict], sections: List[Dict]) -> None:
    """Recursively traverse the form schema to collect all FormItem and FormFieldSet entries.

    Args:
        node (Dict): The current node in the schema (e.g., Form, FormPage, FormFieldSet, FormItem).
        items (List[Dict]): The list to append FormItem entries to.
        sections (List[Dict]): The list to append FormFieldSet entries to.
    """
    if not isinstance(node, dict):
        return
    
    # Collect FormFieldSet (sections) and FormItem entries
    node_type = node.get("type")
    if node_type == "FormFieldSet":
        sections.append(node)
    elif node_type == "FormItem":
        items.append(node)
    
    # Recursively process children
    children = node.get("children", [])
    for child in children:
        _find_form_items_and_sections(child, items, sections)

def _parse_form_schema(data: Dict) -> Dict[str, any]:
    """Parse the form schema response to extract requested information.

    Extracts the form name, form ID, sections, required fields, linked fields, defaults to last known
    value fields, and form item type details from the schema.

    Args:
        data (Dict): The raw API response from the forms/:form_type/:form_id endpoint.

    Returns:
        Dict[str, any]: A dictionary containing:
            - form_name: The name of the form.
            - form_id: The ID of the form.
            - sections_count: The number of sections (FormFieldSet entries).
            - sections: The list of section names and instructions.
            - required_fields_count: The number of required fields.
            - required_fields: The list of required field names and instructions.
            - defaults_to_last_count: The number of fields that default to the last known value.
            - defaults_to_last_fields: The list of field names that default to the last known value and instructions.
            - linked_fields_count: The number of linked fields.
            - linked_fields: The list of linked field names and instructions.
            - form_item_types_count: The number of unique form item types.
            - form_item_types_counts: A dictionary mapping each form item type to its count.
            - form_item_type_fields: A dictionary mapping each form item type to the list of field names and details.
    """
    if not isinstance(data, dict):
        return {
            "form_name": None,
            "form_id": None,
            "sections_count": 0,
            "sections": [],
            "required_fields_count": 0,
            "required_fields": [],
            "defaults_to_last_count": 0,
            "defaults_to_last_fields": [],
            "linked_fields_count": 0,
            "linked_fields": [],
            "form_item_types_count": 0,
            "form_item_types_counts": {},
            "form_item_type_fields": {}
        }
    
    # Extract top-level fields
    form_name = data.get("name")
    form_id = data.get("id")
    
    # Find all FormFieldSet (sections) and FormItem entries
    sections = []
    form_items = []
    _find_form_items_and_sections(data, form_items, sections)
    
    # Process sections
    sections_info = [
        {"name": section.get("name", "Unnamed Section"), "instructions": section.get("instructions", "")}
        for section in sections
    ]
    sections_count = len(sections_info)
    
    # Extract required fields with instructions
    required_fields = [
        {"name": item["name"], "instructions": item.get("instructions", "")}
        for item in form_items if item.get("required", False)
    ]
    required_fields_count = len(required_fields)
    
    # Extract fields that default to the last known value with instructions
    defaults_to_last_fields = [
        {"name": item["name"], "instructions": item.get("instructions", "")}
        for item in form_items if item.get("defaultsToLastKnownValue", False)
    ]
    defaults_to_last_count = len(defaults_to_last_fields)
    
    # Extract linked fields with instructions
    linked_types = {"Linked Text", "Linked Option", "Linked Value", "Linked Date", "Linked Time"}
    linked_fields = [
        {"name": item["name"], "instructions": item.get("instructions", "")}
        for item in form_items if item.get("formItemType", "") in linked_types
    ]
    linked_fields_count = len(linked_fields)
    
    # Extract form item types, their counts, and field details
    form_item_types_list = [item.get("formItemType", "Unknown") for item in form_items]
    form_item_types_counts = dict(Counter(form_item_types_list))
    form_item_types_count = len(form_item_types_counts)
    
    # Map each formItemType to the list of field names and details
    form_item_type_fields = DefaultDict(list)
    for item in form_items:
        item_type = item.get("formItemType", "Unknown")
        field_info = {
            "name": item["name"],
            "instructions": item.get("instructions", ""),
            "options": item.get("options", []),
            "scores": item.get("scores", []),
            "dateSelection": item.get("dateSelection")
        }
        form_item_type_fields[item_type].append(field_info)
    form_item_type_fields = dict(form_item_type_fields)
    
    return {
        "form_name": form_name,
        "form_id": form_id,
        "sections_count": sections_count,
        "sections": sections_info,
        "required_fields_count": required_fields_count,
        "required_fields": required_fields,
        "defaults_to_last_count": defaults_to_last_count,
        "defaults_to_last_fields": defaults_to_last_fields,
        "linked_fields_count": linked_fields_count,
        "linked_fields": linked_fields,
        "form_item_types_count": form_item_types_count,
        "form_item_types_counts": form_item_types_counts,
        "form_item_type_fields": form_item_type_fields
    }
    
    

def _format_form_summary(schema_info: Dict, include_instructions: bool, field_details: bool) -> str:
    """Format the schema information into a human-readable text string.

    Args:
        schema_info (Dict): The parsed schema information.
        include_instructions (bool): Whether to include instructions in the output.
        field_details (bool): Whether to include field details (options, scores, dateSelection) in the output.

    Returns:
        str: A formatted text string summarizing the form schema.
    """
    output = []
    
    # Header
    output.append("=====================================")
    output.append(f"Form Schema Summary: {schema_info['form_name']}")
    output.append("=====================================")
    output.append("")
    
    # Form Details
    output.append("Form Details")
    output.append("------------")
    output.append(f"- Form Name: {schema_info['form_name']}")
    output.append(f"- Form ID: {schema_info['form_id']}")
    output.append("")
    
    # Sections
    output.append("Sections")
    output.append("--------")
    output.append(f"- Total: {schema_info['sections_count']}")
    if schema_info['sections']:
        for section in schema_info['sections']:
            section_name = section['name'] if section['name'] else "Unnamed Section"
            output.append(f"  • {section_name}")
            if include_instructions and section['instructions']:
                output.append(f"    ℹ Instructions: {section['instructions']}")
    else:
        output.append("- No sections found.")
    output.append("")
    
    # Required Fields
    output.append("Required Fields")
    output.append("---------------")
    output.append(f"- Total: {schema_info['required_fields_count']}")
    if schema_info['required_fields']:
        for field in schema_info['required_fields']:
            output.append(f"  • {field['name']}")
            if include_instructions and field['instructions']:
                output.append(f"    ℹ Instructions: {field['instructions']}")
    else:
        output.append("- No required fields found.")
    output.append("")
    
    # Defaults to Last Known Value
    output.append("Defaults to Last Known Value")
    output.append("----------------------------")
    output.append(f"- Total: {schema_info['defaults_to_last_count']}")
    if schema_info['defaults_to_last_fields']:
        for field in schema_info['defaults_to_last_fields']:
            output.append(f"  • {field['name']}")
            if include_instructions and field['instructions']:
                output.append(f"    Instructions: {field['instructions']}")
    else:
        output.append("- No fields default to the last known value.")
    output.append("")
    
    # Linked Fields
    output.append("Linked Fields")
    output.append("-------------")
    output.append(f"- Total: {schema_info['linked_fields_count']}")
    if schema_info['linked_fields']:
        for field in schema_info['linked_fields']:
            output.append(f"  • {field['name']}")
            if include_instructions and field['instructions']:
                output.append(f"    ℹ Instructions: {field['instructions']}")
    else:
        output.append("- No linked fields found.")
    output.append("")
    
    # Form Item Types
    output.append("Form Item Types")
    output.append("---------------")
    output.append(f"- Total Unique Types: {schema_info['form_item_types_count']}")
    if schema_info['form_item_types_counts']:
        for item_type, count in schema_info['form_item_types_counts'].items():
            output.append(f"- {item_type}: {count} field(s)")
            for field in schema_info['form_item_type_fields'][item_type]:
                output.append(f"    • {field['name']}")
                if include_instructions and field['instructions']:
                    output.append(f"      ℹ Instructions: {field['instructions']}")
                if field_details:
                    # Include options if non-empty
                    if field['options']:
                        output.append(f"      > Options: {', '.join(map(str, field['options']))}")
                    # Include scores if non-empty
                    if field['scores']:
                        output.append(f"      > Scores: {', '.join(map(str, field['scores']))}")
                    # Include dateSelection if not None
                    if field['dateSelection'] is not None:
                        output.append(f"      > Date Selection: {field['dateSelection']}")
    else:
        output.append("- No form item types found.")
    output.append("")
    
    # Footer
    output.append("=====================================")
    output.append("End of Form Schema Summary")
    output.append("=====================================")
    
    return "\n".join(output)