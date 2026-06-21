import os

# 🌐 Distributed Cache Architecture Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
QUEUE_NAME = os.getenv("QUEUE_NAME", "scraper_task_queue")

# 🗄️ Relational Database Storage Engine Engine Configuration
# Changed to e-commerce streaming name to map cleanly with your Flask matrices
DB_NAME = os.getenv("DB_NAME", "omnichannel_metrics.db")

# 💬 Twilio Gateway Integration Layer (WhatsApp Notification Engine)
# Secure Environment Fetching Architecture to prevent GitHub API Key leaks
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "AC3217990fdd7ffc3a75347f77adb49767")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "d8778c09b65a2709fd39ea10ff9f8bbe")

# Official Sandbox Endpoint Node Protocols
TWILIO_FROM_WHATSAPP = os.getenv("TWILIO_FROM_WHATSAPP", "whatsapp:+14155238886")
TWILIO_TO_WHATSAPP = os.getenv("TWILIO_TO_WHATSAPP", "whatsapp:+919569270491")