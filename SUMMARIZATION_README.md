# Document Summarization with ChromaDB and LLM

[Back to Readme](README.md)

This module provides advanced document summarization capabilities using ChromaDB for context retrieval and various LLM providers for text generation.

## Features

- **Context-Aware Summarization**: Uses ChromaDB to retrieve relevant document chunks
- **Multiple LLM Providers**: Supports OpenAI and Anthropic Claude
- **Various Summary Types**: Comprehensive, executive, key points, and sectioned summaries
- **Smart Chunk Retrieval**: Automatically finds the most relevant content
- **Metadata Tracking**: Tracks source files, chunk usage, and model information
- **Flexible API**: Both programmatic and command-line interfaces

## Quick Start

### 1. Set up API Keys

```bash
# For OpenAI
export OPENAI_API_KEY='your-openai-api-key'

# For Anthropic
export ANTHROPIC_API_KEY='your-anthropic-api-key'
```

### 2. Basic Usage

```python
from document_summarizer import DocumentSummarizer

# Initialize summarizer
summarizer = DocumentSummarizer(
    llm_provider='openai',  # or 'anthropic'
    collection_name='pdf_documents'
)

# Generate comprehensive summary
result = summarizer.summarize_document(
    query='climate risk management guidelines',
    summary_type='comprehensive'
)

print(result['summary'])
```

### 3. Command Line Usage

```bash
# Generate comprehensive summary
uv run python main.py summarize comprehensive

# Generate executive summary with custom query
uv run python main.py summarize executive "key findings recommendations"

# Extract key points
uv run python main.py summarize key_points "governance oversight"

# Get document overview
uv run python main.py overview openai

# Run full demo
uv run python main.py demo
```

## API Reference

### DocumentSummarizer Class

#### Constructor Parameters

- `collection_name` (str): Name of the ChromaDB collection (default: "pdf_documents")
- `persist_directory` (str): Directory where ChromaDB data is stored (default: "./chroma_db")
- `llm_provider` (str): LLM provider ("openai" or "anthropic")
- `model_name` (str, optional): Specific model to use
- `api_key` (str, optional): API key for the LLM provider

#### Key Methods

##### `summarize_document(query, summary_type, n_chunks, source_filter, max_tokens, temperature)`

Generate a summary of the document using ChromaDB context.

**Parameters:**
- `query` (str): Query to retrieve relevant chunks
- `summary_type` (str): Type of summary ("comprehensive", "executive", "key_points")
- `n_chunks` (int): Number of chunks to retrieve (default: 10)
- `source_filter` (str, optional): Filter by source file
- `max_tokens` (int): Maximum tokens for LLM response (default: 2000)
- `temperature` (float): Temperature for LLM generation (default: 0.7)

**Returns:**
- Dictionary with summary, metadata, and success status

##### `summarize_by_sections(source_filter, section_queries)`

Create a sectioned summary of the document.

**Parameters:**
- `source_filter` (str, optional): Filter by source file
- `section_queries` (dict, optional): Custom queries for different sections

**Returns:**
- Dictionary with sectioned summary

##### `get_document_overview(source_filter)`

Get a high-level overview of the document.

**Parameters:**
- `source_filter` (str, optional): Filter by source file

**Returns:**
- Dictionary with overview and document information

## Summary Types

### 1. Comprehensive Summary
- **Purpose**: Detailed analysis of the entire document
- **Use Case**: Research, detailed analysis, complete understanding
- **Features**: Main topics, key findings, important details, structure, conclusions

```python
result = summarizer.summarize_document(
    query='comprehensive overview main topics findings',
    summary_type='comprehensive',
    n_chunks=15
)
```

### 2. Executive Summary
- **Purpose**: High-level insights for decision-makers
- **Use Case**: Board presentations, executive briefings
- **Features**: Main purpose, key findings, critical insights, recommendations

```python
result = summarizer.summarize_document(
    query='executive summary key findings recommendations',
    summary_type='executive',
    n_chunks=8
)
```

### 3. Key Points
- **Purpose**: Bullet-point extraction of important information
- **Use Case**: Quick reference, action items, highlights
- **Features**: Bullet-point format, most important information

```python
result = summarizer.summarize_document(
    query='key points main findings important information',
    summary_type='key_points',
    n_chunks=10
)
```

### 4. Sectioned Summary
- **Purpose**: Organized summary by document sections
- **Use Case**: Structured analysis, section-by-section review
- **Features**: Multiple sections with custom queries

```python
sections = summarizer.summarize_by_sections(
    source_filter='document.pdf',
    section_queries={
        'introduction': 'introduction background context',
        'methodology': 'methodology approach framework',
        'findings': 'findings results analysis',
        'conclusions': 'conclusions recommendations'
    }
)
```

