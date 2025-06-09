#!/usr/bin/env python3
"""
Configuration file using constants from yad2_mappings
"""

import os
from yad2_mappings import (
    PEUGEOT_3008, FORD_FOCUS, SUZUKI_CROSSOVER,
    AUTOMATIC, GASOLINE
)

CONFIG = {
    "car_preferences": {
        "price_range": {
            "min": 30000,
            "max": 65000
        },
        "models": [
            PEUGEOT_3008,
            FORD_FOCUS,
            SUZUKI_CROSSOVER
        ],
        "transmission": [AUTOMATIC],
        "engine_type": [GASOLINE],
        "year_range": {
            "min": 2017,
            "max": 2025
        },
        "mileage": {
            "max": 130000
        }
    },
    "notification_settings": {
        "whatsapp": {
            # Environment Variables (Non-sensitive configuration)
            "enabled": os.getenv('WHATSAPP_ENABLED', 'True').lower() == 'true',
            "phone_number": os.getenv('WHATSAPP_PHONE_NUMBER', '+972XXXXXXXXX')
        },
        "email": {
            # Environment Variables (Non-sensitive configuration)
            "enabled": os.getenv('EMAIL_ENABLED', 'True').lower() == 'true',
            "smtp_server": os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com'),
            "smtp_port": int(os.getenv('EMAIL_SMTP_PORT', '587')),
            "sender_email": os.getenv('EMAIL_SENDER', 'your_email@gmail.com'),
            "recipient_email": os.getenv('EMAIL_RECIPIENT', 'recipient@gmail.com'),
            
            # SECRETS (Sensitive credentials - should be managed securely)
            "sender_password": os.getenv('EMAIL_APP_PASSWORD', 'your_app_password'),
        },
        "twilio": {
            # SECRETS (Sensitive credentials - should be managed securely)
            "account_sid": os.getenv('TWILIO_ACCOUNT_SID', 'your_twilio_account_sid'),
            "auth_token": os.getenv('TWILIO_AUTH_TOKEN', 'your_twilio_auth_token')
        }
    },
    "scraping_settings": {
        "check_interval_minutes": 30,
        "max_results_per_check": 20,
        "timeout_minutes": 3
    }
} 