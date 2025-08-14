"""
Schema data models for representing extracted schemas.
"""

from typing import Dict, List, Optional, Union, Any
from enum import Enum
from pydantic import BaseModel, Field


class DataType(str, Enum):
    """Data types for schema elements."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    NULL = "null"
    DATE = "date"
    DATETIME = "datetime"
    UNKNOWN = "unknown"


class SchemaAttribute(BaseModel):
    """Represents an attribute in an XML element or JSON object property."""
    name: str
    data_type: DataType = DataType.STRING
    required: bool = False
    default_value: Optional[str] = None
    description: Optional[str] = None


class SchemaElement(BaseModel):
    """Represents an element in the schema."""
    name: str
    data_type: DataType = DataType.OBJECT
    required: bool = False
    description: Optional[str] = None
    
    # For objects
    properties: Dict[str, "SchemaElement"] = Field(default_factory=dict)
    attributes: Dict[str, SchemaAttribute] = Field(default_factory=dict)
    
    # For arrays
    array_type: Optional["SchemaElement"] = None
    
    # For primitive types
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    
    # Metadata
    occurrences: int = 1
    examples: List[Any] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True


class Schema(BaseModel):
    """Main schema representation."""
    name: str
    file_type: str  # "xml" or "json"
    root_element: Optional[SchemaElement] = None
    elements: Dict[str, SchemaElement] = Field(default_factory=dict)
    attributes: Dict[str, SchemaAttribute] = Field(default_factory=dict)
    
    # Metadata
    version: str = "1.0"
    description: Optional[str] = None
    created_at: Optional[str] = None
    
    # Statistics
    total_elements: int = 0
    total_attributes: int = 0
    max_depth: int = 0
    
    class Config:
        arbitrary_types_allowed = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert schema to dictionary representation."""
        return self.model_dump()
    
    def to_json_schema(self) -> Dict[str, Any]:
        """Convert to JSON Schema format."""
        if not self.root_element:
            return {}
        
        return self._element_to_json_schema(self.root_element)
    
    def _element_to_json_schema(self, element: SchemaElement) -> Dict[str, Any]:
        """Convert a schema element to JSON Schema format."""
        # Map our data types to JSON Schema types
        type_mapping = {
            DataType.STRING: "string",
            DataType.INTEGER: "integer",
            DataType.FLOAT: "number",
            DataType.BOOLEAN: "boolean",
            DataType.OBJECT: "object",
            DataType.ARRAY: "array",
            DataType.NULL: "null",
            DataType.DATE: "string",
            DataType.DATETIME: "string",
            DataType.UNKNOWN: "string"
        }
        
        schema = {
            "type": type_mapping.get(element.data_type, "string"),
            "description": element.description
        }
        
        if element.data_type == DataType.OBJECT:
            if element.properties:
                schema["properties"] = {
                    name: self._element_to_json_schema(prop)
                    for name, prop in element.properties.items()
                }
                required_props = [
                    name for name, prop in element.properties.items()
                    if prop.required
                ]
                if required_props:
                    schema["required"] = required_props
        
        elif element.data_type == DataType.ARRAY:
            if element.array_type:
                schema["items"] = self._element_to_json_schema(element.array_type)
        
        elif element.data_type in [DataType.STRING, DataType.INTEGER, DataType.FLOAT]:
            if element.min_value is not None:
                schema["minimum"] = element.min_value
            if element.max_value is not None:
                schema["maximum"] = element.max_value
            if element.min_length is not None:
                schema["minLength"] = element.min_length
            if element.max_length is not None:
                schema["maxLength"] = element.max_length
            if element.pattern:
                schema["pattern"] = element.pattern
        
        return schema
    
    def to_xsd(self) -> str:
        """Convert to XML Schema Definition (XSD) format."""
        if not self.root_element:
            return ""
        
        xsd = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xsd += '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">\n'
        xsd += self._element_to_xsd(self.root_element, indent=2)
        xsd += '</xs:schema>'
        return xsd
    
    def _element_to_xsd(self, element: SchemaElement, indent: int = 0) -> str:
        """Convert a schema element to XSD format."""
        spaces = " " * indent
        
        if element.data_type == DataType.OBJECT:
            xsd = f'{spaces}<xs:element name="{element.name}">\n'
            xsd += f'{spaces}  <xs:complexType>\n'
            
            if element.properties:
                xsd += f'{spaces}    <xs:sequence>\n'
                for prop_name, prop in element.properties.items():
                    xsd += self._element_to_xsd(prop, indent + 6)
                xsd += f'{spaces}    </xs:sequence>\n'
            
            if element.attributes:
                for attr_name, attr in element.attributes.items():
                    xsd += f'{spaces}    <xs:attribute name="{attr_name}" type="xs:{attr.data_type.value}"'
                    if not attr.required:
                        xsd += ' use="optional"'
                    if attr.default_value:
                        xsd += f' default="{attr.default_value}"'
                    xsd += '/>\n'
            
            xsd += f'{spaces}  </xs:complexType>\n'
            xsd += f'{spaces}</xs:element>\n'
            
        elif element.data_type == DataType.ARRAY:
            xsd = f'{spaces}<xs:element name="{element.name}">\n'
            xsd += f'{spaces}  <xs:complexType>\n'
            xsd += f'{spaces}    <xs:sequence>\n'
            xsd += f'{spaces}      <xs:element name="item" type="xs:{element.array_type.data_type.value if element.array_type else "string"}" maxOccurs="unbounded"/>\n'
            xsd += f'{spaces}    </xs:sequence>\n'
            xsd += f'{spaces}  </xs:complexType>\n'
            xsd += f'{spaces}</xs:element>\n'
            
        else:
            xsd = f'{spaces}<xs:element name="{element.name}" type="xs:{element.data_type.value}"'
            if not element.required:
                xsd += ' minOccurs="0"'
            xsd += '/>\n'
        
        return xsd
