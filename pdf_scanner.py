"""
PDF Scanner for ChromaDB Integration

This module provides functionality to scan PDF files, extract text content,
and store it in ChromaDB for vector search and retrieval.
"""

import os
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

import chromadb
from chromadb.config import Settings
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFScanner:
    """A class to scan PDF files and store their content in ChromaDB."""
    
    def __init__(self, 
                 collection_name: str = "pdf_documents",
                 persist_directory: str = "./chroma_db",
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200):
        """
        Initialize the PDF Scanner.
        
        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist ChromaDB data
            chunk_size: Size of text chunks for splitting
            chunk_overlap: Overlap between chunks
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"Using existing collection: {collection_name}")
        except Exception as e:
            # Collection doesn't exist, create it
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "PDF document chunks for RAG"}
            )
            logger.info(f"Created new collection: {collection_name}")
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text content from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        try:
            reader = PdfReader(pdf_path)
            text = ""
            
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text.strip():
                    text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
            
            logger.info(f"Extracted text from {pdf_path}: {len(text)} characters")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            raise
    
    def split_text_into_chunks(self, text: str, metadata: Dict[str, Any] = None) -> List[Document]:
        """
        Split text into chunks using the text splitter.
        
        Args:
            text: Text to split
            metadata: Additional metadata for the chunks
            
        Returns:
            List of Document objects
        """
        if metadata is None:
            metadata = {}
        
        # Create a Document object for the text splitter
        doc = Document(page_content=text, metadata=metadata)
        
        # Split the document
        chunks = self.text_splitter.split_documents([doc])
        
        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks
    
    def add_document_to_chromadb(self, 
                                chunks: List[Document], 
                                pdf_filename: str,
                                pdf_path: str) -> None:
        """
        Add document chunks to ChromaDB.
        
        Args:
            chunks: List of document chunks
            pdf_filename: Name of the PDF file
            pdf_path: Full path to the PDF file
        """
        try:
            # Prepare data for ChromaDB
            documents = []
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                # Generate unique ID for each chunk
                chunk_id = f"{pdf_filename}_{i}_{uuid.uuid4().hex[:8]}"
                
                # Prepare metadata
                chunk_metadata = {
                    "source": pdf_filename,
                    "source_path": pdf_path,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    **chunk.metadata
                }
                
                documents.append(chunk.page_content)
                metadatas.append(chunk_metadata)
                ids.append(chunk_id)
            
            # Add to ChromaDB collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(chunks)} chunks from {pdf_filename} to ChromaDB")
            
        except Exception as e:
            logger.error(f"Error adding document to ChromaDB: {str(e)}")
            raise
    
    def scan_pdf(self, pdf_path: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Complete pipeline to scan a PDF and store it in ChromaDB.
        
        Args:
            pdf_path: Path to the PDF file
            metadata: Additional metadata for the document
            
        Returns:
            Dictionary with scan results
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if not pdf_path.suffix.lower() == '.pdf':
            raise ValueError(f"File is not a PDF: {pdf_path}")
        
        logger.info(f"Scanning PDF: {pdf_path}")
        
        # Extract text
        text = self.extract_text_from_pdf(str(pdf_path))
        
        if not text.strip():
            logger.warning(f"No text content found in {pdf_path}")
            return {
                "success": False,
                "message": "No text content found in PDF",
                "chunks_added": 0
            }
        
        # Prepare metadata
        doc_metadata = {
            "filename": pdf_path.name,
            "file_path": str(pdf_path),
            "file_size": pdf_path.stat().st_size,
            **(metadata or {})
        }
        
        # Split into chunks
        chunks = self.split_text_into_chunks(text, doc_metadata)
        
        # Add to ChromaDB
        self.add_document_to_chromadb(chunks, pdf_path.name, str(pdf_path))
        
        return {
            "success": True,
            "message": f"Successfully processed {pdf_path.name}",
            "chunks_added": len(chunks),
            "total_characters": len(text)
        }
    
    def scan_directory(self, directory_path: str, pattern: str = "*.pdf") -> List[Dict[str, Any]]:
        """
        Scan all PDF files in a directory.
        
        Args:
            directory_path: Path to directory containing PDFs
            pattern: File pattern to match (default: *.pdf)
            
        Returns:
            List of scan results for each file
        """
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        pdf_files = list(directory.glob(pattern))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {directory_path}")
            return []
        
        results = []
        
        for pdf_file in pdf_files:
            try:
                result = self.scan_pdf(str(pdf_file))
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing {pdf_file}: {str(e)}")
                results.append({
                    "success": False,
                    "message": f"Error processing {pdf_file.name}: {str(e)}",
                    "chunks_added": 0
                })
        
        return results
    
    def search_documents(self, 
                        query: str, 
                        n_results: int = 5,
                        where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Search for documents in ChromaDB.
        
        Args:
            query: Search query
            n_results: Number of results to return
            where: Optional metadata filter
            
        Returns:
            Search results
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )
            
            return {
                "query": query,
                "results": results,
                "count": len(results["documents"][0]) if results["documents"] else 0
            }
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            raise
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the ChromaDB collection.
        
        Returns:
            Collection information
        """
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "total_documents": count,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            raise
    
    def delete_document(self, source_filename: str) -> bool:
        """
        Delete all chunks for a specific document.
        
        Args:
            source_filename: Name of the source PDF file
            
        Returns:
            True if successful
        """
        try:
            # Get all documents with the source filename
            results = self.collection.get(
                where={"source": source_filename}
            )
            
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                logger.info(f"Deleted {len(results['ids'])} chunks for {source_filename}")
                return True
            else:
                logger.warning(f"No chunks found for {source_filename}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting document {source_filename}: {str(e)}")
            return False
