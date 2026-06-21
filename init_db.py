import sqlite3
import random
from datetime import datetime, timedelta
from config import DB_NAME

def init_db():
    # Dynamic database execution socket initialization
    conn = sqlite3.connect(DB_NAME, timeout=30)
    
    # ⚡ PRODUCTION ENGINE OPTIMIZATION: Write-Ahead Logging (WAL) Mode
    # Isse multi-threaded scrapers aur Flask backend ke concurrent reads-writes clash nahi karenge
    conn.execute("PRAGMA journal_mode=WAL;")
    
    cursor = conn.cursor()
    
    # 1. Core Products Catalog Metadata Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL UNIQUE,
            target_price REAL NOT NULL,
            image_url TEXT,
            notification_enabled INTEGER DEFAULT 0
        )
    """)
    
    # 2. Omnichannel Price History Dynamic Logs Telemetry Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            platform_name TEXT NOT NULL,
            price REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        )
    """)
    
    # 3. AI Predictive Math Metrics Target Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_analytics (
            product_id INTEGER PRIMARY KEY,
            volatility_index REAL,
            recommendation TEXT,
            deal_score INTEGER,
            deal_quality TEXT,
            pred_7_days REAL,
            pred_15_days REAL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    print(f"📦 [DB SUCCESS] Relational schema fully initialized inside '{DB_NAME}'!")

    # =====================================================================
    # DATA LAYER BOOTSTRAP: Seed Initial Dynamic Mock Items if Database Empty
    # =====================================================================
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        print("🌱 Seeding production tracking telemetry cells for initial load...")
        
        sample_products = [
            ("iPhone 15 Pro Max (256 GB)", 140000.0, "https://images.unsplash.com/photo-1695048133142-1a20484d2569?auto=format&fit=crop&w=300&q=80"),
            ("Optimum Nutrition Whey Gold Standard 2KG", 6500.0, "https://images.unsplash.com/photo-1579758629938-03607ccdbaba?auto=format&fit=crop&w=300&q=80"),
            ("Sony WH-1000XM5 Premium Headphones", 28000.0, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=300&q=80")
        ]
        
        platforms = ["Amazon", "Flipkart", "Croma", "RelianceDigital"]
        
        for name, target, img in sample_products:
            try:
                cursor.execute(
                    "INSERT INTO products (product_name, target_price, image_url, notification_enabled) VALUES (?, ?, ?, 1)",
                    (name, target, img)
                )
                p_id = cursor.lastrowid
                
                # Dynamic Historical Array Generation for Mock ML Vector Processing
                base_price = target * 1.05
                now = datetime.now()
                
                for i in range(10):
                    time_slot = (now - timedelta(hours=(10-i)*2)).strftime('%Y-%m-%d %H:%M:%S')
                    for plat in platforms:
                        # Random fluctuations logic to feed volatility charts
                        fluc_price = round(base_price * random.uniform(0.92, 1.04), 2)
                        cursor.execute(
                            "INSERT INTO price_history (product_id, platform_name, price, timestamp) VALUES (?, ?, ?, ?)",
                            (p_id, plat, fluc_price, time_slot)
                        )
            except Exception as e:
                print(f"⚠️ Bootstrapping error skipped: {e}")
                
        conn.commit()
        print("✅ [SEED SUCCESS] Production pipeline baseline cells generated!")

    conn.close()

if __name__ == "__main__":
    init_db()