"""
Helper functions for schema extraction and validation.
"""

import os
import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional
from jsonschema import validate as jsonschema_validate, ValidationError

from ..models.schema import Schema


def detect_file_type(file_path: str) -> str:
    """
    Detect the file type based on extension and content.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File type: "xml", "json", or "unknown"
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Check file extension
    _, ext = os.path.splitext(file_path.lower())
    
    if ext in ['.xml', '.xhtml', '.svg']:
        return "xml"
    elif ext in ['.json', '.js']:
        return "json"
    
    # Try to detect by content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(1024).strip()
        
        if content.startswith('<?xml') or content.startswith('<'):
            return "xml"
        elif content.startswith('{') or content.startswith('['):
            return "json"
    except Exception:
        pass
    
    return "unknown"


def validate_schema(file_path: str, schema: Schema) -> bool:
    """
    Validate a file against a schema.
    
    Args:
        file_path: Path to the file to validate
        schema: Schema object to validate against
        
    Returns:
        True if valid, False otherwise
    """
    try:
        file_type = detect_file_type(file_path)
        
        if file_type == "xml":
            return _validate_xml_against_schema(file_path, schema)
        elif file_type == "json":
            return _validate_json_against_schema(file_path, schema)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    except Exception as e:
        print(f"Validation error: {e}")
        return False


def _validate_xml_against_schema(file_path: str, schema: Schema) -> bool:
    """Validate XML file against schema."""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Basic validation - check if root element matches
        if schema.root_element and root.tag != schema.root_element.name:
            print(f"Root element mismatch: expected {schema.root_element.name}, got {root.tag}")
            return False
        
        # TODO: Implement more comprehensive XML validation
        return True
    
    except Exception as e:
        print(f"XML validation error: {e}")
        return False


def _validate_json_against_schema(file_path: str, schema: Schema) -> bool:
    """Validate JSON file against schema."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert schema to JSON Schema format
        json_schema = schema.to_json_schema()
        
        # Validate using jsonschema library
        jsonschema_validate(instance=data, schema=json_schema)
        return True
    
    except ValidationError as e:
        print(f"JSON validation error: {e}")
        return False
    except Exception as e:
        print(f"JSON validation error: {e}")
        return False


def save_schema(schema: Schema, output_path: str, format: str = "json") -> None:
    """
    Save schema to a file.
    
    Args:
        schema: Schema object to save
        output_path: Path to save the schema
        format: Output format ("json", "xsd", or "dict")
    """
    # Create directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    if format.lower() == "json":
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(schema.to_dict(), f, indent=2, ensure_ascii=False)
    
    elif format.lower() == "xsd":
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(schema.to_xsd())
    
    elif format.lower() == "dict":
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(schema.to_dict(), f, indent=2, ensure_ascii=False)
    
    else:
        raise ValueError(f"Unsupported format: {format}")


def load_schema(file_path: str) -> Schema:
    """
    Load schema from a file.
    
    Args:
        file_path: Path to the schema file
        
    Returns:
        Schema object
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Schema file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return Schema.model_validate(data)


def format_schema_output(schema: Schema, format: str = "pretty") -> str:
    """
    Format schema for display.
    
    Args:
        schema: Schema object to format
        format: Output format ("pretty", "json", "xsd")
        
    Returns:
        Formatted schema string
    """
    if format == "json":
        return json.dumps(schema.to_dict(), indent=2, ensure_ascii=False)
    
    elif format == "xsd":
        return schema.to_xsd()
    
    elif format == "pretty":
        return _format_schema_pretty(schema)
    
    else:
        raise ValueError(f"Unsupported format: {format}")


def _format_schema_pretty(schema: Schema) -> str:
    """Format schema in a human-readable format."""
    lines = []
    lines.append(f"Schema: {schema.name}")
    lines.append(f"Type: {schema.file_type}")
    lines.append(f"Version: {schema.version}")
    lines.append(f"Created: {schema.created_at}")
    lines.append(f"Total Elements: {schema.total_elements}")
    lines.append(f"Total Attributes: {schema.total_attributes}")
    lines.append(f"Max Depth: {schema.max_depth}")
    lines.append("")
    
    if schema.description:
        lines.append(f"Description: {schema.description}")
        lines.append("")
    
    if schema.root_element:
        lines.append("Root Element:")
        lines.extend(_format_element_pretty(schema.root_element, indent=2))
    
    return "\n".join(lines)


def _format_element_pretty(element: Any, indent: int = 0) -> list:
    """Format a schema element in a human-readable format."""
    lines = []
    spaces = " " * indent
    
    lines.append(f"{spaces}Name: {element.name}")
    lines.append(f"{spaces}Type: {element.data_type.value}")
    lines.append(f"{spaces}Required: {element.required}")
    
    if element.description:
        lines.append(f"{spaces}Description: {element.description}")
    
    if element.examples:
        lines.append(f"{spaces}Examples: {element.examples}")
    
    if element.attributes:
        lines.append(f"{spaces}Attributes:")
        for attr_name, attr in element.attributes.items():
            lines.append(f"{spaces}  {attr_name}: {attr.data_type.value} (required: {attr.required})")
    
    if element.properties:
        lines.append(f"{spaces}Properties:")
        for prop_name, prop in element.properties.items():
            lines.append(f"{spaces}  {prop_name}:")
            lines.extend(_format_element_pretty(prop, indent + 4))
    
    if element.array_type:
        lines.append(f"{spaces}Array Type:")
        lines.extend(_format_element_pretty(element.array_type, indent + 2))
    
    return lines
