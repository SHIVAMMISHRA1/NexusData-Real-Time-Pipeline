import sqlite3
import redis
import json
import urllib.parse
import random
from config import DB_NAME, REDIS_HOST, REDIS_PORT, QUEUE_NAME

# =====================================================================
# MASSIVE 150+ ENTERPRISE ASSETS CATALOG MATRIX (Original Stable CDN Imgs Mapped)
# =====================================================================
MEGA_CATALOG = [
    # --- 📱 SECTION 1: PREMIUM DEVICES ---
    {"name": "Apple iPhone 15 Pro Max (256 GB) Natural Titanium", "target": 135000, "img": "https://m.media-amazon.com/images/I/71d7rfSl0wL._SL1500_.jpg", "cat": "Devices"},
    {"name": "Samsung Galaxy S24 Ultra 5G (AI Edition)", "target": 110000, "img": "https://m.media-amazon.com/images/I/71RVuBr3xsL._SL1500_.jpg", "cat": "Devices"},
    {"name": "Apple MacBook Air M3 Chip 16GB RAM 512GB", "target": 115000, "img": "https://m.media-amazon.com/images/I/71-D1x5qykL._SL1500_.jpg", "cat": "Devices"},
    {"name": "Sony WH-1000XM5 Premium Wireless Headphones", "target": 25000, "img": "https://m.media-amazon.com/images/I/61+btxz95OL._SL1500_.jpg", "cat": "Devices"},
    {"name": "OnePlus 12 5G (Flowy Emerald, 256GB)", "target": 60000, "img": "https://m.media-amazon.com/images/I/717Qo4MH97L._SL1500_.jpg", "cat": "Devices"},
    {"name": "Apple iPad Pro M4 Ultra Thin Liquid Retina", "target": 94000, "img": "https://m.media-amazon.com/images/I/61fA8j4W3tL._SL1500_.jpg", "cat": "Devices"},
    {"name": "Google Pixel 8 Pro (Bay Blue, 128GB)", "target": 98000, "img": "https://m.media-amazon.com/images/I/71206t217NL._SL1500_.jpg", "cat": "Devices"},
    {"name": "Asus ROG Strix Scar 16 Gaming Laptop", "target": 240000, "img": "https://m.media-amazon.com/images/I/71h8b2p-jGL._SL1500_.jpg", "cat": "Devices"},
    
    # --- 💪 SECTION 2: FITNESS GYM NUTRITION & GEAR ---
    {"name": "Optimum Nutrition ON Gold Standard 100% Whey Protein 5 lbs", "target": 6200, "img": "https://m.media-amazon.com/images/I/7162y1uV5xL._SL1500_.jpg", "cat": "Fitness"},
    {"name": "Ultimate Nutrition Prostar 100% Whey Protein 5.28 lbs", "target": 4900, "img": "https://m.media-amazon.com/images/I/61V1h4YtV+L._SL1500_.jpg", "cat": "Fitness"},
    {"name": "MuscleBlaze Biozyme Performance Whey Protein 2kg", "target": 4300, "img": "https://m.media-amazon.com/images/I/61+u4+L9OEL._SL1500_.jpg", "cat": "Fitness"},
    {"name": "GNC Pro Performance Creatine Monohydrate 250g", "target": 1100, "img": "https://m.media-amazon.com/images/I/51rP63n-tIL._SL1500_.jpg", "cat": "Fitness"},
    {"name": "Asitis Nutrition Whey Protein Isolate 1kg", "target": 1800, "img": "https://m.media-amazon.com/images/I/61XfL8oAJKL._SL1100_.jpg", "cat": "Fitness"},
    {"name": "Yogabar Premium Wholegrain Rolled Oats 1kg Pack", "target": 290, "img": "https://m.media-amazon.com/images/I/71Zt9X0yq1L._SL1500_.jpg", "cat": "Fitness"},

    # --- 🥤 SECTION 3: FAST FMCG GROCERY & LIQUIDS ---
    {"name": "Coca-Cola Zero Sugar Premium Can Pack of 6", "target": 230, "img": "https://m.media-amazon.com/images/I/61R5aLpM3zL._SL1500_.jpg", "cat": "Grocery"},
    {"name": "Red Bull Energy Drink 250ml Pack of 4", "target": 460, "img": "https://m.media-amazon.com/images/I/61k3Aap4nSL._SL1000_.jpg", "cat": "Grocery"},
    {"name": "Cadbury Dairy Milk Silk Hazelnut Bar 143g", "target": 150, "img": "https://m.media-amazon.com/images/I/61t-Xh+8KCL._SL1500_.jpg", "cat": "Grocery"},
    {"name": "Maggi 2-Minute Masala Noodles 12-Pack Multipack", "target": 160, "img": "https://m.media-amazon.com/images/I/810vQ7W7RFL._SL1500_.jpg", "cat": "Grocery"},
    {"name": "Tata Salt Vacuum Evaporated Iodized Salt 1kg", "target": 26, "img": "https://m.media-amazon.com/images/I/61D3+f-m4DL._SL1500_.jpg", "cat": "Grocery"}
]

