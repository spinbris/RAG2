"""
Demo script for document summarization using ChromaDB and LLM.

This script demonstrates how to use the DocumentSummarizer class to
generate various types of summaries from documents stored in ChromaDB.
"""

import os
import sys
from pathlib import Path
from document_summarizer import DocumentSummarizer
from config import config


def setup_environment():
    """Set up environment variables for LLM providers."""
    print("Setting up environment for LLM providers...")
    
    # Check for available providers using config
    available_providers = config.get_available_providers()
    
    if not available_providers:
        print("⚠️  No API keys found in configuration.")
        print("Please set one of the following in your .env file:")
        print("  OPENAI_API_KEY=your-openai-key")
        print("  ANTHROPIC_API_KEY=your-anthropic-key")
        print("  GROQ_API_KEY=your-groq-key")
        print("  DEEPSEEK_API_KEY=your-deepseek-key")
        print("\nFor demo purposes, we'll use a mock summarizer.")
        return "mock"
    
    print(f"✓ Found API keys for: {', '.join(available_providers)}")
    return available_providers[0]  # Use first available provider


def demo_comprehensive_summary(summarizer, source_file=None):
    """Demonstrate comprehensive document summarization."""
    print("\n" + "="*60)
    print("COMPREHENSIVE DOCUMENT SUMMARY")
    print("="*60)
    
    result = summarizer.summarize_document(
        query="comprehensive overview main topics findings conclusions",
        summary_type="comprehensive",
        n_chunks=15,
        source_filter=source_file,
        max_tokens=3000
    )
    
    if result["success"]:
        print("✅ Summary generated successfully!")
        print(f"📊 Used {result['metadata']['chunks_used']} chunks")
        print(f"🤖 Model: {result['metadata']['model_used']}")
        print("\n" + "-"*60)
        print("SUMMARY:")
        print("-"*60)
        print(result["summary"])
    else:
        print(f"❌ Failed to generate summary: {result['message']}")


def demo_executive_summary(summarizer, source_file=None):
    """Demonstrate executive summary generation."""
    print("\n" + "="*60)
    print("EXECUTIVE SUMMARY")
    print("="*60)
    
    result = summarizer.summarize_document(
        query="executive summary key findings recommendations",
        summary_type="executive",
        n_chunks=8,
        source_filter=source_file,
        max_tokens=1500
    )
    
    if result["success"]:
        print("✅ Executive summary generated successfully!")
        print("\n" + "-"*60)
        print("EXECUTIVE SUMMARY:")
        print("-"*60)
        print(result["summary"])
    else:
        print(f"❌ Failed to generate executive summary: {result['message']}")


def demo_key_points(summarizer, source_file=None):
    """Demonstrate key points extraction."""
    print("\n" + "="*60)
    print("KEY POINTS EXTRACTION")
    print("="*60)
    
    result = summarizer.summarize_document(
        query="key points main findings important information",
        summary_type="key_points",
        n_chunks=10,
        source_filter=source_file,
        max_tokens=2000
    )
    
    if result["success"]:
        print("✅ Key points extracted successfully!")
        print("\n" + "-"*60)
        print("KEY POINTS:")
        print("-"*60)
        print(result["summary"])
    else:
        print(f"❌ Failed to extract key points: {result['message']}")


def demo_sectioned_summary(summarizer, source_file=None):
    """Demonstrate sectioned summary generation."""
    print("\n" + "="*60)
    print("SECTIONED SUMMARY")
    print("="*60)
    
    # Custom section queries for the CPG229 document
    section_queries = {
        "introduction": "introduction background context purpose scope",
        "methodology": "methodology approach framework guidelines procedures",
        "risk_assessment": "risk assessment climate risks financial risks",
        "scenario_analysis": "scenario analysis stress testing climate scenarios",
        "governance": "governance oversight management responsibilities",
        "implementation": "implementation recommendations next steps action items"
    }
    
    result = summarizer.summarize_by_sections(
        source_filter=source_file,
        section_queries=section_queries
    )
    
    if result["success"]:
        print("✅ Sectioned summary generated successfully!")
        print(f"📊 Generated {result['metadata']['total_sections']} sections")
        
        for section_name, section_data in result["sections"].items():
            if section_data["success"]:
                print(f"\n📋 {section_name.upper().replace('_', ' ')}:")
                print("-" * 40)
                print(section_data["summary"])
            else:
                print(f"❌ Failed to generate {section_name} section")
    else:
        print(f"❌ Failed to generate sectioned summary: {result['message']}")


