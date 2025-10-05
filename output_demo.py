"""
Demo script for file output functionality.

This script demonstrates how to save summaries and results to markdown files
using the enhanced DocumentSummarizer and output utilities.
"""

import os
import sys
from pathlib import Path
from document_summarizer import DocumentSummarizer
from output_utils import MarkdownOutputManager
from pdf_scanner import PDFScanner
from config import config


def demo_basic_file_saving():
    """Demonstrate basic file saving functionality."""
    print("📁 Basic File Saving Demo")
    print("=" * 50)
    
    # Initialize summarizer
    summarizer = DocumentSummarizer()
    
    # Generate and save a comprehensive summary
    print("1. Generating comprehensive summary...")
    result = summarizer.summarize_document(
        query="climate risk management guidelines",
        summary_type="comprehensive",
        n_chunks=5,
        save_to_file=True,
        custom_filename="climate_risk_guidelines"
    )
    
    if result["success"]:
        print(f"✅ Summary generated and saved to: {result.get('file_path', 'Unknown')}")
    else:
        print(f"❌ Failed: {result.get('message', 'Unknown error')}")
    
    # Generate and save an executive summary
    print("\n2. Generating executive summary...")
    result = summarizer.summarize_document(
        query="executive summary key findings",
        summary_type="executive",
        n_chunks=3,
        save_to_file=True,
        custom_filename="executive_brief"
    )
    
    if result["success"]:
        print(f"✅ Executive summary saved to: {result.get('file_path', 'Unknown')}")
    else:
        print(f"❌ Failed: {result.get('message', 'Unknown error')}")
    
    # Generate and save key points
    print("\n3. Generating key points...")
    result = summarizer.summarize_document(
        query="key points important information",
        summary_type="key_points",
        n_chunks=4,
        save_to_file=True,
        custom_filename="key_points"
    )
    
    if result["success"]:
        print(f"✅ Key points saved to: {result.get('file_path', 'Unknown')}")
    else:
        print(f"❌ Failed: {result.get('message', 'Unknown error')}")


def demo_document_overview_saving():
    """Demonstrate saving document overviews."""
    print("\n📊 Document Overview Saving Demo")
    print("=" * 50)
    
    summarizer = DocumentSummarizer()
    
    # Generate and save document overview
    print("Generating document overview...")
    result = summarizer.get_document_overview(
        save_to_file=True,
        custom_filename="document_overview"
    )
    
    if result["success"]:
        print(f"✅ Document overview saved to: {result.get('file_path', 'Unknown')}")
        print(f"📊 Total chunks: {result['document_info']['total_chunks']}")
        print(f"📁 Source files: {', '.join(result['document_info']['source_files'])}")
    else:
        print(f"❌ Failed: {result.get('message', 'Unknown error')}")


def demo_sectioned_summary_saving():
    """Demonstrate saving sectioned summaries."""
    print("\n📋 Sectioned Summary Saving Demo")
    print("=" * 50)
    
    summarizer = DocumentSummarizer()
    
    # Custom section queries
    section_queries = {
        "introduction": "introduction background context purpose",
        "governance": "governance oversight management responsibilities",
        "risk_management": "risk management assessment monitoring",
        "implementation": "implementation recommendations next steps"
    }
    
    print("Generating sectioned summary...")
    result = summarizer.summarize_by_sections(
        section_queries=section_queries,
        save_to_file=True,
        custom_filename="sectioned_analysis"
    )
    
    if result["success"]:
        print(f"✅ Sectioned summary saved to: {result.get('file_path', 'Unknown')}")
        print(f"📊 Generated {result['metadata']['total_sections']} sections")
        
        # Show section status
        for section_name, section_data in result["sections"].items():
            status = "✅" if section_data["success"] else "❌"
            print(f"  {status} {section_name.replace('_', ' ').title()}")
    else:
        print(f"❌ Failed: {result.get('message', 'Unknown error')}")


def demo_search_results_saving():
    """Demonstrate saving search results."""
    print("\n🔍 Search Results Saving Demo")
    print("=" * 50)
    
    # Initialize scanner and output manager
    scanner = PDFScanner()
    output_manager = MarkdownOutputManager()
    
    # Perform searches and save results
    search_queries = [
        "climate risk assessment",
        "governance oversight",
        "stress testing requirements",
        "implementation guidelines"
    ]
    
    for i, query in enumerate(search_queries, 1):
        print(f"{i}. Searching for: '{query}'")
        
        # Perform search
        search_results = scanner.search_documents(query, n_results=3)
        
        if search_results["count"] > 0:
            # Save search results
            file_path = output_manager.save_search_results(
                search_results=search_results,
                query=query,
                custom_filename=f"search_{i}_{query.replace(' ', '_')}"
            )
            print(f"   ✅ Saved to: {file_path}")
        else:
            print(f"   ❌ No results found")


