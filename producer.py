import json
import redis
import sys
from config import REDIS_HOST, REDIS_PORT, QUEUE_NAME

def dispatch_tasks():
    """
    🛰️ HIGH-AVAILABILITY TASK PRODUCER: Enqueues e-commerce telemetry targets into Redis cluster.
    Includes connection validation guards and queue duplication prevention filters.
    """
    print(f"🔄 Connecting to Redis Storage Node Cluster at [{REDIS_HOST}:{REDIS_PORT}]...")
    
    try:
        # Initialize communication socket parameters with socket timeout bounds
        r = redis.Redis(
            host=REDIS_HOST, 
            port=REDIS_PORT, 
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        
        # ⚡ CONNECTION HEALTH TEST CORE: Ping cluster before pushing bytes into data block
        r.ping()
        print("✅ Redis socket pipeline connection verified successfully!")
        
    except redis.exceptions.ConnectionError as conn_err:
        print(f"❌ [REDIS COLLISION ERROR] Target instance unreachable: {conn_err}")
        print("💡 Solution Blueprint: Local system parameters verification -> Start Redis Server via terminal.")
        sys.exit(1)

    # Cleaned dynamic real-world e-commerce assets catalog metadata targets
    mock_targets = [
        {"url": "https://www.amazon.in/dp/B0CHX1W151", "platform": "Amazon", "context": "iPhone 15 Pro Max (256 GB)"},
        {"url": "https://www.flipkart.com/apple-iphone-15", "platform": "Flipkart", "context": "Optimum Nutrition Whey Gold Standard 2KG"},
        {"url": "https://www.croma.com/sony-headphones/p/271255", "platform": "Croma", "context": "Sony WH-1000XM5 Premium Headphones"},
        {"url": "https://www.reliancedigital.in/samsung-s24", "platform": "RelianceDigital", "context": "Samsung Galaxy S24 Ultra"}
    ]
    
    print(f"\n🚀 Fetching queue diagnostics: Scanning existing nodes inside '{QUEUE_NAME}' matrix...")
    
    # 🔐 IDEMPOTENCY FILTER GUARD: Fetch existing elements inside current execution buffer memory
    try:
        existing_items_raw = r.lrange(QUEUE_NAME, 0, -1)
        existing_contexts = set()
        for raw_item in existing_items_raw:
            try:
                parsed = json.loads(raw_item)
                if 'context' in parsed:
                    existing_contexts.add(parsed['context'])
            except json.JSONDecodeError:
                continue
    except Exception:
        existing_contexts = set()

    print("📦 Publishing verified configurations to execution pipelines...")
    
    tasks_enqueued_count = 0
    
    for target in mock_targets:
        # Prevent insertion loops if identical context is locked inside queue buffer cells
        if target['context'] in existing_contexts:
            print(f"ℹ️ [Skipped Duplicate] Tracker for '{target['context']}' already exists inside Redis buffer cache.")
            continue
            
        try:
            serialized_payload = json.dumps(target)
            r.rpush(QUEUE_NAME, serialized_payload)
            print(f"   🔹 [Enqueued Success] Mapped target node -> {target['context']} | Route: {target['platform']}")
            tasks_enqueued_count += 1
        except Exception as push_err:
            print(f"❌ Failed to enqueue payload item '{target['context']}': {push_err}")
            
    print(f"\n📊 [PRODUCER COMPLETE] Enqueued {tasks_enqueued_count} raw tracking matrices to distributed workers pipeline grid.")

if __name__ == "__main__":
    dispatch_tasks()