# Loop scalability structure to populate 50 elements per category quadrant safely
for x in range(1, 45):
    MEGA_CATALOG.append({"name": f"Premium Enterprise Tech Core Series Model X-{x}", "target": 5000 + x * 350, "img": "https://m.media-amazon.com/images/I/61ssDZ62NzL._SL1500_.jpg", "cat": "Devices"})
    MEGA_CATALOG.append({"name": f"Resilient Pure Muscle Amino Powder Blend Matrix-{x}", "target": 1200 + x * 210, "img": "https://m.media-amazon.com/images/I/61uR4A-64yL._SL1500_.jpg", "cat": "Fitness"})
    MEGA_CATALOG.append({"name": f"High-Volume Superstore Organic Pantry Standard Pack-{x}", "target": 90 + x * 15, "img": "https://m.media-amazon.com/images/I/71Zt9X0yq1L._SL1500_.jpg", "cat": "Grocery"})

def build_bypassed_marketplace_urls(product_name):
    encoded_name = urllib.parse.quote(str(product_name))
    return {
        "Amazon": f"https://www.amazon.in/s?k={encoded_name}",
        "Flipkart": f"https://www.flipkart.com/search?q={encoded_name}",
        "Croma": f"https://www.croma.com/search/?text={encoded_name}",
        "RelianceDigital": f"https://www.reliancedigital.in/search?q={encoded_name}:relevance"
    }

def wipe_and_seed_system():
    print(f"🧹 Purging relational structures inside '{DB_NAME}'. Instantiating large catalog data streams...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM price_history")
    cursor.execute("DELETE FROM product_analytics")
    cursor.execute("DELETE FROM products")
    conn.commit()
    
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_connect_timeout=2)
        r.delete(QUEUE_NAME)
        print("⚡ Redis tasks buffer queue wiped successfully.")
    except:
        r = None

    print(f"🌱 Seeding {len(MEGA_CATALOG)} structured categorical items into engine space...")
    
    for item in MEGA_CATALOG:
        cursor.execute(
            "INSERT INTO products (product_name, target_price, image_url, notification_enabled) VALUES (?, ?, ?, 1)", 
            (item["name"], item["target"], item["img"])
        )
        p_id = cursor.lastrowid
        
        # 📈 Live pricing interpolation maps to drop steady baseline analytics values inside system
        cursor.execute("""
            INSERT INTO product_analytics (product_id, volatility_index, recommendation, deal_score, deal_quality, pred_7_days, pred_15_days)
            VALUES (?, 1.5, 'BUY', 78, 'Good Deal', ?, ?)
        """, (p_id, round(item["target"] * 0.97, 2), round(item["target"] * 0.95, 2)))
        
        links_pool = build_bypassed_marketplace_urls(item["name"])
        for platform, url in links_pool.items():
            base_p = item["target"]
            # FIXED QUERY: Using clean variable binding mapping instead of crashing python string interpolation scripts
            for i in range(5):
                mock_p = round(base_p * random.uniform(0.94, 1.06), 2)
                mock_timestamp = f"2026-06-22 00:0{i}:00"
                cursor.execute(
                    "INSERT INTO price_history (product_id, platform_name, price, timestamp) VALUES (?, ?, ?, ?)",
                    (p_id, platform, mock_p, mock_timestamp)
                )
                
            if r:
                task = {"product_id": p_id, "platform": platform, "context": item["name"], "url": url}
                r.rpush(QUEUE_NAME, json.dumps(task))
        
    conn.commit()
    conn.close()
    print("\n🎯 [MIGRATION & SEED COMPLETE] 150+ Dynamic items successfully operational without data leaks!")

if __name__ == "__main__":
    wipe_and_seed_system()