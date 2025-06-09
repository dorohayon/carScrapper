#!/usr/bin/env python3
"""
Yad2 Parameter Mappings
Maps human-readable car preferences to yad2.co.il URL parameters
"""

# Constants for car model keys
PEUGEOT_3008 = "peugeot 3008"
FORD_FOCUS = "ford focus"
SUZUKI_CROSSOVER = "suzuki crossover"

# Constants for engine type keys
GASOLINE = "gasoline"
DIESEL = "diesel"

# Constants for gearbox type keys
AUTOMATIC = "automatic"

# Constants for previous owners keys
ONE_OWNER = "1"
TWO_OWNERS = "2"
THREE_OWNERS = "3"

# Car Models - maps model names to yad2 model codes
CAR_MODELS = {
    PEUGEOT_3008: "10661",  
    FORD_FOCUS: "10598",
    SUZUKI_CROSSOVER: "10490",
}

# Engine Types
ENGINE_TYPES = {
    GASOLINE: "1101",
    DIESEL: "1102", 
}

# Gearbox Types  
GEARBOX_TYPES = {
    AUTOMATIC: "102",
}


# Previous Owners
PREVIOUS_OWNERS = {
    ONE_OWNER: "1",
    TWO_OWNERS: "2",
    THREE_OWNERS: "3",
}


def get_model_codes(model_names):
    """Convert list of model names to yad2 model codes"""
    codes = []
    for name in model_names:
        name_clean = name.strip().lower()
        for model_key, code in CAR_MODELS.items():
            if name_clean == model_key.lower():
                codes.append(code)
                break
    return codes

def get_engine_code(engine_type):
    """Convert engine type to yad2 code"""
    return ENGINE_TYPES.get(engine_type)

def get_gearbox_code(gearbox_type):
    """Convert gearbox type to yad2 code"""
    return GEARBOX_TYPES.get(gearbox_type)

def format_price_range(min_price, max_price):
    """Format price range for yad2 URL"""
    min_val = min_price if min_price else -1
    max_val = max_price if max_price else -1
    return f"{min_val}-{max_val}"

def format_km_range(max_km):
    """Format mileage range for yad2 URL"""
    return f"-1-{max_km}" if max_km else ""

def format_year_range(min_year, max_year):
    """Format year range for yad2 URL"""
    min_val = min_year if min_year else -1
    max_val = max_year if max_year else -1
    return f"{min_val}-{max_val}" 