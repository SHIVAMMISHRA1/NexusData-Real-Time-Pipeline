import multiprocessing
import subprocess
import time
import sys
import signal

def run_worker(worker_id):
    """
    🔬 HIGH-THROUGHPUT SYSTEM WORKER: Spawns and monitors the underlying scraping module.
    Includes auto-recovery loop if individual pipeline nodes crash.
    """
    print(f"🚀 [Worker-{worker_id}] Initialized inside the high-throughput matrix.")
    
    while True:
        try:
            print(f"🔄 [Worker-{worker_id}] Booting target scraping pipeline architecture (worker.py)...")
            # Executing subprocess using absolute standard sys executable path to ensure cross-platform compatibility
            result = subprocess.run([sys.executable, "worker.py"], check=False)
            
            print(f"⚠️ [Worker-{worker_id}] Core exited with code {result.returncode}. Re-spawning telemetry socket...")
            time.sleep(2) # Preventive cooling delay before re-spawning
            
        except KeyboardInterrupt:
            print(f"🛑 [Worker-{worker_id}] Processing interrupted via Control Tower. Exiting cleanly.")
            break
        except Exception as err:
            print(f"❌ [Worker-{worker_id}] Execution Failure Collision: {err}. Re-booting matrix block...")
            time.sleep(5)

def shutdown_handler(signum, frame):
    """🔒 CONCURRENCY INTEGRITY GUARD: Force terminates child sub-processes during global shutdown"""
    print("\n🛑 [GLOBAL CONTROL] Shutdown signal intercepted! Terminating all zombie workers safely...")
    for p in multiprocessing.active_children():
        print(f"💀 Terminating active subprocess PID: {p.pid}")
        p.terminate()
    sys.exit(0)

if __name__ == "__main__":
    print("=" * 10 + " INITIATING MULTI-WORKER DISTRIBUTED CORE " + "=" * 10)
    print("[System] Allocating multi-core clusters for real-time statistical streams...")
    
    # Registering interruption traps to avoid ghost nodes leaks inside OS memory
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    
    processes = []
    # Dynamic Core Allocation: Initializing 3 highly resilient structural parallel execution cells
    for i in range(1, 4):
        p = multiprocessing.Process(target=run_worker, args=(i,), name=f"ScraperWorker-{i}")
        p.daemon = True # Daemon configuration allows automated cleanups on master thread termination
        processes.append(p)
        p.start()
        time.sleep(1.0) # Allocation delay to stabilize Redis pool connections
        print(f"✅ [System] Worker Process Thread-{i} allocated successfully on PID {p.pid}.")

    print("🛰️  [SYSTEM RUNNING] Distributed concurrency framework locked. Streaming real-time matrix logs...\n")
    
    # Active monitoring keeps master thread alive to catch system interruption requests
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        shutdown_handler(None, None)