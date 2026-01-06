import os
import sys
import threading
import time
import uvicorn
import eel
from backend.main import app

# 1. Start FastAPI in a separate thread
def start_fastapi():
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="warning")
    server = uvicorn.Server(config)
    server.run()

# 2. Main Execution
if __name__ == "__main__":
    # Start Backend
    print("BOOTING_SYSTEM: STARTING_BACKEND_THREAD...")
    api_thread = threading.Thread(target=start_fastapi, daemon=True)
    api_thread.start()

    # Wait a bit for FastAPI to be ready
    time.sleep(2)

    # Configure Eel to use the production build
    # We point Eel to the 'frontend/dist' directory
    dist_path = os.path.join("frontend", "dist")
    
    if not os.path.exists(dist_path):
        print(f"ERROR: Build folder not found at {dist_path}. Please run 'npm run build' first.")
        sys.exit(1)

    print("BOOTING_SYSTEM: LAUNCHING_DESKTOP_INTERFACE...")
    eel.init(dist_path)

    # Start the desktop window
    # size=(1400, 900) for a nice Cyberpunk cockpit feel
    try:
        eel.start('index.html', size=(1400, 900))
    except (SystemExit, KeyboardInterrupt):
        print("SYSTEM_SHUTDOWN: TERMINATING_PROCESSES...")
