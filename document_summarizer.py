"""
Document Summarizer using ChromaDB and LLM

This module provides functionality to summarize documents using ChromaDB
for context retrieval and various LLM providers for text generation.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import json

from pdf_scanner import PDFScanner
from langchain.schema import Document
from config import config
from output_utils import MarkdownOutputManager

# LLM imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentSummarizer:
    """A class to summarize documents using ChromaDB context and LLM generation."""
    
    def __init__(self, 
                 collection_name: Optional[str] = None,
                 persist_directory: Optional[str] = None,
                 llm_provider: Optional[str] = None,
                 model_name: Optional[str] = None,
                 api_key: Optional[str] = None,
                 output_directory: Optional[str] = None):
        """
        Initialize the Document Summarizer.
        
        Args:
            collection_name: Name of the ChromaDB collection (uses config default if None)
            persist_directory: Directory where ChromaDB data is stored (uses config default if None)
            llm_provider: LLM provider ("openai", "anthropic") (uses config default if None)
            model_name: Specific model to use (optional)
            api_key: API key for the LLM provider (optional)
            output_directory: Directory for saving output files (uses "./output" if None)
        """
        # Use config defaults if not provided
        self.collection_name = collection_name or config.CHROMA_COLLECTION_NAME
        self.persist_directory = persist_directory or config.CHROMA_PERSIST_DIRECTORY
        self.llm_provider = (llm_provider or config.DEFAULT_LLM_PROVIDER).lower()
        
        # Initialize PDF scanner for ChromaDB access
        self.scanner = PDFScanner(
            collection_name=self.collection_name,
            persist_directory=self.persist_directory
        )
        
        # Set up LLM
        self.model_name = model_name or self._get_default_model()
        self.api_key = api_key or self._get_api_key()
        self.llm_client = self._initialize_llm()
        
        # Initialize output manager
        self.output_manager = MarkdownOutputManager(
            output_directory=output_directory or "./output"
        )
        
        logger.info(f"Initialized DocumentSummarizer with {self.llm_provider} ({self.model_name})")
    
    def _get_default_model(self) -> str:
        """Get default model name based on provider."""
        return config.get_model_name(self.llm_provider)
    
    def _get_api_key(self) -> str:
        """Get API key from configuration."""
        key = config.get_api_key(self.llm_provider)
        if not key:
            raise ValueError(f"{self.llm_provider.upper()}_API_KEY not found in configuration")
        return key
    
    def _initialize_llm(self):
        """Initialize the LLM client."""
        if self.llm_provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI package not available. Install with: pip install openai")
            return openai.OpenAI(api_key=self.api_key)
        elif self.llm_provider == "anthropic":
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("Anthropic package not available. Install with: pip install anthropic")
            return anthropic.Anthropic(api_key=self.api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    def _generate_llm_response(self, 
                             prompt: str, 
                             max_tokens: int = 2000,
                             temperature: float = 0.7) -> str:
        """Generate response using the configured LLM."""
        try:
            if self.llm_provider == "openai":
                response = self.llm_client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content.strip()
            
            elif self.llm_provider == "anthropic":
                response = self.llm_client.messages.create(
                    model=self.model_name,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            raise
    
    def retrieve_relevant_chunks(self, 
                                query: str, 
                                n_results: int = 10,
                                source_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks from ChromaDB.
        
        Args:
            query: Search query
            n_results: Number of chunks to retrieve
            source_filter: Optional source file filter
            
        Returns:
            List of relevant chunks with metadata
        """
        try:
            where_clause = {"source": source_filter} if source_filter else None
            results = self.scanner.search_documents(query, n_results, where_clause)
            
            chunks = []
            if results['results']['documents'] and results['results']['documents'][0]:
                for doc, metadata, distance in zip(
                    results['results']['documents'][0],
                    results['results']['metadatas'][0],
                    results['results']['distances'][0]
                ):
                    chunks.append({
                        'content': doc,
                        'metadata': metadata,
                        'similarity_score': 1 - distance  # Convert distance to similarity
                    })
            
            logger.info(f"Retrieved {len(chunks)} relevant chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error retrieving chunks: {str(e)}")
            raise
    
    def create_summary_prompt(self, 
                            chunks: List[Dict[str, Any]], 
                            summary_type: str = "comprehensive",
                            max_context_length: int = 8000) -> str:
        """
        Create a prompt for document summarization.
        
        Args:
            chunks: Retrieved chunks from ChromaDB
            summary_type: Type of summary ("comprehensive", "executive", "key_points")
            max_context_length: Maximum context length for the prompt
            
        Returns:
            Formatted prompt for the LLM
        """
        # Combine chunks into context
        context_parts = []
        current_length = 0
        
        for i, chunk in enumerate(chunks):
            chunk_text = f"[Chunk {i+1} from {chunk['metadata']['source']}]\n{chunk['content']}\n"
            
            if current_length + len(chunk_text) > max_context_length:
                break
                
            context_parts.append(chunk_text)
            current_length += len(chunk_text)
        
        context = "\n".join(context_parts)
        
        # Create different prompt templates based on summary type
        if summary_type == "comprehensive":
            prompt = f"""Please provide a comprehensive summary of the following document content. 
The content is from a PDF document that has been split into chunks for analysis.

Document Content:
{context}

Please provide a detailed summary that includes:
1. Main topics and themes
2. Key findings and insights
3. Important details and data points
4. Structure and organization of the content
5. Any conclusions or recommendations

Summary:"""
        
        elif summary_type == "executive":
            prompt = f"""Please provide an executive summary of the following document content.
Focus on high-level insights and key takeaways that would be relevant for decision-makers.

Document Content:
{context}

Please provide a concise executive summary that includes:
1. Main purpose and scope
2. Key findings and implications
3. Critical insights
4. Recommendations or next steps

Executive Summary:"""
        
        elif summary_type == "key_points":
            prompt = f"""Please extract and summarize the key points from the following document content.
Focus on the most important information in a bullet-point format.

Document Content:
{context}

Please provide key points in the following format:
• [Key Point 1]
• [Key Point 2]
• [Key Point 3]
... (continue as needed)

Key Points:"""
        
        else:
            raise ValueError(f"Unsupported summary type: {summary_type}")
        
        return prompt
    
    def summarize_document(self, 
                          query: str = "summary overview main topics",
                          summary_type: str = "comprehensive",
                          n_chunks: int = 10,
                          source_filter: Optional[str] = None,
                          max_tokens: int = 2000,
                          temperature: float = 0.7,
                          save_to_file: bool = False,
                          custom_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Summarize a document using ChromaDB context.
        
        Args:
            query: Query to retrieve relevant chunks
            summary_type: Type of summary to generate
            n_chunks: Number of chunks to retrieve
            source_filter: Optional source file filter
            max_tokens: Maximum tokens for LLM response
            temperature: Temperature for LLM generation
            save_to_file: Whether to save the summary to a markdown file
            custom_filename: Custom filename for the saved file (without extension)
            
        Returns:
            Dictionary containing summary, metadata, and optionally file path
        """
        try:
            logger.info(f"Starting document summarization (type: {summary_type})")
            
            # Retrieve relevant chunks
            chunks = self.retrieve_relevant_chunks(
                query=query,
                n_results=n_chunks,
                source_filter=source_filter
            )
            
            if not chunks:
                return {
                    "success": False,
                    "message": "No relevant chunks found for summarization",
                    "summary": "",
                    "metadata": {}
                }
            
            # Create summary prompt
            prompt = self.create_summary_prompt(chunks, summary_type)
            
            # Generate summary using LLM
            summary = self._generate_llm_response(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Prepare metadata
            metadata = {
                "summary_type": summary_type,
                "chunks_used": len(chunks),
                "total_chunks_available": self.scanner.get_collection_info()["total_documents"],
                "query_used": query,
                "source_filter": source_filter,
                "model_used": self.model_name,
                "provider": self.llm_provider
            }
            
            logger.info(f"Successfully generated {summary_type} summary using {len(chunks)} chunks")
            
            result = {
                "success": True,
                "summary": summary,
                "metadata": metadata,
                "chunks_used": chunks
            }
            
            # Save to file if requested
            if save_to_file:
                try:
                    file_path = self.output_manager.save_summary(
                        summary_result=result,
                        summary_type=summary_type,
                        source_file=source_filter,
                        custom_filename=custom_filename
                    )
                    result["file_path"] = file_path
                    logger.info(f"Summary saved to: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to save summary to file: {str(e)}")
                    result["save_error"] = str(e)
            
            return result
            
        except Exception as e:
            logger.error(f"Error during document summarization: {str(e)}")
            return {
                "success": False,
                "message": f"Error during summarization: {str(e)}",
                "summary": "",
                "metadata": {}
            }
    
    def summarize_by_sections(self, 
                            source_filter: Optional[str] = None,
                            section_queries: Optional[Dict[str, str]] = None,
                            save_to_file: bool = False,
                            custom_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a sectioned summary of the document.
        
        Args:
            source_filter: Optional source file filter
            section_queries: Custom queries for different sections
            save_to_file: Whether to save the summary to a markdown file
            custom_filename: Custom filename for the saved file (without extension)
            
        Returns:
            Dictionary containing sectioned summary and optionally file path
        """
        if section_queries is None:
            section_queries = {
                "introduction": "introduction overview background context",
                "main_content": "main topics findings analysis methodology",
                "conclusions": "conclusion recommendations next steps summary",
                "key_data": "data statistics numbers metrics results"
            }
        
        sections = {}
        
        for section_name, query in section_queries.items():
            logger.info(f"Summarizing section: {section_name}")
            
            section_result = self.summarize_document(
                query=query,
                summary_type="key_points",
                n_chunks=5,
                source_filter=source_filter,
                max_tokens=1000
            )
            
            sections[section_name] = {
                "query": query,
                "summary": section_result.get("summary", ""),
                "success": section_result.get("success", False)
            }
        
        result = {
            "success": True,
            "sections": sections,
            "metadata": {
                "source_filter": source_filter,
                "total_sections": len(sections)
            }
        }
        
        # Save to file if requested
        if save_to_file:
            try:
                file_path = self.output_manager.save_sectioned_summary(
                    sections_result=result,
                    source_file=source_filter,
                    custom_filename=custom_filename
                )
                result["file_path"] = file_path
                logger.info(f"Sectioned summary saved to: {file_path}")
            except Exception as e:
                logger.error(f"Failed to save sectioned summary to file: {str(e)}")
                result["save_error"] = str(e)
        
        return result
    
    def get_document_overview(self, 
                            source_filter: Optional[str] = None,
                            save_to_file: bool = False,
                            custom_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a high-level overview of the document.
        
        Args:
            source_filter: Optional source file filter
            save_to_file: Whether to save the overview to a markdown file
            custom_filename: Custom filename for the saved file (without extension)
            
        Returns:
            Document overview information and optionally file path
        """
        try:
            # Get collection info
            collection_info = self.scanner.get_collection_info()
            
            # Get some sample chunks to understand the document
            sample_chunks = self.retrieve_relevant_chunks(
                query="document structure overview main topics",
                n_results=5,
                source_filter=source_filter
            )
            
            # Generate a brief overview
            overview_result = self.summarize_document(
                query="document overview main purpose scope",
                summary_type="executive",
                n_chunks=3,
                source_filter=source_filter,
                max_tokens=500
            )
            
            result = {
                "success": True,
                "overview": overview_result.get("summary", ""),
                "document_info": {
                    "total_chunks": collection_info["total_documents"],
                    "source_files": list(set(chunk["metadata"]["source"] for chunk in sample_chunks)),
                    "chunk_size_range": {
                        "min": min(len(chunk["content"]) for chunk in sample_chunks) if sample_chunks else 0,
                        "max": max(len(chunk["content"]) for chunk in sample_chunks) if sample_chunks else 0
                    }
                },
                "metadata": overview_result.get("metadata", {})
            }
            
            # Save to file if requested
            if save_to_file:
                try:
                    file_path = self.output_manager.save_document_overview(
                        overview_result=result,
                        source_file=source_filter,
                        custom_filename=custom_filename
                    )
                    result["file_path"] = file_path
                    logger.info(f"Document overview saved to: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to save overview to file: {str(e)}")
                    result["save_error"] = str(e)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting document overview: {str(e)}")
            return {
                "success": False,
                "message": f"Error getting overview: {str(e)}",
                "overview": "",
                "document_info": {}
            }
