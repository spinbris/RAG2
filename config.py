"""
Configuration module for RAG2 Document Processing System.

This module handles environment variable loading and provides a centralized
configuration interface for the entire application.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Config:
    """Centralized configuration class for the RAG2 system."""
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    ANTHROPIC_API_KEY: Optional[str] = os.getenv('ANTHROPIC_API_KEY')
    GOOGLE_API_KEY: Optional[str] = os.getenv('GOOGLE_API_KEY')
    HF_TOKEN: Optional[str] = os.getenv('HF_TOKEN')
    WANDB_API_KEY: Optional[str] = os.getenv('WANDB_API_KEY')
    GROQ_API_KEY: Optional[str] = os.getenv('GROQ_API_KEY')
    DEEPSEEK_API_KEY: Optional[str] = os.getenv('DEEPSEEK_API_KEY')
    SERPER_API_KEY: Optional[str] = os.getenv('SERPER_API_KEY')
    YOUTUBE_API_KEY: Optional[str] = os.getenv('YOUTUBE_API_KEY')
    BRAVE_API_KEY: Optional[str] = os.getenv('BRAVE_API_KEY')
    
    # ChromaDB Configuration
    CHROMA_COLLECTION_NAME: str = os.getenv('CHROMA_COLLECTION_NAME', 'pdf_documents')
    CHROMA_PERSIST_DIRECTORY: str = os.getenv('CHROMA_PERSIST_DIRECTORY', './chroma_db')
    
    # PDF Scanner Configuration
    PDF_CHUNK_SIZE: int = int(os.getenv('PDF_CHUNK_SIZE', '1000'))
    PDF_CHUNK_OVERLAP: int = int(os.getenv('PDF_CHUNK_OVERLAP', '200'))
    
    # Document Summarizer Configuration
    DEFAULT_LLM_PROVIDER: str = os.getenv('DEFAULT_LLM_PROVIDER', 'openai')
    DEFAULT_MODEL_OPENAI: str = os.getenv('DEFAULT_MODEL_OPENAI', 'gpt-3.5-turbo')
    DEFAULT_MODEL_ANTHROPIC: str = os.getenv('DEFAULT_MODEL_ANTHROPIC', 'claude-3-sonnet-20240229')
    DEFAULT_MAX_TOKENS: int = int(os.getenv('DEFAULT_MAX_TOKENS', '2000'))
    DEFAULT_TEMPERATURE: float = float(os.getenv('DEFAULT_TEMPERATURE', '0.7'))
    DEFAULT_N_CHUNKS: int = int(os.getenv('DEFAULT_N_CHUNKS', '10'))
    
    # Optional: Custom model names for specific use cases
    COMPREHENSIVE_MODEL_OPENAI: str = os.getenv('COMPREHENSIVE_MODEL_OPENAI', DEFAULT_MODEL_OPENAI)
    EXECUTIVE_MODEL_OPENAI: str = os.getenv('EXECUTIVE_MODEL_OPENAI', DEFAULT_MODEL_OPENAI)
    KEY_POINTS_MODEL_ANTHROPIC: str = os.getenv('KEY_POINTS_MODEL_ANTHROPIC', DEFAULT_MODEL_ANTHROPIC)
    
    @classmethod
    def get_api_key(cls, provider: str) -> Optional[str]:
        """Get API key for a specific provider."""
        key_mapping = {
            'openai': cls.OPENAI_API_KEY,
            'anthropic': cls.ANTHROPIC_API_KEY,
            'google': cls.GOOGLE_API_KEY,
            'huggingface': cls.HF_TOKEN,
            'wandb': cls.WANDB_API_KEY,
            'groq': cls.GROQ_API_KEY,
            'deepseek': cls.DEEPSEEK_API_KEY,
            'serper': cls.SERPER_API_KEY,
            'youtube': cls.YOUTUBE_API_KEY,
            'brave': cls.BRAVE_API_KEY,
        }
        return key_mapping.get(provider.lower())
    
    @classmethod
    def get_model_name(cls, provider: str, summary_type: str = None) -> str:
        """Get model name for a specific provider and optional summary type."""
        if provider.lower() == 'openai':
            if summary_type == 'comprehensive' and cls.COMPREHENSIVE_MODEL_OPENAI != cls.DEFAULT_MODEL_OPENAI:
                return cls.COMPREHENSIVE_MODEL_OPENAI
            elif summary_type == 'executive' and cls.EXECUTIVE_MODEL_OPENAI != cls.DEFAULT_MODEL_OPENAI:
                return cls.EXECUTIVE_MODEL_OPENAI
            return cls.DEFAULT_MODEL_OPENAI
        elif provider.lower() == 'anthropic':
            if summary_type == 'key_points' and cls.KEY_POINTS_MODEL_ANTHROPIC != cls.DEFAULT_MODEL_ANTHROPIC:
                return cls.KEY_POINTS_MODEL_ANTHROPIC
            return cls.DEFAULT_MODEL_ANTHROPIC
        else:
            return cls.DEFAULT_MODEL_OPENAI
    
    @classmethod
    def validate_api_keys(cls) -> Dict[str, bool]:
        """Validate which API keys are available."""
        return {
            'openai': cls.OPENAI_API_KEY is not None,
            'anthropic': cls.ANTHROPIC_API_KEY is not None,
            'google': cls.GOOGLE_API_KEY is not None,
            'huggingface': cls.HF_TOKEN is not None,
            'wandb': cls.WANDB_API_KEY is not None,
            'groq': cls.GROQ_API_KEY is not None,
            'deepseek': cls.DEEPSEEK_API_KEY is not None,
            'serper': cls.SERPER_API_KEY is not None,
            'youtube': cls.YOUTUBE_API_KEY is not None,
            'brave': cls.BRAVE_API_KEY is not None,
        }
    
    @classmethod
    def get_available_providers(cls) -> list:
        """Get list of available LLM providers."""
        available = cls.validate_api_keys()
        llm_providers = ['openai', 'anthropic', 'groq', 'deepseek']
        return [provider for provider in llm_providers if available.get(provider, False)]
    
    @classmethod
    def print_config_summary(cls):
        """Print a summary of the current configuration."""
        print("🔧 RAG2 Configuration Summary")
        print("=" * 50)
        
        # API Keys status
        available_keys = cls.validate_api_keys()
        print("📋 API Keys Status:")
        for provider, available in available_keys.items():
            status = "✅" if available else "❌"
            print(f"  {status} {provider.upper()}")
        
        # Available LLM providers
        llm_providers = cls.get_available_providers()
        print(f"\n🤖 Available LLM Providers: {', '.join(llm_providers) if llm_providers else 'None'}")
        
        # ChromaDB config
        print(f"\n🗄️  ChromaDB Configuration:")
        print(f"  Collection: {cls.CHROMA_COLLECTION_NAME}")
        print(f"  Directory: {cls.CHROMA_PERSIST_DIRECTORY}")
        
        # PDF Scanner config
        print(f"\n📄 PDF Scanner Configuration:")
        print(f"  Chunk Size: {cls.PDF_CHUNK_SIZE}")
        print(f"  Chunk Overlap: {cls.PDF_CHUNK_OVERLAP}")
        
        # Summarizer config
        print(f"\n📝 Summarizer Configuration:")
        print(f"  Default Provider: {cls.DEFAULT_LLM_PROVIDER}")
        print(f"  Default OpenAI Model: {cls.DEFAULT_MODEL_OPENAI}")
        print(f"  Default Anthropic Model: {cls.DEFAULT_MODEL_ANTHROPIC}")
        print(f"  Max Tokens: {cls.DEFAULT_MAX_TOKENS}")
        print(f"  Temperature: {cls.DEFAULT_TEMPERATURE}")
        print(f"  Default Chunks: {cls.DEFAULT_N_CHUNKS}")


# Create a global config instance
config = Config()
