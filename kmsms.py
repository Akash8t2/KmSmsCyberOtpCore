#!/usr/bin/env python3
import requests
import time
import re
import logging
import json
import os
from datetime import datetime
from urllib.parse import urlencode
import html

# ================= CONFIG =================

# AJAX URL - AGENT interface (9 columns)
AJAX_URL = "http://54.36.173.235/ints/agent/res/data_smscdr.php"

# Bot Configuration - ALL from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHAT_IDS = os.getenv("CHAT_IDS", "-1003559187782,-1003316982194").split(",")

# Cookies - from environment variable
PHPSESSID = os.getenv("PHPSESSID", "")
COOKIES = {
    "PHPSESSID": PHPSESSID
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "http://54.36.173.235/ints/agent/smscdr.php",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}

CHECK_INTERVAL = 10
STATE_FILE = "state.json"

# Button URLs - ALL from environment variables
DEVELOPER_URL = "https://t.me/botcasx"
# Get from environment variables with better defaults
NUMBERS_URL_1 = os.getenv("NUMBERS_URL_1", "https://t.me/alltgmethod11")
NUMBERS_URL_2 = os.getenv("NUMBERS_URL_2", "https://t.me/CyberOTPCore")
SUPPORT_URL_1 = os.getenv("SUPPORT_URL_1", "https://t.me/+zu_E8bhN0WU5OTNl")
SUPPORT_URL_2 = os.getenv("SUPPORT_URL_2", "https://t.me/CYBER_OTP1_CORE")

# =========================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

# Suppress urllib3 warnings
logging.getLogger("urllib3").setLevel(logging.WARNING)

session = requests.Session()
session.headers.update(HEADERS)
session.cookies.update(COOKIES)

# ================= STATE =================

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading state: {e}")
    return {"last_uid": None, "processed_ids": []}

def save_state(state):
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        logging.error(f"Error saving state: {e}")

STATE = load_state()

# ================= HELPERS =================

