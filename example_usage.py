"""
Example usage of the PDF Scanner for ChromaDB integration.

This script demonstrates how to use the PDFScanner class to:
1. Scan PDF files and store them in ChromaDB
2. Search through the stored documents
3. Manage the document collection
"""

from pdf_scanner import PDFScanner
from pathlib import Path


def example_basic_usage():
    """Basic example of scanning a PDF file."""
    print("=== Basic PDF Scanning Example ===")
    
    # Initialize the scanner
    scanner = PDFScanner(
        collection_name="example_docs",
        persist_directory="./example_chroma_db",
        chunk_size=500,  # Smaller chunks for this example
        chunk_overlap=100
    )
    
    # Example: Scan a PDF file (replace with actual PDF path)
    pdf_path = "data/sample.pdf"  # You would replace this with an actual PDF
    
    if Path(pdf_path).exists():
        print(f"Scanning PDF: {pdf_path}")
        result = scanner.scan_pdf(pdf_path)
        
        if result["success"]:
            print(f"✓ Successfully processed {result['chunks_added']} chunks")
            print(f"✓ Total characters: {result['total_characters']}")
        else:
            print(f"✗ Failed: {result['message']}")
    else:
        print(f"PDF file not found: {pdf_path}")
        print("Please add a PDF file to the data directory")


def example_search_functionality():
    """Example of searching through stored documents."""
    print("\n=== Search Functionality Example ===")
    
    scanner = PDFScanner(
        collection_name="example_docs",
        persist_directory="./example_chroma_db"
    )
    
    # Search for documents
    queries = [
        "introduction",
        "conclusion",
        "data analysis",
        "methodology"
    ]
    
    for query in queries:
        print(f"\nSearching for: '{query}'")
        results = scanner.search_documents(query, n_results=3)
        
        print(f"Found {results['count']} results")
        
        if results['results']['documents'] and results['results']['documents'][0]:
            for i, (doc, metadata) in enumerate(zip(
                results['results']['documents'][0][:2],  # Show first 2 results
                results['results']['metadatas'][0][:2]
            )):
                print(f"  {i+1}. Source: {metadata['source']}")
                print(f"     Chunk {metadata['chunk_index']}/{metadata['total_chunks']}")
                print(f"     Preview: {doc[:150]}...")


def example_collection_management():
    """Example of managing the document collection."""
    print("\n=== Collection Management Example ===")
    
    scanner = PDFScanner(
        collection_name="example_docs",
        persist_directory="./example_chroma_db"
    )
    
    # Get collection information
    info = scanner.get_collection_info()
    print(f"Collection: {info['collection_name']}")
    print(f"Total documents: {info['total_documents']}")
    print(f"Persist directory: {info['persist_directory']}")
    
    # Example: Delete a specific document (uncomment if needed)
    # filename = "sample.pdf"
    # if scanner.delete_document(filename):
    #     print(f"✓ Deleted all chunks for {filename}")
    # else:
    #     print(f"✗ Failed to delete chunks for {filename}")


def example_batch_processing():
    """Example of processing multiple PDFs in a directory."""
    print("\n=== Batch Processing Example ===")
    
    scanner = PDFScanner(
        collection_name="batch_docs",
        persist_directory="./batch_chroma_db"
    )
    
    # Process all PDFs in a directory
    data_dir = Path("data")
    if data_dir.exists():
        results = scanner.scan_directory(str(data_dir))
        
        print(f"Processed {len(results)} files:")
        for result in results:
            if result["success"]:
                print(f"  ✓ {result['message']} ({result['chunks_added']} chunks)")
            else:
                print(f"  ✗ {result['message']}")
    else:
        print("Data directory not found. Please create it and add PDF files.")


if __name__ == "__main__":
    print("PDF Scanner for ChromaDB - Example Usage")
    print("=" * 50)
    
    # Run examples
    example_basic_usage()
    example_search_functionality()
    example_collection_management()
    example_batch_processing()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("\nTo use with your own PDFs:")
    print("1. Add PDF files to the 'data' directory")
    print("2. Run: python main.py")
    print("3. Or run: python main.py scan <path_to_pdf>")
    print("4. Search with: python main.py search <your_query>")