def demo_output_management():
    """Demonstrate output management features."""
    print("\n🗂️ Output Management Demo")
    print("=" * 50)
    
    output_manager = MarkdownOutputManager()
    
    # Get output statistics
    stats = output_manager.get_output_stats()
    print("📊 Output Statistics:")
    print(f"   Total files: {stats['total_files']}")
    print(f"   Summaries: {stats['summaries']}")
    print(f"   Overviews: {stats['overviews']}")
    print(f"   Sections: {stats['sections']}")
    print(f"   Searches: {stats['searches']}")
    print(f"   Output directory: {stats['output_directory']}")
    
    # Create index file
    print("\n📝 Creating index file...")
    index_path = output_manager.create_index_file()
    print(f"✅ Index file created: {index_path}")
    
    # Show directory structure
    print(f"\n📁 Output Directory Structure:")
    print(f"   {output_manager.output_directory}/")
    for subdir in ["summaries", "overviews", "sections", "searches"]:
        subdir_path = output_manager.output_directory / subdir
        file_count = len(list(subdir_path.glob("*.md")))
        print(f"   ├── {subdir}/ ({file_count} files)")
    print(f"   └── index.md")


def demo_custom_output_directory():
    """Demonstrate using custom output directory."""
    print("\n📂 Custom Output Directory Demo")
    print("=" * 50)
    
    # Create custom output directory
    custom_dir = "./custom_output"
    summarizer = DocumentSummarizer(output_directory=custom_dir)
    
    print(f"Using custom output directory: {custom_dir}")
    
    # Generate summary with custom directory
    result = summarizer.summarize_document(
        query="custom directory test",
        summary_type="key_points",
        n_chunks=2,
        save_to_file=True,
        custom_filename="custom_test"
    )
    
    if result["success"]:
        print(f"✅ Summary saved to custom directory: {result.get('file_path', 'Unknown')}")
        
        # Show custom directory contents
        custom_path = Path(custom_dir)
        if custom_path.exists():
            print(f"\n📁 Custom directory contents:")
            for item in custom_path.rglob("*.md"):
                print(f"   {item.relative_to(custom_path)}")
    else:
        print(f"❌ Failed: {result.get('message', 'Unknown error')}")


def demo_file_formats():
    """Demonstrate different file formats and naming."""
    print("\n📄 File Format Demo")
    print("=" * 50)
    
    summarizer = DocumentSummarizer()
    
    # Different naming patterns
    naming_examples = [
        ("standard", "standard_summary"),
        ("with spaces", "summary with spaces"),
        ("special-chars", "summary@#$%"),
        ("very_long_filename_that_might_be_truncated", "very_long_filename"),
        ("", "no_custom_name")
    ]
    
    for description, custom_name in naming_examples:
        print(f"Testing: {description or 'default naming'}")
        
        result = summarizer.summarize_document(
            query="file format test",
            summary_type="key_points",
            n_chunks=1,
            save_to_file=True,
            custom_filename=custom_name if custom_name != "no_custom_name" else None
        )
        
        if result["success"] and "file_path" in result:
            filename = Path(result["file_path"]).name
            print(f"   ✅ Generated: {filename}")
        else:
            print(f"   ❌ Failed: {result.get('message', 'Unknown error')}")


def main():
    """Main demo function."""
    print("🎯 File Output Functionality Demo")
    print("=" * 60)
    
    # Check if ChromaDB collection exists
    if not Path("./chroma_db").exists():
        print("❌ ChromaDB collection not found. Please run the PDF scanner first:")
        print("   uv run python main.py")
        return
    
    # Check for API keys
    available_providers = config.get_available_providers()
    if not available_providers:
        print("❌ No API keys found. Please set up your .env file with API keys.")
        return
    
    print(f"✅ Found API keys for: {', '.join(available_providers)}")
    
    try:
        # Run demos
        demo_basic_file_saving()
        demo_document_overview_saving()
        demo_sectioned_summary_saving()
        demo_search_results_saving()
        demo_output_management()
        demo_custom_output_directory()
        demo_file_formats()
        
        print("\n" + "=" * 60)
        print("🎉 File Output Demo Completed!")
        print("\nGenerated files are saved in the 'output' directory.")
        print("Check the 'index.md' file for a complete listing of all generated files.")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
