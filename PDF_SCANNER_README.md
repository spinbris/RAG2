# PDF Scanner for ChromaDB Integration

This project provides a comprehensive solution for scanning PDF files and storing their content in ChromaDB for vector search and retrieval.

## Features

- **PDF Text Extraction**: Extract text content from PDF files using PyPDF
- **Text Chunking**: Split large documents into manageable chunks using LangChain's text splitter
- **ChromaDB Integration**: Store document chunks in ChromaDB with metadata
- **Vector Search**: Search through documents using semantic similarity
- **Batch Processing**: Process multiple PDFs at once
- **Collection Management**: Manage document collections and metadata

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Or install with uv:
```bash
uv sync
```

## Quick Start

### 1. Basic Usage

```python
from pdf_scanner import PDFScanner

# Initialize scanner
scanner = PDFScanner(
    collection_name="my_documents",
    persist_directory="./chroma_db",
    chunk_size=1000,
    chunk_overlap=200
)

# Scan a PDF file
result = scanner.scan_pdf("path/to/your/document.pdf")
print(f"Processed {result['chunks_added']} chunks")
```

### 2. Command Line Usage

```bash
# Process all PDFs in data/ directory
python main.py

# Scan a specific PDF file
python main.py scan path/to/document.pdf

# Search documents
python main.py search "your search query"
```

### 3. Search Documents

```python
# Search for relevant documents
results = scanner.search_documents("machine learning", n_results=5)

for doc, metadata in zip(results['results']['documents'][0], 
                        results['results']['metadatas'][0]):
    print(f"Source: {metadata['source']}")
    print(f"Content: {doc[:200]}...")
```

## API Reference

### PDFScanner Class

#### Constructor Parameters

- `collection_name` (str): Name of the ChromaDB collection (default: "pdf_documents")
- `persist_directory` (str): Directory to persist ChromaDB data (default: "./chroma_db")
- `chunk_size` (int): Size of text chunks for splitting (default: 1000)
- `chunk_overlap` (int): Overlap between chunks (default: 200)

#### Key Methods

##### `scan_pdf(pdf_path: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]`
Complete pipeline to scan a PDF and store it in ChromaDB.

**Parameters:**
- `pdf_path`: Path to the PDF file
- `metadata`: Additional metadata for the document

**Returns:**
- Dictionary with scan results including success status, chunks added, and total characters

##### `scan_directory(directory_path: str, pattern: str = "*.pdf") -> List[Dict[str, Any]]`
Scan all PDF files in a directory.

**Parameters:**
- `directory_path`: Path to directory containing PDFs
- `pattern`: File pattern to match (default: "*.pdf")

**Returns:**
- List of scan results for each file

##### `search_documents(query: str, n_results: int = 5, where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`
Search for documents in ChromaDB.

**Parameters:**
- `query`: Search query
- `n_results`: Number of results to return
- `where`: Optional metadata filter

**Returns:**
- Search results with documents, metadata, and relevance scores

##### `get_collection_info() -> Dict[str, Any]`
Get information about the ChromaDB collection.

**Returns:**
- Collection information including name, total documents, and persist directory

##### `delete_document(source_filename: str) -> bool`
Delete all chunks for a specific document.

**Parameters:**
- `source_filename`: Name of the source PDF file

**Returns:**
- True if successful

## Examples

### Example 1: Basic PDF Processing

```python
from pdf_scanner import PDFScanner

scanner = PDFScanner()
result = scanner.scan_pdf("document.pdf")

if result["success"]:
    print(f"Successfully processed {result['chunks_added']} chunks")
else:
    print(f"Failed: {result['message']}")
```

### Example 2: Batch Processing

```python
# Process all PDFs in a directory
results = scanner.scan_directory("./documents")

for result in results:
    if result["success"]:
        print(f"✓ {result['message']}")
    else:
        print(f"✗ {result['message']}")
```

### Example 3: Advanced Search

```python
# Search with metadata filtering
results = scanner.search_documents(
    query="machine learning",
    n_results=10,
    where={"source": "research_paper.pdf"}
)

# Display results
for doc, metadata in zip(results['results']['documents'][0], 
                        results['results']['metadatas'][0]):
    print(f"Source: {metadata['source']}")
    print(f"Chunk: {metadata['chunk_index']}/{metadata['total_chunks']}")
    print(f"Content: {doc[:200]}...")
    print("-" * 50)
```

## File Structure

```
rag2/
├── main.py                 # Main entry point with CLI interface
├── pdf_scanner.py         # Core PDFScanner class
├── example_usage.py       # Usage examples
├── data/                  # Directory for PDF files
├── chroma_db/            # ChromaDB persistence directory
└── requirements.txt       # Dependencies
```

## Dependencies

- `chromadb`: Vector database for storing and searching documents
- `pypdf`: PDF text extraction
- `langchain`: Text splitting and document processing
- `pathlib`: File path handling

## Error Handling

The scanner includes comprehensive error handling:

- File not found errors
- PDF parsing errors
- ChromaDB connection errors
- Text extraction failures

All methods return detailed error information in their response dictionaries.

## Performance Considerations

- **Chunk Size**: Larger chunks provide more context but may reduce search precision
- **Chunk Overlap**: Higher overlap improves context continuity but increases storage
- **Batch Processing**: Process multiple files for better efficiency
- **Memory Usage**: Large PDFs are processed page by page to manage memory

## Troubleshooting

### Common Issues

1. **PDF not found**: Ensure the file path is correct and the file exists
2. **No text extracted**: Some PDFs may be image-based or have text extraction issues
3. **ChromaDB errors**: Check that the persist directory is writable
4. **Memory issues**: Reduce chunk size for very large documents

### Debug Mode

Enable debug logging to see detailed processing information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## License

This project is part of the rag2 workspace and follows the same licensing terms.
