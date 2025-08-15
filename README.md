# Automotive Listing Platform

A professional web application for processing and submitting vehicle listings with AI-powered feature extraction and automated email delivery.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![Azure OpenAI](https://img.shields.io/badge/Azure%20OpenAI-GPT--4-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🚗 Overview

The Automotive Listing Platform is an intelligent vehicle listing system that:
- Extracts structured car information from natural language descriptions using Azure OpenAI
- Processes vehicle images for classification (placeholder for CV integration)
- Validates and sanitizes user input to prevent prompt injection
- Sends formatted listings via email with JSON attachments
- Provides a professional, user-friendly interface

## ✨ Features

### Core Functionality
- **AI-Powered Extraction**: Automatically extracts car details (brand, model, year, price, etc.) from free-text descriptions
- **Image Processing**: Accepts vehicle images with metadata display
- **Email Integration**: Sends formatted listings with attached JSON data and images
- **Input Validation**: Comprehensive security measures against prompt injection
- **Professional UI**: Clean, responsive interface built with Streamlit

### Security Features
- Input sanitization with dangerous pattern detection
- Character filtering and length limits
- Email verification before processing
- No hardcoded credentials

## 🏗️ Architecture

```
automotive-listing-platform/
├── backend/
│   ├── __init__.py          # Backend module initialization
│   ├── car_service.py       # Car processing logic & AI integration
│   ├── email_service.py     # Email handling service
│   ├── config.py           # Configuration management
│   └── prompts.py          # AI prompt templates
├── frontend/
│   ├── __init__.py         # Frontend module initialization
│   ├── app.py              # Main Streamlit application
│   └── components.py       # Reusable UI components
└── requirements.txt        # Python dependencies
```

## 📋 Prerequisites

- Python 3.8 or higher
- Azure OpenAI account with API access
- Gmail account with App Password enabled
- Git (for cloning the repository)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/yourusername/automotive-listing-platform](https://github.com/OmarAminAI/car-selling-platform.git
cd automotive-listing-platform
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Azure OpenAI (Optional)
If you have your own Azure OpenAI credentials, update them in `backend/config.py`:
```python
@dataclass
class AzureOpenAIConfig:
    API_KEY: str = "your-api-key"
    DEPLOYMENT_NAME: str = "your-deployment-name"
    ENDPOINT: str = "https://your-endpoint.openai.azure.com/"
    API_VERSION: str = "2025-01-01-preview"
```

## 📧 Gmail Configuration

### Setting up Gmail App Password

1. Go to your [Google Account settings](https://myaccount.google.com/)
2. Navigate to **Security** → **2-Step Verification** (enable if needed)
3. Click on **App passwords**
4. Select "Mail" and generate a new password
5. Copy the 16-character password (you'll use this in the app)

## 🎯 Usage Guide

### 1. Start the Application
```bash
streamlit run frontend/app.py
```

### 2. Configure Email Settings
1. In the sidebar, enter:
   - **Gmail Address**: Your Gmail address
   - **Gmail App Password**: The 16-character app password
   - **Destination Email**: Where listings will be sent
2. Click **Save Config**
3. Click **Verify Email** to test the connection

### 3. Submit a Vehicle Listing
1. **Upload Image**: Select a vehicle image (JPG, PNG, max 5MB)
2. **Enter Description**: Provide detailed vehicle information
3. Click **Submit Listing**

### 4. Review Results
- View extracted information in the summary
- Check your destination email for the full listing

## 📝 Example Descriptions

### Example 1:
```
Blue Ford Fusion produced in 2015 featuring a 2.0-liter engine. 
The vehicle has low mileage with only 40,000 miles on the odometer. 
Equipped with brand-new all-season tires manufactured in 2022. 
The car's windows are tinted for added privacy. Notably, the rear 
bumper has been replaced after a minor collision. Priced at 1 million L.E.
```

### Example 2:
```
White Daewoo Juliet manufactured at 2001 with a motor size of 1500 cc 
and the four tires are used they are from 2020. The windows are electrical. 
There is a small notice the wind shield has been changed due to a small 
accident. Estimated price is 220K L.E.
```

## 🔧 Configuration Options

### Application Settings (`backend/config.py`)

| Setting | Default | Description |
|---------|---------|-------------|
| `MAX_DESCRIPTION_LENGTH` | 1000 | Maximum characters for descriptions |
| `ALLOWED_IMAGE_TYPES` | None| Accepted image formats |
| `TEMPERATURE` | 0.0 | AI model temperature (0 = deterministic) |
| `MAX_TOKENS` | 500 | Maximum AI response tokens |

### Email Structure

The system sends emails with:
- **Subject**: "New Car Listing: [Year] [Brand] [Model]"
- **Body**: Formatted text with all extracted details
- **Attachments**: 
  - Original vehicle image
  - JSON file with structured data

### Extracted Fields

| Field | Type | Description |
|-------|------|-------------|
| `brand` | String | Car manufacturer |
| `model` | String | Car model name |
| `manufactured_year` | Integer | Year of manufacture |
| `color` | String | Vehicle color |
| `body_type` | String | Body style (sedan, SUV, etc.) |
| `motor_size_cc` | Integer | Engine size in cc |
| `price` | Integer | Asking price |
| `currency` | String | Price currency |
| `tires` | Object | Type and year |
| `windows` | String | Window features |
| `notices` | Array | Repairs/modifications |

## 🛡️ Security Features

### Prompt Injection Prevention
- **Pattern Detection**: Blocks common injection attempts
- **Input Sanitization**: Removes potentially harmful characters
- **Length Limits**: Prevents overflow attacks
- **Validation**: Rejects suspicious inputs before AI processing

### Protected Patterns
- Instruction manipulation attempts
- Role hijacking (system/assistant prompts)
- Code injection (Python, bash, scripts)
- XSS attempts (JavaScript, HTML events)

## 🐛 Troubleshooting

### Common Issues

#### "Connection error" when processing
- Check your internet connection
- Verify Azure OpenAI credentials
- Ensure the endpoint URL is correct
- Check if Azure service is operational

#### "Authentication failed" for email
- Verify Gmail address is correct
- Ensure you're using an App Password, not your regular Gmail password
- Check that 2-Step Verification is enabled
- Try generating a new App Password

#### "File size exceeds maximum limit"
- Compress your image before uploading
- Ensure image is under 5MB
- Use JPG format for smaller file sizes

#### Email not received
- Check spam/junk folder
- Verify destination email is correct
- Ensure email verification was successful
- Check Gmail sending limits (500 emails/day)

### Debug Mode
Enable debug mode in the sidebar to view:
- Current configuration values
- Email settings (masked)
- System status
- File type restrictions

## 📊 API Response Format

### Successful Extraction
```json
{
  "body_type": "sedan",
  "color": "Blue",
  "brand": "Ford",
  "model": "Fusion",
  "manufactured_year": 2015,
  "motor_size_cc": 2000,
  "tires": {
    "type": "brand-new",
    "manufactured_year": 2022
  },
  "windows": "tinted",
  "notices": [
    {
      "type": "collision",
      "description": "The rear bumper has been replaced after a minor collision."
    }
  ],
  "price": 1000000,
  "currency": "L.E",
  "submission_timestamp": "2025-08-15T02:41:28.238307"
}
```

### Integration Points
The placeholder `detect_body_type()` method in `car_service.py` is ready for CV model integration:
```python
@staticmethod
def detect_body_type(image: Image.Image) -> str:
    # TODO: Replace with actual computer vision model
    return "not-detected"
```

## 🤝 Contributing

Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8 guidelines
- Add docstrings to all functions
- Include type hints
- Write unit tests for new features

## 📦 Requirements

```txt
streamlit>=1.28.0
langchain>=0.1.0
langchain-openai>=0.0.5
Pillow>=10.0.0
python-dotenv>=1.0.0
```

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
- Uses [LangChain](https://langchain.com/) for AI orchestration

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

Your Name
- GitHub: [@OmarAminAI](https://github.com/OmarAminAI)
- LinkedIn: [Omar Sadek](https://www.linkedin.com/in/omar-sadek-307430239/)

