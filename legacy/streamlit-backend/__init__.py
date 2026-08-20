"""
Backend module for the Automotive Listing Platform.
Contains services for car data processing, email handling, and configuration.
"""

from backend.car_service import (
    CarListingService,
    CarTypeClassifier,
    InputSanitizer,
    CarFeatureExtractor
)
from backend.email_service import EmailService
from backend.config import (
    email_config,
    azure_openai_config,
    app_config,
    security_config,
    EmailConfig,
    AzureOpenAIConfig,
    AppConfig,
    SecurityConfig
)

__version__ = "1.0.0"

__all__ = [
    # Services
    'CarListingService',
    'EmailService',
    
    # Car processing components
    'CarTypeClassifier',
    'InputSanitizer',
    'CarFeatureExtractor',
    
    # Configuration instances
    'email_config',
    'azure_openai_config',
    'app_config',
    'security_config',
    
    # Configuration classes
    'EmailConfig',
    'AzureOpenAIConfig',
    'AppConfig',
    'SecurityConfig'
]