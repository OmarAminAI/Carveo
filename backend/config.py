import os
from dataclasses import dataclass

@dataclass
class EmailConfig:
    """Email configuration parameters"""
    GMAIL_ADDRESS: str = ""
    GMAIL_APP_PASSWORD: str = ""
    DESTINATION_EMAIL: str = ""
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    
    def update(self, gmail_address: str, gmail_password: str, destination_email: str):
        """Update email configuration dynamically"""
        self.GMAIL_ADDRESS = gmail_address
        self.GMAIL_APP_PASSWORD = gmail_password
        self.DESTINATION_EMAIL = destination_email

@dataclass
class AzureOpenAIConfig:
    """Azure OpenAI configuration parameters"""
    API_KEY: str = "DGiUH36EWKWnVTY104jQ036DkFaKh07jKdUiGCXBU0WfZkATjUuPJQQJ99BHACHYHv6XJ3w3AAABACOGJSBL"
    DEPLOYMENT_NAME: str = "gpt-4o-mini-OE715"
    ENDPOINT: str = "https://orionopenai-techtest.openai.azure.com/"  # Just the base URL
    API_VERSION: str = "2025-01-01-preview"
    TEMPERATURE: float = 0.0
    MAX_TOKENS: int = 500

@dataclass
class AppConfig:
    """Application configuration parameters"""
    MAX_DESCRIPTION_LENGTH: int = 1000
    ALLOWED_IMAGE_TYPES: list = None
    
    def __post_init__(self):
        if self.ALLOWED_IMAGE_TYPES is None:
            self.ALLOWED_IMAGE_TYPES = ['jpg', 'jpeg', 'png']

@dataclass
class SecurityConfig:
    """Security configuration parameters"""
    DANGEROUS_PATTERNS: list = None
    
    def __post_init__(self):
        if self.DANGEROUS_PATTERNS is None:
            self.DANGEROUS_PATTERNS = [
                r"ignore\s+previous\s+instructions",
                r"disregard\s+all",
                r"system\s*:",
                r"assistant\s*:",
                r"user\s*:",
                r"\n\n##",
                r"```python",
                r"```bash",
                r"<script",
                r"</script>",
                r"javascript:",
                r"onclick\s*=",
                r"onerror\s*="
            ]

# Initialize configurations
email_config = EmailConfig()
azure_openai_config = AzureOpenAIConfig()
app_config = AppConfig()
security_config = SecurityConfig()