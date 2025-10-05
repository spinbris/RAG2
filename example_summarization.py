"""
Simple example of using the Document Summarizer with ChromaDB.

This example shows how to use the summarizer without requiring actual API keys.
"""

from document_summarizer import DocumentSummarizer
from pdf_scanner import PDFScanner


def example_without_api_keys():
    """Example showing how the system works without API keys."""
    print("🔍 Document Summarization Example")
    print("=" * 50)
    
    # Initialize the PDF scanner to access ChromaDB
    scanner = PDFScanner(
        collection_name="pdf_documents",
        persist_directory="./chroma_db"
    )
    
    # Get collection information
    info = scanner.get_collection_info()
    print(f"📚 Collection: {info['collection_name']}")
    print(f"📊 Total chunks: {info['total_documents']}")
    
    # Search for relevant chunks
    print("\n🔍 Searching for relevant content...")
    results = scanner.search_documents("climate risk management guidelines", n_results=5)
    
    if results['count'] > 0:
        print(f"✅ Found {results['count']} relevant chunks")
        
        # Show the retrieved chunks
        print("\n📄 Retrieved Chunks:")
        print("-" * 40)
        
        for i, (doc, metadata) in enumerate(zip(
            results['results']['documents'][0],
            results['results']['metadatas'][0]
        )):
            print(f"\n{i+1}. Source: {metadata['source']}")
            print(f"   Chunk {metadata['chunk_index']}/{metadata['total_chunks']}")
            print(f"   Content preview: {doc[:200]}...")
    
    else:
        print("❌ No relevant chunks found")
    
    # Demonstrate different search queries
    print("\n🔍 Different Search Queries:")
    print("-" * 40)
    
    queries = [
        "introduction overview",
        "methodology approach",
        "risk assessment",
        "governance oversight",
        "implementation recommendations"
    ]
    
    for query in queries:
        results = scanner.search_documents(query, n_results=2)
        print(f"\nQuery: '{query}'")
        print(f"Results: {results['count']} chunks found")
        
        if results['count'] > 0:
            # Show first result
            first_doc = results['results']['documents'][0][0]
            first_meta = results['results']['metadatas'][0][0]
            print(f"  → {first_meta['source']} (chunk {first_meta['chunk_index']})")
            print(f"    {first_doc[:100]}...")


def example_with_mock_summarizer():
    """Example showing how to use the summarizer (requires API keys)."""
    print("\n🤖 LLM Summarization Example")
    print("=" * 50)
    print("To use actual LLM summarization, you need to:")
    print("1. Set up an API key:")
    print("   export OPENAI_API_KEY='your-key'")
    print("   # OR")
    print("   export ANTHROPIC_API_KEY='your-key'")
    print("")
    print("2. Then you can use:")
    print("   from document_summarizer import DocumentSummarizer")
    print("   ")
    print("   summarizer = DocumentSummarizer(")
    print("       llm_provider='openai',  # or 'anthropic'")
    print("       collection_name='pdf_documents'")
    print("   )")
    print("   ")
    print("   # Generate different types of summaries")
    print("   result = summarizer.summarize_document(")
    print("       query='climate risk management',")
    print("       summary_type='comprehensive'")
    print("   )")
    print("   ")
    print("   # Get document overview")
    print("   overview = summarizer.get_document_overview()")
    print("   ")
    print("   # Generate sectioned summary")
    print("   sections = summarizer.summarize_by_sections()")


def show_available_commands():
    """Show available command-line commands."""
    print("\n💻 Available Commands")
    print("=" * 50)
    print("Command Line Usage:")
    print("")
    print("1. Process PDFs:")
    print("   uv run python main.py")
    print("")
    print("2. Search documents:")
    print("   uv run python main.py search 'your query'")
    print("")
    print("3. Summarize documents (requires API key):")
    print("   uv run python main.py summarize comprehensive")
    print("   uv run python main.py summarize executive 'climate risk'")
    print("   uv run python main.py summarize key_points 'governance'")
    print("")
    print("4. Get document overview (requires API key):")
    print("   uv run python main.py overview openai")
    print("   uv run python main.py overview anthropic")
    print("")
    print("5. Run full demo (requires API key):")
    print("   uv run python main.py demo")


if __name__ == "__main__":
    example_without_api_keys()
    example_with_mock_summarizer()
    show_available_commands()
    
    print("\n🎉 Example completed!")
    print("The system is ready to use with your PDF documents!")