def extract_otp(text):
    """Extract OTP from SMS text"""
    if not text:
        return "N/A"
    
    # Telegram codes
    telegram_match = re.search(r'Telegram code\s+(\d{4,8})', text)
    if telegram_match:
        return telegram_match.group(1)
    
    # General patterns
    patterns = [
        r'\b(\d{4,8})\b',
        r'code[\s:]+(\d{4,8})',
        r'OTP[\s:]+(\d{4,8})',
        r'verification[\s:]+(\d{4,8})',
        r'密码[\s:]+(\d{4,8})',
        r'코드[\s:]+(\d{4,8})',
        r'код[\s:]+(\d{4,8})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return "N/A"

def clean_phone_number(number):
    """Clean and format phone number"""
    if not number:
        return "N/A"
    
    cleaned = re.sub(r'\D', '', number)
    if len(cleaned) >= 10:
        return f"+{cleaned}"
    return number

def build_payload():
    """Build AJAX payload for AGENT interface (9 columns)"""
    today = datetime.now().strftime("%Y-%m-%d")
    timestamp = int(time.time() * 1000)
    
    params = {
        "fdate1": f"{today} 00:00:00",
        "fdate2": f"{today} 23:59:59",
        "frange": "",
        "fclient": "",  # Different from client interface
        "fnum": "",
        "fcli": "",
        "fgdate": "",
        "fgmonth": "",
        "fgrange": "",
        "fgclient": "",  # Different from client interface
        "fgnumber": "",
        "fgcli": "",
        "fg": 0,
        "sEcho": 1,
        "iColumns": 9,  # 9 columns for agent interface
        "sColumns": ",,,,,,,,",  # 8 commas for 9 columns
        "iDisplayStart": 0,
        "iDisplayLength": 25,
        "mDataProp_0": 0,
        "sSearch_0": "",
        "bRegex_0": "false",
        "bSearchable_0": "true",
        "bSortable_0": "true",
        "mDataProp_1": 1,
        "sSearch_1": "",
        "bRegex_1": "false",
        "bSearchable_1": "true",
        "bSortable_1": "true",
        "mDataProp_2": 2,
        "sSearch_2": "",
        "bRegex_2": "false",
        "bSearchable_2": "true",
        "bSortable_2": "true",
        "mDataProp_3": 3,
        "sSearch_3": "",
        "bRegex_3": "false",
        "bSearchable_3": "true",
        "bSortable_3": "true",
        "mDataProp_4": 4,
        "sSearch_4": "",
        "bRegex_4": "false",
        "bSearchable_4": "true",
        "bSortable_4": "true",
        "mDataProp_5": 5,
        "sSearch_5": "",
        "bRegex_5": "false",
        "bSearchable_5": "true",
        "bSortable_5": "true",
        "mDataProp_6": 6,
        "sSearch_6": "",
        "bRegex_6": "false",
        "bSearchable_6": "true",
        "bSortable_6": "true",
        "mDataProp_7": 7,
        "sSearch_7": "",
        "bRegex_7": "false",
        "bSearchable_7": "true",
        "bSortable_7": "true",
        "mDataProp_8": 8,
        "sSearch_8": "",
        "bRegex_8": "false",
        "bSearchable_8": "true",
        "bSortable_8": "false",
        "sSearch": "",
        "bRegex": "false",
        "iSortCol_0": 0,
        "sSortDir_0": "desc",
        "iSortingCols": 1,
        "_": timestamp
    }
    
    return params

def format_message(row):
    """Format SMS data into HTML Telegram message for AGENT interface (9 columns)"""
    try:
        # AGENT interface has 9 columns
        # Based on sample: [date, route, number, service, null, message, currency, cost, status]
        date = row[0] if len(row) > 0 else "N/A"
        route = row[1] if len(row) > 1 else "Unknown"
        number = clean_phone_number(row[2]) if len(row) > 2 else "N/A"
        service = row[3] if len(row) > 3 else "Unknown"
        
        # Message might be in column 5 (index 5) for agent interface
        # Check both column 4 and 5
        message = ""
        if len(row) > 5 and row[5]:
            message = row[5]
        elif len(row) > 4 and row[4]:
            message = row[4]
        
        # Extract country from route
        country = "Unknown"
        if route and isinstance(route, str):
            # Remove any numbers/dashes and take first word
            country_parts = re.split(r'[\d-]', route, 1)
            if country_parts and country_parts[0].strip():
                country = country_parts[0].strip()
        
        # Extract OTP
        otp = extract_otp(message)
        
        # Escape HTML special characters
        safe_number = html.escape(str(number))
        safe_otp = html.escape(str(otp))
        safe_service = html.escape(str(service))
        safe_country = html.escape(str(country))
        safe_date = html.escape(str(date))
        
        # Format message
        safe_message = html.escape(str(message))
        
        # Format as HTML with newlines
        formatted = (
            "💎 <b>PREMIUM OTP ALERT</b> 💎\n"
            "<i>Instant • Secure • Verified</i>\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"📞 <b>Number</b> <code>{safe_number}</code>\n"
            f"🔐 <b>OTP CODE</b> 🔥 <code>{safe_otp}</code> 🔥\n"
            f"🏷 <b>Service</b> <b>{safe_service}</b>\n"
            f"🌍 <b>Country</b> <b>{safe_country}</b>\n"
            f"🕒 <b>Received At</b> <code>{safe_date}</code>\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"💬 <b>Message Content</b>\n"
            f"<i>{safe_message}</i>\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "⚡ <b>POWERED BY @Nexora_00</b>"
        )
        
        return formatted
    except Exception as e:
        logging.error(f"Error formatting message: {e}")
        return None

def create_keyboard():
    """Create inline keyboard with 5 buttons"""
    return {
        "inline_keyboard": [
            # First row: 3 buttons
            [
                {"text": "🧑‍💻 Dev", "url": DEVELOPER_URL},
                {"text": "📱 Numbers 1", "url": NUMBERS_URL_1},
                {"text": "📱 Numbers 2", "url": NUMBERS_URL_2}
            ],
            # Second row: 2 buttons
            [
                {"text": "🆘 Support 1", "url": SUPPORT_URL_1},
                {"text": "🆘 Support 2", "url": SUPPORT_URL_2}
            ]
        ]
    }

def send_telegram(text, chat_id):
    """Send message to specific Telegram chat"""
    if not text:
        return False
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": create_keyboard()
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            return True
        else:
            error_data = response.json()
            logging.error(f"Telegram API error: {error_data.get('description', 'Unknown error')}")
            return False
    except Exception as e:
        logging.error(f"Error sending to Telegram: {e}")
        return False

# ================= CORE LOGIC =================

def fetch_latest_sms():
    """Fetch latest SMS from AGENT website"""
    global STATE
    
    try:
        params = build_payload()
        
        logging.info(f"Fetching data from {AJAX_URL}")
        response = session.get(AJAX_URL, params=params, timeout=30)
        
        if response.status_code != 200:
            logging.error(f"HTTP Error: {response.status_code}")
            return
        
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {e}")
            logging.debug(f"Response text: {response.text[:200]}")
            return
        
        rows = data.get("aaData", [])
        if not rows:
            logging.debug("No data found in response")
            return
        
        logging.info(f"Found {len(rows)} total rows")
        
        # Filter valid rows
        valid_rows = []
        for row in rows:
            if not isinstance(row, list) or len(row) < 6:  # At least 6 columns for agent
                continue
            
            # Skip summary rows (they start with "0,0,0," or similar)
            if isinstance(row[0], str) and (row[0].startswith("0,0,0,") or row[0].startswith("0,0.01,0,")):
                continue
            
            # Check for valid date format
            if not row[0] or not re.match(r'\d{4}-\d{2}-\d{2}', str(row[0])):
                continue
            
            valid_rows.append(row)
        
        logging.info(f"Valid SMS rows: {len(valid_rows)}")
        
        if not valid_rows:
            return
        
        # Sort by date (newest first)
        valid_rows.sort(
            key=lambda x: datetime.strptime(x[0], "%Y-%m-%d %H:%M:%S"),
            reverse=True
        )
        
        # Process newest row
        newest = valid_rows[0]
        
        # Create unique ID
        sms_id = f"{newest[0]}_{newest[2]}"
        if len(newest) > 5 and newest[5]:
            sms_id += f"_{hash(str(newest[5])[:50])}"
        elif len(newest) > 4 and newest[4]:
            sms_id += f"_{hash(str(newest[4])[:50])}"
        
        # Check if already processed
        if STATE["last_uid"] == sms_id or sms_id in STATE.get("processed_ids", []):
            logging.debug("No new SMS found")
            return
        
        logging.info(f"New SMS detected: {newest[2]} at {newest[0]}")
        
        # Format message
        formatted_msg = format_message(newest)
        if not formatted_msg:
            logging.error("Failed to format message")
            return
        
        # Send to all chat IDs
        success_count = 0
        for chat_id in CHAT_IDS:
            if send_telegram(formatted_msg, chat_id):
                success_count += 1
                time.sleep(1)  # Small delay between sends
        
        if success_count > 0:
            logging.info(f"OTP sent to {success_count} chats for {newest[2]}")
            
            # Update state
            STATE["last_uid"] = sms_id
            
            # Keep track of processed IDs
            processed_ids = STATE.get("processed_ids", [])
            processed_ids.append(sms_id)
            if len(processed_ids) > 200:
                processed_ids = processed_ids[-200:]
            STATE["processed_ids"] = processed_ids
            
            save_state(STATE)
        else:
            logging.error("Failed to send to any chat")
        
    except requests.RequestException as e:
        logging.error(f"Network error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = ["BOT_TOKEN", "PHPSESSID"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logging.warning(f"Missing environment variables: {', '.join(missing_vars)}")
        logging.warning("Using default values. This may not work properly.")
        return False
    
    return True

def print_config():
    """Print configuration details"""
    logging.info("=" * 60)
    logging.info("🚀 PREMIUM OTP BOT STARTED (AGENT INTERFACE)")
    logging.info("=" * 60)
    logging.info(f"Website URL: {AJAX_URL}")
    logging.info(f"Interface Type: AGENT (9 columns)")
    logging.info(f"Chat IDs: {', '.join(CHAT_IDS)}")
    logging.info(f"Check Interval: {CHECK_INTERVAL} seconds")
    logging.info("=" * 60)
    logging.info("Authentication:")
    logging.info(f"Bot Token: {'✓ Set' if os.getenv('BOT_TOKEN') else '✗ Using default'}")
    logging.info(f"Session ID: {'✓ Set' if os.getenv('PHPSESSID') else '✗ Using default'}")
    logging.info("=" * 60)
    logging.info("Button Configuration:")
    logging.info(f"1. 🧑‍💻 Dev: {DEVELOPER_URL}")
    logging.info(f"2. 📱 Numbers 1: {NUMBERS_URL_1}")
    logging.info(f"3. 📱 Numbers 2: {NUMBERS_URL_2}")
    logging.info(f"4. 🆘 Support 1: {SUPPORT_URL_1}")
    logging.info(f"5. 🆘 Support 2: {SUPPORT_URL_2}")
    logging.info("=" * 60)

# ================= MAIN =================

def main():
    """Main function"""
    # Check environment
    check_environment()
    print_config()
    
    # Main loop
    error_count = 0
    max_errors = 5
    
    while True:
        try:
            fetch_latest_sms()
            error_count = 0  # Reset error count on success
        except KeyboardInterrupt:
            logging.info("Bot stopped by user")
            break
        except Exception as e:
            error_count += 1
            logging.error(f"Error in main loop ({error_count}/{max_errors}): {e}")
            
            if error_count >= max_errors:
                logging.error("Too many consecutive errors. Waiting 60 seconds...")
                time.sleep(60)
                error_count = 0
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
