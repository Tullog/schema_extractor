# Schema Extractor

A Python tool for extracting schemas from XML and JSON files. This tool analyzes the structure of XML and JSON documents and generates a comprehensive schema representation.

## Features

- **XML Schema Extraction**: Parse XML files and extract element structure, attributes, and data types
- **JSON Schema Extraction**: Parse JSON files and extract object structure, array types, and data types
- **Schema Validation**: Validate files against extracted schemas
- **Multiple Output Formats**: Export schemas in JSON, XML Schema (XSD), or human-readable format
- **CLI Interface**: Easy-to-use command-line interface
- **Rich Output**: Beautiful terminal output with syntax highlighting

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd schema_extractor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

Extract schema from an XML file:
```bash
python schema_extractor.py extract --input data.xml --output schema.json
```

Extract schema from a JSON file:
```bash
python schema_extractor.py extract --input data.json --output schema.json
```

Extract schema and display in terminal:
```bash
python schema_extractor.py extract --input data.xml --display
```

Validate a file against a schema:
```bash
python schema_extractor.py validate --input data.xml --schema schema.json
```

### Python API

```python
from schema_extractor import SchemaExtractor

# Extract XML schema
extractor = SchemaExtractor()
schema = extractor.extract_xml_schema("data.xml")

# Extract JSON schema
schema = extractor.extract_json_schema("data.json")

# Validate file against schema
is_valid = extractor.validate_file("data.xml", schema)
```

## Project Structure

```
schema_extractor/
├── schema_extractor.py      # Main CLI interface
├── schema_extractor/        # Core package
│   ├── __init__.py
│   ├── extractors/          # Schema extraction logic
│   │   ├── __init__.py
│   │   ├── xml_extractor.py
│   │   └── json_extractor.py
│   ├── models/              # Data models
│   │   ├── __init__.py
│   │   └── schema.py
│   └── utils/               # Utility functions
│       ├── __init__.py
│       └── helpers.py
├── examples/                # Example files
│   ├── sample.xml
│   └── sample.json
├── tests/                   # Test files
├── requirements.txt
└── README.md
```

## Examples

See the `examples/` directory for sample XML and JSON files to test with.

## License

MIT License
