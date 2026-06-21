import sqlite3
import random
from config import DB_NAME

print(f"🔄 Smasher Module Engaging: Breaking straight price graphs inside '{DB_NAME}'")

try:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, product_name, target_price FROM products")
    all_products = cursor.fetchall()
    
    if not all_products:
        print("⚠️ Database is completely empty. Run seed.py first.")
    else:
        print(f"📈 Processing {len(all_products)} inventory clusters to calculate zigzag historical variances...")
        
        timestamps = [
            '2026-06-22 01:00:00',
            '2026-06-22 01:05:00',
            '2026-06-22 01:10:00',
            '2026-06-22 01:15:00'
        ]
        
        # Fluctuation wave configurations to trigger genuine looking e-commerce ups and downs
        multipliers = [1.03, 0.94, 1.05, 0.97]
        platforms = ["Amazon", "Flipkart", "Croma", "RelianceDigital"]
        
        for prod in all_products:
            p_id, name, target = prod
            
            for i, mult in enumerate(multipliers):
                t_stamp = timestamps[i]
                for plat in platforms:
                    swung_price = round(target * mult * random.uniform(0.98, 1.02), 2)
                    
                    cursor.execute("SELECT COUNT(*) FROM price_history WHERE product_id = ? AND platform_name = ? AND timestamp = ?", (p_id, plat, t_stamp))
                    if cursor.fetchone()[0] == 0:
                        cursor.execute("""
                            INSERT INTO price_history (product_id, platform_name, price, timestamp) 
                            VALUES (?, ?, ?, ?)
                        """, (p_id, plat, swung_price, t_stamp))
                        
        conn.commit()
        print("\n🚀 [SUCCESS] Straight lines smashed cleanly! Visual assets are fully functional.")
    conn.close()
except Exception as e:
    print(f"❌ Error during historical metrics generation: {e}")