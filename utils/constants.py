"""
Constants for the Streamlit application.
This file contains all the constant values used throughout the application.
"""
from enum import Enum
from typing import Dict, List

# Application Constants
APP_NAME = "Dashboard Analytics"
APP_VERSION = "1.0.0"
DEBUG_MODE = True

# Page Configuration
PAGE_CONFIG = {
    "page_title": APP_NAME,
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
    "menu_items": {
        "Get Help": "https://github.com/your-repo",
        "Report a bug": "https://github.com/your-repo/issues",
        "About": "# My Dashboard App v1.0.0"
    }
}

# Status Border Configuration
class StatusBorder(Enum):
    BORDER = False

class ValidateFile(Enum):
    LIST_DUOI_FILE_IMPORT = ['xlsx', 'xlsm', 'xls', 'RPT', 'txt', 'TXT', None]
    LIST_DUOI_FILE_EO = ['xlsx', 'xlsm', 'xls']
    LIST_DUOI_FILE_TXT = ['RPT', 'txt', 'TXT', None]
    DECODE_FILE_TXT = "utf-8"
    CATEGORY_FG = ['F']
    CATEGORY_RPM = ['P']
    LEN_RPM_LOST_VNL = 7
    LEN_LINE_FINAL = 9
    

class Pattern(Enum):
    DOT = '.'
    DOT_PATTERN = r'\.'
    CATEGORY_FILE = r'(?<=Class:\s)(?:F|P)(?=\s+Item:)'
    GET_DATETIME = r'(?:.+)(?=BinhDuong\sRTCIS)'
    GET_TONKHO = r'^(?:.+)(?<=NONE)(?:\b){0}'
    VN07 = r'(VN07)'
    TWO_SPACE = r'\s{2,}'
    ONE_SPACE = r'\s{1,}'
    STATUS = r'(RL|QU|HD)'

class Columns(Enum):
    COLUMNS_FILE_EO = ['stt', 'barcode', 'lot#', 'po#', 'owner', 'gcas', 'description', 'supply_chain', 'type', 'status', 'created_by', 'created_date', 'wh_date', 'bin', 'assignment#', 'qty', 'remained_qty']
    COLUMNS_INV = ['gcas', 'batch', 'vnl', 'status', 'qty', 'pallet', 'location', 'note_inv', 'cat_inv']
    COLUMNS_EO_NEED = ['GCAS', 'Lot#', 'Barcode', 'Qty', 'Bin', 'Type']
    COLUMNS_MASTERDATA_NEED = ['gcas','description', 'cat', 'type1', 'type2', 'source', 'jit']
    
class VNL_CAT(Enum):
    VNL_FG = 'VNL_FG'
    RPM_LOST_VNL = 'RPM_LOST_VNL'
    FG = 'FG'
    RPM = 'RPM'


    
# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "dashboard_db",
    "user": "admin",
    "password": "admin"  # Should be moved to environment variables
}

# File Paths
DATA_PATHS = {
    "raw_data": "data/raw/",
    "processed_data": "data/processed/",
    "models": "models/",
    "reports": "reports/"
}

# Date Formats
DATE_FORMATS = {
    "display": "%d-%m-%Y",
    "input": "%Y-%m-%d",
    "datetime": "%Y-%m-%d %H:%M:%S"
}

# Chart Configuration
CHART_CONFIG = {
    "default_height": 400,
    "default_width": 800,
    "color_scheme": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
}

# Status Codes
class StatusCode(Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

# User Roles
class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"

# Message Templates
MESSAGES = {
    "success": "Operation completed successfully",
    "error": "An error occurred",
    "no_data": "No data available",
    "loading": "Loading data...",
    "processing": "Processing...",
}

# API Endpoints
API_ENDPOINTS = {
    "base_url": "http://api.example.com",
    "auth": "/auth",
    "data": "/data",
    "analytics": "/analytics"
}

# Cache Configuration
CACHE_CONFIG = {
    "ttl": 3600,  # Time to live in seconds
    "max_entries": 100
}

# Visualization Settings
VIZ_SETTINGS = {
    "plot_bgcolor": "#ffffff",
    "paper_bgcolor": "#ffffff",
    "font_size": 12,
    "title_font_size": 16
}

# Data Processing
DATA_PROCESSING = {
    "chunk_size": 1000,
    "max_rows": 100000,
    "timeout": 30  # seconds
}

# Units and Measurements
UNITS = {
    "currency": "USD",
    "weight": "kg",
    "distance": "km",
    "temperature": "°C"
}

# Default Values
DEFAULTS = {
    "page_size": 50,
    "timeout": 30,
    "retry_count": 3,
    "date_range": 30  # days
}

# Error Messages
ERROR_MESSAGES = {
    "db_connection": "Failed to connect to database",
    "invalid_input": "Invalid input provided",
    "auth_failed": "Authentication failed",
    "timeout": "Operation timed out",
    "not_found": "Resource not found"
}

# Validation Rules
VALIDATION = {
    "username": {
        "min_length": 3,
        "max_length": 50,
        "pattern": r"^[a-zA-Z0-9_]+$"
    },
    "password": {
        "min_length": 8,
        "max_length": 128
    },
    "email": {
        "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    }
}

# Feature Flags
FEATURES = {
    "enable_cache": True,
    "enable_analytics": True,
    "enable_notifications": False,
    "enable_dark_mode": True
}

# Menu Items
MENU_ITEMS: Dict[str, List[str]] = {
    "Dashboard": ["Overview", "Analytics", "Reports"],
    "Data": ["Upload", "Process", "Export"],
    "Settings": ["Profile", "Preferences", "Security"]
}

# Chart Types
class ChartType(Enum):
    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"
    PIE = "pie"
    HEATMAP = "heatmap"

# Time Intervals
class TimeInterval(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"