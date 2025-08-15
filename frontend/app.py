import streamlit as st
from PIL import Image
import io
import json
import sys
import os
from datetime import datetime

# Add parent directory to path for backend imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.car_service import CarListingService
from backend.email_service import EmailService
from backend.config import app_config, email_config
from frontend.components import UIComponents

# Page configuration
st.set_page_config(
    page_title="Automotive Listing Platform",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

#initialize the car listing service and email service
@st.cache_resource
def init_services():
    return CarListingService(), EmailService()

car_service, email_service = init_services()


# Initialize session state for email config
if 'email_configured' not in st.session_state:
    st.session_state.email_configured = False
if 'email_verified' not in st.session_state:
    st.session_state.email_verified = False

with st.sidebar:
    st.header("📧 Email Configuration (Required)")
    
    st.info("Please configure and verify email settings before submitting listings.")
    
    # Email Configuration
    st.subheader("Email Settings")
    user_email = st.text_input("Gmail Address", value="", placeholder="your@gmail.com", key="gmail_address")
    user_email_password = st.text_input("Gmail App Password", type="password", value="", key="gmail_password", 
                                      help="Use an App Password, not your regular Gmail password")
    destination_email = st.text_input("Destination Email", value="", placeholder="recipient@example.com", key="dest_email")
    
    # Save configuration button
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Config", type="primary", use_container_width=True):
            if user_email and user_email_password and destination_email:
                # Update email configuration
                email_config.update(user_email, user_email_password, destination_email)
                st.session_state.email_configured = True
                st.session_state.email_verified = False  # Reset verification when config changes
                st.success("Configuration saved!")
            else:
                st.error("Please fill in all email fields")
    
    with col2:
        if st.button("Verify Email", type="secondary", use_container_width=True, 
                     disabled=not st.session_state.email_configured):
            with st.spinner("Verifying email configuration..."):
                success, message = email_service.verify_email_config()
                if success:
                    st.session_state.email_verified = True
                    st.success(message)
                else:
                    st.session_state.email_verified = False
                    st.error(message)
    
    # Show configuration status
    if st.session_state.email_configured:
        UIComponents.render_status_indicator("Email Config", "Saved", "success")
    else:
        UIComponents.render_status_indicator("Email Config", "Not Configured", "error")
    
    if st.session_state.email_verified:
        UIComponents.render_status_indicator("Email Verification", "Verified ✓", "success")
    else:
        UIComponents.render_status_indicator("Email Verification", "Not Verified", "warning")
    
    # Azure OpenAI Status (Already configured)
    st.subheader("Azure OpenAI Status")
    UIComponents.render_status_indicator("Azure OpenAI", "Configured", "success")
    st.caption("Azure OpenAI is pre-configured")

# Professional CSS styling
st.markdown("""
<style>
    .main {
        padding: 1rem 2rem;
        background-color: #f8f9fa;
    }
    
    .stButton > button {
        background-color: #2c3e50;
        color: white;
        font-weight: 500;
        padding: 0.75rem 2rem;
        border: none;
        border-radius: 4px;
        font-size: 1rem;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #1a252f;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .uploadedFile {
        border: 1px solid #dee2e6;
        border-radius: 4px;
        padding: 1rem;
        background-color: white;
    }
    
    .stTextArea > div > div > textarea {
        font-family: 'Segoe UI', sans-serif;
        font-size: 1rem;
        border: 1px solid #dee2e6;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Header
UIComponents.render_header(
    "Automotive Listing Platform",
    "Submit your vehicle information for processing"
)

# Check if email is configured
if not st.session_state.email_configured:
    UIComponents.render_alert(
        "Please configure email settings in the sidebar before submitting listings.",
        type="warning"
    )

# Create main layout
col1, col2 = st.columns([1, 1], gap="large")

# Left column - Image upload
with col1:
    UIComponents.render_section_header("Vehicle Image")
    
    uploaded_file = st.file_uploader(
        "Select vehicle image file",
        type=app_config.ALLOWED_IMAGE_TYPES,
        help="Supported formats: JPG, JPEG, PNG. Maximum file size: 5MB"
    )
    
    if uploaded_file is not None:
        # Check file size
        if uploaded_file.size > 5 * 1024 * 1024:  # 5MB
            UIComponents.render_alert("File size exceeds maximum limit of 5MB.", type="error")
            uploaded_file = None
        else:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded vehicle image", use_container_width=True)
            

# Right column - Text input
with col2:
    UIComponents.render_section_header("Vehicle Description")
    
    # Reference examples
    with st.expander("View Example Descriptions"):
        st.markdown("""
        **Example 1:**
        Blue Ford Fusion produced in 2015 featuring a 2.0-liter engine. The vehicle has low mileage with only 40,000 miles on the odometer. Equipped with brand-new all-season tires manufactured in 2022. The car's windows are tinted for added privacy. Notably, the rear bumper has been replaced after a minor collision. Priced at 1 million L.E.
        
        **Example 2:**
        White Daewoo Juliet manufactured at 2001 with a motor size of 1500 cc and the four tires are used they are from 2020. The windows are electrical. There is a small notice the wind shield has been changed due to a small accident. Estimated price is 220K L.E.
        """)
    
    description = st.text_area(
        "Enter vehicle details",
        placeholder="Include: brand, model, year, color, engine size, tire condition, maintenance history, price",
        height=300,
        max_chars=app_config.MAX_DESCRIPTION_LENGTH,
        help=f"Maximum {app_config.MAX_DESCRIPTION_LENGTH} characters"
    )
    
    # Character counter
    if description:
        remaining = app_config.MAX_DESCRIPTION_LENGTH - len(description)
        if remaining < 100:
            st.caption(f"Characters remaining: {remaining}")

# Submission section
UIComponents.render_divider()

# Center the submit button
_, col_center, _ = st.columns([2, 1, 2])
with col_center:
    submit_button = st.button("Submit Listing", type="primary", use_container_width=True, 
                            disabled=not st.session_state.email_verified)

# Show warning if email not verified
if not st.session_state.email_verified:
    UIComponents.render_alert(
        "Please configure and verify email settings in the sidebar before submitting listings.",
        type="warning"
    )

# Process submission
if submit_button:
    # Double-check email verification
    if not st.session_state.email_verified:
        UIComponents.render_alert("Email must be verified before submission.", type="error")
    else:
        # Validation
        errors = []
        if uploaded_file is None:
            errors.append("Vehicle image is required")
        if not description.strip():
            errors.append("Vehicle description is required")
        
        if errors:
            UIComponents.render_alert("Please correct the following errors:", type="error")
            for error in errors:
                st.error(f"• {error}")
        else:
            # Process submission
            with st.spinner("Processing vehicle listing..."):
                try:
                    # Convert image for processing
                    image = Image.open(uploaded_file)
                    
                    # Process listing (this calls the model)
                    car_data, success, error_msg = car_service.process_listing(
                        description=description,
                        image=image
                    )
                    
                    if not success:
                        UIComponents.render_alert(error_msg, type="error")
                    else:
                        # Prepare image bytes for email
                        img_byte_arr = io.BytesIO()
                        img_format = 'JPEG' if uploaded_file.type in ['image/jpeg', 'image/jpg'] else 'PNG'
                        image.save(img_byte_arr, format=img_format)
                        img_bytes = img_byte_arr.getvalue()
                        
                        # Send email
                        email_sent = email_service.send_car_listing(
                            car_data=car_data,
                            image_bytes=img_bytes,
                            image_filename=uploaded_file.name
                        )
                        
                        if email_sent:
                            # Success message
                            UIComponents.render_alert("Vehicle listing submitted successfully", type="success")
                            
                            # Display extracted data
                            UIComponents.render_submission_summary(car_data)
                            
                            # Submission metrics
                            col_m1, col_m2, col_m3 = st.columns(3)
                            with col_m1:
                                UIComponents.render_metric_card("Submission Time", datetime.now().strftime('%H:%M:%S'))
                            with col_m2:
                                UIComponents.render_metric_card("Status", "Sent")
                            with col_m3:
                                UIComponents.render_metric_card("Email", email_service.config.DESTINATION_EMAIL.split('@')[0] + "@...")
                            
                            # Option to submit another
                            UIComponents.render_divider()
                            _, col_btn, _ = st.columns([2, 1, 2])
                            with col_btn:
                                if st.button("Submit Another Vehicle", use_container_width=True):
                                    st.rerun()
                        else:
                            UIComponents.render_alert("Failed to send email. Please verify email configuration.", type="error")
                            
                except Exception as e:
                    UIComponents.render_alert(f"An error occurred during processing: {str(e)}", type="error")
                    with st.expander("Error Details"):
                        st.code(str(e))

# Information section
UIComponents.render_divider()
UIComponents.render_section_header("Guidelines")

info_col1, info_col2, info_col3 = st.columns(3)

with info_col1:
    UIComponents.render_info_card(
        "Image Requirements",
        "JPG, JPEG, or PNG format • Maximum file size: 5MB • Minimum resolution: 200x200 • Clear vehicle photo recommended"
    )

with info_col2:
    UIComponents.render_info_card(
        "Description Guidelines",
        "Include make, model, and year • Specify engine size and mileage • Note any repairs or modifications • State asking price and currency"
    )

with info_col3:
    UIComponents.render_info_card(
        "Processing Information",
        "Automatic data extraction • Structured JSON formatting • Email delivery confirmation • Secure data handling"
    )

    # Sidebar for configuration status
    with st.sidebar:
        st.markdown("---")
        
