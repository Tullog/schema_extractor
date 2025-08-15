#!/usr/bin/env python3
"""
Schema Extractor CLI - Command-line interface for extracting schemas from XML and JSON files.
"""

import os
import sys
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn

from schema_extractor import SchemaExtractor
from schema_extractor.utils.helpers import save_schema, load_schema, format_schema_output
from schema_extractor.models.schema import DataType

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Schema Extractor - Extract schemas from XML and JSON files."""
    pass


@cli.command()
@click.option('--input', '-i', 'input_file', required=True, help='Input file path (XML or JSON)')
@click.option('--output', '-o', 'output_file', help='Output file path for schema')
@click.option('--format', '-f', 'output_format', 
              type=click.Choice(['json', 'xsd', 'dict']), 
              default='json', help='Output format')
@click.option('--display', '-d', is_flag=True, help='Display schema in terminal')
@click.option('--pretty', '-p', is_flag=True, help='Pretty print output')
def extract(input_file, output_file, output_format, display, pretty):
    """Extract schema from XML or JSON file."""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Extracting schema...", total=None)
            
            # Initialize extractor
            extractor = SchemaExtractor()
            
            # Extract schema
            schema = extractor.extract_schema(input_file)
            
            progress.update(task, description="Schema extraction completed!")
        
        # Display schema if requested
        if display:
            console.print("\n")
            if pretty:
                formatted_output = format_schema_output(schema, "pretty")
                console.print(Panel(formatted_output, title="Extracted Schema", border_style="blue"))
            else:
                formatted_output = format_schema_output(schema, "json")
                syntax = Syntax(formatted_output, "json", theme="monokai")
                console.print(Panel(syntax, title="Extracted Schema", border_style="blue"))
        
        # Save schema if output file specified
        if output_file:
            save_schema(schema, output_file, output_format)
            console.print(f"[green]Schema saved to: {output_file}[/green]")
        
        # Display summary
        _display_schema_summary(schema)
        
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', 'input_file', required=True, help='Input file path to validate')
@click.option('--schema', '-s', 'schema_file', required=True, help='Schema file path')
def validate(input_file, schema_file):
    """Validate a file against a schema."""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Loading schema...", total=None)
            
            # Load schema
            schema = load_schema(schema_file)
            
            progress.update(task, description="Validating file...")
            
            # Initialize extractor
            extractor = SchemaExtractor()
            
            # Validate file
            is_valid = extractor.validate_file(input_file, schema)
            
            progress.update(task, description="Validation completed!")
        
        # Display results
        if is_valid:
            console.print("[green]✓ File is valid against the schema![/green]")
        else:
            console.print("[red]✗ File is not valid against the schema![/red]")
            sys.exit(1)
        
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', 'input_file', required=True, help='Input file path')
@click.option('--output', '-o', 'output_file', help='Output file path')
@click.option('--format', '-f', 'output_format', 
              type=click.Choice(['json', 'xsd']), 
              default='json', help='Output format')
def convert(input_file, output_file, output_format):
    """Convert schema between formats."""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Converting schema...", total=None)
            
            # Load schema
            schema = load_schema(input_file)
            
            # Determine output file
            if not output_file:
                base_name = Path(input_file).stem
                output_file = f"{base_name}.{output_format}"
            
            # Save in new format
            save_schema(schema, output_file, output_format)
            
            progress.update(task, description="Conversion completed!")
        
        console.print(f"[green]Schema converted and saved to: {output_file}[/green]")
        
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', 'input_files', required=True, multiple=True, help='Input schema files')
@click.option('--output', '-o', 'output_file', required=True, help='Output merged schema file')
def merge(input_files, output_file):
    """Merge multiple schemas into one."""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Loading schemas...", total=len(input_files))
            
            # Load all schemas
            schemas = []
            for schema_file in input_files:
                schema = load_schema(schema_file)
                schemas.append(schema)
                progress.advance(task)
            
            progress.update(task, description="Merging schemas...")
            
            # Merge schemas (assuming all are JSON schemas for now)
            from schema_extractor.extractors.json_extractor import JSONExtractor
            extractor = JSONExtractor()
            merged_schema = extractor.merge_schemas(schemas)
            
            # Save merged schema
            save_schema(merged_schema, output_file)
            
            progress.update(task, description="Merge completed!")
        
        console.print(f"[green]Schemas merged and saved to: {output_file}[/green]")
        
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', 'input_file', required=True, help='Input file path (XML or JSON)')
@click.option('--output', '-o', 'output_file', help='Output file path for data nodes')
@click.option('--type', '-t', 'data_type', help='Filter by data type (string, integer, float, boolean, object, array)')
@click.option('--path', '-p', 'path_pattern', help='Filter by path pattern (regex)')
@click.option('--leaf-only', '-l', is_flag=True, help='Show only leaf nodes (nodes with actual values)')
@click.option('--format', '-f', 'output_format', 
              type=click.Choice(['table', 'json', 'csv']), 
              default='table', help='Output format')
@click.option('--max-depth', '-d', type=int, help='Maximum depth to display')
def nodes(input_file, output_file, data_type, path_pattern, leaf_only, output_format, max_depth):
    """List data nodes from XML or JSON file."""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Extracting data nodes...", total=None)
            
            # Initialize extractor
            extractor = SchemaExtractor()
            
            # Extract schema (which includes data nodes)
            schema = extractor.extract_schema(input_file)
            
            progress.update(task, description="Data nodes extraction completed!")
        
        # Filter data nodes
        data_nodes = schema.data_nodes
        
        if data_type:
            try:
                filter_type = DataType(data_type.lower())
                data_nodes = schema.get_data_nodes_by_type(filter_type)
            except ValueError:
                console.print(f"[red]Error: Invalid data type '{data_type}'. Valid types: {[t.value for t in DataType]}[/red]")
                sys.exit(1)
        
        if path_pattern:
            data_nodes = schema.get_data_nodes_by_path(path_pattern)
        
        if leaf_only:
            data_nodes = schema.get_leaf_nodes()
        
        if max_depth is not None:
            data_nodes = [node for node in data_nodes if node.depth <= max_depth]
        
        # Display results
        if output_format == 'table':
            _display_data_nodes_table(data_nodes, schema.name)
        elif output_format == 'json':
            _display_data_nodes_json(data_nodes)
        elif output_format == 'csv':
            _display_data_nodes_csv(data_nodes)
        
        # Save to file if requested
        if output_file:
            _save_data_nodes(data_nodes, output_file, output_format)
            console.print(f"[green]Data nodes saved to: {output_file}[/green]")
        
        # Display summary
        _display_data_nodes_summary(data_nodes, schema)
        
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def _display_schema_summary(schema):
    """Display a summary of the extracted schema."""
    table = Table(title="Schema Summary")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("Name", schema.name)
    table.add_row("Type", schema.file_type)
    table.add_row("Version", schema.version)
    table.add_row("Total Elements", str(schema.total_elements))
    table.add_row("Total Attributes", str(schema.total_attributes))
    table.add_row("Total Data Nodes", str(schema.total_data_nodes))
    table.add_row("Max Depth", str(schema.max_depth))
    
    if schema.created_at:
        table.add_row("Created", schema.created_at)
    
    console.print(table)


def _display_data_nodes_table(data_nodes, schema_name):
    """Display data nodes in a table format."""
    if not data_nodes:
        console.print("[yellow]No data nodes found matching the criteria.[/yellow]")
        return
    
    table = Table(title=f"Data Nodes - {schema_name}")
    table.add_column("Path", style="cyan", no_wrap=True)
    table.add_column("Name", style="green")
    table.add_column("Type", style="blue")
    table.add_column("Value", style="magenta", max_width=50)
    table.add_column("Depth", style="yellow", justify="right")
    table.add_column("Leaf", style="red", justify="center")
    
    for node in data_nodes:
        # Truncate long values for display
        value_str = str(node.value) if node.value is not None else "None"
        if len(value_str) > 50:
            value_str = value_str[:47] + "..."
        
        table.add_row(
            node.path,
            node.name,
            node.data_type.value,
            value_str,
            str(node.depth),
            "✓" if node.is_leaf else "✗"
        )
    
    console.print(table)


def _display_data_nodes_json(data_nodes):
    """Display data nodes in JSON format."""
    import json
    
    nodes_data = []
    for node in data_nodes:
        nodes_data.append({
            "path": node.path,
            "name": node.name,
            "value": node.value,
            "data_type": node.data_type.value,
            "depth": node.depth,
            "parent_path": node.parent_path,
            "is_leaf": node.is_leaf,
            "description": node.description
        })
    
    json_output = json.dumps(nodes_data, indent=2, default=str)
    syntax = Syntax(json_output, "json", theme="monokai")
    console.print(Panel(syntax, title="Data Nodes (JSON)", border_style="blue"))


def _display_data_nodes_csv(data_nodes):
    """Display data nodes in CSV format."""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(["Path", "Name", "Value", "Type", "Depth", "Is Leaf", "Parent Path"])
    
    # Write data
    for node in data_nodes:
        writer.writerow([
            node.path,
            node.name,
            str(node.value) if node.value is not None else "",
            node.data_type.value,
            node.depth,
            node.is_leaf,
            node.parent_path or ""
        ])
    
    console.print(Panel(output.getvalue(), title="Data Nodes (CSV)", border_style="green"))


def _save_data_nodes(data_nodes, output_file, format_type):
    """Save data nodes to a file."""
    import json
    import csv
    
    if format_type == 'json':
        nodes_data = []
        for node in data_nodes:
            nodes_data.append({
                "path": node.path,
                "name": node.name,
                "value": node.value,
                "data_type": node.data_type.value,
                "depth": node.depth,
                "parent_path": node.parent_path,
                "is_leaf": node.is_leaf,
                "description": node.description
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(nodes_data, f, indent=2, default=str)
    
    elif format_type == 'csv':
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Path", "Name", "Value", "Type", "Depth", "Is Leaf", "Parent Path"])
            
            for node in data_nodes:
                writer.writerow([
                    node.path,
                    node.name,
                    str(node.value) if node.value is not None else "",
                    node.data_type.value,
                    node.depth,
                    node.is_leaf,
                    node.parent_path or ""
                ])


def _display_data_nodes_summary(data_nodes, schema):
    """Display a summary of the data nodes."""
    table = Table(title="Data Nodes Summary")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("Total Nodes Found", str(len(data_nodes)))
    table.add_row("Total Nodes in Schema", str(schema.total_data_nodes))
    table.add_row("Leaf Nodes", str(len([n for n in data_nodes if n.is_leaf])))
    table.add_row("Max Depth", str(max([n.depth for n in data_nodes]) if data_nodes else 0))
    
    # Count by type
    type_counts = {}
    for node in data_nodes:
        type_counts[node.data_type.value] = type_counts.get(node.data_type.value, 0) + 1
    
    for data_type, count in sorted(type_counts.items()):
        table.add_row(f"Type: {data_type}", str(count))
    
    console.print(table)


@cli.command()
def info():
    """Display information about the schema extractor."""
    info_text = """
    [bold blue]Schema Extractor[/bold blue]
    
    A powerful tool for extracting schemas from XML and JSON files.
    
    [bold]Features:[/bold]
    • XML Schema Extraction
    • JSON Schema Extraction  
    • Schema Validation
    • Multiple Output Formats (JSON, XSD)
    • Schema Merging
    • Beautiful CLI Interface
    
    [bold]Supported Formats:[/bold]
    • XML files (.xml, .xhtml, .svg)
    • JSON files (.json, .js)
    
    [bold]Output Formats:[/bold]
    • JSON Schema
    • XML Schema Definition (XSD)
    • Human-readable format
    
    For more information, visit the project repository.
    """
    
    console.print(Panel(info_text, title="Schema Extractor Info", border_style="green"))


if __name__ == '__main__':
    cli()
