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
    table.add_row("Max Depth", str(schema.max_depth))
    
    if schema.created_at:
        table.add_row("Created", schema.created_at)
    
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