## Advanced Usage

### Custom Queries

You can use custom queries to focus on specific aspects of the document:

```python
# Focus on specific topics
result = summarizer.summarize_document(
    query='climate risk stress testing scenarios',
    summary_type='key_points'
)

# Focus on specific sections
result = summarizer.summarize_document(
    query='governance oversight responsibilities',
    summary_type='executive'
)
```

### Source Filtering

Filter summaries to specific source files:

```python
# Summarize only specific document
result = summarizer.summarize_document(
    query='risk management guidelines',
    source_filter='CPG229.pdf'
)
```

### Model Configuration

Use different models for different purposes:

```python
# Use GPT-4 for complex analysis
summarizer = DocumentSummarizer(
    llm_provider='openai',
    model_name='gpt-4'
)

# Use Claude for detailed summaries
summarizer = DocumentSummarizer(
    llm_provider='anthropic',
    model_name='claude-3-opus-20240229'
)
```

## Examples

### Example 1: Basic Document Summary

```python
from document_summarizer import DocumentSummarizer

# Initialize
summarizer = DocumentSummarizer(llm_provider='openai')

# Generate summary
result = summarizer.summarize_document(
    query='document overview main topics',
    summary_type='comprehensive'
)

if result['success']:
    print("Summary:", result['summary'])
    print("Chunks used:", result['metadata']['chunks_used'])
else:
    print("Error:", result['message'])
```

### Example 2: Executive Briefing

```python
# Generate executive summary
exec_summary = summarizer.summarize_document(
    query='executive summary key findings recommendations',
    summary_type='executive',
    n_chunks=5,
    max_tokens=1000
)

# Get document overview
overview = summarizer.get_document_overview()

print("Document Overview:")
print(overview['overview'])
print("\nExecutive Summary:")
print(exec_summary['summary'])
```

### Example 3: Sectioned Analysis

```python
# Create sectioned summary
sections = summarizer.summarize_by_sections(
    section_queries={
        'introduction': 'introduction background purpose',
        'methodology': 'methodology approach framework',
        'risk_assessment': 'risk assessment climate risks',
        'governance': 'governance oversight management',
        'implementation': 'implementation recommendations'
    }
)

for section_name, section_data in sections['sections'].items():
    print(f"\n{section_name.upper()}:")
    print(section_data['summary'])
```

### Example 4: Custom Query Analysis

```python
# Analyze specific aspects
queries = [
    'climate risk management guidelines',
    'stress testing requirements',
    'governance responsibilities',
    'implementation timeline'
]

for query in queries:
    result = summarizer.summarize_document(
        query=query,
        summary_type='key_points',
        n_chunks=3
    )
    print(f"\n{query.upper()}:")
    print(result['summary'])
```

## Error Handling

The summarizer includes comprehensive error handling:

```python
try:
    result = summarizer.summarize_document(
        query='your query',
        summary_type='comprehensive'
    )
    
    if result['success']:
        print("Summary:", result['summary'])
    else:
        print("Error:", result['message'])
        
except Exception as e:
    print(f"Unexpected error: {str(e)}")
```

## Performance Tips

1. **Chunk Selection**: Use appropriate `n_chunks` based on document size
2. **Query Specificity**: More specific queries yield better results
3. **Model Selection**: Choose models based on complexity needs
4. **Token Limits**: Adjust `max_tokens` based on summary type
5. **Temperature**: Lower values (0.3-0.5) for factual summaries, higher (0.7-0.9) for creative summaries

## Troubleshooting

### Common Issues

1. **API Key Not Set**: Ensure environment variables are properly set
2. **No Chunks Found**: Check if documents are properly scanned into ChromaDB
3. **Model Not Available**: Verify model name and provider compatibility
4. **Token Limits**: Reduce `max_tokens` or `n_chunks` if hitting limits

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Integration with PDF Scanner

The summarizer works seamlessly with the PDF scanner:

```python
# First, scan PDFs
from pdf_scanner import PDFScanner
scanner = PDFScanner()
scanner.scan_pdf('document.pdf')

# Then summarize
from document_summarizer import DocumentSummarizer
summarizer = DocumentSummarizer()
result = summarizer.summarize_document('document overview')
```

## File Structure

```
rag2/
├── document_summarizer.py    # Main summarizer class
├── summarize_demo.py         # Full demo script
├── example_summarization.py  # Simple examples
├── main.py                   # CLI interface
├── pdf_scanner.py           # PDF scanning functionality
└── chroma_db/               # ChromaDB persistence directory
```

This summarization system provides a powerful way to extract insights from your PDF documents using the latest LLM technology while maintaining context through ChromaDB vector search.
