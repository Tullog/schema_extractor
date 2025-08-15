# Schema Extractor

A Python tool for extracting schemas from XML and JSON files. This tool analyzes the structure of XML and JSON documents and generates a comprehensive schema representation.

## Features

- **XML Schema Extraction**: Parse XML files and extract element structure, attributes, and data types
- **JSON Schema Extraction**: Parse JSON files and extract object structure, array types, and data types
- **Data Nodes Extraction**: Extract and list all data nodes with their values, types, and paths
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

**List data nodes from a file:**
```bash
# List all data nodes
python schema_extractor.py nodes --input data.json

# List only leaf nodes (nodes with actual values)
python schema_extractor.py nodes --input data.json --leaf-only

# Filter by data type
python schema_extractor.py nodes --input data.json --type string

# Filter by path pattern
python schema_extractor.py nodes --input data.json --path "user.*"

# Export to JSON format
python schema_extractor.py nodes --input data.json --format json --output nodes.json

# Export to CSV format
python schema_extractor.py nodes --input data.json --format csv --output nodes.csv
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

# Access data nodes
for node in schema.data_nodes:
    print(f"Path: {node.path}, Value: {node.value}, Type: {node.data_type}")

# Get leaf nodes only
leaf_nodes = schema.get_leaf_nodes()

# Filter by data type
string_nodes = schema.get_data_nodes_by_type(DataType.STRING)

# Filter by path pattern
user_nodes = schema.get_data_nodes_by_path("user.*")

# Validate file against schema
is_valid = extractor.validate_file("data.xml", schema)
```

## Data Nodes Feature

The data nodes feature extracts all individual data points from your XML or JSON files, including:

- **Path**: Full path to the data node (e.g., "root.user.name")
- **Name**: Node name
- **Value**: Actual data value
- **Type**: Data type (string, integer, float, boolean, object, array)
- **Depth**: Nesting level in the structure
- **Leaf Status**: Whether the node contains actual data (leaf) or is a container

### CLI Options for Data Nodes

- `--input, -i`: Input file path (required)
- `--output, -o`: Output file path for saving results
- `--type, -t`: Filter by data type (string, integer, float, boolean, object, array)
- `--path, -p`: Filter by path pattern using regex
- `--leaf-only, -l`: Show only leaf nodes (nodes with actual values)
- `--format, -f`: Output format (table, json, csv)
- `--max-depth, -d`: Maximum depth to display

### Output Formats

1. **Table**: Rich formatted table in terminal
2. **JSON**: Structured JSON output
3. **CSV**: Comma-separated values for spreadsheet import

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
