# File Output Functionality

This document describes the file output capabilities of the RAG2 Document Processing System, which allows you to save summaries, search results, and other outputs to organized markdown files.

## Overview

The system now includes comprehensive file output functionality that:
- Saves summaries to organized markdown files
- Creates structured output directories
- Generates index files for easy navigation
- Supports custom filenames and directories
- Provides rich metadata in each file

## Quick Start

### Command Line Usage

```bash
# Save a summary to file
uv run python main.py summarize executive "climate risk" --save

# Save with custom filename
uv run python main.py summarize comprehensive "governance" --save --filename my_analysis

# Save document overview
uv run python main.py overview openai --save

# Run full output demo
uv run python output_demo.py
```

### Programmatic Usage

```python
from document_summarizer import DocumentSummarizer

# Initialize summarizer
summarizer = DocumentSummarizer()

# Generate and save summary
result = summarizer.summarize_document(
    query="climate risk management",
    summary_type="comprehensive",
    save_to_file=True,
    custom_filename="climate_analysis"
)

if result["success"]:
    print(f"Summary saved to: {result['file_path']}")
```

## File Structure

The system creates an organized directory structure:

```
output/
├── summaries/          # Document summaries
│   ├── comprehensive_20251004_180125_climate_risk_guidelines.md
│   ├── executive_20251004_180126_executive_brief.md
│   └── key_points_20251004_180127_key_points.md
├── overviews/          # Document overviews
│   └── overview_20251004_180130_document_overview.md
├── sections/           # Sectioned summaries
│   └── sections_20251004_180137_sectioned_analysis.md
├── searches/           # Search results
│   ├── search_20251004_180137_climate_risk_assessment.md
│   └── search_20251004_180137_governance_oversight.md
└── index.md           # Index of all files
```

## File Types

### 1. Summary Files
Comprehensive, executive, and key points summaries.

**Filename Format**: `{type}_{timestamp}_{custom_name}.md`

**Content Includes**:
- Document information (source, generation time, model used)
- Full summary text
- Metadata (chunks used, query, provider)
- JSON metadata section

### 2. Overview Files
High-level document overviews with statistics.

**Filename Format**: `overview_{timestamp}_{custom_name}.md`

**Content Includes**:
- Document overview text
- Document statistics (total chunks, source files)
- Chunk size information
- Metadata

### 3. Sectioned Summary Files
Organized summaries by document sections.

**Filename Format**: `sections_{timestamp}_{custom_name}.md`

**Content Includes**:
- Multiple sections with individual summaries
- Section-specific queries used
- Success status for each section
- Metadata

### 4. Search Result Files
Saved search results with context.

**Filename Format**: `search_{timestamp}_{query}_{custom_name}.md`

**Content Includes**:
- Search query and results count
- Individual results with similarity scores
- Source file and chunk information
- Full search metadata

## API Reference

### DocumentSummarizer Methods

#### `summarize_document(save_to_file, custom_filename)`

Generate and optionally save a document summary.

**Parameters**:
- `save_to_file` (bool): Whether to save to file
- `custom_filename` (str): Custom filename (without extension)

**Returns**:
- Dictionary with `file_path` if saved successfully

#### `get_document_overview(save_to_file, custom_filename)`

Generate and optionally save document overview.

**Parameters**:
- `save_to_file` (bool): Whether to save to file
- `custom_filename` (str): Custom filename (without extension)

**Returns**:
- Dictionary with `file_path` if saved successfully

#### `summarize_by_sections(save_to_file, custom_filename)`

Generate and optionally save sectioned summary.

**Parameters**:
- `save_to_file` (bool): Whether to save to file
- `custom_filename` (str): Custom filename (without extension)

**Returns**:
- Dictionary with `file_path` if saved successfully

### MarkdownOutputManager Class

#### `save_summary(summary_result, summary_type, source_file, custom_filename)`

Save a summary result to markdown file.

#### `save_document_overview(overview_result, source_file, custom_filename)`

Save document overview to markdown file.

#### `save_sectioned_summary(sections_result, source_file, custom_filename)`

Save sectioned summary to markdown file.

#### `save_search_results(search_results, query, source_file, custom_filename)`

Save search results to markdown file.

#### `create_index_file()`

Create an index file listing all generated outputs.

#### `get_output_stats()`

Get statistics about generated outputs.

## Command Line Options

### Basic Options

```bash
# Save to file
--save, -s

# Custom filename
--filename <name>
```

### Examples

```bash
# Basic summary with file saving
uv run python main.py summarize executive --save

# Custom filename
uv run python main.py summarize comprehensive "climate risk" --save --filename climate_analysis

# Document overview with custom name
uv run python main.py overview openai --save --filename doc_overview

# Multiple options
uv run python main.py summarize key_points "governance oversight" --save --filename governance_summary
```

## File Naming

### Automatic Naming
Files are automatically named using the pattern:
`{type}_{timestamp}_{custom_name}.md`

