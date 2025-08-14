"""
Schema Extractor - A tool for extracting schemas from XML and JSON files.
"""

from .models.schema import Schema
from .extractors.xml_extractor import XMLExtractor
from .extractors.json_extractor import JSONExtractor
from .utils.helpers import detect_file_type, validate_schema


class SchemaExtractor:
    """Main class for extracting schemas from XML and JSON files."""
    
    def __init__(self):
        self.xml_extractor = XMLExtractor()
        self.json_extractor = JSONExtractor()
    
    def extract_schema(self, file_path: str) -> Schema:
        """
        Extract schema from a file (auto-detects file type).
        
        Args:
            file_path: Path to the XML or JSON file
            
        Returns:
            Schema object containing the extracted schema
        """
        file_type = detect_file_type(file_path)
        
        if file_type == "xml":
            return self.extract_xml_schema(file_path)
        elif file_type == "json":
            return self.extract_json_schema(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def extract_xml_schema(self, file_path: str) -> Schema:
        """
        Extract schema from an XML file.
        
        Args:
            file_path: Path to the XML file
            
        Returns:
            Schema object containing the extracted XML schema
        """
        return self.xml_extractor.extract(file_path)
    
    def extract_json_schema(self, file_path: str) -> Schema:
        """
        Extract schema from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Schema object containing the extracted JSON schema
        """
        return self.json_extractor.extract(file_path)
    
    def validate_file(self, file_path: str, schema: Schema) -> bool:
        """
        Validate a file against a schema.
        
        Args:
            file_path: Path to the file to validate
            schema: Schema object to validate against
            
        Returns:
            True if valid, False otherwise
        """
        return validate_schema(file_path, schema)


__version__ = "1.0.0"
__all__ = ["SchemaExtractor", "Schema", "XMLExtractor", "JSONExtractor"]
