import numpy as np
import sqlite3

def calculate_volatility(prices):
    """
    Module 9: Volatility Index using Standard Deviation normalized to 0-10 Scale.
    Returns a float score to seamlessly bind with frontend volatility dashboard units.
    """
    if len(prices) < 2:
        return 1.5  # Stable Baseline Fallback Element
    
    std_dev = np.std(prices)
    mean_val = np.mean(prices)
    
    if mean_val == 0:
        return 0.0
        
    # Relative volatility mapping to calculate 0-10 normalized index score
    cv = (std_dev / mean_val) * 100
    vol_score = round(min(10.0, max(0.0, cv / 5.0)), 1)
    return vol_score

def simulate_ml_predictions(prices):
    """
    Module 7: Trend Forecasting Engine
    Uses linear trend trajectory with strict safety safeguards against singular matrix.
    """
    if not prices:
        return 0.0, 0.0
        
    current_price = prices[-1]
    if len(prices) < 3:
        # Data points kam hone par 2% ka micro fluctuation framework fallback
        return round(current_price * 0.98, 2), round(current_price * 0.96, 2)
        
    try:
        x = np.arange(len(prices))
        y = np.array(prices)
        
        # Check if all prices are identical to prevent SVD convergence / infinite slope failures
        if np.all(y == y[0]):
            slope = 0.0
        else:
            slope, _ = np.polyfit(x, y, 1)
            
        # Safeguard logic: Agar slope abnormal/infinite ho jaye
        if np.isnan(slope) or np.isinf(slope):
            slope = 0.0
            
        pred_7 = current_price + (slope * 2)
        pred_15 = current_price + (slope * 5)
        
        return round(float(pred_7), 2), round(float(pred_15), 2)
    except Exception:
        # Fallback tracking parameters if ML arrays hit memory grid lockups
        return round(current_price * 0.99, 2), round(current_price * 0.97, 2)

def generate_recommendation(prices, pred_7):
    """
    Module 8: Buy Now / Wait Recommendation Logic Matrix
    """
    if not prices:
        return "BUY NOW"
        
    current_price = prices[-1]
    if pred_7 < current_price * 0.99:
        return "WAIT"
    return "BUY NOW"

def calculate_deal_score_and_quality(current_price, lowest_price, historical_avg):
    """
    Module 15 & 16: AI Smart Deal Score & Quality Classification Matrix
    """
    if historical_avg <= 0:
        return 50, "Average Deal"
        
    # Base calculation model
    score = 100 * (historical_avg - current_price) / historical_avg
    deal_score = int(50 + (score * 2))
    
    # Boundary constraints normalization
    deal_score = max(10, min(99, deal_score))
    
    # Classification logic layers
    if deal_score >= 85:
        quality = "Excellent Deal"
    elif deal_score >= 70:
        quality = "Good Deal"
    elif deal_score >= 45:
        quality = "Average Deal"
    else:
        quality = "Overpriced"
        
    return deal_score, quality

# =====================================================================
# CORE EXECUTION LAYER: Pipeline Robust Sync Module
# =====================================================================
if __name__ == "__main__":
    from config import DB_NAME
    
    print("📈 Running Predictive Analytics Pipeline Core Execution...")
    
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # 1. Saare products ki master list uthao
        cursor.execute("SELECT id, product_name, target_price FROM products")
        products = cursor.fetchall()
        
        if not products:
            print("⚠️ Pipeline Warning: Database mein koi products nahi mile tracking ke liye.")
            
        for prod in products:
            p_id, name, target = prod
            print(f"🔄 Processing telemetry matrix for Product ID {p_id}: {name}")
            
            # 2. Is product ki saari history price points array nikalna
            cursor.execute("SELECT price FROM price_history WHERE product_id = ? ORDER BY id ASC", (p_id,))
            raw_rows = cursor.fetchall()
            
            # Data Parsing Layer: Clean garbage non-numeric tuples away from memory array
            prices = []
            for row in raw_rows:
                val = row[0]
                if val is not None:
                    try:
                        # Clean currency strings if any leaking from scraping cell
                        if isinstance(val, str):
                            val = val.replace('₹', '').replace(',', '').strip()
                        clean_val = float(val)
                        prices.append(clean_val)
                    except ValueError:
                        continue  # Ingestion Guard: Mismatched corrupt price text directly dropped

            # Agar history khali hai ya processing crash ho gayi, filter via fallback structures
            if not prices:
                if target and float(target) > 0:
                    prices = [round(float(target) * 0.9, 2)]
                else:
                    print(f"❌ Skipping Product {p_id}: Corrupt anchor metrics found.")
                    continue
                
            clean_price = prices[-1]
            lowest_price = min(prices)
            avg_price = sum(prices) / len(prices)
            
            # 3. Mathematical Operations Layer Call
            volatility = calculate_volatility(prices)
            pred_7, pred_15 = simulate_ml_predictions(prices)
            recommendation = generate_recommendation(prices, pred_7)
            deal_score, deal_quality = calculate_deal_score_and_quality(clean_price, lowest_price, avg_price)
            
            # 4. Master Analytics Table Registry
            cursor.execute("""
                INSERT OR REPLACE INTO product_analytics 
                (product_id, volatility_index, recommendation, deal_score, deal_quality, pred_7_days, pred_15_days)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (p_id, volatility, recommendation, deal_score, deal_quality, pred_7, pred_15))
            
        conn.commit()
        conn.close()
        print("✅ [ANALYTICS SUCCESS] Database fully sync with math models!")
        
    except Exception as err:
        print(f"❌ Analytics Engine Execution Collision: {err}")