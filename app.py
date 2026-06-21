from flask import Flask, render_template, request, jsonify
import sqlite3
import json
import urllib.parse
import random
import redis
from config import DB_NAME, REDIS_HOST, REDIS_PORT, QUEUE_NAME

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect(DB_NAME, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn

def build_bypassed_marketplace_urls(product_name):
    encoded_name = urllib.parse.quote(str(product_name))
    return {
        "Amazon": f"https://www.amazon.in/s?k={encoded_name}",
        "Flipkart": f"https://www.flipkart.com/search?q={encoded_name}"
    }

def calculate_statistical_telemetry(p_id, cursor):
    cursor.execute("SELECT platform_name, price, timestamp FROM price_history WHERE product_id = ? ORDER BY id ASC", (p_id,))
    history_rows = cursor.fetchall()
    
    prices = [float(row['price']) for row in history_rows if row['price'] is not None]
    if not prices: return None

    hist_min = min(prices)
    hist_max = max(prices)
    hist_avg = sum(prices) / len(prices)
    
    platforms = ["Amazon", "Flipkart"]
    store_prices = {p: "N/A" for p in platforms}
    
    for row in reversed(history_rows):
        plat, val = row['platform_name'], row['price']
        if plat in store_prices and store_prices[plat] == "N/A" and val is not None:
            store_prices[plat] = float(val)

    n = len(prices)
    x = list(range(n))
    m = 0.0
    if n >= 2:
        sum_x = sum(x)
        sum_y = sum(prices)
        sum_xy = sum(i * j for i, j in zip(x, prices))
        sum_xx = sum(i ** 2 for i in x)
        den = (n * sum_xx - sum_x ** 2)
        m = (n * sum_xy - sum_x * sum_y) / den if den != 0 else 0
        
    pred_7 = round(float(prices[-1] + (m * 2)), 2)
    pred_15 = round(float(prices[-1] + (m * 5)), 2)
    
    chart_labels, chart_prices = [], []
    for r in history_rows[-8:]:
        t_val = r['timestamp'] or "00:00"
        t_clean = t_val.split(" ")[1][:5] if " " in t_val else t_val
        chart_labels.append(t_clean)
        chart_prices.append(float(r['price']))

    return {
        "hist_min": hist_min, "hist_max": hist_max, "hist_avg": int(hist_avg),
        "store_prices": store_prices, "pred_7": pred_7, "pred_15": pred_15,
        "chart_labels": chart_labels, "chart_prices": chart_prices
    }

@app.route('/')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, product_name, target_price, image_url, notification_enabled FROM products ORDER BY id DESC")
    products = cursor.fetchall()
    
    inventory_payload = []
    for p in products:
        stats = calculate_statistical_telemetry(p['id'], cursor)
        urls_pool = build_bypassed_marketplace_urls(p['product_name'])
        
        best_price = p['target_price']
        best_platform = "Flipkart"
        if stats:
            valid_p = {k: v for k, v in stats["store_prices"].items() if v != "N/A"}
            if valid_p:
                best_price = min(valid_p.values())
                best_platform = [k for k, v in valid_p.items() if v == best_price][0]
                
        name_l = p['product_name'].lower()
        if any(x in name_l for x in ["iphone", "macbook", "ipad", "gadget", "sony", "s24", "pixel", "laptop", "series", "watch"]): category = "Devices"
        elif any(x in name_l for x in ["protein", "whey", "creatine", "supplement", "fitness", "powder", "shoes", "puma"]): category = "Fitness"
        else: category = "Grocery"

        inventory_payload.append({
            "id": p['id'], "name": p['product_name'], "target": p['target_price'], "image": p['image_url'],
            "best_price": best_price, "best_platform": best_platform, "stats": stats, "urls_pool": urls_pool,
            "notify": p['notification_enabled'], "category": category
        })
    conn.close()
    return render_template('dashboard.html', inventory_payload=inventory_payload)

@app.route('/api/live-search', methods=['POST'])
def live_search():
    query_data = request.json
    search_keyword = query_data.get("keyword", "").strip()
    if not search_keyword:
        return jsonify({"success": False, "message": "Query empty"})

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM products WHERE product_name LIKE ?", (f"%{search_keyword}%",))
    existing = cursor.fetchone()
    
    if not existing:
        # CRITICAL FIX: Target ko high set karenge taaki worker live price aate hi trigger hit kar de
        estimated_target = 999999 
        default_img = "https://images.unsplash.com/photo-1531403009284-440f080d1e12?w=600"
        
        cursor.execute(
            "INSERT INTO products (product_name, target_price, image_url, notification_enabled) VALUES (?, ?, ?, 1)",
            (search_keyword, estimated_target, default_img)
        )
        p_id = cursor.lastrowid
        
        try:
            r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
            urls_pool = build_bypassed_marketplace_urls(search_keyword)
            for platform, target_url in urls_pool.items():
                task = {"product_id": p_id, "platform": platform, "context": search_keyword, "url": target_url}
                r.rpush(QUEUE_NAME, json.dumps(task))
        except Exception as queue_err:
            print(f"❌ Redis Ingestion Error: {queue_err}")
            
        conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    query = request.args.get('q', '').strip().lower()
    if not query: return jsonify([])
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT product_name FROM products WHERE product_name LIKE ? LIMIT 6", (f"%{query}%",))
    suggestions = [row['product_name'] for row in cursor.fetchall()]
    conn.close()
    return jsonify(suggestions)

@app.route('/api/toggle-alert/<int:p_id>', methods=['POST'])
def toggle_alert(p_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT notification_enabled FROM products WHERE id = ?", (p_id,))
    row = cursor.fetchone()
    new_state = 0
    if row:
        new_state = 0 if row[0] == 1 else 1
        cursor.execute("UPDATE products SET notification_enabled = ? WHERE id = ?", (new_state, p_id))
        conn.commit()
    conn.close()
    return jsonify({"success": True, "new_state": new_state})

@app.route('/api/telemetry')
def api_telemetry():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, product_name, target_price, image_url, notification_enabled FROM products ORDER BY id DESC")
    products = cursor.fetchall()
    
    inventory_payload = []
    for p in products:
        stats = calculate_statistical_telemetry(p['id'], cursor)
        urls_pool = build_bypassed_marketplace_urls(p['product_name'])
        best_price = p['target_price']
        best_platform = "Flipkart"
        if stats:
            valid_p = {k: v for k, v in stats["store_prices"].items() if v != "N/A"}
            if valid_p:
                best_price = min(valid_p.values())
                best_platform = [k for k, v in valid_p.items() if v == best_price][0]
                
        name_l = p['product_name'].lower()
        if any(x in name_l for x in ["iphone", "macbook", "ipad", "gadget", "sony", "s24", "pixel", "laptop", "series", "watch"]): category = "Devices"
        elif any(x in name_l for x in ["protein", "whey", "creatine", "supplement", "fitness", "powder", "shoes", "puma"]): category = "Fitness"
        else: category = "Grocery"

        inventory_payload.append({
            "id": p['id'], "name": p['product_name'], "target": p['target_price'], "image": p['image_url'],
            "best_price": best_price, "best_platform": best_platform, "stats": stats, "urls_pool": urls_pool,
            "notify": p['notification_enabled'], "category": category
        })
    conn.close()
    return jsonify({"inventory": inventory_payload})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)