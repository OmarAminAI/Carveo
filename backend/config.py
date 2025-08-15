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
                # Original patterns (updated)
                r"ignore.*previous.*instructions",
                r"disregard.*all",
                r"system\s*[:：]",
                r"assistant\s*[:：]",
                r"user\s*[:：]",
                r"\n\n##",
                r"```python",
                r"```bash",
                r"<script",
                r"</script>",
                r"javascript:",
                r"onclick\s*=",
                r"onerror\s*=",
                
                # JSON manipulation patterns
                r"return.*following.*json",
                r"output.*json.*format",
                
                # Role manipulation patterns
                r"forget.*everything",
                r"new\s+instructions?",
                r"you\s+are\s+now",
                r"act\s+as",
                r"pretend\s+to\s+be",
                r"roleplay\s+as",
                r"bypass\s+your",
                r"override\s+your",
                
                # HTML comment patterns
                r"<!--",
                r"-->",
                
                # Instruction markers
                r"###.*instruction",
                r"##.*instruction",
                r"\$\$.*instruction.*\$\$",
                r"\{.*instruction.*\}",
                
                # API/Config/Password extraction attempts
                r"api.*key",
                r"configuration.*values",
                r"extract.*config",
                r"return.*config",
                r"show.*config",
                r"display.*config",
                r"reveal.*credentials",
                r"access.*token",
                r"secret.*key",
                r"password",
                r"email.*password",
                r"return.*password",
                r"show.*password",
                r"gmail.*password",
                r"smtp.*credential",
                
                # Common injection delimiters
                r"end\s+of\s+.*description",
                r"ignore\s+below",
                r"ignore\s+above",
                r"</.*>",
                r"<[^>]*>",
                
                # Command-like patterns
                r"^/\w+",
                r"^\!\w+",
                r"^\\w+",
                
                # Base64 and encoding attacks
                r"base64\s*:",
                r"decode.*execute",
                r"decode.*and.*execute",
                r"execute.*above",
                r"execute.*below",
                r"run.*decoded",
                r"eval\s*\(",
                r"exec\s*\(",
                r"decrypt.*execute",
                r"encoding\s*:",
                r"encoded\s*:",

                # SMTP injection patterns
                r"\\r\\n|\\n\\r",  # Escaped CRLF sequences
                r"\r\n|\n\r",       # Actual CRLF characters
                r"MAIL\s+FROM\s*:",
                r"RCPT\s+TO\s*:",
                r"DATA\s*:",
                r"HELO\s+",
                r"EHLO\s+",
                r"VRFY\s+",
                r"EXPN\s+",
                r"QUIT\s*$",
                r"RSET\s*$",
                r"NOOP\s*$",
                r"smtp\s*commands?",
                r"email\s*injection",
                r"mail\s*header\s*injection",
                r"mime\s*header\s*injection",
                r"content-type\s*injection",

                # File security patterns - add these to DANGEROUS_PATTERNS
                r"\.\.+[/\\]",                    # Any path traversal
                r"[\"';`].*rm\s+-rf",             # rm -rf command injection
                r"\.(jpg|jpeg|png|gif)\.exe",     # Image files with .exe
                r"%00|\\x00|\0",                  # Null bytes in any form
                r"/etc/(passwd|shadow|hosts)",     # Sensitive Linux files
                r"(cmd|powershell)\.exe",         # Windows command execution

            ]

# Initialize configurations
email_config = EmailConfig()
azure_openai_config = AzureOpenAIConfig()
app_config = AppConfig()
security_config = SecurityConfig()