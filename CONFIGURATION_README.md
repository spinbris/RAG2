# Configuration Management with .env File

This document explains how the RAG2 system now uses a centralized configuration system with `.env` file support for better environment variable management.

## Overview

The system now includes a comprehensive configuration management system that:
- Loads environment variables from a `.env` file
- Provides centralized configuration with sensible defaults
- Supports multiple LLM providers
- Offers easy configuration validation and status checking

## Files Added/Modified

### New Files
- `config.py` - Centralized configuration management
- `CONFIGURATION_README.md` - This documentation

### Modified Files
- `document_summarizer.py` - Updated to use config system
- `main.py` - Updated to use config system
- `summarize_demo.py` - Updated to use config system

## Configuration Features

### 1. Environment Variable Loading
The system automatically loads variables from `.env` file using `python-dotenv`:

```python
from dotenv import load_dotenv
load_dotenv()
```

### 2. Centralized Configuration Class
All configuration is managed through the `Config` class in `config.py`:

```python
from config import config

# Access configuration values
api_key = config.get_api_key('openai')
model_name = config.get_model_name('openai', 'comprehensive')
```

### 3. Multiple LLM Provider Support
The system now supports multiple LLM providers:
- OpenAI (GPT models)
- Anthropic (Claude models)
- Groq (Fast inference)
- DeepSeek (Cost-effective alternative)

### 4. Smart Model Selection
Different models can be configured for different summary types:

```python
# In .env file
DEFAULT_MODEL_OPENAI=gpt-3.5-turbo
COMPREHENSIVE_MODEL_OPENAI=gpt-4
EXECUTIVE_MODEL_OPENAI=gpt-3.5-turbo
KEY_POINTS_MODEL_ANTHROPIC=claude-3-haiku-20240307
```

## Environment Variables

### Required API Keys (at least one)
```bash
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Groq (optional)
GROQ_API_KEY=your_groq_api_key_here

# DeepSeek (optional)
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### ChromaDB Configuration
```bash
CHROMA_COLLECTION_NAME=pdf_documents
CHROMA_PERSIST_DIRECTORY=./chroma_db
```

### PDF Scanner Configuration
```bash
PDF_CHUNK_SIZE=1000
PDF_CHUNK_OVERLAP=200
```

### Document Summarizer Configuration
```bash
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL_OPENAI=gpt-3.5-turbo
DEFAULT_MODEL_ANTHROPIC=claude-3-sonnet-20240229
DEFAULT_MAX_TOKENS=2000
DEFAULT_TEMPERATURE=0.7
DEFAULT_N_CHUNKS=10
```

### Optional: Custom Models for Specific Use Cases
```bash
COMPREHENSIVE_MODEL_OPENAI=gpt-4
EXECUTIVE_MODEL_OPENAI=gpt-3.5-turbo
KEY_POINTS_MODEL_ANTHROPIC=claude-3-haiku-20240307
```

### Logging Configuration
```bash
LOG_LEVEL=INFO
```

## Usage Examples

### 1. Check Configuration Status
```bash
uv run python main.py config
```

This shows:
- Available API keys
- Available LLM providers
- Current configuration settings
- ChromaDB settings
- PDF scanner settings

### 2. Use Default Configuration
```python
from document_summarizer import DocumentSummarizer

# Uses default configuration from .env file
summarizer = DocumentSummarizer()
```

### 3. Override Specific Settings
```python
from document_summarizer import DocumentSummarizer

# Override specific settings
summarizer = DocumentSummarizer(
    llm_provider='anthropic',
    model_name='claude-3-opus-20240229'
)
```

### 4. Access Configuration Programmatically
```python
from config import config

# Check available providers
providers = config.get_available_providers()
print(f"Available providers: {providers}")

# Get API key for specific provider
api_key = config.get_api_key('openai')

# Get model name for specific use case
model = config.get_model_name('openai', 'comprehensive')

# Print full configuration
config.print_config_summary()
```

## Benefits of the New Configuration System

### 1. **Centralized Management**
- All configuration in one place
- Easy to modify settings
- Consistent across all modules

### 2. **Environment-Specific Settings**
- Different settings for development/production
- Easy to switch between providers
- Secure API key management

### 3. **Flexible Model Selection**
- Different models for different tasks
- Easy to experiment with new models
- Cost optimization through model selection

### 4. **Better Error Handling**
- Clear error messages for missing configuration
- Validation of API keys
- Graceful fallbacks

### 5. **Easy Debugging**
- Configuration status command
- Clear logging of settings used
- Easy to identify configuration issues

## Migration from Old System

### Before (Old System)
```python
# Hard-coded values
scanner = PDFScanner(
    collection_name="pdf_documents",
    persist_directory="./chroma_db",
    chunk_size=1000,
    chunk_overlap=200
)

# Manual API key checking
if not os.getenv("OPENAI_API_KEY"):
    print("API key not set")
```

### After (New System)
```python
# Configuration-driven
scanner = PDFScanner()  # Uses config defaults

# Automatic API key validation
summarizer = DocumentSummarizer()  # Uses config defaults
```

## Best Practices

### 1. **Environment File Management**
- Keep `.env` file in `.gitignore`
- Use `.env.example` for documentation
- Never commit API keys to version control

### 2. **Configuration Validation**
- Always check configuration status before running
- Use `config.print_config_summary()` for debugging
- Validate API keys before expensive operations

### 3. **Model Selection**
- Use appropriate models for different tasks
- Consider cost vs. quality trade-offs
- Test different models for your use case

### 4. **Error Handling**
- Always check for API key availability
- Provide clear error messages
- Offer fallback options when possible

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   ```
   ❌ OPENAI_API_KEY not found in configuration
   ```
   **Solution**: Add the key to your `.env` file

2. **No Available Providers**
   ```
   ⚠️ No API keys found in configuration
   ```
   **Solution**: Set at least one API key in `.env` file

3. **Configuration Not Loading**
   ```
   AttributeError: 'Config' object has no attribute 'SOME_SETTING'
   ```
   **Solution**: Check `.env` file format and restart the application

### Debug Commands

```bash
# Check configuration status
uv run python main.py config

# Test with specific provider
uv run python main.py overview openai

# Run demo to test all functionality
uv run python main.py demo
```

## Future Enhancements

The configuration system is designed to be extensible:

1. **Additional LLM Providers**: Easy to add new providers
2. **Custom Configuration Sources**: Support for other config sources
3. **Dynamic Configuration**: Runtime configuration updates
4. **Configuration Validation**: Schema validation for settings
5. **Configuration Templates**: Pre-defined configurations for different use cases

This configuration system makes the RAG2 system more robust, flexible, and easier to manage across different environments and use cases.
