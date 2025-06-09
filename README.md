# Yad2 Car Scraper

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Your Preferences
Edit `config.py` with your car preferences:
- Update price ranges, models, transmission, engine type, year range, mileage, etc.
- Sensitive credentials are read from environment variables for security

### 3. Setup Notifications

#### WhatsApp Notifications (Twilio)
1. Create a free account at [twilio.com](https://www.twilio.com)
2. Go to Console > Develop > Messaging > WhatsApp sandbox
3. Follow the WhatsApp Sandbox setup
4. Set environment variables:
   ```bash
   export TWILIO_ACCOUNT_SID="your_actual_account_sid"
   export TWILIO_AUTH_TOKEN="your_actual_auth_token"
   export WHATSAPP_PHONE_NUMBER="+972XXXXXXXXX"
   ```

#### Email Notifications
The scraper supports email notifications with embedded car images. Set environment variables:
```bash
export EMAIL_ENABLED="True"
export EMAIL_SENDER="your_email@gmail.com"
export EMAIL_APP_PASSWORD="your_app_password"
export EMAIL_RECIPIENT="recipient@gmail.com"
export EMAIL_SMTP_SERVER="smtp.gmail.com"
export EMAIL_SMTP_PORT="587"
```

### 4. Test the Scraper
```bash
# Run once
python main.py

# Run with scheduler (continuous monitoring)
python scheduler.py
```

## 🚀 GitHub Actions Deployment

### Setup GitHub Repository
1. Create a new repository on GitHub
2. Push this code to your repository
3. Configure GitHub Secrets (see below)
4. The scraper will automatically run every 30 minutes

### Required GitHub Secrets
Go to your repository → Settings → Secrets and variables → Actions → New repository secret:

#### Email Secrets:
- `EMAIL_ENABLED`: `True` or `False`
- `EMAIL_SENDER`: Your Gmail address
- `EMAIL_APP_PASSWORD`: Your Gmail app password (not regular password!)
- `EMAIL_RECIPIENT`: Email to receive notifications
- `EMAIL_SMTP_SERVER`: `smtp.gmail.com` (or your provider)
- `EMAIL_SMTP_PORT`: `587`

#### WhatsApp Secrets:
- `WHATSAPP_ENABLED`: `True` or `False`
- `WHATSAPP_PHONE_NUMBER`: Your phone number with country code (e.g., `+972123456789`)
- `TWILIO_ACCOUNT_SID`: Your Twilio Account SID
- `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token

### GitHub Actions Features:
- ✅ **Automatic scheduling**: Runs every 30 minutes
- ✅ **Manual trigger**: Can be triggered manually from Actions tab
- ✅ **Headless Chrome**: Runs in GitHub's servers
- ✅ **State persistence**: Automatically commits `seen_cars.json` updates
- ✅ **Secure secrets**: All sensitive data stored in GitHub Secrets

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

#### Environment Variables
All sensitive configuration is read from environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `EMAIL_ENABLED` | Enable email notifications | `True` |
| `EMAIL_SENDER` | Sender email address | `your_email@gmail.com` |
| `EMAIL_APP_PASSWORD` | Gmail app password | `abcd1234efgh5678` |
| `EMAIL_RECIPIENT` | Recipient email | `alerts@example.com` |
| `WHATSAPP_ENABLED` | Enable WhatsApp notifications | `True` |
| `WHATSAPP_PHONE_NUMBER` | Phone number with country code | `+972123456789` |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID | `ACxxxx...` |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token | `your_auth_token` |

## 🏃‍♂️ Running Options

### Option 1: Single Run
```bash
python main.py
```
Runs the scraper once and exits.

### Option 2: Continuous Monitoring (Local)
```bash
python scheduler.py
```
Runs the scraper continuously at the interval specified in config.

### Option 3: GitHub Actions (Recommended)
- Push to GitHub repository
- Configure secrets
- Automatic execution every 30 minutes
- No need to keep your computer running

## 🛠 Troubleshooting

### Common Issues

1. **ChromeDriver Issues**
   - The script automatically downloads ChromeDriver using webdriver-manager
   - Make sure Chrome browser is installed

2. **Missing Dependencies**
   - Run `pip install -r requirements.txt` to install all required packages

3. **Email Configuration for Gmail**
   - Use App Password instead of regular password
   - Enable 2-factor authentication first
   - Generate App Password in Google Account Security settings

4. **WhatsApp Sandbox Limitations**
   - Twilio sandbox only sends to verified numbers
   - For production, apply for Twilio WhatsApp Business API

5. **GitHub Actions Issues**
   - Check that all required secrets are set
   - View logs in Actions tab for debugging
   - Make sure repository has write permissions for the action

### Testing Tips

1. **Test locally first** with environment variables
2. **Test GitHub Action manually** using workflow_dispatch
3. **Monitor GitHub Actions logs** for any issues
4. **Check `seen_cars.json`** updates in repository commits

## 📝 File Structure

- `main.py` - Main scraper logic
- `config.py` - Configuration settings (reads from environment variables)
- `scheduler.py` - Continuous monitoring scheduler (for local use)
- `yad2_mappings.py` - URL parameter mappings for yad2.co.il
- `seen_cars.json` - Tracks previously seen cars (auto-generated)
- `requirements.txt` - Python dependencies
- `.github/workflows/scraper.yml` - GitHub Actions workflow
- `.gitignore` - Files to exclude from git

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
2. **GitHub Actions runs every 30 minutes** - this is a reasonable interval
3. **Keep your credentials secure** using GitHub Secrets
4. **Monitor your usage** - GitHub Actions has usage limits (but generous for free tier)
5. **Repository must be public** for free GitHub Actions, or use private with paid plan

## 🎯 Next Steps

Once everything is working:
1. Fine-tune your search criteria in `config.py`
2. Push to GitHub and configure secrets
3. Monitor GitHub Actions for successful runs
4. Add more car models using the mapping system
5. Customize notification messages in `main.py`

Good luck finding your perfect car! 🚗 