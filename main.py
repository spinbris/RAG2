"""
Main module demonstrating PDF scanning and ChromaDB integration.
"""

import os
import sys
from pathlib import Path
from pdf_scanner import PDFScanner
from document_summarizer import DocumentSummarizer
from config import config


def main():
    """Main function demonstrating PDF scanning capabilities."""
    print("PDF Scanner for ChromaDB Integration")
    print("=" * 40)
    
    # Initialize the PDF scanner using config
    scanner = PDFScanner(
        collection_name=config.CHROMA_COLLECTION_NAME,
        persist_directory=config.CHROMA_PERSIST_DIRECTORY,
        chunk_size=config.PDF_CHUNK_SIZE,
        chunk_overlap=config.PDF_CHUNK_OVERLAP
    )
    
    # Check if PDF files exist in the data directory
    data_dir = Path("data")
    if not data_dir.exists():
        data_dir.mkdir()
        print(f"Created data directory: {data_dir}")
    
    # Look for PDF files
    pdf_files = list(data_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {data_dir}")
        print("Please add PDF files to the 'data' directory and run again.")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s) to process:")
    for pdf_file in pdf_files:
        print(f"  - {pdf_file.name}")
    
    # Process each PDF file
    print("\nProcessing PDF files...")
    for pdf_file in pdf_files:
        print(f"\nScanning: {pdf_file.name}")
        try:
            result = scanner.scan_pdf(str(pdf_file))
            if result["success"]:
                print(f"  ✓ Successfully processed {result['chunks_added']} chunks")
                print(f"  ✓ Total characters: {result['total_characters']}")
            else:
                print(f"  ✗ Failed: {result['message']}")
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
    
    # Display collection information
    print("\nChromaDB Collection Information:")
    print("-" * 30)
    try:
        info = scanner.get_collection_info()
        print(f"Collection: {info['collection_name']}")
        print(f"Total documents: {info['total_documents']}")
        print(f"Persist directory: {info['persist_directory']}")
    except Exception as e:
        print(f"Error getting collection info: {str(e)}")
    
    # Demonstrate search functionality
    print("\nSearch Demo:")
    print("-" * 15)
    search_queries = [
        "introduction",
        "conclusion", 
        "methodology",
        "results"
    ]
    
    for query in search_queries:
        try:
            results = scanner.search_documents(query, n_results=3)
            print(f"\nQuery: '{query}'")
            print(f"Found {results['count']} results")
            
            if results['results']['documents'] and results['results']['documents'][0]:
                for i, (doc, metadata) in enumerate(zip(
                    results['results']['documents'][0][:2],  # Show first 2 results
                    results['results']['metadatas'][0][:2]
                )):
                    print(f"  {i+1}. Source: {metadata['source']}")
                    print(f"     Chunk {metadata['chunk_index']}/{metadata['total_chunks']}")
                    print(f"     Preview: {doc[:100]}...")
        except Exception as e:
            print(f"Search error for '{query}': {str(e)}")


def scan_single_pdf(pdf_path: str):
    """Scan a single PDF file."""
    scanner = PDFScanner()
    
    try:
        result = scanner.scan_pdf(pdf_path)
        if result["success"]:
            print(f"Successfully processed {pdf_path}")
            print(f"Chunks added: {result['chunks_added']}")
            print(f"Total characters: {result['total_characters']}")
        else:
            print(f"Failed to process {pdf_path}: {result['message']}")
    except Exception as e:
        print(f"Error processing {pdf_path}: {str(e)}")


def search_documents(query: str, n_results: int = 5):
    """Search documents in ChromaDB."""
    scanner = PDFScanner()
    
    try:
        results = scanner.search_documents(query, n_results)
        print(f"Search results for '{query}':")
        print(f"Found {results['count']} results")
        
        if results['results']['documents'] and results['results']['documents'][0]:
            for i, (doc, metadata) in enumerate(zip(
                results['results']['documents'][0],
                results['results']['metadatas'][0]
            )):
                print(f"\n{i+1}. Source: {metadata['source']}")
                print(f"   Chunk {metadata['chunk_index']}/{metadata['total_chunks']}")
                print(f"   Content: {doc[:200]}...")
    except Exception as e:
        print(f"Search error: {str(e)}")


