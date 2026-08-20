import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import Dict

from backend.config import email_config

class EmailService:
    """Handles sending car listings via email"""
    
    def __init__(self):
        self.config = email_config
    
    def send_car_listing(self, car_data: Dict, image_bytes: bytes, image_filename: str) -> bool:
        """
        Sends car listing data and image via email.
        
        Args:
            car_data: Dictionary with car information
            image_bytes: Image file bytes
            image_filename: Name of the image file
            
        Returns:
            bool: Success status
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config.GMAIL_ADDRESS
            msg['To'] = self.config.DESTINATION_EMAIL
            msg['Subject'] = self._create_subject(car_data)
            
            # Add body
            body = self._create_email_body(car_data)
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach JSON
            self._attach_json(msg, car_data)
            
            # Attach image
            self._attach_image(msg, image_bytes, image_filename)
            
            # Send email
            with smtplib.SMTP(self.config.SMTP_SERVER, self.config.SMTP_PORT) as server:
                server.starttls()
                server.login(self.config.GMAIL_ADDRESS, self.config.GMAIL_APP_PASSWORD)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Email error: {str(e)}")
            return False
    
    def verify_email_config(self) -> tuple[bool, str]:
        """
        Verifies email configuration by testing SMTP connection.
        
        Returns:
            tuple: (success, message)
        """
        try:
            # Check if all fields are filled
            if not all([self.config.GMAIL_ADDRESS, self.config.GMAIL_APP_PASSWORD, self.config.DESTINATION_EMAIL]):
                return False, "Email configuration incomplete"
            
            # Validate email format
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, self.config.GMAIL_ADDRESS):
                return False, "Invalid Gmail address format"
            if not re.match(email_pattern, self.config.DESTINATION_EMAIL):
                return False, "Invalid destination email format"
            
            # Test SMTP connection and authentication
            with smtplib.SMTP(self.config.SMTP_SERVER, self.config.SMTP_PORT) as server:
                server.starttls()
                server.login(self.config.GMAIL_ADDRESS, self.config.GMAIL_APP_PASSWORD)
                # Connection successful - no need to send test email
            
            return True, "Email configuration verified successfully! SMTP connection established."
            
        except smtplib.SMTPAuthenticationError:
            return False, "Authentication failed. Please check your Gmail address and app password."
        except smtplib.SMTPException as e:
            return False, f"SMTP error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def _create_subject(self, car_data: Dict) -> str:
        """Creates email subject line"""
        year = car_data.get('manufactured_year', '')
        brand = car_data.get('brand', '')
        model = car_data.get('model', '')
        return f"New Car Listing: {year} {brand} {model}".strip()

    def _create_email_body(self, car_data: Dict) -> str:
        """Creates email body text"""
        # Handle notices
        notices_text = ""
        if car_data.get('notices'):
            notices_list = []
            for notice in car_data.get('notices', []):
                notices_list.append(f"- {notice.get('type', 'Notice')}: {notice.get('description', '')}")
            notices_text = '\n'.join(notices_list)
        else:
            notices_text = "- None"
        
        # Handle tires
        tires = car_data.get('tires', {})
        if isinstance(tires, dict):
            tire_info = f"{tires.get('type', 'Not specified')} (Year: {tires.get('manufactured_year', 'Not specified')})"
        else:
            tire_info = "Not specified"
        
        return f"""
    New car listing submission received on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

    Car Details:
    ============
    Brand: {car_data.get('brand', 'Not specified')}
    Model: {car_data.get('model', 'Not specified')}
    Year: {car_data.get('manufactured_year', 'Not specified')}
    Color: {car_data.get('color', 'Not specified')}
    Body Type: {car_data.get('body_type', 'Not specified')}
    Engine Size: {car_data.get('motor_size_cc', 'Not specified')} cc
    Price: {car_data.get('price', 'Not specified')} {car_data.get('currency', '')}

    Tires: {tire_info}
    Windows: {car_data.get('windows', 'Not specified')}

    Notices/Repairs:
    {notices_text}

    Submission Timestamp: {car_data.get('submission_timestamp', 'Not specified')}

    Full JSON data is attached.
    """
    
    def _attach_json(self, msg: MIMEMultipart, car_data: Dict):
        """Attaches JSON data to email"""
        json_attachment = MIMEBase('application', 'json')
        json_data = json.dumps(car_data, indent=2).encode('utf-8')
        json_attachment.set_payload(json_data)
        encoders.encode_base64(json_attachment)
        json_attachment.add_header(
            'Content-Disposition',
            f'attachment; filename="car_listing_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
        )
        msg.attach(json_attachment)
    
    def _attach_image(self, msg: MIMEMultipart, image_bytes: bytes, filename: str):
        """Attaches image to email"""
        image_attachment = MIMEBase('application', 'octet-stream')
        image_attachment.set_payload(image_bytes)
        encoders.encode_base64(image_attachment)
        image_attachment.add_header(
            'Content-Disposition',
            f'attachment; filename="{filename}"'
        )
        msg.attach(image_attachment)
        
