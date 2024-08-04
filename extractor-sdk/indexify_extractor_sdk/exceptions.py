import sys
from typing import Dict, Type

import requests
import aiohttp
import torch
from transformers import TensorflowAutoModelException, PyTorchAutoModelException
from openai import OpenAIError
from google.api_core import exceptions as google_exceptions
from azure.core import exceptions as azure_exceptions
from botocore import exceptions as aws_exceptions
from pydantic import ValidationError
from PIL import UnidentifiedImageError

class IndexifyError(Exception):
    """Base class for all Indexify-related errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class ExtractorError(IndexifyError):
    """Base class for extractor-related errors."""
    pass

class InputValidationError(ExtractorError):
    """Raised when input validation fails."""
    pass

class ExtractionProcessError(ExtractorError):
    """Raised when the extraction process fails."""
    pass

class DependencyError(ExtractorError):
    """Raised when there's an issue with dependencies."""
    pass

class ModelLoadError(ExtractorError):
    """Raised when there's an error loading a machine learning model."""
    pass

class ConfigurationError(IndexifyError):
    """Raised when there's a configuration issue."""
    pass

class NetworkError(IndexifyError):
    """Raised when there's a network-related issue."""
    pass

class APIError(IndexifyError):
    """Raised when there's an error with an external API."""
    pass

class StorageError(IndexifyError):
    """Raised when there's an error with storage operations."""
    pass

class UnsupportedContentTypeError(ExtractorError):
    """Raised when the content type is not supported by the extractor."""
    pass

class ResourceExhaustedError(IndexifyError):
    """Raised when a resource (e.g., API quota, memory) is exhausted."""
    pass

class AuthenticationError(IndexifyError):
    """Raised when there's an authentication issue."""
    pass

class TimeoutError(IndexifyError):
    """Raised when an operation times out."""
    pass

# Mapping of external exceptions to Indexify exceptions
EXCEPTION_MAP: Dict[Type[Exception], Type[IndexifyError]] = {
    ValueError: InputValidationError,
    TypeError: InputValidationError,
    requests.RequestException: NetworkError,
    aiohttp.ClientError: NetworkError,
    ImportError: DependencyError,
    ModuleNotFoundError: DependencyError,
    FileNotFoundError: StorageError,
    PermissionError: StorageError,
    NotImplementedError: ExtractorError,
    TensorflowAutoModelException: ModelLoadError,
    PyTorchAutoModelException: ModelLoadError,
    torch.cuda.CudaError: ModelLoadError,
    OpenAIError: APIError,
    google_exceptions.GoogleAPIError: APIError,
    azure_exceptions.AzureError: APIError,
    aws_exceptions.BotoCoreError: APIError,
    ValidationError: InputValidationError,
    UnidentifiedImageError: InputValidationError,
    TimeoutError: TimeoutError,
    MemoryError: ResourceExhaustedError,
}

def translate_exception(exc: Exception) -> IndexifyError:
    """
    Translate third-party exceptions to Indexify exceptions.
    
    Args:
        exc (Exception): The original exception.

    Returns:
        IndexifyError: An Indexify-specific exception.
    """
    exc_type = type(exc)
    
    if exc_type in EXCEPTION_MAP:
        return EXCEPTION_MAP[exc_type](str(exc))
    
    # Handle subclasses
    for base_exc, indexify_exc in EXCEPTION_MAP.items():
        if isinstance(exc, base_exc):
            return indexify_exc(str(exc))
    
    # If no specific match is found, wrap it in a generic IndexifyError
    return IndexifyError(f"Unexpected error: {exc.__class__.__name__}: {str(exc)}")

def handle_exception(exc: Exception):
    """
    Handle exceptions by logging and optionally re-raising.

    Args:
        exc (Exception): The exception to handle.
    """
    from .logging_config import logger  # Import here to avoid circular import

    indexify_error = translate_exception(exc)
    error_type = indexify_error.__class__.__name__
    
    logger.error(f"{error_type}: {indexify_error.message}")
    logger.debug("Exception details:", exc_info=True)
    
    # Optionally re-raise the translated exception
    raise indexify_error

def safe_execute(func):
    """
    Decorator to safely execute a function and handle exceptions.

    Args:
        func (callable): The function to execute safely.

    Returns:
        callable: A wrapped version of the input function.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            handle_exception(e)
    
    return wrapper