def demo_document_overview(summarizer, source_file=None):
    """Demonstrate document overview generation."""
    print("\n" + "="*60)
    print("DOCUMENT OVERVIEW")
    print("="*60)
    
    result = summarizer.get_document_overview(source_filter=source_file)
    
    if result["success"]:
        print("✅ Document overview generated successfully!")
        print("\n" + "-"*60)
        print("OVERVIEW:")
        print("-"*60)
        print(result["overview"])
        
        print("\n" + "-"*60)
        print("DOCUMENT INFO:")
        print("-"*60)
        doc_info = result["document_info"]
        print(f"📄 Total chunks: {doc_info['total_chunks']}")
        print(f"📁 Source files: {', '.join(doc_info['source_files'])}")
        print(f"📏 Chunk size range: {doc_info['chunk_size_range']['min']}-{doc_info['chunk_size_range']['max']} characters")
    else:
        print(f"❌ Failed to generate document overview: {result['message']}")


def demo_custom_query_summary(summarizer, source_file=None):
    """Demonstrate custom query-based summarization."""
    print("\n" + "="*60)
    print("CUSTOM QUERY SUMMARY")
    print("="*60)
    
    # Example custom queries for the CPG229 document
    custom_queries = [
        "climate risk management guidelines",
        "stress testing requirements",
        "governance and oversight responsibilities",
        "implementation timeline and milestones"
    ]
    
    for i, query in enumerate(custom_queries, 1):
        print(f"\n🔍 Query {i}: '{query}'")
        print("-" * 50)
        
        result = summarizer.summarize_document(
            query=query,
            summary_type="key_points",
            n_chunks=5,
            source_filter=source_file,
            max_tokens=1000
        )
        
        if result["success"]:
            print("✅ Summary generated!")
            print(result["summary"][:300] + "..." if len(result["summary"]) > 300 else result["summary"])
        else:
            print(f"❌ Failed: {result['message']}")


def main():
    """Main demo function."""
    print("🤖 Document Summarization Demo using ChromaDB + LLM")
    print("=" * 70)
    
    # Set up environment
    provider = setup_environment()
    
    # Check if ChromaDB collection exists
    if not Path("./chroma_db").exists():
        print("❌ ChromaDB collection not found. Please run the PDF scanner first:")
        print("   uv run python main.py")
        return
    
    # Initialize summarizer
    try:
        if provider == "mock":
            print("Using mock summarizer (no actual LLM calls)")
            # For demo purposes, we'll create a mock summarizer
            summarizer = None
        else:
            summarizer = DocumentSummarizer(
                collection_name="pdf_documents",
                persist_directory="./chroma_db",
                llm_provider=provider
            )
    except Exception as e:
        print(f"❌ Failed to initialize summarizer: {str(e)}")
        return
    
    # Get available source files
    try:
        from pdf_scanner import PDFScanner
        scanner = PDFScanner(collection_name="pdf_documents", persist_directory="./chroma_db")
        collection_info = scanner.get_collection_info()
        
        if collection_info["total_documents"] == 0:
            print("❌ No documents found in ChromaDB. Please scan some PDFs first.")
            return
        
        print(f"📚 Found {collection_info['total_documents']} document chunks in ChromaDB")
        
        # Get source files
        results = scanner.search_documents("document", n_results=1)
        if results['results']['metadatas'] and results['results']['metadatas'][0]:
            source_files = list(set(meta['source'] for meta in results['results']['metadatas'][0]))
            print(f"📁 Available source files: {', '.join(source_files)}")
            source_file = source_files[0] if source_files else None
        else:
            source_file = None
            
    except Exception as e:
        print(f"⚠️  Could not determine source files: {str(e)}")
        source_file = None
    
    if provider == "mock":
        print("\n🎭 MOCK DEMO MODE")
        print("(Set up API keys to see actual LLM-generated summaries)")
        print("\nThis demo would normally show:")
        print("1. Comprehensive document summary")
        print("2. Executive summary")
        print("3. Key points extraction")
        print("4. Sectioned summary")
        print("5. Document overview")
        print("6. Custom query summaries")
        return
    
    # Run demos
    try:
        # 1. Document Overview
        demo_document_overview(summarizer, source_file)
        
        # 2. Executive Summary
        demo_executive_summary(summarizer, source_file)
        
        # 3. Key Points
        demo_key_points(summarizer, source_file)
        
        # 4. Comprehensive Summary
        demo_comprehensive_summary(summarizer, source_file)
        
        # 5. Sectioned Summary
        demo_sectioned_summary(summarizer, source_file)
        
        # 6. Custom Query Summary
        demo_custom_query_summary(summarizer, source_file)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {str(e)}")
    
    print("\n" + "="*70)
    print("🎉 Demo completed!")
    print("\nTo use the summarizer in your own code:")
    print("```python")
    print("from document_summarizer import DocumentSummarizer")
    print("")
    print("summarizer = DocumentSummarizer(")
    print("    llm_provider='openai',  # or 'anthropic'")
    print("    collection_name='pdf_documents'")
    print(")")
    print("")
    print("result = summarizer.summarize_document(")
    print("    query='your search query',")
    print("    summary_type='comprehensive'")
    print(")")
    print("```")


if __name__ == "__main__":
    main()
