# Yad2 Car Scraper Setup Guide

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Your Preferences
Edit `config.py` with your car preferences:
- Update price ranges, models, transmission, engine type, year range, mileage, etc.
- Set your phone number for WhatsApp notifications
- Configure email settings for email notifications

### 3. Setup Notifications

#### WhatsApp Notifications (Twilio)
1. Create a free account at [twilio.com](https://www.twilio.com)
2. Go to Console > Develop > Messaging > WhatsApp sandbox
3. Follow the WhatsApp Sandbox setup
4. Get your Account SID and Auth Token
5. Update `main.py` lines 45-46 with your credentials:
   ```python
   account_sid = "your_actual_account_sid"
   auth_token = "your_actual_auth_token"
   ```

#### Email Notifications
The scraper supports email notifications with embedded car images. Configure in `config.py`:
- Update `smtp_server`, `smtp_port` for your email provider
- Set `sender_email` and `sender_password` (use App Password for Gmail)
- Set `recipient_email` for notifications
- Set `enabled: True` to activate email notifications

### 4. Test the Scraper
```bash
# Run once
python main.py

# Run with scheduler (continuous monitoring)
python scheduler.py
```

## 🔧 Configuration Details

### config.py Settings

#### Car Preferences
```python
"car_preferences": {
    "price_range": {"min": 30000, "max": 65000},
    "models": [PEUGEOT_3008, FORD_FOCUS, SUZUKI_CROSSOVER],
    "transmission": [AUTOMATIC],
    "engine_type": [GASOLINE],
    "year_range": {"min": 2017, "max": 2025},
    "mileage": {"max": 130000}
}
```

Available model constants (from `yad2_mappings.py`):
- `PEUGEOT_3008`
- `FORD_FOCUS` 
- `SUZUKI_CROSSOVER`

Available transmission constants:
- `AUTOMATIC`

Available engine type constants:
- `GASOLINE`
- `DIESEL`

#### Notification Settings
```python
"notification_settings": {
    "whatsapp": {
        "enabled": True,
        "phone_number": "+972XXXXXXXXX"
    },
    "email": {
        "enabled": True,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": "your_email@gmail.com",
        "sender_password": "your_app_password",
        "recipient_email": "recipient@gmail.com"
    }
}
```

#### Scraping Settings
```python
"scraping_settings": {
    "check_interval_minutes": 30,  # How often to check
    "max_results_per_check": 20,   # Max listings to process per check
    "timeout_minutes": 3           # Browser timeout
}
```

## 🏃‍♂️ Running Options

### Option 1: Single Run
```bash
python main.py
```
Runs the scraper once and exits.

### Option 2: Continuous Monitoring (Recommended)
```bash
python scheduler.py
```
Runs the scraper continuously at the interval specified in config.

## 🛠 Troubleshooting

### Common Issues

1. **ChromeDriver Issues**
   - The script automatically downloads ChromeDriver using webdriver-manager
   - Make sure Chrome browser is installed

2. **Missing Dependencies**
   - Run `pip install -r requirements.txt` to install all required packages
   - Make sure `twilio` package is installed for WhatsApp notifications

3. **Email Configuration for Gmail**
   - Use App Password instead of regular password
   - Enable 2-factor authentication first
   - Generate App Password in Google Account Security settings

4. **WhatsApp Sandbox Limitations**
   - Twilio sandbox only sends to verified numbers
   - For production, apply for Twilio WhatsApp Business API

5. **Website Structure Changes**
   - Yad2 may change their HTML structure
   - Update CSS selectors in `extract_car_data()` method if needed

### Testing Tips

1. **Start with longer intervals** (30+ minutes) to avoid being blocked
2. **Test with broader search criteria** first
3. **Monitor console output** for errors
4. **Check `seen_cars.json`** to see tracked cars
5. **Test notifications** with a small price range first

## 📝 File Structure

- `main.py` - Main scraper logic
- `config.py` - Configuration settings
- `scheduler.py` - Continuous monitoring scheduler
- `yad2_mappings.py` - URL parameter mappings for yad2.co.il
- `seen_cars.json` - Tracks previously seen cars (auto-generated)
- `requirements.txt` - Python dependencies

## 🔍 Adding More Car Models

To add more car models:

1. Find the model code from yad2.co.il URL parameters
2. Add the model to `yad2_mappings.py`:
   ```python
   NEW_MODEL = "new model name"
   CAR_MODELS = {
       # ... existing models ...
       NEW_MODEL: "model_code_from_yad2",
   }
   ```
3. Import and use in `config.py`:
   ```python
   from yad2_mappings import NEW_MODEL
   # Add to models list
   "models": [PEUGEOT_3008, FORD_FOCUS, NEW_MODEL]
   ```

## 📧 Notification Features

### Email Notifications
- **Embedded Images**: Car photos are embedded directly in email
- **Comprehensive Reports**: Multiple cars in single email
- **Fallback Support**: Text-only mode if image download fails
- **Rich HTML Format**: Clean, readable email layout

### WhatsApp Notifications
- **Text Messages**: Car details via WhatsApp
- **Image Support**: Car photos sent as attachments
- **Twilio Integration**: Uses Twilio WhatsApp API

## ⚠️ Important Notes

1. **Respect yad2.co.il's terms of service**
2. **Don't set check intervals too frequently** (recommend 30+ minutes minimum)
3. **Use the scheduler for continuous monitoring**
4. **Keep your Twilio and email credentials secure**
5. **Monitor rate limiting** to avoid being blocked

## 🎯 Next Steps

Once everything is working:
1. Fine-tune your search criteria in `config.py`
2. Adjust notification frequency and methods
3. Consider running `scheduler.py` on a VPS for 24/7 monitoring
4. Add more car models using the mapping system
5. Customize notification messages in `main.py`

Good luck finding your perfect car! 🚗 