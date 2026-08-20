import streamlit as st
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

class UIComponents:
    """Professional UI components for the automotive listing platform"""
    
    @staticmethod
    def render_header(title: str, subtitle: Optional[str] = None):
        """Render a professional page header"""
        st.markdown(f"""
        <div style='border-bottom: 3px solid #2c3e50; padding-bottom: 1rem; margin-bottom: 2rem;'>
            <h1 style='color: #2c3e50; margin: 0; font-weight: 400;'>{title}</h1>
            {f"<p style='color: #7f8c8d; margin: 0.5rem 0 0 0; font-size: 1.1rem;'>{subtitle}</p>" if subtitle else ""}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_section_header(title: str):
        """Render a section header with underline"""
        st.markdown(f"""
        <h2 style='color: #34495e; border-bottom: 2px solid #ecf0f1; padding-bottom: 0.5rem; margin-top: 2rem;'>
            {title}
        </h2>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_info_card(title: str, content: str, color: str = "#2c3e50"):
        """Render an information card"""
        st.markdown(f"""
        <div style='
            background-color: #ffffff;
            border-left: 4px solid {color};
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-radius: 4px;
        '>
            <h4 style='color: {color}; margin: 0 0 0.5rem 0; font-weight: 500;'>{title}</h4>
            <p style='color: #555; margin: 0; line-height: 1.6;'>{content}</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_status_indicator(label: str, status: str, type: str = "info"):
        """Render a status indicator"""
        colors = {
            "success": "#27ae60",
            "error": "#e74c3c",
            "warning": "#f39c12",
            "info": "#3498db"
        }
        
        color = colors.get(type, colors["info"])
        
        st.markdown(f"""
        <div style='
            display: inline-flex;
            align-items: center;
            padding: 0.5rem 1rem;
            background-color: {color}15;
            border: 1px solid {color}30;
            border-radius: 4px;
            margin: 0.25rem 0;
        '>
            <span style='
                width: 8px;
                height: 8px;
                background-color: {color};
                border-radius: 50%;
                margin-right: 0.5rem;
            '></span>
            <span style='color: {color}; font-weight: 500;'>{label}: {status}</span>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_data_table(data: Dict[str, Any], title: Optional[str] = None):
        """Render data in a professional table format"""
        if title:
            st.markdown(f"<h3 style='color: #34495e; margin-bottom: 1rem;'>{title}</h3>", unsafe_allow_html=True)
        
        table_html = """
        <table style='
            width: 100%;
            border-collapse: collapse;
            background-color: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-radius: 4px;
            overflow: hidden;
        '>
        """
        
        for key, value in data.items():
            # Format the key
            formatted_key = key.replace('_', ' ').title()
            
            # Format the value
            if isinstance(value, dict):
                formatted_value = json.dumps(value, indent=2)
            elif isinstance(value, list):
                formatted_value = ', '.join(str(item) for item in value)
            else:
                formatted_value = str(value)
            
            table_html += f"""
            <tr style='border-bottom: 1px solid #ecf0f1;'>
                <td style='
                    padding: 1rem;
                    font-weight: 500;
                    color: #34495e;
                    background-color: #f8f9fa;
                    width: 40%;
                '>{formatted_key}</td>
                <td style='
                    padding: 1rem;
                    color: #555;
                '>{formatted_value}</td>
            </tr>
            """
        
        table_html += "</table>"
        st.markdown(table_html, unsafe_allow_html=True)
    
    @staticmethod
    def render_metric_card(label: str, value: Any, delta: Optional[str] = None):
        """Render a professional metric card"""
        st.markdown(f"""
        <div style='
            background-color: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        '>
            <p style='
                color: #7f8c8d;
                margin: 0;
                font-size: 0.9rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            '>{label}</p>
            <h2 style='
                color: #2c3e50;
                margin: 0.5rem 0;
                font-weight: 600;
                font-size: 2rem;
            '>{value}</h2>
            {f"<p style='color: #27ae60; margin: 0; font-size: 0.9rem;'>{delta}</p>" if delta else ""}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_json_viewer(data: Dict[str, Any], title: str = "Data Structure"):
        """Render JSON data in a professional viewer"""
        st.markdown(f"""
        <div style='
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 1rem;
            margin: 1rem 0;
        '>
            <h4 style='color: #495057; margin: 0 0 1rem 0;'>{title}</h4>
            <pre style='
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                padding: 1rem;
                overflow-x: auto;
                margin: 0;
                font-family: "Monaco", "Consolas", monospace;
                font-size: 0.9rem;
                line-height: 1.5;
                color: #495057;
            '>{json.dumps(data, indent=2)}</pre>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_progress_indicator(current: int, total: int, label: str = "Progress"):
        """Render a professional progress bar"""
        percentage = (current / total) * 100 if total > 0 else 0
        
        st.markdown(f"""
        <div style='margin: 1rem 0;'>
            <div style='
                display: flex;
                justify-content: space-between;
                                margin-bottom: 0.5rem;
            '>
                <span style='color: #495057; font-weight: 500;'>{label}</span>
                <span style='color: #6c757d;'>{current} / {total}</span>
            </div>
            <div style='
                background-color: #e9ecef;
                border-radius: 4px;
                height: 8px;
                overflow: hidden;
            '>
                <div style='
                    background-color: #2c3e50;
                    height: 100%;
                    width: {percentage}%;
                    transition: width 0.3s ease;
                '></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_alert(message: str, type: str = "info"):
        """Render a professional alert message"""
        styles = {
            "info": {
                "bg": "#e3f2fd",
                "border": "#2196f3",
                "text": "#0d47a1"
            },
            "success": {
                "bg": "#e8f5e9",
                "border": "#4caf50",
                "text": "#1b5e20"
            },
            "warning": {
                "bg": "#fff3e0",
                "border": "#ff9800",
                "text": "#e65100"
            },
            "error": {
                "bg": "#ffebee",
                "border": "#f44336",
                "text": "#b71c1c"
            }
        }
        
        style = styles.get(type, styles["info"])
        
        st.markdown(f"""
        <div style='
            background-color: {style["bg"]};
            border-left: 4px solid {style["border"]};
            color: {style["text"]};
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 4px;
        '>
            {message}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_submission_summary(car_data: Dict[str, Any]):
        """Render a professional submission summary"""
        st.markdown("""
        <div style='
            background-color: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        '>
        """, unsafe_allow_html=True)
        
        # Header
        st.markdown(f"""
        <h3 style='color: #2c3e50; margin: 0 0 1.5rem 0; border-bottom: 2px solid #ecf0f1; padding-bottom: 1rem;'>
            {car_data.get('brand', 'Unknown')} {car_data.get('model', 'Unknown')}
        </h3>
        """, unsafe_allow_html=True)
        
        # Details grid
        col1, col2 = st.columns(2)
        
        with col1:
            details = {
                "Year": car_data.get('manufactured_year', 'N/A'),
                "Color": car_data.get('color', 'N/A'),
                "Body Type": car_data.get('body_type', 'N/A'),
                "Engine": f"{car_data.get('motor_size_cc', 'N/A')} cc"
            }
            
            for key, value in details.items():
                st.markdown(f"""
                <div style='margin-bottom: 0.75rem;'>
                    <span style='color: #7f8c8d; font-size: 0.9rem;'>{key}:</span>
                    <span style='color: #2c3e50; font-weight: 500; margin-left: 0.5rem;'>{value}</span>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Price - Fixed the f-string issue
            price = car_data.get('price', 'N/A')
            currency = car_data.get('currency', '')
            if price and price != 'N/A' and price != 'Not specified':
                # Format price with commas if it's a number
                price_display = f"{price:,}" if isinstance(price, (int, float)) else str(price)
                st.markdown(f"""
                <div style='
                    background-color: #f8f9fa;
                    padding: 1rem;
                    border-radius: 4px;
                    text-align: center;
                    margin-bottom: 1rem;
                '>
                    <p style='color: #7f8c8d; margin: 0; font-size: 0.9rem;'>Price</p>
                    <p style='color: #2c3e50; margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: 600;'>
                        {currency} {price_display}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # Tires
            tires = car_data.get('tires', {})
            if isinstance(tires, dict) and tires:
                st.markdown(f"""
                <div style='margin-bottom: 0.75rem;'>
                    <span style='color: #7f8c8d; font-size: 0.9rem;'>Tires:</span>
                    <span style='color: #2c3e50; font-weight: 500; margin-left: 0.5rem;'>
                        {tires.get('type', 'N/A')} ({tires.get('manufactured_year', 'N/A')})
                    </span>
                </div>
                """, unsafe_allow_html=True)
            
            # Windows
            windows = car_data.get('windows', 'N/A')
            if windows and windows != 'N/A' and windows != 'Not specified':
                st.markdown(f"""
                <div style='margin-bottom: 0.75rem;'>
                    <span style='color: #7f8c8d; font-size: 0.9rem;'>Windows:</span>
                    <span style='color: #2c3e50; font-weight: 500; margin-left: 0.5rem;'>{windows}</span>
                </div>
                """, unsafe_allow_html=True)
        
        # Notices
        notices = car_data.get('notices', [])
        if notices:
            st.markdown("<h4 style='color: #34495e; margin: 1.5rem 0 1rem 0;'>Notices</h4>", unsafe_allow_html=True)
            for notice in notices:
                st.markdown(f"""
                <div style='
                    background-color: #fff3e0;
                    border-left: 3px solid #ff9800;
                    padding: 0.75rem;
                    margin-bottom: 0.5rem;
                    border-radius: 4px;
                '>
                    <strong style='color: #e65100;'>{notice.get('type', 'Notice')}:</strong>
                    <span style='color: #555; margin-left: 0.5rem;'>{notice.get('description', '')}</span>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    @staticmethod
    def render_button(label: str, key: str = None, type: str = "primary"):
        """Render a styled button"""
        button_styles = {
            "primary": {
                "bg": "#2c3e50",
                "hover": "#1a252f",
                "text": "white"
            },
            "secondary": {
                "bg": "#95a5a6",
                "hover": "#7f8c8d",
                "text": "white"
            },
            "success": {
                "bg": "#27ae60",
                "hover": "#219a52",
                "text": "white"
            }
        }
        
        style = button_styles.get(type, button_styles["primary"])
        
        return st.button(
            label,
            key=key,
            help=None,
            on_click=None,
            args=None,
            kwargs=None,
            type="primary" if type == "primary" else "secondary"
        )
    
    @staticmethod
    def render_divider():
        """Render a professional divider"""
        st.markdown("""
        <hr style='
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 2rem 0;
        '>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_footer():
        """Render a professional footer"""
        st.markdown("""
        <div style='
            margin-top: 3rem;
            padding: 2rem 0;
            border-top: 2px solid #ecf0f1;
            text-align: center;
            color: #7f8c8d;
        '>
            <p style='margin: 0;'>Automotive Listing Platform</p>
            <p style='margin: 0.5rem 0 0 0; font-size: 0.9rem;'>
                &copy; 2025 All rights reserved. Professional vehicle listing service.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_empty_state(message: str = "No data available"):
        """Render an empty state message"""
        st.markdown(f"""
        <div style='
            text-align: center;
            padding: 3rem;
            color: #7f8c8d;
        '>
            <div style='
                font-size: 3rem;
                margin-bottom: 1rem;
                opacity: 0.3;
            '>📄</div>
            <p style='
                font-size: 1.1rem;
                margin: 0;
            '>{message}</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_loading_skeleton():
        """Render a loading skeleton"""
        st.markdown("""
        <div style='
            background-color: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 2rem;
            animation: pulse 1.5s ease-in-out infinite;
        '>
            <div style='
                height: 20px;
                background-color: #e9ecef;
                border-radius: 4px;
                margin-bottom: 1rem;
                width: 60%;
            '></div>
            <div style='
                height: 16px;
                background-color: #e9ecef;
                border-radius: 4px;
                margin-bottom: 0.5rem;
                width: 100%;
            '></div>
            <div style='
                height: 16px;
                background-color: #e9ecef;
                border-radius: 4px;
                margin-bottom: 0.5rem;
                width: 80%;
            '></div>
            <div style='
                height: 16px;
                background-color: #e9ecef;
                border-radius: 4px;
                width: 90%;
            '></div>
        </div>
        
        <style>
            @keyframes pulse {
                0% { opacity: 0.6; }
                50% { opacity: 1; }
                100% { opacity: 0.6; }
            }
        </style>
        """, unsafe_allow_html=True)