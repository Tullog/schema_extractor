"""
JSON Schema Extractor - Extracts schema information from JSON files.
"""

import os
import json
import re
from typing import Dict, List, Optional, Any, Union
from collections import defaultdict

from ..models.schema import Schema, SchemaElement, SchemaAttribute, DataType, DataNode


class JSONExtractor:
    """Extracts schema information from JSON files."""
    
    def __init__(self):
        self.property_counts = defaultdict(int)
        self.data_type_patterns = {
            DataType.INTEGER: re.compile(r'^-?\d+$'),
            DataType.FLOAT: re.compile(r'^-?\d+\.\d+$'),
            DataType.BOOLEAN: re.compile(r'^(true|false)$', re.IGNORECASE),
            DataType.DATE: re.compile(r'^\d{4}-\d{2}-\d{2}$'),
            DataType.DATETIME: re.compile(r'^\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}'),
        }
    
    def extract(self, file_path: str) -> Schema:
        """
        Extract schema from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Schema object containing the extracted JSON schema
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"JSON file not found: {file_path}")
        
        # Read and parse JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Reset counters
        self.property_counts.clear()
        
        # Extract schema information
        schema_name = os.path.splitext(os.path.basename(file_path))[0]
        schema = Schema(
            name=schema_name,
            file_type="json",
            created_at=self._get_creation_time(file_path)
        )
        
        # Extract root element schema
        root_element = self._extract_element_schema(data, "root")
        schema.root_element = root_element
        
        # Extract data nodes
        schema.data_nodes = self._extract_data_nodes(data, "root")
        schema.total_data_nodes = len(schema.data_nodes)
        
        # Calculate statistics
        schema.total_elements = len(self.property_counts)
        schema.max_depth = self._calculate_max_depth(data)
        
        return schema
    
    def _extract_element_schema(self, data: Any, name: str, depth: int = 0) -> SchemaElement:
        """Extract schema information from a JSON element."""
        data_type = self._determine_data_type(data)
        
        # Create schema element
        schema_element = SchemaElement(
            name=name,
            data_type=data_type,
            description=f"Property: {name}"
        )
        
        if data_type == DataType.OBJECT:
            # Process object properties
            if isinstance(data, dict):
                for prop_name, prop_value in data.items():
                    self.property_counts[prop_name] += 1
                    prop_schema = self._extract_element_schema(prop_value, prop_name, depth + 1)
                    schema_element.properties[prop_name] = prop_schema
        
        elif data_type == DataType.ARRAY:
            # Process array elements
            if isinstance(data, list) and data:
                # Analyze first element to determine array type
                first_element = data[0]
                array_type_schema = self._extract_element_schema(first_element, "item", depth + 1)
                schema_element.array_type = array_type_schema
                schema_element.occurrences = len(data)
                
                # Check if all elements are of the same type
                for item in data[1:]:
                    item_type = self._determine_data_type(item)
                    if item_type != array_type_schema.data_type:
                        # Mixed types - update to more general type
                        array_type_schema.data_type = DataType.UNKNOWN
                        break
        
        elif data_type in [DataType.STRING, DataType.INTEGER, DataType.FLOAT, DataType.BOOLEAN]:
            # Store example values for primitive types
            schema_element.examples = [data]
        
        elif data_type == DataType.NULL:
            # Handle null values
            schema_element.description = f"Property: {name} (nullable)"
        
        return schema_element
    
    def _determine_data_type(self, data: Any) -> DataType:
        """Determine the data type of a JSON value."""
        if data is None:
            return DataType.NULL
        elif isinstance(data, bool):
            return DataType.BOOLEAN
        elif isinstance(data, int):
            return DataType.INTEGER
        elif isinstance(data, float):
            return DataType.FLOAT
        elif isinstance(data, str):
            # For JSON, strings should remain strings unless they're clearly dates/datetimes
            return self._infer_string_type(data)
        elif isinstance(data, list):
            return DataType.ARRAY
        elif isinstance(data, dict):
            return DataType.OBJECT
        else:
            return DataType.UNKNOWN
    
    def _infer_string_type(self, value: str) -> DataType:
        """Infer more specific type for string values."""
        if not value:
            return DataType.STRING
        
        # Only convert dates and datetimes, keep everything else as strings
        for data_type, pattern in self.data_type_patterns.items():
            if data_type in [DataType.DATE, DataType.DATETIME] and pattern.match(value):
                return data_type
        
        return DataType.STRING
    
    def _calculate_max_depth(self, data: Any, current_depth: int = 0) -> int:
        """Calculate the maximum depth of the JSON structure."""
        max_depth = current_depth
        
        if isinstance(data, dict):
            for value in data.values():
                child_depth = self._calculate_max_depth(value, current_depth + 1)
                max_depth = max(max_depth, child_depth)
        elif isinstance(data, list):
            for item in data:
                child_depth = self._calculate_max_depth(item, current_depth + 1)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def _get_creation_time(self, file_path: str) -> str:
        """Get file creation time."""
        try:
            import datetime
            stat = os.stat(file_path)
            return datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
        except:
            return ""
    
    def extract_from_string(self, json_string: str) -> Schema:
        """
        Extract schema from a JSON string.
        
        Args:
            json_string: JSON content as string
            
        Returns:
            Schema object containing the extracted JSON schema
        """
        # Parse JSON string
        data = json.loads(json_string)
        
        # Reset counters
        self.property_counts.clear()
        
        # Extract schema information
        schema = Schema(
            name="json_schema",
            file_type="json"
        )
        
        # Extract root element schema
        root_element = self._extract_element_schema(data, "root")
        schema.root_element = root_element
        
        # Calculate statistics
        schema.total_elements = len(self.property_counts)
        schema.max_depth = self._calculate_max_depth(data)
        
        return schema
    
    def merge_schemas(self, schemas: List[Schema]) -> Schema:
        """
        Merge multiple JSON schemas into a single schema.
        
        Args:
            schemas: List of schemas to merge
            
        Returns:
            Merged schema
        """
        if not schemas:
            raise ValueError("No schemas provided for merging")
        
        if len(schemas) == 1:
            return schemas[0]
        
        # Start with the first schema
        merged_schema = schemas[0].model_copy()
        merged_schema.name = "merged_schema"
        
        # Merge root elements
        if merged_schema.root_element and all(s.root_element for s in schemas[1:]):
            merged_root = self._merge_elements(
                [s.root_element for s in schemas]
            )
            merged_schema.root_element = merged_root
        
        return merged_schema
    
    def _merge_elements(self, elements: List[SchemaElement]) -> SchemaElement:
        """Merge multiple schema elements."""
        if not elements:
            raise ValueError("No elements provided for merging")
        
        if len(elements) == 1:
            return elements[0]
        
        # Start with the first element
        merged_element = elements[0].model_copy()
        
        # Merge properties
        all_properties = {}
        for element in elements:
            for prop_name, prop_schema in element.properties.items():
                if prop_name in all_properties:
                    # Merge existing property
                    all_properties[prop_name] = self._merge_elements([
                        all_properties[prop_name], prop_schema
                    ])
                else:
                    all_properties[prop_name] = prop_schema
        
        merged_element.properties = all_properties
        
        # Merge attributes
        all_attributes = {}
        for element in elements:
            for attr_name, attr_schema in element.attributes.items():
                if attr_name in all_attributes:
                    # Merge existing attribute
                    existing_attr = all_attributes[attr_name]
                    existing_attr.required = existing_attr.required and attr_schema.required
                    if attr_schema.default_value and not existing_attr.default_value:
                        existing_attr.default_value = attr_schema.default_value
                else:
                    all_attributes[attr_name] = attr_schema
        
        merged_element.attributes = all_attributes
        
        return merged_element

    def _extract_data_nodes(self, data: Any, path: str, depth: int = 0, parent_path: Optional[str] = None) -> List[DataNode]:
        """
        Extract all data nodes from JSON data.
        
        Args:
            data: JSON data to extract nodes from
            path: Current path in the data structure
            depth: Current depth level
            parent_path: Path of the parent node
            
        Returns:
            List of DataNode objects
        """
        nodes = []
        data_type = self._determine_data_type(data)
        
        # Create node for current element
        node = DataNode(
            path=path,
            name=path.split('.')[-1] if '.' in path else path,
            value=data,
            data_type=data_type,
            depth=depth,
            parent_path=parent_path,
            is_leaf=data_type not in [DataType.OBJECT, DataType.ARRAY],
            description=f"Data node at path: {path}"
        )
        nodes.append(node)
        
        # Process children based on data type
        if data_type == DataType.OBJECT and isinstance(data, dict):
            for key, value in data.items():
                child_path = f"{path}.{key}" if path != "root" else key
                child_nodes = self._extract_data_nodes(value, child_path, depth + 1, path)
                nodes.extend(child_nodes)
        
        elif data_type == DataType.ARRAY and isinstance(data, list):
            for i, item in enumerate(data):
                child_path = f"{path}[{i}]"
                child_nodes = self._extract_data_nodes(item, child_path, depth + 1, path)
                nodes.extend(child_nodes)
        
        return nodes
