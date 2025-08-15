import re
import json
from datetime import datetime
from typing import Dict, Tuple, Optional
from PIL import Image
import io

from langchain_openai import AzureChatOpenAI
from backend.config import azure_openai_config, security_config, app_config
from backend.prompts import CarListingPrompts

class CarTypeClassifier:
    """Handles car body type classification from images"""
    
    @staticmethod
    def detect_body_type(image: Image.Image) -> str:
        """
        Dummy function for car body type detection.
        This will be replaced with actual CV model by the CV engineer.
        
        Args:
            image: PIL Image object
            
        Returns:
            str: Car body type (always returns 'not-detected' for now)
        """
        # TODO: Replace with actual computer vision model
        # Placeholder implementation
        return "not-detected"

class InputSanitizer:
    """Handles input sanitization to prevent prompt injection"""
    
    @staticmethod
    def sanitize_text(text: str) -> Tuple[str, bool]:
        """
        Sanitizes user input to prevent prompt injection attacks.
        
        Args:
            text: Raw user input
            
        Returns:
            Tuple of (sanitized_text, is_valid)
        """
        if not text:
            return "", False
        
        # Check for dangerous patterns
        for pattern in security_config.DANGEROUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return "[INVALID INPUT DETECTED]", False
        
        # Remove excessive special characters but keep car-related ones
        text = re.sub(r'[^\w\s\.\,\-\$\(\)\:\;\/\&]', '', text)
        
        # Limit length
        text = text[:app_config.MAX_DESCRIPTION_LENGTH]
        
        return text.strip(), True

class CarFeatureExtractor:
    """Handles extraction of car features using Azure GPT"""
    
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_deployment=azure_openai_config.DEPLOYMENT_NAME,
            azure_endpoint=azure_openai_config.ENDPOINT,
            api_key=azure_openai_config.API_KEY,
            api_version=azure_openai_config.API_VERSION,
            temperature=azure_openai_config.TEMPERATURE,
            max_tokens=azure_openai_config.MAX_TOKENS,
            request_timeout=30,  # Add timeout
            max_retries=2  # Add retries
        )
        self.prompt, self.parser = CarListingPrompts.get_extraction_prompt()
    
    def extract_features(self, description: str) -> Dict:
        """
        Extracts car features from description using Azure GPT.
        
        Args:
            description: Sanitized car description
            
        Returns:
            Dict containing structured car information
        """
        try:
            # Create chain
            chain = self.prompt | self.llm
            
            # Get response
            response = chain.invoke({
                "format_instructions": self.parser.get_format_instructions(),
                "description": description
            })
            
            # Parse response
            parsed = self.parser.parse(response.content)
            
            # Convert features string to list if needed
            if isinstance(parsed.get("features"), str):
                parsed["features"] = [f.strip() for f in parsed["features"].split(",") if f.strip()]
            
            return parsed
            
        except Exception as e:
            print(f"Error extracting features: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            
            # Return default values that indicate failure
            return {
                "body_type": "Not specified",
                "color": "Not specified",
                "brand": "Not specified",
                "model": "Not specified",
                "manufactured_year": "Not specified",
                "motor_size_cc": "Not specified",
                "tires": {"type": "Not specified", "manufactured_year": "Not specified"},
                "windows": "Not specified",
                "notices": [],
                "price": "Not specified",
                "currency": "Not specified"
            }

class CarListingService:
    """Main service for processing car listings"""
    
    def __init__(self):
        self.sanitizer = InputSanitizer()
        self.extractor = CarFeatureExtractor()
        self.classifier = CarTypeClassifier()
    
    def process_listing(self, description: str, image: Image.Image) -> Tuple[Dict, bool, str]:
        """
        Processes a car listing submission.
        
        Args:
            description: User's car description
            image: Car image (PIL Image)
            
        Returns:
            Tuple of (car_data, success, error_message)
        """
        # Sanitize input
        sanitized_text, is_valid = self.sanitizer.sanitize_text(description)
        
        if not is_valid:
            return None, False, "Invalid input detected. Please provide a legitimate car description."
        
        # Extract features
        car_data = self.extractor.extract_features(sanitized_text)
        
        # Check if extraction failed (all fields are "Not specified")
        required_fields = ['brand', 'model', 'manufactured_year', 'price']
        extraction_failed = all(
            car_data.get(field) == "Not specified" 
            for field in required_fields
        )
        
        if extraction_failed:
            return None, False, "Failed to extract car information due to API connection error. Please try again later."
        
        # Detect body type from image if not already specified in text
        if car_data.get('body_type') == "Not specified":
            detected_body_type = self.classifier.detect_body_type(image)
            car_data['body_type'] = detected_body_type
        
        # Add metadata
        car_data['submission_timestamp'] = datetime.now().isoformat()
        
        return car_data, True, ""