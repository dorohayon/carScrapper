#!/usr/bin/env python3
"""
Configuration file using constants from yad2_mappings
"""

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
            "enabled": True,
            "phone_number": "+972XXXXXXXXX"
        },
        "email": {
            "enabled": True,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "dornir9@gmail.com",
            "sender_password": "nyxpjtjbeltalhob",
            "recipient_email": "dornir9@gmail.com"
        }
    },
    "scraping_settings": {
        "check_interval_minutes": 30,
        "max_results_per_check": 20,
        "timeout_minutes": 3
    }
} 