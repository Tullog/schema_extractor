"""
XML Schema Extractor - Extracts schema information from XML files.
"""

import os
import re
from typing import Dict, List, Optional, Any
from collections import defaultdict
from lxml import etree
import xmltodict

from ..models.schema import Schema, SchemaElement, SchemaAttribute, DataType, DataNode


class XMLExtractor:
    """Extracts schema information from XML files."""
    
    def __init__(self):
        self.element_counts = defaultdict(int)
        self.attribute_counts = defaultdict(int)
        self.data_type_patterns = {
            DataType.INTEGER: re.compile(r'^-?\d+$'),
            DataType.FLOAT: re.compile(r'^-?\d+\.\d+$'),
            DataType.BOOLEAN: re.compile(r'^(true|false|yes|no|1|0)$', re.IGNORECASE),
            DataType.DATE: re.compile(r'^\d{4}-\d{2}-\d{2}$'),
            DataType.DATETIME: re.compile(r'^\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}'),
        }
    
    def extract(self, file_path: str) -> Schema:
        """
        Extract schema from an XML file.
        
        Args:
            file_path: Path to the XML file
            
        Returns:
            Schema object containing the extracted XML schema
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"XML file not found: {file_path}")
        
        # Parse XML using lxml for structure analysis
        tree = etree.parse(file_path)
        root = tree.getroot()
        
        # Reset counters
        self.element_counts.clear()
        self.attribute_counts.clear()
        
        # Extract schema information
        schema_name = os.path.splitext(os.path.basename(file_path))[0]
        schema = Schema(
            name=schema_name,
            file_type="xml",
            created_at=self._get_creation_time(file_path)
        )
        
        # Extract root element schema
        root_element = self._extract_element_schema(root)
        schema.root_element = root_element
        
        # Extract data nodes
        schema.data_nodes = self._extract_data_nodes(root, root.tag)
        schema.total_data_nodes = len(schema.data_nodes)
        
        # Calculate statistics
        schema.total_elements = len(self.element_counts)
        schema.total_attributes = len(self.attribute_counts)
        schema.max_depth = self._calculate_max_depth(root)
        
        return schema
    
    def _extract_element_schema(self, element: etree._Element, depth: int = 0) -> SchemaElement:
        """Extract schema information from an XML element."""
        element_name = element.tag
        self.element_counts[element_name] += 1
        
        # Determine data type
        data_type = self._determine_element_type(element)
        
        # Create schema element
        schema_element = SchemaElement(
            name=element_name,
            data_type=data_type,
            description=f"Element: {element_name}"
        )
        
        # Extract attributes
        for attr_name, attr_value in element.attrib.items():
            attr_data_type = self._determine_data_type(attr_value)
            schema_element.attributes[attr_name] = SchemaAttribute(
                name=attr_name,
                data_type=attr_data_type,
                required=True,  # Assume required for now
                default_value=attr_value if attr_value else None
            )
            self.attribute_counts[attr_name] += 1
        
        # Extract child elements
        if data_type == DataType.OBJECT:
            child_elements = defaultdict(list)
            
            for child in element:
                child_elements[child.tag].append(child)
            
            # Process child elements
            for child_name, children in child_elements.items():
                if len(children) == 1:
                    # Single child element
                    child_schema = self._extract_element_schema(children[0], depth + 1)
                    schema_element.properties[child_name] = child_schema
                else:
                    # Multiple children with same name - treat as array
                    child_schema = self._extract_element_schema(children[0], depth + 1)
                    array_element = SchemaElement(
                        name=child_name,
                        data_type=DataType.ARRAY,
                        array_type=child_schema,
                        occurrences=len(children)
                    )
                    schema_element.properties[child_name] = array_element
        
        # Extract text content if present
        if element.text and element.text.strip():
            text_content = element.text.strip()
            data_type = self._determine_data_type(text_content)
            
            if data_type != DataType.STRING:
                # Create a text property
                text_element = SchemaElement(
                    name="text",
                    data_type=data_type,
                    examples=[text_content]
                )
                schema_element.properties["text"] = text_element
        
        return schema_element
    
    def _determine_element_type(self, element: etree._Element) -> DataType:
        """Determine the data type of an XML element."""
        # Check if element has children
        if len(element) > 0:
            return DataType.OBJECT
        
        # Check if element has text content
        if element.text and element.text.strip():
            return DataType.STRING
        
        # Check if element has attributes
        if element.attrib:
            return DataType.OBJECT
        
        # Empty element
        return DataType.STRING
    
    def _determine_data_type(self, value: str) -> DataType:
        """Determine the data type of a string value."""
        if not value:
            return DataType.STRING
        
        # Check against patterns
        for data_type, pattern in self.data_type_patterns.items():
            if pattern.match(value):
                return data_type
        
        return DataType.STRING
    
    def _calculate_max_depth(self, element: etree._Element, current_depth: int = 0) -> int:
        """Calculate the maximum depth of the XML tree."""
        max_depth = current_depth
        
        for child in element:
            child_depth = self._calculate_max_depth(child, current_depth + 1)
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
    
    def extract_from_string(self, xml_string: str) -> Schema:
        """
        Extract schema from an XML string.
        
        Args:
            xml_string: XML content as string
            
        Returns:
            Schema object containing the extracted XML schema
        """
        # Parse XML string
        root = etree.fromstring(xml_string.encode('utf-8'))
        
        # Reset counters
        self.element_counts.clear()
        self.attribute_counts.clear()
        
        # Extract schema information
        schema = Schema(
            name="xml_schema",
            file_type="xml"
        )
        
        # Extract root element schema
        root_element = self._extract_element_schema(root)
        schema.root_element = root_element
        
        # Calculate statistics
        schema.total_elements = len(self.element_counts)
        schema.total_attributes = len(self.attribute_counts)
        schema.max_depth = self._calculate_max_depth(root)
        
        return schema

    def _extract_data_nodes(self, element: etree._Element, path: str, depth: int = 0, parent_path: Optional[str] = None) -> List[DataNode]:
        """
        Extract all data nodes from XML element.
        
        Args:
            element: XML element to extract nodes from
            path: Current path in the data structure
            depth: Current depth level
            parent_path: Path of the parent node
            
        Returns:
            List of DataNode objects
        """
        nodes = []
        
        # Create node for current element
        element_type = self._determine_element_type(element)
        node = DataNode(
            path=path,
            name=element.tag,
            value=element.text.strip() if element.text and element.text.strip() else None,
            data_type=element_type,
            depth=depth,
            parent_path=parent_path,
            is_leaf=len(element) == 0 and (not element.text or not element.text.strip()),
            description=f"XML element: {element.tag}"
        )
        nodes.append(node)
        
        # Extract attribute nodes
        for attr_name, attr_value in element.attrib.items():
            attr_path = f"{path}@{attr_name}"
            attr_data_type = self._determine_data_type(attr_value)
            attr_node = DataNode(
                path=attr_path,
                name=attr_name,
                value=attr_value,
                data_type=attr_data_type,
                depth=depth + 1,
                parent_path=path,
                is_leaf=True,
                description=f"Attribute: {attr_name}"
            )
            nodes.append(attr_node)
        
        # Extract text content node if present
        if element.text and element.text.strip():
            text_path = f"{path}#text"
            text_data_type = self._determine_data_type(element.text.strip())
            text_node = DataNode(
                path=text_path,
                name="text",
                value=element.text.strip(),
                data_type=text_data_type,
                depth=depth + 1,
                parent_path=path,
                is_leaf=True,
                description=f"Text content of {element.tag}"
            )
            nodes.append(text_node)
        
        # Process child elements
        for i, child in enumerate(element):
            child_path = f"{path}.{child.tag}"
            child_nodes = self._extract_data_nodes(child, child_path, depth + 1, path)
            nodes.extend(child_nodes)
        
        return nodes
