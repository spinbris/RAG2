"""
Output utilities for saving summaries and results to markdown files.

This module provides functionality to save document summaries, search results,
and other outputs to organized markdown files in an output directory.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from config import config

# Configure logging
logger = logging.getLogger(__name__)


class MarkdownOutputManager:
    """Manages saving summaries and results to markdown files."""
    
    def __init__(self, output_directory: str = "./output"):
        """
        Initialize the MarkdownOutputManager.
        
        Args:
            output_directory: Directory to save output files
        """
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.summaries_dir = self.output_directory / "summaries"
        self.searches_dir = self.output_directory / "searches"
        self.overviews_dir = self.output_directory / "overviews"
        self.sections_dir = self.output_directory / "sections"
        
        for dir_path in [self.summaries_dir, self.searches_dir, self.overviews_dir, self.sections_dir]:
            dir_path.mkdir(exist_ok=True)
        
        logger.info(f"Output manager initialized with directory: {self.output_directory}")
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system usage."""
        # Replace invalid characters with underscores
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove extra spaces and limit length
        filename = '_'.join(filename.split())
        return filename[:100]  # Limit to 100 characters
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for file naming."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def save_summary(self, 
                    summary_result: Dict[str, Any], 
                    summary_type: str,
                    source_file: Optional[str] = None,
                    custom_filename: Optional[str] = None) -> str:
        """
        Save a summary result to a markdown file.
        
        Args:
            summary_result: Result from DocumentSummarizer.summarize_document()
            summary_type: Type of summary (comprehensive, executive, key_points)
            source_file: Source PDF file name
            custom_filename: Custom filename (without extension)
            
        Returns:
            Path to the saved file
        """
        if not summary_result.get("success", False):
            raise ValueError("Cannot save failed summary result")
        
        # Generate filename
        timestamp = self._get_timestamp()
        source_part = f"_{self._sanitize_filename(source_file)}" if source_file else ""
        custom_part = f"_{self._sanitize_filename(custom_filename)}" if custom_filename else ""
        filename = f"{summary_type}_{timestamp}{source_part}{custom_part}.md"
        
        file_path = self.summaries_dir / filename
        
        # Create markdown content
        content = self._format_summary_markdown(summary_result, summary_type, source_file)
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Summary saved to: {file_path}")
        return str(file_path)
    
    def save_document_overview(self, 
                             overview_result: Dict[str, Any],
                             source_file: Optional[str] = None,
                             custom_filename: Optional[str] = None) -> str:
        """
        Save a document overview to a markdown file.
        
        Args:
            overview_result: Result from DocumentSummarizer.get_document_overview()
            source_file: Source PDF file name
            custom_filename: Custom filename (without extension)
            
        Returns:
            Path to the saved file
        """
        if not overview_result.get("success", False):
            raise ValueError("Cannot save failed overview result")
        
        # Generate filename
        timestamp = self._get_timestamp()
        source_part = f"_{self._sanitize_filename(source_file)}" if source_file else ""
        custom_part = f"_{self._sanitize_filename(custom_filename)}" if custom_filename else ""
        filename = f"overview_{timestamp}{source_part}{custom_part}.md"
        
        file_path = self.overviews_dir / filename
        
        # Create markdown content
        content = self._format_overview_markdown(overview_result, source_file)
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Document overview saved to: {file_path}")
        return str(file_path)
    
    def save_sectioned_summary(self, 
                             sections_result: Dict[str, Any],
                             source_file: Optional[str] = None,
                             custom_filename: Optional[str] = None) -> str:
        """
        Save a sectioned summary to a markdown file.
        
        Args:
            sections_result: Result from DocumentSummarizer.summarize_by_sections()
            source_file: Source PDF file name
            custom_filename: Custom filename (without extension)
            
        Returns:
            Path to the saved file
        """
        if not sections_result.get("success", False):
            raise ValueError("Cannot save failed sections result")
        
        # Generate filename
        timestamp = self._get_timestamp()
        source_part = f"_{self._sanitize_filename(source_file)}" if source_file else ""
        custom_part = f"_{self._sanitize_filename(custom_filename)}" if custom_filename else ""
        filename = f"sections_{timestamp}{source_part}{custom_part}.md"
        
        file_path = self.sections_dir / filename
        
        # Create markdown content
        content = self._format_sections_markdown(sections_result, source_file)
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Sectioned summary saved to: {file_path}")
        return str(file_path)
    
    def save_search_results(self, 
                          search_results: Dict[str, Any],
                          query: str,
                          source_file: Optional[str] = None,
                          custom_filename: Optional[str] = None) -> str:
        """
        Save search results to a markdown file.
        
        Args:
            search_results: Results from PDFScanner.search_documents()
            query: Search query used
            source_file: Source PDF file name
            custom_filename: Custom filename (without extension)
            
        Returns:
            Path to the saved file
        """
        # Generate filename
        timestamp = self._get_timestamp()
        query_part = f"_{self._sanitize_filename(query)}" if query else ""
        source_part = f"_{self._sanitize_filename(source_file)}" if source_file else ""
        custom_part = f"_{self._sanitize_filename(custom_filename)}" if custom_filename else ""
        filename = f"search_{timestamp}{query_part}{source_part}{custom_part}.md"
        
        file_path = self.searches_dir / filename
        
        # Create markdown content
        content = self._format_search_markdown(search_results, query, source_file)
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Search results saved to: {file_path}")
        return str(file_path)
    
    def _format_summary_markdown(self, 
                                summary_result: Dict[str, Any], 
                                summary_type: str,
                                source_file: Optional[str]) -> str:
        """Format summary result as markdown."""
        metadata = summary_result.get("metadata", {})
        
        content = f"""# {summary_type.title()} Summary

## Document Information
- **Source File**: {source_file or 'Multiple files'}
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Summary Type**: {summary_type}
- **Model Used**: {metadata.get('model_used', 'Unknown')}
- **Provider**: {metadata.get('provider', 'Unknown')}
- **Chunks Used**: {metadata.get('chunks_used', 'Unknown')}
- **Query**: {metadata.get('query_used', 'N/A')}

## Summary

{summary_result.get('summary', 'No summary available')}

## Metadata

```json
{json.dumps(metadata, indent=2)}
```

---
*Generated by RAG2 Document Processing System*
"""
        return content
    
    def _format_overview_markdown(self, 
                                 overview_result: Dict[str, Any],
                                 source_file: Optional[str]) -> str:
        """Format document overview as markdown."""
        doc_info = overview_result.get("document_info", {})
        metadata = overview_result.get("metadata", {})
        
        content = f"""# Document Overview

## Document Information
- **Source File**: {source_file or 'Multiple files'}
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Total Chunks**: {doc_info.get('total_chunks', 'Unknown')}
- **Source Files**: {', '.join(doc_info.get('source_files', []))}
- **Chunk Size Range**: {doc_info.get('chunk_size_range', {}).get('min', 'N/A')}-{doc_info.get('chunk_size_range', {}).get('max', 'N/A')} characters

## Overview

{overview_result.get('overview', 'No overview available')}

## Document Statistics

- **Total Document Chunks**: {doc_info.get('total_chunks', 'Unknown')}
- **Source Files**: {len(doc_info.get('source_files', []))}
- **Average Chunk Size**: {((doc_info.get('chunk_size_range', {}).get('min', 0) + doc_info.get('chunk_size_range', {}).get('max', 0)) / 2):.0f} characters

## Metadata

```json
{json.dumps(metadata, indent=2)}
```

---
*Generated by RAG2 Document Processing System*
"""
        return content
    
    def _format_sections_markdown(self, 
                                 sections_result: Dict[str, Any],
                                 source_file: Optional[str]) -> str:
        """Format sectioned summary as markdown."""
        sections = sections_result.get("sections", {})
        metadata = sections_result.get("metadata", {})
        
        content = f"""# Sectioned Summary

## Document Information
- **Source File**: {source_file or 'Multiple files'}
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Total Sections**: {metadata.get('total_sections', len(sections))}

## Sections

"""
        
        for section_name, section_data in sections.items():
            if section_data.get("success", False):
                content += f"""### {section_name.replace('_', ' ').title()}

**Query Used**: {section_data.get('query', 'N/A')}

{section_data.get('summary', 'No summary available')}

---

"""
            else:
                content += f"""### {section_name.replace('_', ' ').title()}

❌ **Failed to generate this section**

"""
        
        content += f"""## Metadata

```json
{json.dumps(metadata, indent=2)}
```

---
*Generated by RAG2 Document Processing System*
"""
        return content
    
    def _format_search_markdown(self, 
                               search_results: Dict[str, Any],
                               query: str,
                               source_file: Optional[str]) -> str:
        """Format search results as markdown."""
        results = search_results.get("results", {})
        documents = results.get("documents", [[]])[0] if results.get("documents") else []
        metadatas = results.get("metadatas", [[]])[0] if results.get("metadatas") else []
        distances = results.get("distances", [[]])[0] if results.get("distances") else []
        
        content = f"""# Search Results

## Search Information
- **Query**: {query}
- **Source File**: {source_file or 'All files'}
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Results Found**: {search_results.get('count', 0)}

## Results

"""
        
        for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
            similarity_score = 1 - distance if distance is not None else 0
            
            content += f"""### Result {i+1}

- **Source**: {metadata.get('source', 'Unknown')}
- **Chunk**: {metadata.get('chunk_index', 'Unknown')}/{metadata.get('total_chunks', 'Unknown')}
- **Similarity Score**: {similarity_score:.3f}
- **Content**:

{doc}

---

"""
        
        content += f"""## Search Metadata

```json
{json.dumps(search_results, indent=2)}
```

---
*Generated by RAG2 Document Processing System*
"""
        return content
    
    def create_index_file(self) -> str:
        """Create an index file listing all generated outputs."""
        index_path = self.output_directory / "index.md"
        
        content = f"""# RAG2 Output Index

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Directory Structure

```
{self.output_directory.name}/
├── summaries/          # Document summaries
├── searches/           # Search results
├── overviews/          # Document overviews
├── sections/           # Sectioned summaries
└── index.md           # This file
```

## Recent Files

### Summaries
"""
        
        # List recent summary files
        summary_files = sorted(self.summaries_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)
        for file_path in summary_files[:10]:  # Show last 10
            content += f"- [{file_path.name}](summaries/{file_path.name})\n"
        
        content += "\n### Document Overviews\n"
        overview_files = sorted(self.overviews_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)
        for file_path in overview_files[:10]:
            content += f"- [{file_path.name}](overviews/{file_path.name})\n"
        
        content += "\n### Sectioned Summaries\n"
        section_files = sorted(self.sections_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)
        for file_path in section_files[:10]:
            content += f"- [{file_path.name}](sections/{file_path.name})\n"
        
        content += "\n### Search Results\n"
        search_files = sorted(self.searches_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)
        for file_path in search_files[:10]:
            content += f"- [{file_path.name}](searches/{file_path.name})\n"
        
        content += f"""
---
*Generated by RAG2 Document Processing System*
*Output directory: {self.output_directory}*
"""
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Index file created: {index_path}")
        return str(index_path)
    
    def get_output_stats(self) -> Dict[str, Any]:
        """Get statistics about generated outputs."""
        stats = {
            "total_files": 0,
            "summaries": len(list(self.summaries_dir.glob("*.md"))),
            "overviews": len(list(self.overviews_dir.glob("*.md"))),
            "sections": len(list(self.sections_dir.glob("*.md"))),
            "searches": len(list(self.searches_dir.glob("*.md"))),
            "output_directory": str(self.output_directory)
        }
        
        stats["total_files"] = stats["summaries"] + stats["overviews"] + stats["sections"] + stats["searches"]
        
        return stats
