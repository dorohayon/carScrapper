#!/usr/bin/env python3
"""
Yad2 Car Scraper - Monitors yad2.co.il for new car listings
Sends WhatsApp notifications when new cars matching your criteria are found
"""

import json
import time

import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from twilio.rest import Client
from yad2_mappings import (
    get_model_codes, get_engine_code, get_gearbox_code, 
    format_price_range, format_km_range, format_year_range
)
from config import CONFIG

class Yad2CarScraper:
    def __init__(self):
        self.config = CONFIG
        self.seen_cars = self.load_seen_cars()
        self.twilio_client = None
        self.setup_twilio()
    
    def load_seen_cars(self):
        """Load previously seen cars from seen_cars.json"""
        try:
            with open('seen_cars.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"seen_car_ids": [], "last_check": None}
    
    def save_seen_cars(self):
        """Save seen cars to JSON file"""
        with open('seen_cars.json', 'w', encoding='utf-8') as f:
            json.dump(self.seen_cars, f, ensure_ascii=False, indent=2)
    
    def setup_twilio(self):
        """Setup Twilio WhatsApp client"""
        try:
            # You'll need to set these environment variables or add them to config
            account_sid = "your_twilio_account_sid"  # Replace with your Twilio Account SID
            auth_token = "your_twilio_auth_token"   # Replace with your Twilio Auth Token
            
            self.twilio_client = Client(account_sid, auth_token)
            print("✅ Twilio WhatsApp client initialized")
        except Exception as e:
            print(f"❌ Failed to setup Twilio: {e}")

    def send_email(self, subject, message, image_url=None):
        """Send email notification using free email services with embedded image"""
        email_config = self.config.get('notification_settings', {}).get('email', {})
        
        if not email_config.get('enabled', False):
            print("📧 Email notifications disabled")
            return
            
        try:
            # Email configuration
            smtp_server = email_config['smtp_server']
            smtp_port = email_config['smtp_port']
            sender_email = email_config['sender_email']
            sender_password = email_config['sender_password']  # Use app password for Gmail
            recipient_email = email_config['recipient_email']
            
            # Create message
            msg = MIMEMultipart('related')
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Create HTML email body
            if image_url:
                # Extract the ad link from the message for separate placement
                message_lines = message.split('\n')
                ad_link = ""
                clean_message_lines = []
                
                for line in message_lines:
                    if line.startswith("🔗 Link to ad:"):
                        ad_link = line.replace("🔗 Link to ad:", "").strip()
                    else:
                        clean_message_lines.append(line)
                
                clean_message = '\n'.join(clean_message_lines).strip()
                
                html_body = f"""
                <html>
                <body>
                    <pre style="font-family: Arial, sans-serif; font-size: 14px;">{clean_message}</pre>
                    <br>
                    {f'<p><strong>🔗 <a href="{ad_link}" target="_blank">Link to ad</a></strong></p><br>' if ad_link else ''}
                    <img src="cid:car_image" style="max-width: 100%; height: auto; border-radius: 8px;">
                    <br><br>
                    <a href="{image_url.split('?')[0]}" target="_blank">View Full Size Image</a>
                </body>
                </html>
                """
                
                msg.attach(MIMEText(html_body, 'html', 'utf-8'))
                
                # Download and attach the image
                try:
                    print(f"📥 Downloading image: {image_url}")
                    response = requests.get(image_url, timeout=10)
                    if response.status_code == 200:
                        img = MIMEImage(response.content)
                        img.add_header('Content-ID', '<car_image>')
                        img.add_header('Content-Disposition', 'inline', filename="car_image.jpg")
                        msg.attach(img)
                        print("✅ Image downloaded and embedded")
                    else:
                        print(f"❌ Failed to download image: HTTP {response.status_code}")
                except Exception as img_error:
                    print(f"❌ Image download failed: {img_error}")
                    # Fallback to text email with link
                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = recipient_email
                    msg['Subject'] = subject
                    fallback_body = f"{message}\n\n📸 Car Image: {image_url}"
                    msg.attach(MIMEText(fallback_body, 'plain', 'utf-8'))
            else:
                # No image, send plain text
                msg.attach(MIMEText(message, 'plain', 'utf-8'))
            
            # Gmail SMTP configuration
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # Enable encryption
            server.login(sender_email, sender_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(sender_email, recipient_email, text)
            server.quit()
            
            print(f"✅ Email sent successfully to {recipient_email}")
            if image_url:
                print(f"📸 Image embedded in email")
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            print("💡 Make sure to use an App Password for Gmail, not your regular password")

    def send_comprehensive_email(self, new_cars):
        """Send one email with all new cars using existing email configuration"""
        # Create comprehensive email content
        count = len(new_cars)
        if count == 1:
            subject = f"🚗 New Car Alert: {new_cars[0]['model']} - {new_cars[0]['price']}"
        else:
            subject = f"🚗 {count} New Cars Found on Yad2!"
        
        # Build comprehensive message
        message_parts = [
            f"🚗 {"New Car Alert!" if count == 1 else f"{count} New Cars Found!"}",
            "",
            f"Found {count} new car{'s' if count > 1 else ''} matching your criteria:",
            "=" * 50
        ]
        
        # Add each car
        for i, car in enumerate(new_cars, 1):
            car_details = [f"\n🚗 Car #{i}:"]
            car_details.append(f"🏷️ {car['model']}")
            if car['year']:
                car_details.append(f"📅 {car['year']}")
            if car['yad']:
                car_details.append(f"👥 {car['yad']}")
            car_details.append(f"💰 {car['price']}")
            if car['agency'] != "private person":
                car_details.append(f"🏢 {car['agency']}")
            else:
                car_details.append("👤 Private Person")
            if car['marketing_text']:
                car_details.append(f"ℹ️ {car['marketing_text']}")
            car_details.append(f"🔗 Link to ad: {car['link']}")
            car_details.append("-" * 30)
            
            message_parts.extend(car_details)
        
        message_parts.extend([
            "",
            "Happy car hunting! 🚗",
            "This is an automated notification from your Yad2 Car Scraper"
        ])
        
        comprehensive_message = "\n".join(message_parts)
        
        # Use existing send_email method with special handling for multiple images
        self._send_email_with_multiple_images(subject, comprehensive_message, new_cars)

    def _send_email_with_multiple_images(self, subject, message, new_cars):
        """Helper method to send email with multiple car images"""
        email_config = self.config.get('notification_settings', {}).get('email', {})
        
        if not email_config.get('enabled', False):
            print("📧 Email notifications disabled")
            return
            
        try:
            # Use existing email configuration from config
            smtp_server = email_config['smtp_server']
            smtp_port = email_config['smtp_port']
            sender_email = email_config['sender_email']
            sender_password = email_config['sender_password']
            recipient_email = email_config['recipient_email']
            
            # Create HTML version for better formatting
            html_body = self._create_html_email_body(message, new_cars)
            
            # Create message
            msg = MIMEMultipart('related')
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # Download and attach all images
            images_attached = 0
            for i, car in enumerate(new_cars, 1):
                if car.get('image_url'):
                    try:
                        print(f"📥 Downloading image {i}/{len(new_cars)}: {car['image_url']}")
                        response = requests.get(car['image_url'], timeout=10)
                        if response.status_code == 200:
                            img = MIMEImage(response.content)
                            img.add_header('Content-ID', f'<car_image_{i}>')
                            img.add_header('Content-Disposition', 'inline', filename=f"car_{i}.jpg")
                            msg.attach(img)
                            images_attached += 1
                        else:
                            print(f"❌ Failed to download image {i}: HTTP {response.status_code}")
                    except Exception as img_error:
                        print(f"❌ Image {i} download failed: {img_error}")
            
            # Send email using existing SMTP logic
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            server.quit()
            
            print(f"✅ Email sent successfully to {recipient_email}")
            print(f"📧 Email contains: {len(new_cars)} cars, {images_attached} images")
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            print("💡 Make sure to use an App Password for Gmail, not your regular password")

    def _create_html_email_body(self, message, new_cars):
        """Create beautiful HTML email body"""
        count = len(new_cars)
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #2c5aa0;">🚗 {"New Car Alert!" if count == 1 else f"{count} New Cars Found!"}</h2>
            <p style="font-size: 16px; color: #666;">Found {count} new car{'s' if count > 1 else ''} matching your criteria:</p>
            <hr style="border: 1px solid #ddd; margin: 20px 0;">
        """
        
        # Add each car
        for i, car in enumerate(new_cars, 1):
            car_details = []
            car_details.append(f"🏷️ {car['model']}")
            if car['year']:
                car_details.append(f"📅 {car['year']}")
            if car['yad']:
                car_details.append(f"👥 {car['yad']}")
            car_details.append(f"💰 {car['price']}")
            if car['agency'] != "private person":
                car_details.append(f"🏢 {car['agency']}")
            else:
                car_details.append("👤 Private Person")
            if car['marketing_text']:
                car_details.append(f"ℹ️ {car['marketing_text']}")
            
            html_body += f"""
            <div style="border: 2px solid #e0e0e0; border-radius: 10px; padding: 20px; margin: 20px 0; background-color: #f9f9f9;">
                <h3 style="color: #2c5aa0; margin-top: 0;">Car #{i}</h3>
                <div style="font-size: 14px; line-height: 1.8;">
                    {"<br>".join(car_details)}
                </div>
                <br>
                <div style="margin: 15px 0;">
                    <strong>🔗 <a href="{car['link']}" target="_blank" style="color: #2c5aa0; text-decoration: none; font-size: 16px;">View this car on Yad2</a></strong>
                </div>
            """
            
            # Add image if available
            if car.get('image_url'):
                html_body += f"""
                <div style="margin: 15px 0;">
                    <img src="cid:car_image_{i}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                </div>
                """
            
            html_body += "</div>"
        
        html_body += """
            <hr style="border: 1px solid #ddd; margin: 30px 0;">
            <p style="font-size: 12px; color: #999; text-align: center;">
                This is an automated notification from your Yad2 Car Scraper<br>
                Happy car hunting! 🚗
            </p>
        </body>
        </html>
        """
        
        return html_body
    
    def send_whatsapp_message(self, message, image_url=None):
        """Send WhatsApp message via Twilio with optional image"""
        if not self.twilio_client:
            print("❌ WhatsApp not configured")
            return
            
        try:
            phone_number = self.config['notification_settings']['whatsapp']['phone_number']
            
            # Prepare message parameters
            message_params = {
                'body': message,
                'from_': 'whatsapp:+14155238886',  # Twilio WhatsApp sandbox number
                'to': f'whatsapp:{phone_number}'
            }
            
            # Add image if available
            if image_url:
                message_params['media_url'] = [image_url]
            
            message_obj = self.twilio_client.messages.create(**message_params)
            print(f"✅ WhatsApp message sent: {message_obj.sid}")
            if image_url:
                print(f"📸 Image included: {image_url}")
        except Exception as e:
            print(f"❌ Failed to send WhatsApp: {e}")
    
    def setup_driver(self):
        """Setup Chrome WebDriver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Add user agent to look more human
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def build_search_url(self):
        """Build Yad2 search URL based on configuration with proper parameter mapping"""
        base_url = "https://www.yad2.co.il/vehicles/cars"
        params = []
        
        prefs = self.config['car_preferences']
        
        # Models - convert to yad2 model codes
        if prefs.get('models'):
            model_codes = get_model_codes(prefs['models'])
            if model_codes:
                # Join multiple models with comma
                params.append(f"model={','.join(model_codes)}")
        
        # Price range - yad2 format: min-max
        if prefs.get('price_range'):
            min_price = prefs['price_range'].get('min')
            max_price = prefs['price_range'].get('max') 
            if min_price or max_price:
                price_range = format_price_range(min_price, max_price)
                params.append(f"price={price_range}")
        
        # Year range - yad2 format: min-max
        if prefs.get('year_range'):
            min_year = prefs['year_range'].get('min')
            max_year = prefs['year_range'].get('max')
            if min_year or max_year:
                year_range = format_year_range(min_year, max_year)
                params.append(f"year={year_range}")
        
        # Mileage - yad2 format: -1-maxkm
        if prefs.get('mileage', {}).get('max'):
            km_range = format_km_range(prefs['mileage']['max'])
            params.append(f"km={km_range}")
        
        # Engine type
        if prefs.get('engine_type'):
            engine_codes = []
            for engine in prefs['engine_type']:
                code = get_engine_code(engine)
                if code:
                    engine_codes.append(code)
            if engine_codes:
                params.append(f"engineType={','.join(engine_codes)}")
        
        # Gearbox/Transmission
        if prefs.get('transmission'):
            gearbox_codes = []
            for transmission in prefs['transmission']:
                code = get_gearbox_code(transmission)
                if code:
                    gearbox_codes.append(code)
            if gearbox_codes:
                params.append(f"gearBox={','.join(gearbox_codes)}")
        
        
        # Build final URL
        if params:
            return f"{base_url}?{'&'.join(params)}"
        return base_url
    
    def extract_car_data(self, car_element):
        """Extract car data from a listing element based on real yad2 HTML structure"""
        try:
            # Extract model/title from heading
            try:
                title_elem = car_element.find_element(By.CSS_SELECTOR, '.feed-item-info_heading__k5pVC')
                model = title_elem.text.strip()
            except:
                model = "Unknown Model"
            
            # Extract marketing text (Active, mileage info, etc.)
            try:
                marketing_elem = car_element.find_element(By.CSS_SELECTOR, '.feed-item-info_marketingText__eNE4R')
                marketing_text = marketing_elem.text.strip()
            except:
                marketing_text = ""
            
            # Extract year and hand info
            try:
                year_and_yad_elem = car_element.find_element(By.CSS_SELECTOR, '.feed-item-info_yearAndHandBox___JLbc')
                year_and_yad_info = year_and_yad_elem.text.strip()
                parts = year_and_yad_info.split('•')
                parts = [part.strip() for part in parts]
                year = parts[0] if len(parts) > 0 else ""
                yad = parts[1] if len(parts) > 1 else ""
            except:
                year = ""
                yad = ""
            
            # Extract price
            try:
                # Try to find price inside private-item-left-side first
                private_section = car_element.find_element(By.CSS_SELECTOR, '[data-testid="private-item-left-side"]')
                price_elem = private_section.find_element(By.CSS_SELECTOR, '.price_price__xQt90')
                price_text = price_elem.text.strip()
            except:
                price_text = "Price not found"
            
            # Get link from the feed-item-base-link element
            try:
                # The car_element itself should be the link element with href
                href = car_element.get_attribute('href')
                if href:
                    # Build full URL from relative href
                    # href format: "item/kdqeegdr?opened-from=feed&component-type=main_feed&spot=standard&location=1&pagination=1"
                    if href.startswith('item/'):
                        link = f"https://www.yad2.co.il/{href}"
                    elif href.startswith('http'):
                        link = href  # Already full URL
                    else:
                        link = f"https://www.yad2.co.il/{href}"
                else:
                    link = ""
            except:
                link = ""
            
            # Extract agency/seller info if available
            try:
                # Try first selector for commercial items
                agency_elem = car_element.find_element(By.CSS_SELECTOR, '.commercial-item-left-side_agencyName__psfbp')
                agency = agency_elem.text.strip()
            except:
                try:
                    # Try second selector for ultra-plus items
                    agency_elem = car_element.find_element(By.CSS_SELECTOR, '.ultra-plus-item-left-side_agencyName__0Aand')
                    agency = agency_elem.text.strip()
                except:
                    # If both selectors fail, it's likely a private person
                    agency = "private person"
            
            # Extract image URL
            try:
                image_elem = car_element.find_element(By.CSS_SELECTOR, '[data-nagish="feed-item-main-image"]')
                image_url = image_elem.get_attribute('src')
                if not image_url:
                    # Fallback: try data-src attribute (lazy loading)
                    image_url = image_elem.get_attribute('data-src')
            except:
                image_url = ""
            
            # Create comprehensive title
            title_parts = [model]
            if year:
                title_parts.append(year)
            if yad:
                title_parts.append(yad)
            if marketing_text and len(marketing_text) < 80:  # Only add if short
                title_parts.append(marketing_text)
            
            full_title = " - ".join(filter(None, title_parts))
            
            # Generate unique ID from link
            if link and 'item/' in link:
                # Extract car ID from URL like: https://www.yad2.co.il/item/kdqeegdr?...
                # Get the part after 'item/' and before any query parameters
                item_part = link.split('item/')[-1]
                car_id = item_part.split('?')[0]  # Remove query parameters
            else:
                # Fallback: use element text content hash
                import hashlib
                content = f"{model}_{price_text}_{year}_{yad}_{marketing_text}_{agency}"
                car_id = hashlib.md5(content.encode()).hexdigest()[:8]
            
            return {
                'id': car_id,
                'title': full_title,
                'model': model,
                'price': price_text,
                'year': year,
                'yad': yad,
                'marketing_text': marketing_text,
                'agency': agency,
                'link': link,
                'image_url': image_url,
                'found_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error extracting car data: {e}")
            # Print element HTML for debugging
            try:
                print(f"🔍 Element HTML: {car_element.get_attribute('outerHTML')[:200]}...")
            except:
                pass
            return None
        
    
    def scrape_cars(self):
        """Main scraping function"""
        if not self.config:
            print("❌ No configuration loaded")
            return
        
        print("🔍 ")
        
        driver = None
        try:
            driver = self.setup_driver()
            search_url = self.build_search_url()
            
            print(f"📍 Searching: {search_url}")
            driver.get(search_url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Find car listings using the real yad2 selectors
            car_elements = driver.find_elements(By.CSS_SELECTOR, '[data-nagish="feed-item-base-link"]')
            
            print(f"📊 Found {len(car_elements)} listings")
            
            new_cars = []
            
            for car_element in car_elements[:self.config['scraping_settings']['max_results_per_check']]:
                car_data = self.extract_car_data(car_element)
                
                if not car_data:
                    continue
                
                # Check if we've seen this car before
                if car_data['id'] in self.seen_cars['seen_car_ids']:
                    continue
                
                new_cars.append(car_data)
                self.seen_cars['seen_car_ids'].append(car_data['id'])
            
            # Send notifications for new cars
            if new_cars:
                print(f"🚗 Found {len(new_cars)} new cars!")
                
                # Send individual WhatsApp notifications (if enabled)
                for car in new_cars:
                    message_parts = [
                        "🚗 New Car Alert!",
                        "",
                        f"🏷️ {car['model']}",
                        f"📅 {car['year']}" if car['year'] else "",
                        f"👥 {car['yad']}" if car['yad'] else "",
                        f"💰 {car['price']}",
                        f"🏢 {car['agency']}" if car['agency'] != "private person" else "👤 Private Person",
                        f"ℹ️ {car['marketing_text']}" if car['marketing_text'] else "",
                        "",
                        "",
                        f"🔗 Link to ad: {car['link']}" if car['link'] else ""
                    ]
                    
                    # Filter out empty parts
                    message = "\n".join(filter(None, message_parts))
                    print(f"📩 Email notification prepared for: {car['model']}")
                    
                    # Send WhatsApp notification with image
                    # self.send_whatsapp_message(message, car.get('image_url'))
                    
                    time.sleep(1)  # Rate limiting between WhatsApp messages
                
                # Send ONE comprehensive email with all cars
                self.send_comprehensive_email(new_cars)
            else:
                print("😴 No new cars found")
            
            # Update last check time
            self.seen_cars['last_check'] = datetime.now().isoformat()
            self.save_seen_cars()
            
        except Exception as e:
            print(f"❌ Scraping error: {e}")
        finally:
            if driver:
                driver.quit()
    
def main():
    print("🚗 Yad2 Car Scraper Starting...")
    print(f"⏰ Running at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    scraper = Yad2CarScraper()
    
    if not scraper.config:
        print("❌ Configuration not loaded. Exiting.")
        return
    
    try:
        # Run single scrape
        scraper.scrape_cars()
        print("✅ Scrape completed successfully")
    except KeyboardInterrupt:
        print("\n👋 Scraper interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    
    print(f"⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