def summarize_document(summary_type: str = "comprehensive", 
                      query: str = "summary overview main topics",
                      source_file: str = None,
                      provider: str = None,
                      save_to_file: bool = False,
                      custom_filename: str = None):
    """Summarize documents using ChromaDB and LLM."""
    try:
        # Use config default if provider not specified
        provider = provider or config.DEFAULT_LLM_PROVIDER
        
        # Check for API key
        api_key = config.get_api_key(provider)
        if not api_key:
            print(f"❌ {provider.upper()}_API_KEY not found in configuration")
            print("Please set it in your .env file or environment variables")
            return
        
        print(f"🤖 Initializing {provider} summarizer...")
        summarizer = DocumentSummarizer(llm_provider=provider)
        
        print(f"📝 Generating {summary_type} summary...")
        result = summarizer.summarize_document(
            query=query,
            summary_type=summary_type,
            n_chunks=config.DEFAULT_N_CHUNKS,
            source_filter=source_file,
            max_tokens=config.DEFAULT_MAX_TOKENS,
            save_to_file=save_to_file,
            custom_filename=custom_filename
        )
        
        if result["success"]:
            print("✅ Summary generated successfully!")
            print(f"📊 Used {result['metadata']['chunks_used']} chunks")
            print(f"🤖 Model: {result['metadata']['model_used']}")
            
            if save_to_file and "file_path" in result:
                print(f"💾 Summary saved to: {result['file_path']}")
            elif save_to_file and "save_error" in result:
                print(f"❌ Failed to save file: {result['save_error']}")
            
            print("\n" + "="*60)
            print("SUMMARY:")
            print("="*60)
            print(result["summary"])
        else:
            print(f"❌ Failed to generate summary: {result['message']}")
            
    except Exception as e:
        print(f"❌ Error during summarization: {str(e)}")


def get_document_overview(provider: str = None, source_file: str = None, save_to_file: bool = False, custom_filename: str = None):
    """Get a high-level overview of the document."""
    try:
        # Use config default if provider not specified
        provider = provider or config.DEFAULT_LLM_PROVIDER
        
        # Check for API key
        api_key = config.get_api_key(provider)
        if not api_key:
            print(f"❌ {provider.upper()}_API_KEY not found in configuration")
            print("Please set it in your .env file or environment variables")
            return
        
        print(f"🤖 Getting document overview using {provider}...")
        summarizer = DocumentSummarizer(llm_provider=provider)
        
        result = summarizer.get_document_overview(
            source_filter=source_file,
            save_to_file=save_to_file,
            custom_filename=custom_filename
        )
        
        if result["success"]:
            print("✅ Document overview generated!")
            
            if save_to_file and "file_path" in result:
                print(f"💾 Overview saved to: {result['file_path']}")
            elif save_to_file and "save_error" in result:
                print(f"❌ Failed to save file: {result['save_error']}")
            
            print("\n" + "="*60)
            print("OVERVIEW:")
            print("="*60)
            print(result["overview"])
            
            doc_info = result["document_info"]
            print(f"\n📊 Document Info:")
            print(f"   Total chunks: {doc_info['total_chunks']}")
            print(f"   Source files: {', '.join(doc_info['source_files'])}")
        else:
            print(f"❌ Failed to get overview: {result['message']}")
            
    except Exception as e:
        print(f"❌ Error getting overview: {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "scan" and len(sys.argv) > 2:
            # Scan a specific PDF file
            pdf_path = sys.argv[2]
            scan_single_pdf(pdf_path)
        elif command == "search" and len(sys.argv) > 2:
            # Search documents
            query = " ".join(sys.argv[2:])
            search_documents(query)
        elif command == "summarize":
            # Summarize documents
            summary_type = sys.argv[2] if len(sys.argv) > 2 else "comprehensive"
            query = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else "summary overview main topics"
            provider = "openai"  # Default to OpenAI
            save_to_file = "--save" in sys.argv or "-s" in sys.argv
            custom_filename = None
            if "--filename" in sys.argv:
                filename_idx = sys.argv.index("--filename")
                if filename_idx + 1 < len(sys.argv):
                    custom_filename = sys.argv[filename_idx + 1]
            summarize_document(summary_type, query, None, provider, save_to_file, custom_filename)
        elif command == "overview":
            # Get document overview
            provider = sys.argv[2] if len(sys.argv) > 2 else "openai"
            save_to_file = "--save" in sys.argv or "-s" in sys.argv
            custom_filename = None
            if "--filename" in sys.argv:
                filename_idx = sys.argv.index("--filename")
                if filename_idx + 1 < len(sys.argv):
                    custom_filename = sys.argv[filename_idx + 1]
            get_document_overview(provider, None, save_to_file, custom_filename)
        elif command == "demo":
            # Run the full demo
            import subprocess
            subprocess.run([sys.executable, "summarize_demo.py"])
        elif command == "config":
            # Show configuration
            config.print_config_summary()
        else:
            print("Usage:")
            print("  python main.py                           # Process all PDFs in data/ directory")
            print("  python main.py scan <pdf_path>           # Scan a specific PDF file")
            print("  python main.py search <query>            # Search documents")
            print("  python main.py summarize [type] [query] [--save] [--filename name]  # Summarize documents")
            print("  python main.py overview [provider] [--save] [--filename name]       # Get document overview")
            print("  python main.py demo                      # Run full summarization demo")
            print("  python main.py config                    # Show configuration status")
            print("")
            print("Options:")
            print("  --save, -s                               # Save output to markdown file")
            print("  --filename <name>                        # Custom filename for saved file")
            print("")
            print("Summary types: comprehensive, executive, key_points")
            print("Providers: openai, anthropic, groq, deepseek")
            print("")
            print("Examples:")
            print("  python main.py summarize executive --save")
            print("  python main.py summarize comprehensive 'climate risk' --save --filename my_summary")
            print("  python main.py overview openai --save")
    else:
        # Default: process all PDFs in data directory
        main()
