import sqlite3
import pandas as pd
from config import DB_NAME

def generate_report():
    try:
        conn = sqlite3.connect(DB_NAME)
        
        # 1. Fetch Raw Data
        df = pd.read_sql_query("SELECT * FROM job_market_trends", conn)
        
        if df.empty:
            print("\n[Analytics] Database is currently empty. Run worker.py first to collect data!")
            conn.close()
            return
            
        print("\n" + "="*20 + " SYSTEM REPORT: DISTRIBUTED SCRAPER " + "="*20)
        
        print("\n--- RAW DATA METRICS INGESTED ---")
        print(df.to_string(index=False))
        
        print("\n--- REPORT: MOST DEMANDED SKILLS BY REGION ---")
        skill_counts = df.groupby(['region', 'skill_demand']).size().reset_index(name='Demand Count')
        print(skill_counts.to_string(index=False))
        
        print("\n--- REPORT: AVERAGE REGIONAL STUDY COST ---")
        avg_cost = df.groupby('region')['avg_tuition_usd'].mean().reset_index()
        avg_cost.columns = ['Region', 'Mean Cost (USD)']
        print(avg_cost.to_string(index=False))
        
        print("\n" + "="*56 + "\n")
        conn.close()
        
    except Exception as e:
        print(f"[Analytics Error] Could not generate report: {str(e)}")

if __name__ == "__main__":
    generate_report()