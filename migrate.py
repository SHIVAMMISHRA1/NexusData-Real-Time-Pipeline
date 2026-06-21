import sqlite3
from config import DB_NAME

print(f"🛠️ Starting Database Schema Migration Framework for: {DB_NAME}")

conn = sqlite3.connect(DB_NAME, timeout=30)
cursor = conn.cursor()

# Dynamic Target Migration Columns Mapped Array Vector
new_columns = [
    ("image_url", "TEXT DEFAULT 'https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=500'"),
    ("is_active", "INTEGER DEFAULT 1"),
    ("notification_enabled", "INTEGER DEFAULT 1")
]

try:
    # 1. Fetch current structural columns grid matrix from products table metadata
    cursor.execute("PRAGMA table_info(products)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    
    migration_triggered = False
    
    # 2. Iterate and dynamically check column existence before running ALTER queries
    for col_name, col_definition in new_columns:
        if col_name not in existing_columns:
            print(f"🚀 Altering Table: Injecting missing column [{col_name}] into storage memory cells...")
            cursor.execute(f"ALTER TABLE products ADD COLUMN {col_name} {col_definition}")
            migration_triggered = True
        else:
            print(f"ℹ️ Skipping Column [{col_name}]: Already mapped inside the system architecture schema.")
            
    if migration_triggered:
        conn.commit()
        print("✅ [MIGRATION SUCCESS] Database schema upgraded flawlessly with new control flags!")
    else:
        print("🔒 [NO CHANGE NEEDED] Database structure is already running the latest standard matrix framework.")

except Exception as err:
    print(f"❌ Structural Migration Collision Exception: {err}")
    conn.rollback()

finally:
    conn.close()