Where:
- `type`: Summary type (comprehensive, executive, key_points, overview, sections, search)
- `timestamp`: YYYYMMDD_HHMMSS format
- `custom_name`: User-provided custom name (sanitized)

### Filename Sanitization
- Invalid characters (`<>:"/\|?*`) are replaced with underscores
- Extra spaces are removed
- Filenames are limited to 100 characters
- Special characters are handled gracefully

### Examples
```
comprehensive_20251004_180125_climate_risk_guidelines.md
executive_20251004_180126_executive_brief.md
key_points_20251004_180127_key_points.md
overview_20251004_180130_document_overview.md
sections_20251004_180137_sectioned_analysis.md
search_20251004_180137_climate_risk_assessment.md
```

## File Content Format

### Markdown Structure
Each file follows a consistent markdown structure:

```markdown
# {Title}

## Document Information
- **Source File**: {source}
- **Generated**: {timestamp}
- **Summary Type**: {type}
- **Model Used**: {model}
- **Provider**: {provider}
- **Chunks Used**: {count}

## {Main Content Section}
{Content}

## Metadata
```json
{JSON metadata}
```

---
*Generated by RAG2 Document Processing System*
```

### Metadata Included
- Generation timestamp
- Model and provider information
- Chunk usage statistics
- Query information
- Source file details
- Processing parameters

## Custom Output Directories

You can specify custom output directories:

```python
# Custom output directory
summarizer = DocumentSummarizer(output_directory="./my_output")

# Or use MarkdownOutputManager directly
output_manager = MarkdownOutputManager("./custom_output")
```

## Index File

The system automatically generates an `index.md` file that:
- Lists all generated files by category
- Provides links to each file
- Shows directory structure
- Includes generation statistics
- Updates automatically with new files

## Error Handling

The system includes comprehensive error handling:

### File Save Errors
- Invalid filenames are sanitized
- Directory creation failures are handled gracefully
- Permission errors are caught and reported
- Disk space issues are detected

### Error Reporting
```python
result = summarizer.summarize_document(
    query="test",
    save_to_file=True
)

if "save_error" in result:
    print(f"Save failed: {result['save_error']}")
elif "file_path" in result:
    print(f"Saved to: {result['file_path']}")
```

## Best Practices

### 1. File Organization
- Use descriptive custom filenames
- Group related outputs in the same directory
- Regularly clean up old files
- Use the index file for navigation

### 2. Naming Conventions
- Use consistent naming patterns
- Include relevant keywords in filenames
- Avoid special characters
- Keep names concise but descriptive

### 3. Directory Management
- Use custom directories for different projects
- Keep output directories in version control (excluding generated files)
- Regularly archive old outputs
- Monitor disk usage

### 4. Error Handling
- Always check for save errors
- Implement fallback strategies
- Log file operations
- Validate file paths

## Integration Examples

### Batch Processing
```python
# Process multiple documents and save all outputs
documents = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
summarizer = DocumentSummarizer()

for doc in documents:
    # Scan document
    scanner.scan_pdf(doc)
    
    # Generate and save summary
    result = summarizer.summarize_document(
        query="comprehensive analysis",
        summary_type="comprehensive",
        source_filter=doc,
        save_to_file=True,
        custom_filename=f"analysis_{doc.replace('.pdf', '')}"
    )
```

### Custom Workflow
```python
# Custom workflow with file outputs
def analyze_document(pdf_path):
    # Scan document
    scanner.scan_pdf(pdf_path)
    
    # Generate different types of summaries
    summaries = {
        "executive": summarizer.summarize_document(
            query="executive summary",
            summary_type="executive",
            save_to_file=True,
            custom_filename="executive"
        ),
        "technical": summarizer.summarize_document(
            query="technical details methodology",
            summary_type="comprehensive",
            save_to_file=True,
            custom_filename="technical"
        )
    }
    
    # Generate overview
    overview = summarizer.get_document_overview(
        save_to_file=True,
        custom_filename="overview"
    )
    
    return summaries, overview
```

## Troubleshooting

### Common Issues

1. **Permission Denied**
   - Check directory write permissions
   - Ensure sufficient disk space
   - Verify file path validity

2. **Invalid Filenames**
   - System automatically sanitizes filenames
   - Check for reserved characters
   - Verify filename length

3. **Directory Creation Failed**
   - Check parent directory permissions
   - Verify path validity
   - Ensure sufficient disk space

4. **File Not Found After Save**
   - Check the returned file path
   - Verify directory structure
   - Look for error messages in logs

### Debug Commands

```bash
# Check output directory
ls -la output/

# View index file
cat output/index.md

# Check file permissions
ls -la output/summaries/

# Run output demo
uv run python output_demo.py
```

This file output functionality makes the RAG2 system much more practical for real-world use, allowing you to save, organize, and share your document analysis results easily.
