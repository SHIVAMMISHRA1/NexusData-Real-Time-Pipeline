import sqlite3
from config import DB_NAME

def init_db():
    # Dynamic database execution socket initialization
    conn = sqlite3.connect(DB_NAME)
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
    conn.close()
    print(f"📦 [DB SUCCESS] Relational schema fully initialized inside '{DB_NAME}'!")

if __name__ == "__main__":
    init_db()