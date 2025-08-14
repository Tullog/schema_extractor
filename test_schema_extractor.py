#!/usr/bin/env python3
"""
Simple test script for the Schema Extractor.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from schema_extractor import SchemaExtractor


def test_xml_extraction():
    """Test XML schema extraction."""
    print("Testing XML schema extraction...")
    
    extractor = SchemaExtractor()
    xml_file = "examples/sample.xml"
    
    if not os.path.exists(xml_file):
        print(f"XML file not found: {xml_file}")
        return False
    
    try:
        schema = extractor.extract_xml_schema(xml_file)
        print(f"✓ XML schema extracted successfully!")
        print(f"  - Name: {schema.name}")
        print(f"  - Type: {schema.file_type}")
        print(f"  - Total Elements: {schema.total_elements}")
        print(f"  - Total Attributes: {schema.total_attributes}")
        print(f"  - Max Depth: {schema.max_depth}")
        return True
    except Exception as e:
        print(f"✗ XML extraction failed: {e}")
        return False


def test_json_extraction():
    """Test JSON schema extraction."""
    print("\nTesting JSON schema extraction...")
    
    extractor = SchemaExtractor()
    json_file = "examples/sample.json"
    
    if not os.path.exists(json_file):
        print(f"JSON file not found: {json_file}")
        return False
    
    try:
        schema = extractor.extract_json_schema(json_file)
        print(f"✓ JSON schema extracted successfully!")
        print(f"  - Name: {schema.name}")
        print(f"  - Type: {schema.file_type}")
        print(f"  - Total Elements: {schema.total_elements}")
        print(f"  - Max Depth: {schema.max_depth}")
        return True
    except Exception as e:
        print(f"✗ JSON extraction failed: {e}")
        return False


def test_auto_detection():
    """Test automatic file type detection."""
    print("\nTesting automatic file type detection...")
    
    extractor = SchemaExtractor()
    xml_file = "examples/sample.xml"
    json_file = "examples/sample.json"
    
    try:
        # Test XML
        schema = extractor.extract_schema(xml_file)
        print(f"✓ Auto-detected XML file: {schema.file_type}")
        
        # Test JSON
        schema = extractor.extract_schema(json_file)
        print(f"✓ Auto-detected JSON file: {schema.file_type}")
        
        return True
    except Exception as e:
        print(f"✗ Auto-detection failed: {e}")
        return False


def test_schema_output():
    """Test schema output formats."""
    print("\nTesting schema output formats...")
    
    extractor = SchemaExtractor()
    json_file = "examples/sample.json"
    
    try:
        schema = extractor.extract_json_schema(json_file)
        
        # Test JSON output
        json_output = schema.to_json_schema()
        print(f"✓ JSON Schema output generated ({len(str(json_output))} characters)")
        
        # Test XSD output
        xsd_output = schema.to_xsd()
        print(f"✓ XSD output generated ({len(xsd_output)} characters)")
        
        # Test dict output
        dict_output = schema.to_dict()
        print(f"✓ Dictionary output generated ({len(str(dict_output))} characters)")
        
        return True
    except Exception as e:
        print(f"✗ Schema output failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Schema Extractor Test Suite")
    print("=" * 40)
    
    tests = [
        test_xml_extraction,
        test_json_extraction,
        test_auto_detection,
        test_schema_output
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The schema extractor is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
